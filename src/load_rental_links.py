from getpass import getpass
from pathlib import Path

import pandas as pd
import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[1]

audit = pd.read_csv(
    PROJECT_ROOT / "docs" / "rental_geography_name_audit.csv",
    dtype={
        "sal_code": "string",
        "boundary_equivalence_verified": "boolean",
    },
)

methods = ["name_match_candidate", "alias_match_candidate"]
links = audit.loc[audit["match_status"].isin(methods)].copy()

required = [
    "source_region", "source_area", "sal_code",
    "match_status", "boundary_equivalence_verified",
]
if links[required].isna().any().any():
    raise ValueError("Missing candidate link values")

if links["boundary_equivalence_verified"].any():
    raise ValueError("Expected unverified candidate links")

if links.duplicated(["source_region", "source_area", "sal_code"]).any():
    raise ValueError("Duplicate candidate links")

password = getpass("Password for unimove_dev: ")

with psycopg.connect(
    host="localhost",
    port=5432,
    dbname="unimove",
    user="unimove_dev",
    password=password,
    connect_timeout=10,
) as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM unimove.rental_suburb_link")
        if cursor.fetchone()[0] != 0:
            raise ValueError("Link table must be empty for initial load")

        cursor.execute("""
            SELECT source_region, source_area, rental_area_id
            FROM unimove.rental_area
            WHERE include_in_melbourne_scope
        """)
        area_ids = {
            (region, area): area_id
            for region, area, area_id in cursor.fetchall()
        }

        rows = []
        for row in links.itertuples(index=False):
            area_key = (row.source_region, row.source_area)
            if area_key not in area_ids:
                raise ValueError(f"Unknown Melbourne rental area: {area_key}")

            evidence = (
                "config/rental_area_aliases.csv"
                if row.match_status == "alias_match_candidate"
                else "docs/rental_geography_name_audit.csv"
            )

            rows.append((
                area_ids[area_key],
                str(row.sal_code),
                row.match_status,
                False,
                evidence,
            ))

        cursor.executemany("""
            INSERT INTO unimove.rental_suburb_link (
                rental_area_id, sal_code, match_method,
                boundary_equivalence_verified, evidence_reference
            )
            VALUES (%s, %s, %s, %s, %s)
        """, rows)

        cursor.execute("""
            SELECT match_method, count(*)
            FROM unimove.rental_suburb_link
            GROUP BY match_method
            ORDER BY match_method
        """)
        summary = cursor.fetchall()

        if sum(count for _, count in summary) != len(links):
            raise ValueError("Loaded link count differs from input")

        for method, count in summary:
            print(f"{method}: {count}")

print("Candidate link load committed successfully.")
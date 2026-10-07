from getpass import getpass
from pathlib import Path

import pandas as pd
import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[1]

review = pd.read_csv(
    PROJECT_ROOT / "docs" / "campus_rental_label_review.csv",
    dtype={"sal_code": "string"},
)

links = review.loc[
    review["review_status"].eq("explicit_label_component_candidate")
].copy()

required = ["sal_code", "source_region", "source_area"]
if links[required].isna().any().any():
    raise ValueError("Missing component candidate values")

if links.duplicated(required).any():
    raise ValueError("Duplicate component candidates")

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
        cursor.execute("""
            SELECT source_region, source_area, rental_area_id
            FROM unimove.rental_area
            WHERE include_in_melbourne_scope
        """)
        area_ids = {
            (region, area): area_id
            for region, area, area_id in cursor.fetchall()
        }

        inserted = 0

        for row in links.itertuples(index=False):
            area_key = (row.source_region, row.source_area)
            if area_key not in area_ids:
                raise ValueError(f"Unknown rental area: {area_key}")

            cursor.execute("""
                INSERT INTO unimove.rental_suburb_link (
                    rental_area_id, sal_code, match_method,
                    boundary_equivalence_verified, evidence_reference
                )
                VALUES (%s, %s, %s, false, %s)
                ON CONFLICT (rental_area_id, sal_code) DO NOTHING
            """, (
                area_ids[area_key],
                str(row.sal_code),
                "explicit_label_component_candidate",
                "docs/campus_rental_label_review.csv",
            ))
            inserted += cursor.rowcount

        cursor.execute("""
            SELECT match_method, count(*)
            FROM unimove.rental_suburb_link
            GROUP BY match_method
            ORDER BY match_method
        """)

        print("New links inserted:", inserted)
        for method, count in cursor.fetchall():
            print(f"{method}: {count}")

print("Component candidate load committed successfully.")
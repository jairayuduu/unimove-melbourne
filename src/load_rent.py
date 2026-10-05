from decimal import Decimal
from getpass import getpass
from pathlib import Path

import pandas as pd
import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[1]

rent = pd.read_csv(
    PROJECT_ROOT / "data" / "interim" / "rent_all_categories.csv",
    parse_dates=["period_start", "period_end"],
    dtype={
        "lease_count": "Int64",
        "median_weekly_rent_aud": "Float64",
    },
)
scope = pd.read_csv(
    PROJECT_ROOT / "config" / "rental_region_scope.csv",
    dtype={"include_in_melbourne_scope": "boolean"},
)

if scope.isna().any().any():
    raise ValueError("Missing scope configuration values")

rent = rent.merge(
    scope,
    on="source_region",
    how="left",
    validate="many_to_one",
)

if rent["include_in_melbourne_scope"].isna().any():
    raise ValueError("A rental region has no scope decision")

key = [
    "source_region", "source_area",
    "dwelling_category", "period_end",
]
if rent[key].isna().any().any() or rent.duplicated(key).any():
    raise ValueError("Missing or duplicate observation keys")

areas = rent[
    ["source_region", "source_area", "include_in_melbourne_scope"]
].drop_duplicates()

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
            SELECT
                (SELECT count(*) FROM unimove.rental_area),
                (SELECT count(*) FROM unimove.rental_observation)
        """)
        if cursor.fetchone() != (0, 0):
            raise ValueError("Rental tables must be empty for initial load")

        cursor.executemany("""
            INSERT INTO unimove.rental_area (
                source_region, source_area, include_in_melbourne_scope
            )
            VALUES (%s, %s, %s)
        """, [
            (row.source_region, row.source_area,
             bool(row.include_in_melbourne_scope))
            for row in areas.itertuples(index=False)
        ])

        cursor.execute("""
            SELECT source_region, source_area, rental_area_id
            FROM unimove.rental_area
        """)
        area_ids = {
            (region, area): area_id
            for region, area, area_id in cursor.fetchall()
        }

        # COPY streams observations efficiently into PostgreSQL.
        with cursor.copy("""
            COPY unimove.rental_observation (
                rental_area_id, dwelling_category,
                period_start, period_end, period_basis,
                lease_count, median_weekly_rent_aud
            ) FROM STDIN
        """) as copy:
            for row in rent.itertuples(index=False):
                copy.write_row((
                    area_ids[(row.source_region, row.source_area)],
                    row.dwelling_category,
                    row.period_start.date(),
                    row.period_end.date(),
                    row.period_basis,
                    None if pd.isna(row.lease_count)
                    else int(row.lease_count),
                    None if pd.isna(row.median_weekly_rent_aud)
                    else Decimal(str(row.median_weekly_rent_aud)),
                ))

        cursor.execute("""
            SELECT
                (SELECT count(*) FROM unimove.rental_area),
                (SELECT count(*) FROM unimove.rental_observation),
                (SELECT count(*) FROM unimove.rental_area
                 WHERE include_in_melbourne_scope)
        """)
        counts = cursor.fetchone()

        expected = (
            len(areas),
            len(rent),
            int(areas["include_in_melbourne_scope"].sum()),
        )
        if counts != expected:
            raise ValueError("Database counts differ from input counts")

        print("Rental areas loaded:", counts[0])
        print("Rental observations loaded:", counts[1])
        print("Melbourne rental areas:", counts[2])

print("Transaction committed successfully.")
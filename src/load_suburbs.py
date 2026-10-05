from getpass import getpass
from pathlib import Path

import geopandas as gpd
import pandas as pd
import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

suburbs = gpd.read_file(
    DATA_DIR / "melbourne_suburbs_2021.geojson"
)
population = pd.read_csv(
    DATA_DIR / "melbourne_suburb_population_2021.csv",
    dtype={"sal_code": "string"},
)

suburbs["sal_code"] = suburbs["sal_code"].astype("string")

if suburbs.crs is None or suburbs.crs.to_epsg() != 4326:
    raise ValueError("Expected suburb geometry in EPSG:4326")

for label, frame in [("suburbs", suburbs), ("population", population)]:
    if frame["sal_code"].isna().any():
        raise ValueError(f"Missing codes in {label}")
    if frame["sal_code"].duplicated().any():
        raise ValueError(f"Duplicate codes in {label}")

if set(suburbs["sal_code"]) != set(population["sal_code"]):
    raise ValueError("Suburb and population codes differ")

suburb_rows = [
    (
        str(row.sal_code),
        row.suburb_name,
        int(row.geography_year),
        row.scope_method,
        float(row.outside_melbourne_pct),
        bool(row.boundary_review_required),
        float(row.area_sq_km),
        row.geometry.wkt,
    )
    for row in suburbs.itertuples(index=False)
]

population_rows = [
    (
        str(row.sal_code),
        int(row.census_year),
        int(row.population_total),
        int(row.population_18_24),
    )
    for row in population.itertuples(index=False)
]

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
        # This initial loader expects empty tables.
        cursor.execute("""
            SELECT
                (SELECT count(*) FROM unimove.suburb),
                (SELECT count(*) FROM unimove.suburb_population)
        """)
        if cursor.fetchone() != (0, 0):
            raise ValueError(
                "Tables already contain data; initial load cancelled"
            )

        cursor.executemany("""
            INSERT INTO unimove.suburb (
                sal_code, suburb_name, geography_year, scope_method,
                outside_melbourne_pct, boundary_review_required,
                area_sq_km, geom
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                public.ST_Multi(public.ST_GeomFromText(%s, 4326))
            )
        """, suburb_rows)

        cursor.executemany("""
            INSERT INTO unimove.suburb_population (
                sal_code, census_year,
                population_total, population_18_24
            )
            VALUES (%s, %s, %s, %s)
        """, population_rows)

        cursor.execute("""
            SELECT
                (SELECT count(*) FROM unimove.suburb),
                (SELECT count(*) FROM unimove.suburb_population)
        """)
        counts = cursor.fetchone()

        if counts != (len(suburbs), len(population)):
            raise ValueError("Database row counts differ from source files")

        print("Suburb rows loaded:", counts[0])
        print("Population rows loaded:", counts[1])

print("Transaction committed successfully.")
from getpass import getpass
from pathlib import Path

import pandas as pd
import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"

register = pd.read_csv(CONFIG_DIR / "campuses.csv")
locations = pd.read_csv(CONFIG_DIR / "campus_locations.csv")

campuses = register.merge(
    locations,
    on="campus_id",
    how="outer",
    validate="one_to_one",
    indicator=True,
)

if not campuses["_merge"].eq("both").all():
    raise ValueError("Campus register and location identifiers differ")

if campuses.drop(columns="_merge").isna().any().any():
    raise ValueError("Missing campus details")

for column in ["latitude", "longitude"]:
    campuses[column] = pd.to_numeric(
        campuses[column], errors="raise"
    )

if not campuses["latitude"].between(-90, 90).all():
    raise ValueError("Invalid latitude")
if not campuses["longitude"].between(-180, 180).all():
    raise ValueError("Invalid longitude")

rows = [
    (
        row.campus_id,
        row.university_name,
        row.campus_name,
        row.source_url,
        row.coordinate_source_url,
        row.location_method,
        float(row.longitude),
        float(row.latitude),
    )
    for row in campuses.itertuples(index=False)
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
        cursor.execute("SELECT count(*) FROM unimove.campus")
        if cursor.fetchone()[0] != 0:
            raise ValueError("Campus table must be empty for initial load")

        cursor.executemany("""
            INSERT INTO unimove.campus (
                campus_id, university_name, campus_name,
                source_url, coordinate_source_url,
                location_method, geom
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                public.ST_SetSRID(public.ST_MakePoint(%s, %s), 4326)
            )
        """, rows)

        cursor.execute("""
            SELECT campus_id,
                   public.ST_Y(geom) AS latitude,
                   public.ST_X(geom) AS longitude
            FROM unimove.campus
            ORDER BY campus_id
        """)
        loaded = cursor.fetchall()

        if len(loaded) != len(campuses):
            raise ValueError("Loaded campus count differs from input")

        for campus_id, latitude, longitude in loaded:
            print(f"{campus_id}: {latitude}, {longitude}")

print("Campus load committed successfully.")
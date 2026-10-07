from getpass import getpass
from pathlib import Path
import re

import pandas as pd
import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def normalise(value):
    value = str(value).casefold().strip()
    value = re.sub(r"\s*\(vic\.?\)\s*$", "", value)
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


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
            SELECT sal_code, suburb_name
            FROM unimove.campus_rental_candidates
            WHERE campus_id = 'monash_clayton'
              AND dwelling_category = '1 bedroom flat'
              AND straight_line_km <= 5
              AND rental_coverage_status = 'no_candidate_link'
            ORDER BY suburb_name
        """)
        nearby = cursor.fetchall()

        cursor.execute("""
            SELECT source_region, source_area
            FROM unimove.rental_area
            WHERE include_in_melbourne_scope
            ORDER BY source_region, source_area
        """)
        rental_areas = cursor.fetchall()

rows = []

for sal_code, suburb_name in nearby:
    matches = [
        (region, area)
        for region, area in rental_areas
        if "-" in area
        and normalise(suburb_name) in {
            normalise(part) for part in area.split("-")
        }
    ]

    if matches:
        for region, area in matches:
            rows.append({
                "sal_code": sal_code,
                "suburb_name": suburb_name,
                "source_region": region,
                "source_area": area,
                "review_status": "explicit_label_component_candidate",
            })
    else:
        rows.append({
            "sal_code": sal_code,
            "suburb_name": suburb_name,
            "source_region": "",
            "source_area": "",
            "review_status": "no_explicit_label_match",
        })

report = pd.DataFrame(rows, columns=[
    "sal_code", "suburb_name", "source_region",
    "source_area", "review_status",
])

print(report.to_string(index=False))

report.to_csv(
    PROJECT_ROOT / "docs" / "clayton_rental_label_review.csv",
    index=False,
)
print("\nReview report saved.")
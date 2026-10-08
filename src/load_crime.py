from datetime import date
from getpass import getpass
from pathlib import Path

import pandas as pd
import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AREA_KEYS = ["source_lga", "source_postcode", "source_suburb"]


def main():
    detail = pd.read_csv(
        PROJECT_ROOT / "data" / "interim"
        / "crime_latest_source_detail.csv",
        dtype=str,
        keep_default_na=False,
    )
    links = pd.read_csv(
        PROJECT_ROOT / "docs"
        / "crime_geography_name_candidates.csv",
        dtype=str,
        keep_default_na=False,
    )

    if detail.empty or links.empty:
        raise ValueError("An input file is empty")

    observation_keys = AREA_KEYS + [
        "period_end",
        "offence_division",
        "offence_subdivision",
        "offence_subgroup",
    ]
    if detail.duplicated(observation_keys).any():
        raise ValueError("Duplicate crime observation keys")
    if links.duplicated(AREA_KEYS + ["sal_code"]).any():
        raise ValueError("Duplicate candidate links")

    allowed = {"name_match_candidate", "alias_match_candidate"}
    if not links["match_status"].isin(allowed).all():
        raise ValueError("Unresolved or unsupported candidate method")
    if not links["boundary_equivalence_verified"].str.lower().eq(
        "false"
    ).all():
        raise ValueError("Unexpected boundary verification flag")

    areas = detail[AREA_KEYS].drop_duplicates()
    counts = pd.to_numeric(detail["offence_count"], errors="raise")
    if counts.lt(0).any() or counts.mod(1).ne(0).any():
        raise ValueError("Invalid offence counts")
    detail["offence_count"] = counts.astype("int64")

    password = getpass("Password for unimove_dev: ")

    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname="unimove",
        user="unimove_dev",
        password=password,
    ) as connection:
        with connection.cursor() as cursor:
            for table in [
                "crime_source_area",
                "crime_observation",
                "crime_suburb_link",
            ]:
                cursor.execute(
                    f"SELECT count(*) FROM unimove.{table}"
                )
                if cursor.fetchone()[0]:
                    raise ValueError(
                        f"{table} already contains data; stopping"
                    )

            cursor.executemany(
                """
                INSERT INTO unimove.crime_source_area (
                    source_lga, source_postcode, source_suburb
                )
                VALUES (%s, %s, %s)
                """,
                list(areas.itertuples(index=False, name=None)),
            )

            cursor.execute("""
                SELECT source_lga, source_postcode, source_suburb,
                       crime_area_id
                FROM unimove.crime_source_area
            """)
            area_ids = {
                (lga, postcode, suburb): area_id
                for lga, postcode, suburb, area_id
                in cursor.fetchall()
            }

            with cursor.copy("""
                COPY unimove.crime_observation (
                    crime_area_id, period_start, period_end,
                    offence_division, offence_subdivision,
                    offence_subgroup, offence_count
                ) FROM STDIN
            """) as copy:
                for row in detail.itertuples(index=False):
                    key = (
                        row.source_lga,
                        row.source_postcode,
                        row.source_suburb,
                    )
                    copy.write_row((
                        area_ids[key],
                        date.fromisoformat(row.period_start),
                        date.fromisoformat(row.period_end),
                        row.offence_division,
                        row.offence_subdivision,
                        row.offence_subgroup,
                        int(row.offence_count),
                    ))

            link_rows = []
            for row in links.itertuples(index=False):
                key = (
                    row.source_lga,
                    row.source_postcode,
                    row.source_suburb,
                )
                if key not in area_ids:
                    raise ValueError(f"Unknown source area: {key}")

                link_rows.append((
                    area_ids[key],
                    row.sal_code,
                    row.match_status,
                    False,
                    "docs/crime_geography_name_candidates.csv",
                ))

            cursor.executemany(
                """
                INSERT INTO unimove.crime_suburb_link (
                    crime_area_id, sal_code, match_method,
                    boundary_equivalence_verified, evidence_reference
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                link_rows,
            )

            for table, expected in [
                ("crime_source_area", len(areas)),
                ("crime_observation", len(detail)),
                ("crime_suburb_link", len(links)),
            ]:
                cursor.execute(
                    f"SELECT count(*) FROM unimove.{table}"
                )
                loaded = cursor.fetchone()[0]
                if loaded != expected:
                    raise ValueError(f"Row-count mismatch: {table}")
                print(f"{table}: {loaded:,}")

            cursor.execute("""
                SELECT sum(offence_count)
                FROM unimove.crime_observation
            """)
            if cursor.fetchone()[0] != int(counts.sum()):
                raise ValueError("Offence total differs from source CSV")

            print("Source CSV and database offence totals match.")

    print("Transaction committed successfully.")


if __name__ == "__main__":
    main()
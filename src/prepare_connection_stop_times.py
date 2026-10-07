import argparse
from datetime import date
from getpass import getpass
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw" / "transport" / "gtfs.zip"
OUTPUT = PROJECT_ROOT / "data" / "interim"

COLUMNS = [
    "trip_id",
    "stop_id",
    "stop_sequence",
    "arrival_time",
    "departure_time",
    "pickup_type",
    "drop_off_type",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="2026-10-08")
    args = parser.parse_args()
    day = date.fromisoformat(args.date)
    date_key = day.strftime("%Y%m%d")

    trips = pd.read_csv(
        OUTPUT / f"transport_trips_{date_key}.csv",
        dtype=str,
        keep_default_na=False,
    )

    password = getpass("Password for unimove_dev: ")
    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname="unimove",
        user="unimove_dev",
        password=password,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT feed_id, stop_id
                FROM unimove.campus_transport_stops
                UNION
                SELECT b.feed_id, b.stop_id
                FROM unimove.suburb_boarding_candidates AS b
                JOIN unimove.campus_suburb_distance AS d
                  ON d.sal_code = b.sal_code
                WHERE d.straight_line_km <= 5
            """)
            relevant = pd.DataFrame(
                cursor.fetchall(),
                columns=["feed_id", "stop_id"],
            )

    destination = OUTPUT / f"connection_stop_times_{date_key}.csv"
    temporary = destination.with_suffix(".tmp")
    totals = {}

    # Stream the output rather than keeping all timetable rows in memory.
    with temporary.open("w", encoding="utf-8", newline="") as output:
        pd.DataFrame(
            columns=["feed_id", "service_date"] + COLUMNS
        ).to_csv(output, index=False)

        with ZipFile(RAW) as outer:
            for feed_id in ["2", "3", "4"]:
                active_trips = set(
                    trips.loc[
                        trips["feed_id"].eq(feed_id), "trip_id"
                    ]
                )
                relevant_stops = set(
                    relevant.loc[
                        relevant["feed_id"].eq(feed_id), "stop_id"
                    ]
                )
                total = 0

                with ZipFile(
                    BytesIO(
                        outer.read(f"{feed_id}/google_transit.zip")
                    )
                ) as inner:
                    matches = [
                        name for name in inner.namelist()
                        if Path(name).name == "stop_times.txt"
                    ]
                    if len(matches) != 1:
                        raise ValueError("Expected one stop_times.txt")

                    with inner.open(matches[0]) as source:
                        chunks = pd.read_csv(
                            source,
                            dtype=str,
                            keep_default_na=False,
                            encoding="utf-8-sig",
                            chunksize=250_000,
                        )
                        for chunk in chunks:
                            for column in ["pickup_type", "drop_off_type"]:
                                if column not in chunk:
                                    chunk[column] = ""

                            selected = chunk.loc[
                                chunk["trip_id"].isin(active_trips)
                                & chunk["stop_id"].isin(relevant_stops),
                                COLUMNS,
                            ].copy()

                            if selected.empty:
                                continue

                            selected.insert(0, "feed_id", feed_id)
                            selected.insert(1, "service_date", args.date)
                            selected.to_csv(
                                output, index=False, header=False
                            )
                            total += len(selected)

                totals[feed_id] = total
                print(f"Feed {feed_id}: {total:,} relevant stop-time rows")

    if sum(totals.values()) == 0:
        raise ValueError("No relevant stop times found")

    temporary.replace(destination)
    print(f"\nService date: {args.date}")
    print(f"Total rows: {sum(totals.values()):,}")
    print(f"Saved: {destination}")


if __name__ == "__main__":
    main()
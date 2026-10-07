import csv
from getpass import getpass
from pathlib import Path

import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    PROJECT_ROOT / "data" / "interim"
    / "transport_boarding_stops.csv"
)


def main():
    with SOURCE.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))

    if not rows:
        raise ValueError("Transport CSV is empty.")

    keys = [(row["feed_id"], row["stop_id"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate feed/stop keys in CSV.")

    password = getpass("Password for unimove_dev: ")

    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname="unimove",
        user="unimove_dev",
        password=password,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM unimove.transport_stop"
            )
            if cursor.fetchone()[0] != 0:
                raise ValueError(
                    "Transport table already contains data. "
                    "Stopping to avoid an accidental duplicate load."
                )

            cursor.executemany(
                """
                INSERT INTO unimove.transport_stop (
                    feed_id, stop_id, transport_mode,
                    stop_name, parent_station, geom
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    public.ST_SetSRID(
                        public.ST_MakePoint(%s, %s),
                        4326
                    )
                )
                """,
                [
                    (
                        row["feed_id"],
                        row["stop_id"],
                        row["transport_mode"],
                        row["stop_name"],
                        row["parent_station"] or None,
                        float(row["stop_lon"]),
                        float(row["stop_lat"]),
                    )
                    for row in rows
                ],
            )

            cursor.execute("""
                SELECT transport_mode, count(*)
                FROM unimove.transport_stop
                GROUP BY transport_mode
                ORDER BY transport_mode
            """)
            for mode, count in cursor.fetchall():
                print(f"{mode}: {count:,}")

            cursor.execute(
                "SELECT count(*) FROM unimove.transport_stop"
            )
            loaded = cursor.fetchone()[0]

            if loaded != len(rows):
                raise ValueError("Loaded row count differs from CSV.")

            print(f"Total stops loaded: {loaded:,}")

    print("Transaction committed successfully.")


if __name__ == "__main__":
    main()
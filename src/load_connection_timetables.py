import argparse
import csv
import re
from datetime import date
from getpass import getpass
from pathlib import Path

import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "data" / "interim"


def seconds(value):
    if not value:
        return None

    match = re.fullmatch(r"(\d{2,}):([0-5]\d):([0-5]\d)", value)
    if not match:
        raise ValueError(f"Invalid timetable time: {value!r}")

    hours, minutes, secs = map(int, match.groups())
    return hours * 3600 + minutes * 60 + secs


def restriction(value):
    result = int(value) if value else 0
    if result not in {0, 1, 2, 3}:
        raise ValueError(f"Invalid passenger restriction: {value!r}")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="2026-10-08")
    args = parser.parse_args()
    service_date = date.fromisoformat(args.date)
    date_key = service_date.strftime("%Y%m%d")

    trip_file = INPUT / f"transport_trips_{date_key}.csv"
    stop_file = INPUT / f"connection_stop_times_{date_key}.csv"

    # Check both input files exist before opening a database transaction.
    for source in [trip_file, stop_file]:
        if not source.is_file():
            raise FileNotFoundError(source)

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
                SELECT count(*)
                FROM unimove.transport_service_trip
                WHERE service_date = %s
            """, (service_date,))
            if cursor.fetchone()[0]:
                raise ValueError(
                    "This service date is already loaded. Stopping."
                )

            trip_count = 0
            with trip_file.open(
                encoding="utf-8-sig", newline=""
            ) as source:
                with cursor.copy("""
                    COPY unimove.transport_service_trip (
                        service_date, feed_id, trip_id, route_id,
                        transport_mode, route_short_name, route_long_name
                    ) FROM STDIN
                """) as copy:
                    for row in csv.DictReader(source):
                        if row["service_date"] != args.date:
                            raise ValueError("Unexpected trip service date")

                        copy.write_row((
                            service_date,
                            row["feed_id"],
                            row["trip_id"],
                            row["route_id"],
                            row["transport_mode"],
                            row["route_short_name"],
                            row["route_long_name"],
                        ))
                        trip_count += 1

            stop_count = 0
            missing_arrivals = 0
            missing_departures = 0

            with stop_file.open(
                encoding="utf-8-sig", newline=""
            ) as source:
                with cursor.copy("""
                    COPY unimove.transport_connection_stop_time (
                        service_date, feed_id, trip_id, stop_sequence,
                        stop_id, arrival_seconds, departure_seconds,
                        pickup_type, drop_off_type
                    ) FROM STDIN
                """) as copy:
                    for row in csv.DictReader(source):
                        if row["service_date"] != args.date:
                            raise ValueError("Unexpected stop service date")

                        arrival = seconds(row["arrival_time"])
                        departure = seconds(row["departure_time"])

                        if (
                            arrival is not None
                            and departure is not None
                            and departure < arrival
                        ):
                            raise ValueError(
                                "Departure precedes arrival at a stop"
                            )

                        copy.write_row((
                            service_date,
                            row["feed_id"],
                            row["trip_id"],
                            int(row["stop_sequence"]),
                            row["stop_id"],
                            arrival,
                            departure,
                            restriction(row["pickup_type"]),
                            restriction(row["drop_off_type"]),
                        ))

                        stop_count += 1
                        missing_arrivals += arrival is None
                        missing_departures += departure is None

            if not trip_count or not stop_count:
                raise ValueError("An input file contains no records")

            cursor.execute("""
                SELECT
                    t.transport_mode,
                    count(*) AS stop_time_rows,
                    count(DISTINCT s.trip_id) AS represented_trips
                FROM unimove.transport_connection_stop_time AS s
                JOIN unimove.transport_service_trip AS t
                  USING (service_date, feed_id, trip_id)
                WHERE s.service_date = %s
                GROUP BY t.transport_mode
                ORDER BY t.transport_mode
            """, (service_date,))

            for mode, rows, represented in cursor.fetchall():
                print(
                    f"{mode}: {rows:,} stop times; "
                    f"{represented:,} represented trips"
                )

            print(f"Trips loaded: {trip_count:,}")
            print(f"Stop times loaded: {stop_count:,}")
            print(f"Missing arrivals: {missing_arrivals:,}")
            print(f"Missing departures: {missing_departures:,}")

    print("Transaction committed successfully.")


if __name__ == "__main__":
    main()
import argparse
from datetime import date
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "data" / "raw" / "transport" / "gtfs.zip"
OUTPUT = PROJECT_ROOT / "data" / "interim"

FEEDS = {
    "2": "metropolitan_train",
    "3": "tram",
    "4": "bus",
}


def read_table(archive, filename):
    matches = [
        name for name in archive.namelist()
        if Path(name).name == filename
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one {filename}: {matches}")

    with archive.open(matches[0]) as source:
        return pd.read_csv(
            source,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="2026-10-08")
    args = parser.parse_args()

    travel_date = date.fromisoformat(args.date)
    date_key = travel_date.strftime("%Y%m%d")
    weekday = [
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday",
    ][travel_date.weekday()]

    OUTPUT.mkdir(parents=True, exist_ok=True)
    outputs = []

    print(f"Service date: {travel_date} ({weekday})")

    with ZipFile(SOURCE) as outer:
        for feed_id, mode in FEEDS.items():
            with ZipFile(
                BytesIO(outer.read(f"{feed_id}/google_transit.zip"))
            ) as inner:
                calendar = read_table(inner, "calendar.txt")
                exceptions = read_table(inner, "calendar_dates.txt")
                trips = read_table(inner, "trips.txt")
                routes = read_table(inner, "routes.txt")

                if calendar["service_id"].duplicated().any():
                    raise ValueError("Duplicate calendar service IDs")
                if exceptions.duplicated(["service_id", "date"]).any():
                    raise ValueError("Duplicate service/date exceptions")
                if not exceptions["exception_type"].isin(["1", "2"]).all():
                    raise ValueError("Unexpected exception type")

                active = set(
                    calendar.loc[
                        calendar["start_date"].le(date_key)
                        & calendar["end_date"].ge(date_key)
                        & calendar[weekday].eq("1"),
                        "service_id",
                    ]
                )

                daily_exceptions = exceptions.loc[
                    exceptions["date"].eq(date_key)
                ]
                active.difference_update(
                    daily_exceptions.loc[
                        daily_exceptions["exception_type"].eq("2"),
                        "service_id",
                    ]
                )
                active.update(
                    daily_exceptions.loc[
                        daily_exceptions["exception_type"].eq("1"),
                        "service_id",
                    ]
                )

                selected = trips.loc[
                    trips["service_id"].isin(active)
                ].merge(
                    routes[
                        [
                            "route_id", "route_short_name",
                            "route_long_name", "route_type",
                        ]
                    ],
                    on="route_id",
                    how="left",
                    validate="many_to_one",
                )

                if selected["route_type"].isna().any():
                    raise ValueError("Trip references an unknown route")

                replacement = selected[
                    "route_short_name"
                ].str.contains("replacement", case=False, na=False)
                excluded = int(replacement.sum())
                selected = selected.loc[~replacement].copy()

                if selected.empty:
                    raise ValueError(
                        f"No regular trips for {mode} on {travel_date}"
                    )
                if selected["trip_id"].duplicated().any():
                    raise ValueError("Duplicate trip IDs")

                selected.insert(0, "feed_id", feed_id)
                selected.insert(1, "transport_mode", mode)
                selected.insert(2, "service_date", args.date)
                outputs.append(selected)

                print(
                    f"{mode}: {len(active):,} active services; "
                    f"{len(selected):,} regular trips; "
                    f"{excluded:,} replacement trips excluded"
                )

    result = pd.concat(outputs, ignore_index=True)
    if result.duplicated(["feed_id", "trip_id"]).any():
        raise ValueError("Duplicate feed/trip keys")

    destination = OUTPUT / f"transport_trips_{date_key}.csv"
    result.to_csv(destination, index=False)
    print(f"\nSaved: {destination}")


if __name__ == "__main__":
    main()
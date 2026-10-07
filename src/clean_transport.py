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


def table_path(archive, filename):
    matches = [
        name for name in archive.namelist()
        if Path(name).name == filename
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one {filename}: {matches}")
    return matches[0]


def read_table(archive, filename):
    with archive.open(table_path(archive, filename)) as source:
        return pd.read_csv(
            source,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
        )


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    outputs = []

    with ZipFile(SOURCE) as outer:
        for feed_id, mode in FEEDS.items():
            feed_path = f"{feed_id}/google_transit.zip"

            with ZipFile(BytesIO(outer.read(feed_path))) as inner:
                routes = read_table(inner, "routes.txt")
                trips = read_table(inner, "trips.txt")
                stops = read_table(inner, "stops.txt")

                if stops["stop_id"].duplicated().any():
                    raise ValueError(f"Duplicate stop IDs: feed {feed_id}")

                if trips["trip_id"].duplicated().any():
                    raise ValueError(f"Duplicate trip IDs: feed {feed_id}")

                if not trips["route_id"].isin(routes["route_id"]).all():
                    raise ValueError(f"Unknown route IDs: feed {feed_id}")

                replacement = routes["route_short_name"].str.contains(
                    "replacement", case=False, na=False
                )
                regular_routes = routes.loc[~replacement, "route_id"]
                regular_trips = set(
                    trips.loc[
                        trips["route_id"].isin(regular_routes),
                        "trip_id",
                    ]
                )

                served_stops = set()
                unknown_trips = set()
                all_trips = set(trips["trip_id"])

                with inner.open(
                    table_path(inner, "stop_times.txt")
                ) as source:
                    chunks = pd.read_csv(
                        source,
                        usecols=["trip_id", "stop_id"],
                        dtype=str,
                        keep_default_na=False,
                        encoding="utf-8-sig",
                        chunksize=250_000,
                    )
                    for chunk in chunks:
                        unknown_trips.update(
                            set(chunk["trip_id"]) - all_trips
                        )
                        served_stops.update(
                            chunk.loc[
                                chunk["trip_id"].isin(regular_trips),
                                "stop_id",
                            ]
                        )

                if unknown_trips:
                    raise ValueError(
                        f"Unknown timetable trip IDs: feed {feed_id}"
                    )

                if served_stops - set(stops["stop_id"]):
                    raise ValueError(
                        f"Unknown timetable stop IDs: feed {feed_id}"
                    )

                # Keep served boarding stops/platforms only.
                boarding = stops["location_type"].isin(["", "0"])
                selected = stops.loc[
                    boarding & stops["stop_id"].isin(served_stops),
                    [
                        "stop_id",
                        "stop_name",
                        "stop_lat",
                        "stop_lon",
                        "parent_station",
                    ],
                ].copy()

                for column in ["stop_lat", "stop_lon"]:
                    selected[column] = pd.to_numeric(
                        selected[column], errors="raise"
                    )

                valid_coordinates = (
                    selected["stop_lat"].between(-90, 90)
                    & selected["stop_lon"].between(-180, 180)
                )
                if not valid_coordinates.all():
                    raise ValueError(
                        f"Invalid stop coordinates: feed {feed_id}"
                    )

                selected.insert(0, "feed_id", feed_id)
                selected.insert(1, "transport_mode", mode)
                outputs.append(selected)

                print(
                    f"{mode}: {len(selected):,} served boarding "
                    f"stops/platforms; "
                    f"{int(replacement.sum())} replacement routes excluded"
                )

    result = pd.concat(outputs, ignore_index=True)

    if result.duplicated(["feed_id", "stop_id"]).any():
        raise ValueError("Duplicate feed/stop keys")

    destination = OUTPUT / "transport_boarding_stops.csv"
    result.to_csv(destination, index=False)

    print(f"\nTotal records: {len(result):,}")
    print(f"Saved: {destination}")


if __name__ == "__main__":
    main()
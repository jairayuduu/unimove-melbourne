from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, is_zipfile

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "data" / "raw" / "transport" / "gtfs.zip"


def read_table(archive, filename):
    matches = [
        name for name in archive.namelist()
        if Path(name).name.lower() == filename.lower()
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Expected one {filename}; found {len(matches)}"
        )

    with archive.open(matches[0]) as source:
        return pd.read_csv(
            source,
            dtype=str,
            encoding="utf-8-sig",
            keep_default_na=False,
        )


def main():
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Download not found: {SOURCE}")

    if not is_zipfile(SOURCE):
        raise ValueError(f"Invalid ZIP archive: {SOURCE}")

    with ZipFile(SOURCE) as outer:
        feeds = sorted(
            name for name in outer.namelist()
            if name.lower().endswith(".zip")
        )

        print(f"Archive: {SOURCE.name}")
        print(f"Nested feeds: {len(feeds)}")

        for feed in feeds:
            print(f"\nFeed: {feed}")

            with ZipFile(BytesIO(outer.read(feed))) as inner:
                filenames = [
                    name for name in inner.namelist()
                    if not name.endswith("/")
                ]
                print("Tables:", ", ".join(
                    Path(name).name for name in filenames
                ))

                routes = read_table(inner, "routes.txt")
                stops = read_table(inner, "stops.txt")
                if feed.split("/")[0] in {"2", "3", "4"}:
                    print("\nLocation types (blank means stop/platform):")
                    location_types = stops["location_type"].replace(
                        "", "blank"
                    )
                    print(
                        location_types.value_counts()
                        .sort_index()
                        .to_string()
                    )

                    print(
                        "\nDuplicate stop IDs:",
                        int(stops["stop_id"].duplicated().sum()),
                    )

                    coordinates = stops[
                        ["stop_lat", "stop_lon"]
                    ].apply(pd.to_numeric, errors="coerce")

                    print(
                        "Records with missing/non-numeric coordinates:",
                        int(coordinates.isna().any(axis=1).sum()),
                    )

                    replacement = routes[
                        "route_short_name"
                    ].str.contains(
                        "replacement",
                        case=False,
                        na=False,
                    )
                    print(
                        "Routes labelled replacement:",
                        int(replacement.sum()),
                    )

                    trips = read_table(inner, "trips.txt")
                    print(f"Trips: {len(trips):,}")
                    print(
                        "Trips referencing unknown routes:",
                        int(
                            (~trips["route_id"].isin(
                                routes["route_id"]
                            )).sum()
                        ),
                    )
                print(f"Routes: {len(routes):,}")
                print(f"Stop/location records: {len(stops):,}")

                print("\nRoute types:")
                print(
                    routes["route_type"]
                    .value_counts()
                    .sort_index()
                    .to_string()
                )

                route_columns = [
                    column for column in (
                        "route_id",
                        "route_short_name",
                        "route_long_name",
                        "route_type",
                    )
                    if column in routes.columns
                ]
                print("\nFirst five routes:")
                print(
                    routes[route_columns]
                    .head(5)
                    .to_string(index=False)
                )

                stop_columns = [
                    column for column in (
                        "stop_id",
                        "stop_name",
                        "stop_lat",
                        "stop_lon",
                        "location_type",
                        "parent_station",
                    )
                    if column in stops.columns
                ]
                print("\nFirst three stop/location records:")
                print(
                    stops[stop_columns]
                    .head(3)
                    .to_string(index=False)
                )


if __name__ == "__main__":
    main()
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "data" / "raw" / "transport" / "gtfs.zip"


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
    with ZipFile(SOURCE) as outer:
        for feed_id in ["2", "3", "4"]:
            with ZipFile(
                BytesIO(outer.read(f"{feed_id}/google_transit.zip"))
            ) as inner:
                calendar = read_table(inner, "calendar.txt")
                exceptions = read_table(inner, "calendar_dates.txt")

                print(f"\nFeed: {feed_id}")
                print(f"Calendar service records: {len(calendar):,}")
                print(f"Exception records: {len(exceptions):,}")

                if not calendar.empty:
                    starts = pd.to_datetime(
                        calendar["start_date"],
                        format="%Y%m%d",
                        errors="raise",
                    )
                    ends = pd.to_datetime(
                        calendar["end_date"],
                        format="%Y%m%d",
                        errors="raise",
                    )
                    print(
                        "Regular calendar range:",
                        starts.min().date(),
                        "to",
                        ends.max().date(),
                    )

                    print("Calendar columns:", calendar.columns.tolist())
                    print("\nFirst three calendar records:")
                    print(calendar.head(3).to_string(index=False))

                if not exceptions.empty:
                    dates = pd.to_datetime(
                        exceptions["date"],
                        format="%Y%m%d",
                        errors="raise",
                    )
                    print(
                        "\nException date range:",
                        dates.min().date(),
                        "to",
                        dates.max().date(),
                    )
                    print("Exception types:")
                    print(
                        exceptions["exception_type"]
                        .value_counts()
                        .sort_index()
                        .to_string()
                    )

                    if exceptions.duplicated(
                        ["service_id", "date"]
                    ).any():
                        raise ValueError(
                            f"Duplicate service/date exceptions: {feed_id}"
                        )


if __name__ == "__main__":
    main()
import json
from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path

import pandas as pd
import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "demo_data"

VIEWS = {
    "campus_distances": "campus_suburb_distance",
    "campus_rent": "campus_rental_candidates",
    "rent_latest": "latest_melbourne_rent",
    "population_profiles": "campus_population_profiles",
    "map_points": "campus_suburb_map_points",
    "transport_access": "suburb_transport_access_cached",
    "direct_services": "direct_campus_services",
    "crime_candidates": "suburb_crime_candidates",
}


def main():
    password = getpass("Password for unimove_dev: ")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "datasets": {},
    }

    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname="unimove",
        user="unimove_dev",
        password=password,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"
            )

            for filename, view in VIEWS.items():
                # View names come exclusively from the fixed mapping above.
                cursor.execute(f"SELECT * FROM unimove.{view}")
                columns = [
                    column.name for column in cursor.description
                ]
                frame = pd.DataFrame(
                    cursor.fetchall(), columns=columns
                )

                if frame.empty:
                    raise ValueError(f"Empty dataset: {view}")

                destination = OUTPUT / f"{filename}.csv"
                frame.to_csv(destination, index=False)

                manifest["datasets"][filename] = {
                    "source_view": f"unimove.{view}",
                    "rows": len(frame),
                    "bytes": destination.stat().st_size,
                }
                print(
                    f"{filename}: {len(frame):,} rows; "
                    f"{destination.stat().st_size:,} bytes"
                )

    (OUTPUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    print(f"\nDemo snapshots exported to: {OUTPUT}")


if __name__ == "__main__":
    main()
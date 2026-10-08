from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

frame = pd.read_csv(
    PROJECT_ROOT / "data" / "interim"
    / "crime_latest_source_detail.csv",
    dtype=str,
    keep_default_na=False,
)

areas = frame[
    ["source_lga", "source_postcode", "source_suburb"]
].drop_duplicates()

for name in [
    "Bellfield",
    "Bend Of Islands",
    "Gilderoy",
    "Hillside",
    "Springfield",
    "Tonimbuk",
]:
    matches = areas.loc[
        areas["source_suburb"].str.contains(
            name, case=False, regex=False, na=False
        )
    ]
    print(f"\n{name}:")
    if matches.empty:
        print("No source name containing this text.")
    else:
        print(matches.to_string(index=False))
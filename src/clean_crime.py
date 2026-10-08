from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    PROJECT_ROOT / "data" / "raw" / "crime"
    / "recorded_offences_jun2026.xlsx"
)
OUTPUT = PROJECT_ROOT / "data" / "interim"


def main():
    frame = pd.read_excel(
        SOURCE,
        sheet_name="Table 03",
        dtype=str,
        keep_default_na=False,
    )
    frame.columns = frame.columns.str.strip()

    columns = {
        "Year": "reporting_year",
        "Year ending": "year_ending",
        "Local Government Area": "source_lga",
        "Postcode": "source_postcode",
        "Suburb/Town Name": "source_suburb",
        "Offence Division": "offence_division",
        "Offence Subdivision": "offence_subdivision",
        "Offence Subgroup": "offence_subgroup",
        "Offence Count": "offence_count",
    }
    frame = frame[list(columns)].rename(columns=columns)

    for column in frame.columns:
        frame[column] = frame[column].str.strip()

    frame["reporting_year"] = pd.to_numeric(
        frame["reporting_year"], errors="raise"
    )
    frame["offence_count"] = pd.to_numeric(
        frame["offence_count"], errors="raise"
    )

    for column in ["reporting_year", "offence_count"]:
        if frame[column].mod(1).ne(0).any():
            raise ValueError(f"Non-integer values: {column}")
        frame[column] = frame[column].astype("int64")

    if frame["offence_count"].lt(0).any():
        raise ValueError("Negative offence counts")

    if not frame["year_ending"].eq("June").all():
        raise ValueError("Unexpected reporting endpoint")

    keys = list(columns.values())[:-1]
    if frame.duplicated(keys).any():
        raise ValueError("Duplicate observation keys")

    latest_year = int(frame["reporting_year"].max())
    latest = frame.loc[
        frame["reporting_year"].eq(latest_year)
    ].copy()

    required_labels = [
        "source_lga", "source_postcode", "source_suburb",
        "offence_division", "offence_subdivision", "offence_subgroup",
    ]
    if latest[required_labels].eq("").any().any():
        raise ValueError("Blank geographic or offence labels")

    latest["period_start"] = f"{latest_year - 1}-07-01"
    latest["period_end"] = f"{latest_year}-06-30"

    OUTPUT.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT / "crime_latest_source_detail.csv"
    latest.to_csv(destination, index=False)

    geography = [
        "source_lga", "source_postcode", "source_suburb"
    ]
    areas = latest[geography].drop_duplicates()

    # Show names associated with several geographic combinations.
    repeated_names = (
        areas.groupby("source_suburb")
        .size()
        .loc[lambda counts: counts > 1]
        .sort_values(ascending=False)
    )

    print(f"Latest endpoint: {latest_year}-06-30")
    print(f"Detail observations: {len(latest):,}")
    print(f"Source geographic combinations: {len(areas):,}")
    print(
        "Suburb names with multiple LGA/postcode combinations:",
        len(repeated_names),
    )

    print("\nSelected suburb geographic combinations:")
    print(
        areas.loc[
            areas["source_suburb"].isin(
                ["Carlton", "Parkville", "Clayton", "Notting Hill"]
            )
        ].sort_values(geography).to_string(index=False)
    )

    print("\nCounts by offence division:")
    print(
        latest.groupby("offence_division")["offence_count"]
        .sum()
        .to_string()
    )
    print(f"\nSaved: {destination}")


if __name__ == "__main__":
    main()
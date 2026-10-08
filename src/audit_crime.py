from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    PROJECT_ROOT / "data" / "raw" / "crime"
    / "recorded_offences_jun2026.xlsx"
)


def main():
    frame = pd.read_excel(
        SOURCE,
        sheet_name="Table 03",
        dtype=str,
        keep_default_na=False,
    )
    frame.columns = frame.columns.str.strip()

    print(f"Table 03 rows: {len(frame):,}")
    print("Columns:", frame.columns.tolist())

    print("\nReporting periods:")
    print(
        frame[["Year", "Year ending"]]
        .drop_duplicates()
        .sort_values(["Year", "Year ending"])
        .to_string(index=False)
    )

    keys = [
        "Year",
        "Year ending",
        "Local Government Area",
        "Postcode",
        "Suburb/Town Name",
        "Offence Division",
        "Offence Subdivision",
        "Offence Subgroup",
    ]
    print(
        "\nDuplicate full observation keys:",
        int(frame.duplicated(keys).sum()),
    )

    numeric = pd.to_numeric(
        frame["Offence Count"], errors="coerce"
    )
    markers = frame.loc[numeric.isna(), "Offence Count"]
    print(f"Non-numeric offence counts: {len(markers):,}")
    if not markers.empty:
        print(markers.value_counts(dropna=False).to_string())

    print("Negative counts:", int(numeric.lt(0).sum()))
    print(
        "Non-integer counts:",
        int((numeric.notna() & numeric.mod(1).ne(0)).sum()),
    )

    print("\nOffence divisions:")
    print(
        frame["Offence Division"]
        .drop_duplicates()
        .sort_values()
        .to_string(index=False)
    )

    years = pd.to_numeric(frame["Year"], errors="raise")
    latest = frame.loc[years.eq(years.max())].copy()

    print(f"\nLatest year: {int(years.max())}")
    print(f"Latest-year rows: {len(latest):,}")
    print(
        "Distinct LGA/postcode/suburb combinations:",
        len(
            latest[
                ["Local Government Area", "Postcode", "Suburb/Town Name"]
            ].drop_duplicates()
        ),
    )

    print("\nExample latest-year records:")
    print(
        latest.loc[
            latest["Suburb/Town Name"].isin(
                ["Clayton", "Notting Hill", "Carlton", "Parkville"]
            )
        ].head(12).to_string(index=False)
    )

    footnotes = pd.read_excel(
        SOURCE,
        sheet_name="Footnotes",
        header=None,
        dtype=str,
        keep_default_na=False,
    )
    print("\nFull workbook footnotes:")
    for row in footnotes.itertuples(index=False, name=None):
        values = [value.strip() for value in row if value.strip()]
        if values:
            print(" | ".join(values))


if __name__ == "__main__":
    main()
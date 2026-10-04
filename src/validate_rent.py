from pathlib import Path

import openpyxl
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

tidy = pd.read_csv(
    PROJECT_ROOT / "data" / "interim" / "rent_all_properties.csv",
    parse_dates=["period_start", "period_end"],
    dtype={
        "lease_count": "Int64",
        "median_weekly_rent_aud": "Float64",
    },
)

count_missing = tidy["lease_count"].isna()
median_missing = tidy["median_weekly_rent_aud"].isna()

print("Rows missing both values:", int((count_missing & median_missing).sum()))
print(
    "Rows missing only one value:",
    int((count_missing != median_missing).sum()),
)

print("\nObservations with unavailable values:")
print(tidy.loc[
    count_missing | median_missing,
    ["source_area", "period_end", "lease_count", "median_weekly_rent_aud"],
].to_string(index=False))

print("\nNumeric summary across all historical periods:")
print(tidy[[
    "lease_count", "median_weekly_rent_aud",
]].describe().to_string())

assert tidy["lease_count"].dropna().ge(0).all(), "Negative lease count"
assert tidy["median_weekly_rent_aud"].dropna().gt(0).all(), "Nonpositive rent"

workbook = openpyxl.load_workbook(
    PROJECT_ROOT / "data" / "raw" / "rent_sep2025.xlsx",
    read_only=True,
    data_only=True,
)
sheet = workbook["All properties"]

# Check early, recent and unpublished observations.
cases = [
    ("Armadale", "2000-03-31", "C5", "D5"),
    ("Clayton", "2025-09-30", "GY35", "GZ35"),
    ("Docklands", "2000-03-31", "C10", "D10"),
]

print("\nDirect source comparisons:")

for area, endpoint, count_cell, median_cell in cases:
    match = tidy[
        tidy["source_area"].eq(area)
        & tidy["period_end"].eq(pd.Timestamp(endpoint))
    ]
    assert len(match) == 1, f"Expected one observation for {area}"

    record = match.iloc[0]

    for field, cell in [
        ("lease_count", count_cell),
        ("median_weekly_rent_aud", median_cell),
    ]:
        expected = sheet[cell].value
        observed = record[field]

        if expected == "-":
            assert pd.isna(observed), f"Missing-value mismatch at {cell}"
        else:
            assert pd.notna(observed), f"Unexpected missing value at {cell}"
            assert observed == expected, f"Value mismatch at {cell}"

    print(f"PASS: {area}, {endpoint}")

workbook.close()
print("\nValidation completed successfully.")
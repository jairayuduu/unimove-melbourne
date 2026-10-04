from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
source_file = PROJECT_ROOT / "data" / "raw" / "rent_sep2025.xlsx"

raw = pd.read_excel(
    source_file,
    sheet_name="All properties",
    header=None,
    engine="openpyxl",
)

data = raw.iloc[3:].copy()

# Blank region labels continue the preceding region.
data[0] = data[0].ffill()

# Keep detail areas; regional totals have a different geographic grain.
data = data[
    data[1].notna() & data[1].ne("Group Total")
].copy()

frames = []

# Starting at column C, read each Count/Median pair.
for column in range(2, raw.shape[1], 2):
    if (
        raw.iloc[2, column] != "Count"
        or raw.iloc[2, column + 1] != "Median"
        or raw.iloc[1, column] != raw.iloc[1, column + 1]
    ):
        raise ValueError(f"Unexpected headers at column {column + 1}")

    period_end = (
        pd.to_datetime(raw.iloc[1, column], format="%b %Y")
        + pd.offsets.MonthEnd(0)
    )

    frame = pd.DataFrame({
        "source_region": data[0],
        "source_area": data[1],
        "source_excel_row": data.index + 1,
        "lease_count_raw": data[column],
        "median_weekly_rent_raw": data[column + 1],
    })

    frame["dwelling_category"] = "All properties"
    frame["period_end"] = period_end
    frame["period_basis"] = "moving_annual"

    frame["lease_count"] = pd.to_numeric(
        frame["lease_count_raw"].replace("-", pd.NA),
        errors="raise",
    ).astype("Int64")

    frame["median_weekly_rent_aud"] = pd.to_numeric(
        frame["median_weekly_rent_raw"].replace("-", pd.NA),
        errors="raise",
    ).astype("Float64")

    frames.append(frame)

tidy = pd.concat(frames, ignore_index=True)

tidy["period_start"] = (
    tidy["period_end"]
    - pd.DateOffset(years=1)
    + pd.Timedelta(days=1)
)

key = [
    "source_region",
    "source_area",
    "dwelling_category",
    "period_end",
]

if tidy.duplicated(key).any():
    raise ValueError("Duplicate observation keys found")

if tidy[["source_region", "source_area"]].isna().any().any():
    raise ValueError("Missing geographic labels found")

if len(tidy) != len(data) * len(frames):
    raise ValueError("Unexpected number of output observations")

output_folder = PROJECT_ROOT / "data" / "interim"
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "rent_all_properties.csv"
tidy.to_csv(output_file, index=False)

print("Detail rental areas:", len(data))
print("Reporting periods:", len(frames))
print("Output observations:", len(tidy))
print("Unavailable lease counts:", tidy["lease_count"].isna().sum())
print("Unavailable medians:", tidy["median_weekly_rent_aud"].isna().sum())

print("\nSample observations:")
print(tidy[[
    "source_area", "period_start", "period_end",
    "lease_count", "median_weekly_rent_aud",
]].head().to_string(index=False))

print("\nSaved:", output_file)
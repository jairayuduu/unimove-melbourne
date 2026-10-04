from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
source_file = PROJECT_ROOT / "data" / "raw" / "rent_sep2025.xlsx"


def clean_sheet(raw, sheet_name):
    """Convert one rental worksheet into tidy detail observations."""
    data = raw.iloc[3:].copy()
    data[0] = data[0].ffill()

    data = data[
        data[1].notna() & data[1].ne("Group Total")
    ].copy()

    frames = []

    for column in range(2, raw.shape[1], 2):
        if (
            raw.iloc[2, column] != "Count"
            or raw.iloc[2, column + 1] != "Median"
            or raw.iloc[1, column] != raw.iloc[1, column + 1]
        ):
            raise ValueError(f"Unexpected headers in {sheet_name}")

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

        frame["dwelling_category"] = sheet_name
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

    if len(tidy) != len(data) * len(frames):
        raise ValueError(f"Unexpected row count in {sheet_name}")

    return tidy


tables = []
area_sets = []

with pd.ExcelFile(source_file, engine="openpyxl") as workbook:
    for sheet_name in workbook.sheet_names:
        raw = pd.read_excel(workbook, sheet_name=sheet_name, header=None)
        tidy = clean_sheet(raw, sheet_name)
        tables.append(tidy)

        area_sets.append(
            set(zip(tidy["source_region"], tidy["source_area"]))
        )

combined = pd.concat(tables, ignore_index=True)

key = [
    "source_region", "source_area",
    "dwelling_category", "period_end",
]

assert not combined.duplicated(key).any(), "Duplicate observation keys"
assert combined[["source_region", "source_area"]].notna().all().all()
assert combined["lease_count"].dropna().ge(0).all()
assert combined["median_weekly_rent_aud"].dropna().gt(0).all()

same_area_labels = all(areas == area_sets[0] for areas in area_sets)

summary = combined.groupby("dwelling_category", sort=False).agg(
    observations=("source_area", "size"),
    unavailable_counts=("lease_count", lambda values: values.isna().sum()),
    unavailable_medians=(
        "median_weekly_rent_aud",
        lambda values: values.isna().sum(),
    ),
)

output_folder = PROJECT_ROOT / "data" / "interim"
output_folder.mkdir(parents=True, exist_ok=True)

combined.to_csv(output_folder / "rent_all_categories.csv", index=False)

# Keep the existing output so our earlier validator still works.
all_properties = combined[
    combined["dwelling_category"].eq("All properties")
]
all_properties.to_csv(
    output_folder / "rent_all_properties.csv",
    index=False,
)

print("Category summary:")
print(summary.to_string())
print("\nTotal detail observations:", len(combined))
print("All categories have identical region/area labels:", same_area_labels)
print("Duplicate observation keys:", int(combined.duplicated(key).sum()))
print("\nSaved outputs to:", output_folder)
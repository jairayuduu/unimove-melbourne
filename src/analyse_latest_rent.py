from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

rent = pd.read_csv(
    PROJECT_ROOT / "data" / "interim" / "rent_all_categories.csv",
    parse_dates=["period_start", "period_end"],
    dtype={
        "lease_count": "Int64",
        "median_weekly_rent_aud": "Float64",
    },
)

# Check missing-value alignment across the complete history.
rent["unpaired_missing"] = (
    rent["lease_count"].isna()
    != rent["median_weekly_rent_aud"].isna()
)

alignment = rent.groupby("dwelling_category", sort=False)[
    "unpaired_missing"
].sum()

latest_endpoint = rent["period_end"].max()
latest = rent[rent["period_end"].eq(latest_endpoint)].copy()

coverage = latest.groupby("dwelling_category", sort=False).agg(
    area_rows=("source_area", "size"),
    published_medians=("median_weekly_rent_aud", "count"),
    unavailable_medians=(
        "median_weekly_rent_aud",
        lambda values: values.isna().sum(),
    ),
)

coverage["published_pct"] = (
    100 * coverage["published_medians"] / coverage["area_rows"]
).round(1)

coverage["unpaired_missing_all_periods"] = alignment

print("Latest reporting endpoint:", latest_endpoint.date())
print("\nCoverage across all workbook rental areas:")
print(coverage.to_string())

print("\nRental areas by source region:")
print(
    latest.groupby("source_region")["source_area"]
    .nunique()
    .to_string()
)

output_folder = PROJECT_ROOT / "data" / "processed"
output_folder.mkdir(parents=True, exist_ok=True)

latest.drop(columns="unpaired_missing").to_csv(
    output_folder / "rent_latest_by_area_category.csv",
    index=False,
)

coverage["period_end"] = latest_endpoint.date().isoformat()
coverage["scope"] = "All workbook rental areas"

coverage.to_csv(
    PROJECT_ROOT / "docs" / "rental_latest_coverage.csv"
)

print("\nLatest snapshot and coverage report saved.")

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

latest = pd.read_csv(
    PROJECT_ROOT / "data" / "processed" / "rent_latest_by_area_category.csv",
    parse_dates=["period_start", "period_end"],
)

scope = pd.read_csv(
    PROJECT_ROOT / "config" / "rental_region_scope.csv",
    dtype={"include_in_melbourne_scope": "boolean"},
)

if scope["source_region"].duplicated().any():
    raise ValueError("Duplicate regions in the scope configuration")

if scope.isna().any().any():
    raise ValueError("Missing values in the scope configuration")

# Every source region must have an explicit inclusion decision.
labelled = latest.merge(
    scope,
    on="source_region",
    how="left",
    validate="many_to_one",
)

if labelled["include_in_melbourne_scope"].isna().any():
    raise ValueError("A source region has no configured scope decision")

melbourne = labelled[
    labelled["include_in_melbourne_scope"]
].copy()

excluded = labelled[
    ~labelled["include_in_melbourne_scope"]
].copy()

area_key = ["source_region", "source_area"]

print("Included rental areas:", len(melbourne[area_key].drop_duplicates()))
print("Excluded rental areas:", len(excluded[area_key].drop_duplicates()))
print("Included category observations:", len(melbourne))

coverage = melbourne.groupby("dwelling_category", sort=False).agg(
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

print("\nPublication coverage within the selected Melbourne scope:")
print(coverage.to_string())

melbourne.to_csv(
    PROJECT_ROOT / "data" / "processed"
    / "melbourne_rent_latest_by_area_category.csv",
    index=False,
)

coverage["period_end"] = melbourne["period_end"].max().date().isoformat()
coverage["scope"] = "Selected Melbourne publisher rental regions"

coverage.to_csv(
    PROJECT_ROOT / "docs" / "melbourne_rental_coverage.csv"
)

print("\nFiltered snapshot and coverage report saved.")
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = (
    PROJECT_ROOT / "data" / "raw" / "census"
    / "2021_GCP_SAL_for_VIC_short-header.zip"
)
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


def read_table(archive, table, value_columns):
    matches = [
        name for name in archive.namelist()
        if name.endswith(f"2021Census_{table}_VIC_SAL.csv")
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one file for {table}")

    with archive.open(matches[0]) as source:
        frame = pd.read_csv(
            source,
            usecols=["SAL_CODE_2021"] + value_columns,
            dtype={"SAL_CODE_2021": "string"},
        )

    codes = frame["SAL_CODE_2021"]
    if not codes.str.fullmatch(r"SAL\d{5}", na=False).all():
        raise ValueError(f"Unexpected Census codes in {table}")

    frame["sal_code"] = codes.str.removeprefix("SAL")
    if frame["sal_code"].duplicated().any():
        raise ValueError(f"Duplicate codes in {table}")

    return frame


age_columns = [f"Age_yr_{age}_P" for age in range(18, 25)]

with ZipFile(SOURCE_FILE) as archive:
    population = read_table(archive, "G01", ["Tot_P_P"])
    ages = read_table(archive, "G04A", age_columns)

profile = population[["sal_code", "Tot_P_P"]].merge(
    ages[["sal_code"] + age_columns],
    on="sal_code",
    how="outer",
    validate="one_to_one",
    indicator=True,
)

if not profile["_merge"].eq("both").all():
    raise ValueError("Population and age table codes differ")

numeric_columns = ["Tot_P_P"] + age_columns
for column in numeric_columns:
    profile[column] = pd.to_numeric(
        profile[column], errors="raise"
    ).astype("Int64")

if profile[numeric_columns].isna().any().any():
    raise ValueError("Missing population or age counts")

if profile[numeric_columns].lt(0).any().any():
    raise ValueError("Negative population or age counts")

profile = profile.rename(columns={"Tot_P_P": "population_total"})
profile["population_18_24"] = profile[age_columns].sum(axis=1)
profile["share_18_24_pct"] = (
    100 * profile["population_18_24"]
    / profile["population_total"].where(
        profile["population_total"].gt(0)
    )
)
profile["census_year"] = 2021

master = pd.read_csv(
    OUTPUT_DIR / "melbourne_suburb_master.csv",
    dtype={"sal_code": "string"},
)

result = master.merge(
    profile[
        [
            "sal_code", "census_year", "population_total",
            "population_18_24", "share_18_24_pct",
        ]
    ],
    on="sal_code",
    how="left",
    validate="one_to_one",
    indicator=True,
)

if not result["_merge"].eq("both").all():
    raise ValueError("A selected suburb has no Census match")

result = result.drop(columns="_merge")

print("Selected suburb rows:", len(result))
print("Matched Census rows:", result["population_total"].notna().sum())

zero_population = result["population_total"].eq(0)
print("Zero-population suburbs:", zero_population.sum())
print(
    result.loc[
        zero_population, ["sal_code", "suburb_name", "population_total"]
    ].to_string(index=False)
)

print("\nFirst five population profiles:")
print(
    result[
        [
            "suburb_name", "population_total",
            "population_18_24", "share_18_24_pct",
        ]
    ].head().round({"share_18_24_pct": 2}).to_string(index=False)
)

result.to_csv(
    OUTPUT_DIR / "melbourne_suburb_population_2021.csv",
    index=False,
)
print("\nPopulation profile saved.")
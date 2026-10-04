from pathlib import Path
import re

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"


def normalise_name(value):
    value = str(value).casefold().strip()
    value = re.sub(r"\s*\(vic\.?\)\s*$", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


rent = pd.read_csv(
    DATA_DIR / "melbourne_rent_latest_by_area_category.csv"
)
suburbs = pd.read_csv(
    DATA_DIR / "melbourne_suburb_master.csv",
    dtype={"sal_code": "string"},
)

areas = rent[
    ["source_region", "source_area"]
].drop_duplicates().copy()

areas["name_key"] = areas["source_area"].map(normalise_name)
suburbs["name_key"] = suburbs["suburb_name"].map(normalise_name)

if suburbs["name_key"].duplicated().any():
    raise ValueError("Ambiguous normalised suburb names need review")

audit = areas.merge(
    suburbs[["name_key", "sal_code", "suburb_name"]],
    on="name_key",
    how="left",
    validate="many_to_one",
)

audit["match_status"] = "unmatched_name"
audit.loc[
    audit["sal_code"].notna(), "match_status"
] = "name_match_candidate"

audit["boundary_equivalence_verified"] = False

print("Distinct Melbourne rental areas:", len(audit))
print("\nName matching results:")
print(audit["match_status"].value_counts().to_string())

print("\nRental areas without a matching suburb name:")
print(
    audit.loc[
        audit["sal_code"].isna(),
        ["source_region", "source_area"],
    ].to_string(index=False)
)

audit.to_csv(
    PROJECT_ROOT / "docs" / "rental_geography_name_audit.csv",
    index=False,
)

print("\nName audit saved.")

alias_candidates = {
    "East St Kilda": "St Kilda East",
    "East Hawthorn": "Hawthorn East",
    "East Brunswick": "Brunswick East",
    "West Brunswick": "Brunswick West",
}

print("\nDirectional alias candidates:")

for source_area, target_name in alias_candidates.items():
    matches = suburbs.loc[
        suburbs["name_key"].eq(normalise_name(target_name)),
        ["sal_code", "suburb_name"],
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Expected one suburb candidate for {source_area}"
        )

    print(
        f"{source_area} -> "
        f"{matches.iloc[0]['suburb_name']} "
        f"({matches.iloc[0]['sal_code']})"
    )

aliases = pd.read_csv(
    PROJECT_ROOT / "config" / "rental_area_aliases.csv",
    dtype={"target_sal_code": "string"},
)

if aliases.isna().any().any():
    raise ValueError("Missing alias configuration values")

if aliases["source_area"].duplicated().any():
    raise ValueError("Duplicate source areas in alias configuration")

for alias in aliases.itertuples(index=False):
    target = suburbs.loc[
        suburbs["sal_code"].eq(alias.target_sal_code)
    ]

    if len(target) != 1:
        raise ValueError(f"Unknown alias code: {alias.target_sal_code}")

    if target.iloc[0]["suburb_name"] != alias.target_suburb_name:
        raise ValueError(f"Alias code/name mismatch: {alias.source_area}")

    source_mask = audit["source_area"].eq(alias.source_area)

    if source_mask.sum() != 1:
        raise ValueError(f"Ambiguous alias source: {alias.source_area}")

    if audit.loc[source_mask, "sal_code"].notna().any():
        raise ValueError(f"Alias overwrites a match: {alias.source_area}")

    audit.loc[source_mask, "sal_code"] = alias.target_sal_code
    audit.loc[source_mask, "suburb_name"] = alias.target_suburb_name
    audit.loc[source_mask, "match_status"] = "alias_match_candidate"

audit.to_csv(
    PROJECT_ROOT / "docs" / "rental_geography_name_audit.csv",
    index=False,
)

print("\nResults after configured aliases:")
print(audit["match_status"].value_counts().to_string())
print(
    "Boundary-verified rental areas:",
    audit["boundary_equivalence_verified"].sum(),
)
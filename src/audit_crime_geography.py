import re
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_KEYS = ["source_lga", "source_postcode", "source_suburb"]


def normalise(value):
    value = re.sub(
        r"\s*\(Vic\.\)\s*$", "", str(value), flags=re.IGNORECASE
    )
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def main():
    detail = pd.read_csv(
        PROJECT_ROOT / "data" / "interim"
        / "crime_latest_source_detail.csv",
        dtype=str,
        keep_default_na=False,
    )
    suburbs = pd.read_csv(
        PROJECT_ROOT / "data" / "processed"
        / "melbourne_suburb_master.csv",
        dtype={"sal_code": str},
    )
    aliases = pd.read_csv(
        PROJECT_ROOT / "config" / "crime_area_aliases.csv",
        dtype=str,
        keep_default_na=False,
    )

    if suburbs["sal_code"].duplicated().any():
        raise ValueError("Duplicate ABS suburb codes")
    if aliases.duplicated(SOURCE_KEYS).any():
        raise ValueError("Duplicate alias source keys")
    if not aliases["sal_code"].isin(suburbs["sal_code"]).all():
        raise ValueError("Alias references an unknown ABS code")

    areas = detail[SOURCE_KEYS].drop_duplicates().copy()
    areas["name_key"] = areas["source_suburb"].map(normalise)
    suburbs["name_key"] = suburbs["suburb_name"].map(normalise)

    names = areas.merge(
        suburbs[["sal_code", "suburb_name", "name_key"]],
        on="name_key",
        how="inner",
    )
    names["match_status"] = "name_match_candidate"

    alias_links = aliases.merge(
        areas,
        on=SOURCE_KEYS,
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    if not alias_links["_merge"].eq("both").all():
        raise ValueError("Alias source combination not found in crime data")
    alias_links = alias_links.drop(columns="_merge").merge(
        suburbs[["sal_code", "suburb_name"]],
        on="sal_code",
        how="left",
        validate="many_to_one",
    )
    alias_links["match_status"] = "alias_match_candidate"

    # Configured aliases take precedence for their exact source keys.
    names = names.merge(
        aliases[SOURCE_KEYS].assign(configured_alias=True),
        on=SOURCE_KEYS,
        how="left",
        validate="many_to_one",
    )
    names = names.loc[
        names["configured_alias"].isna()
    ].drop(columns="configured_alias")

    candidates = pd.concat(
        [names, alias_links], ignore_index=True
    )

    matches_per_source = candidates.groupby(SOURCE_KEYS)[
        "sal_code"
    ].transform("nunique")
    candidates.loc[
        matches_per_source.gt(1), "match_status"
    ] = "ambiguous_abs_name"

    candidates["source_combinations_per_sal"] = (
        candidates.groupby("sal_code")["sal_code"].transform("size")
    )
    candidates["boundary_equivalence_verified"] = False

    if candidates.duplicated(SOURCE_KEYS + ["sal_code"]).any():
        raise ValueError("Duplicate candidate links")

    matched_codes = set(candidates["sal_code"])
    unmatched = suburbs.loc[
        ~suburbs["sal_code"].isin(matched_codes),
        ["sal_code", "suburb_name"],
    ]

    print(f"ABS suburbs: {len(suburbs)}")
    print(f"ABS suburbs with candidates: {len(matched_codes)}")
    print(f"ABS suburbs without candidates: {len(unmatched)}")

    print("\nCandidate link methods:")
    print(candidates["match_status"].value_counts().to_string())

    print(
        "\nSource areas matching multiple ABS codes:",
        len(
            candidates.loc[
                candidates["match_status"].eq("ambiguous_abs_name"),
                SOURCE_KEYS,
            ].drop_duplicates()
        ),
    )
    print(
        "ABS suburbs linked to multiple source combinations:",
        candidates.loc[
            candidates["source_combinations_per_sal"].gt(1),
            "sal_code",
        ].nunique(),
    )

    print("\nUnmatched ABS suburbs:")
    print(unmatched.to_string(index=False))

    print("\nConfigured alias links:")
    print(
        candidates.loc[
            candidates["match_status"].eq("alias_match_candidate"),
            SOURCE_KEYS + ["sal_code", "suburb_name"],
        ].to_string(index=False)
    )

    docs = PROJECT_ROOT / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    candidates.sort_values(
        ["sal_code"] + SOURCE_KEYS
    ).to_csv(
        docs / "crime_geography_name_candidates.csv",
        index=False,
    )
    unmatched.to_csv(
        docs / "crime_geography_unmatched_suburbs.csv",
        index=False,
    )
    print("\nGeography audit reports saved.")


if __name__ == "__main__":
    main()
from pathlib import Path
from zipfile import ZipFile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "data" / "raw" / "geography"

for archive_path in sorted(SOURCE_DIR.glob("*.zip")):
    print(f"\nArchive: {archive_path.name}")

    with ZipFile(archive_path) as archive:
        for member in archive.infolist():
            if not member.is_dir():
                print(f"  {member.filename} ({member.file_size:,} bytes)")

import geopandas as gpd

sources = {
    "Suburbs and Localities": (
        SOURCE_DIR / "SAL_2021_AUST_GDA2020_SHP.zip"
    ),
    "Capital City Areas": (
        SOURCE_DIR / "GCCSA_2021_AUST_SHP_GDA94.zip"
    ),
}

for label, archive_path in sources.items():
    boundaries = gpd.read_file(f"zip://{archive_path.as_posix()}")

    print(f"\nDataset: {label}")
    print("Rows:", len(boundaries))
    print("Columns:", boundaries.columns.tolist())
    print("Coordinate system:", boundaries.crs)
    print("Geometry types:")
    print(boundaries.geometry.geom_type.value_counts().to_string())
    print("Missing geometries:", boundaries.geometry.isna().sum())
    print("Empty geometries:", boundaries.geometry.is_empty.sum())
    print("Invalid geometries:", (~boundaries.geometry.is_valid).sum())

    attributes = boundaries.drop(columns=boundaries.geometry.name)

    if label == "Capital City Areas":
        print("\nCapital city area attributes:")
        print(attributes.to_string(index=False))
    else:
        print("\nFirst five suburb records:")
        print(attributes.head().to_string(index=False))


sal = gpd.read_file(
    f"zip://{sources['Suburbs and Localities'].as_posix()}"
)
gccsa = gpd.read_file(
    f"zip://{sources['Capital City Areas'].as_posix()}"
)

victoria = sal[sal["STE_CODE21"].astype(str).eq("2")].copy()
melbourne = gccsa[gccsa["GCC_CODE21"].eq("2GMEL")].copy()

print("\nVictoria SAL records:", len(victoria))

missing = victoria.geometry.isna()
invalid_present = (
    victoria.geometry.notna() & ~victoria.geometry.is_valid
)

print("Missing Victorian geometries:", missing.sum())
print("Invalid present Victorian geometries:", invalid_present.sum())

print("\nVictorian records without geometry:")
print(
    victoria.loc[missing, ["SAL_CODE21", "SAL_NAME21"]]
    .to_string(index=False)
)

if len(melbourne) != 1:
    raise ValueError("Expected exactly one Greater Melbourne boundary")

if (
    melbourne.geometry.isna().any()
    or melbourne.geometry.is_empty.any()
    or not melbourne.geometry.is_valid.all()
):
    raise ValueError("Greater Melbourne boundary failed geometry checks")

# Use a shared projected coordinate system for spatial operations.
victoria_spatial = victoria.loc[~missing].to_crs(epsg=7855)
melbourne_spatial = melbourne.to_crs(epsg=7855)

print("\nShared coordinate system:", victoria_spatial.crs)
print("Victorian records with geometry:", len(victoria_spatial))
print("Greater Melbourne boundary check: PASS")


melbourne_boundary = melbourne_spatial.geometry.iloc[0]

if victoria_spatial.geometry.is_empty.any():
    raise ValueError("An empty Victorian geometry needs review")

# A representative point lies inside its suburb polygon.
representative_points = victoria_spatial.geometry.representative_point()

selected = victoria_spatial.loc[
    representative_points.within(melbourne_boundary)
].copy()

print("\nMelbourne selection comparison:")
print(
    "Any boundary intersection:",
    victoria_spatial.geometry.intersects(melbourne_boundary).sum(),
)
print(
    "Entire suburb within Melbourne:",
    victoria_spatial.geometry.within(melbourne_boundary).sum(),
)
print("Representative point within Melbourne:", len(selected))

# Measure how much of each selected suburb falls outside Melbourne.
outside_area = selected.geometry.difference(melbourne_boundary).area
selected["outside_melbourne_pct"] = (
    100 * outside_area / selected.geometry.area
)

print("\nSelected suburbs with more than 0.1% of area outside Melbourne:")
print(
    selected.loc[
        selected["outside_melbourne_pct"] > 0.1,
        ["SAL_CODE21", "SAL_NAME21", "outside_melbourne_pct"],
    ]
    .sort_values("outside_melbourne_pct", ascending=False)
    .round({"outside_melbourne_pct": 2})
    .to_string(index=False)
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

master = selected[
    ["SAL_CODE21", "SAL_NAME21", "outside_melbourne_pct", "geometry"]
].copy()

master = master.rename(
    columns={
        "SAL_CODE21": "sal_code",
        "SAL_NAME21": "suburb_name",
    }
)

master["sal_code"] = master["sal_code"].astype("string")
master["geography_year"] = 2021
master["scope_method"] = "representative_point_within_2GMEL"
master["boundary_review_required"] = (
    master["outside_melbourne_pct"] > 0.1
)
master["area_sq_km"] = master.geometry.area / 1_000_000

if master["sal_code"].isna().any():
    raise ValueError("Missing suburb codes")

if master["sal_code"].duplicated().any():
    raise ValueError("Duplicate suburb codes")

if not master["area_sq_km"].gt(0).all():
    raise ValueError("Non-positive suburb areas")

master = master.sort_values("sal_code").reset_index(drop=True)

# Geographic coordinates for later mapping.
master.to_crs(epsg=4326).to_file(
    OUTPUT_DIR / "melbourne_suburbs_2021.geojson",
    driver="GeoJSON",
    index=False,
)

master.drop(columns="geometry").to_csv(
    OUTPUT_DIR / "melbourne_suburb_master.csv",
    index=False,
)

# Small, tracked report documenting substantial boundary crossings.
master.loc[
    master["boundary_review_required"],
    ["sal_code", "suburb_name", "outside_melbourne_pct"],
].to_csv(
    PROJECT_ROOT / "docs" / "suburb_boundary_review.csv",
    index=False,
)

print("\nSaved suburb master rows:", len(master))
print("Unique suburb codes:", master["sal_code"].nunique())
print("Boundary review flags:", master["boundary_review_required"].sum())
print("Geography outputs saved:", OUTPUT_DIR)
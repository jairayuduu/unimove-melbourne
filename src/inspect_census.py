from pathlib import Path
from zipfile import ZipFile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = (
    PROJECT_ROOT / "data" / "raw" / "census"
    / "2021_GCP_SAL_for_VIC_short-header.zip"
)

with ZipFile(SOURCE_FILE) as archive:
    files = [
        member for member in archive.infolist()
        if not member.is_dir()
    ]

    print("Archive:", SOURCE_FILE.name)
    print("Total files:", len(files))

    print("\nPopulation, age and metadata candidates:")
    for member in files:
        filename = Path(member.filename).name
        upper_name = filename.upper()

        if (
            "_G01_" in upper_name
            or "_G04" in upper_name
            or "METADATA" in upper_name
            or filename.lower().endswith((".xlsx", ".xls"))
        ):
            print(
                f"{member.filename} "
                f"({member.file_size:,} bytes)"
            )

import pandas as pd

with ZipFile(SOURCE_FILE) as archive:
    for table in ["G01", "G04A", "G04B"]:
        matches = [
            name for name in archive.namelist()
            if name.endswith(f"2021Census_{table}_VIC_SAL.csv")
        ]

        if len(matches) != 1:
            raise ValueError(f"Expected one file for {table}")

        with archive.open(matches[0]) as source:
            frame = pd.read_csv(source, dtype={"SAL_CODE_2021": "string"})

        print(f"\nTable: {table}")
        print("Rows:", len(frame))
        print("Columns:", frame.columns.tolist())
        print("\nFirst two records, first eight columns:")
        print(frame.iloc[:2, :8].to_string(index=False))

    metadata_path = "Metadata/Metadata_2021_GCP_DataPack_R1_R2.xlsx"

    with archive.open(metadata_path) as source:
        with pd.ExcelFile(source) as workbook:
            print("\nMetadata worksheets:")
            for sheet_name in workbook.sheet_names:
                print("-", sheet_name)

            first_sheet = workbook.sheet_names[0]
            preview = pd.read_excel(
                workbook,
                sheet_name=first_sheet,
                header=None,
                nrows=8,
            )

            print(f"\nMetadata preview: {first_sheet}")
            print(preview.to_string(index=False, header=False))

with ZipFile(SOURCE_FILE) as archive:
    with archive.open(
        "Metadata/Metadata_2021_GCP_DataPack_R1_R2.xlsx"
    ) as source:
        with pd.ExcelFile(source) as workbook:
            tables = pd.read_excel(
                workbook,
                sheet_name="Table Number, Name, Population",
                header=None,
            )

            cells = pd.read_excel(
                workbook,
                sheet_name="Cell Descriptors Information",
                header=None,
            )

def matching_rows(frame, pattern):
    return frame.loc[
        frame.astype("string")
        .apply(
            lambda column: column.str.contains(
                pattern, case=False, regex=True, na=False
            )
        )
        .any(axis=1)
    ].dropna(axis=1, how="all")

print("\nG01 and G04 table definitions:")
print(
    matching_rows(tables, r"\bG0[14]\b")
    .to_string(index=False, header=False)
)

print("\nSelected population and age cell definitions:")
print(
    matching_rows(
        cells,
        r"\bTot_P_P\b|\bAge_yr_(18|19|20|21|22|23|24)_P\b",
    ).to_string(index=False, header=False)
)
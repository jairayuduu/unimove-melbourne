from pathlib import Path

import pandas as pd

# Locate the project independently of the terminal's current folder.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
source_file = PROJECT_ROOT / "data" / "raw" / "rent_sep2025.xlsx"

print("pandas version:", pd.__version__)
print("Source file:", source_file)

with pd.ExcelFile(source_file, engine="openpyxl") as workbook:
    print("\nWorksheets:")
    for sheet_name in workbook.sheet_names:
        print("-", sheet_name)

    preview = pd.read_excel(
        workbook,
        sheet_name="All properties",
        header=None,
        nrows=8,
        usecols="A:H",
    )

print("\nFirst eight rows, columns A to H:")
print(preview.to_string(index=False, header=False))
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    PROJECT_ROOT / "data" / "raw" / "crime"
    / "recorded_offences_jun2026.xlsx"
)


def main():
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)

    with pd.ExcelFile(SOURCE) as workbook:
        print(f"Workbook: {SOURCE.name}")
        print("\nWorksheets:")
        for sheet in workbook.sheet_names:
            print(f"- {sheet}")

        for sheet in workbook.sheet_names:
            preview = pd.read_excel(
                workbook,
                sheet_name=sheet,
                header=None,
                nrows=12,
                dtype=object,
            )
            print(f"\nWorksheet: {sheet}")
            print("First 12 rows, up to 12 columns:")
            print(
                preview.iloc[:, :12]
                .fillna("")
                .to_string(index=False, header=False)
            )


if __name__ == "__main__":
    main()
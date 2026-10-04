from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
source_file = PROJECT_ROOT / "data" / "raw" / "rent_sep2025.xlsx"


def audit_sheet(sheet_name, raw):
    """Apply consistent structural checks to one worksheet."""
    period_headers = raw.iloc[1, 2:]
    metric_headers = raw.iloc[2, 2:]
    observations = raw.iloc[3:]

    period_labels = period_headers.dropna().unique().tolist()
    periods = pd.to_datetime(period_labels, format="%b %Y")

    area_labels = observations.iloc[:, 1].dropna()
    detail_labels = area_labels[area_labels != "Group Total"]

    values = observations.iloc[:, 2:]
    flattened = pd.Series(values.to_numpy().ravel()).dropna()
    text_values = flattened[
        flattened.map(lambda value: isinstance(value, str))
    ]
    unexpected_markers = sorted(set(text_values) - {"-"})

    report = {
        "sheet": sheet_name,
        "rows": raw.shape[0],
        "columns": raw.shape[1],
        "periods": len(periods),
        "first_period": periods.min().strftime("%b %Y"),
        "last_period": periods.max().strftime("%b %Y"),
        "rental_areas": len(detail_labels),
        "regional_totals": int(area_labels.eq("Group Total").sum()),
        "repeated_detail_labels": int(detail_labels.duplicated().sum()),
        "blank_cells": int(values.isna().sum().sum()),
        "dash_cells": int(values.eq("-").sum().sum()),
        "dates_paired": (
            period_headers.iloc[::2].tolist()
            == period_headers.iloc[1::2].tolist()
        ),
        "metrics_alternate": (
            metric_headers.tolist()
            == ["Count", "Median"] * len(periods)
        ),
        "unexpected_markers": ", ".join(unexpected_markers),
    }

    return report, period_labels


reports = []
period_sequences = []

with pd.ExcelFile(source_file, engine="openpyxl") as workbook:
    for sheet_name in workbook.sheet_names:
        raw = pd.read_excel(workbook, sheet_name=sheet_name, header=None)
        report, period_labels = audit_sheet(sheet_name, raw)
        reports.append(report)
        period_sequences.append(period_labels)

summary = pd.DataFrame(reports)

print("Workbook coverage:")
print(summary[[
    "sheet", "periods", "first_period", "last_period",
    "rental_areas", "regional_totals", "dash_cells",
]].to_string(index=False))

print("\nStructural checks:")
print(summary[[
    "sheet", "dates_paired", "metrics_alternate",
    "repeated_detail_labels", "blank_cells", "unexpected_markers",
]].to_string(index=False))

same_periods = all(
    sequence == period_sequences[0]
    for sequence in period_sequences
)
print("\nAll sheets have identical reporting periods:", same_periods)

report_file = PROJECT_ROOT / "docs" / "rental_workbook_audit.csv"
summary.to_csv(report_file, index=False)
print("\nAudit report saved:", report_file)
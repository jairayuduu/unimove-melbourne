from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
source_file = PROJECT_ROOT / "data" / "raw" / "rent_sep2025.xlsx"

raw = pd.read_excel(
    source_file,
    sheet_name="All properties",
    header=None,
    engine="openpyxl",
)

# Separate the period headers, metric headers and observations.
period_headers = raw.iloc[1, 2:]
metric_headers = raw.iloc[2, 2:]
observations = raw.iloc[3:]

periods = pd.to_datetime(
    period_headers.dropna().unique(),
    format="%b %Y",
)

print("Worksheet dimensions:", raw.shape)
print("Reporting periods:", len(periods))
print("First period:", periods.min().strftime("%b %Y"))
print("Last period:", periods.max().strftime("%b %Y"))

print(
    "Each period has matching Count/Median dates:",
    period_headers.iloc[::2].tolist()
    == period_headers.iloc[1::2].tolist(),
)
print(
    "Metric headers alternate Count and Median:",
    metric_headers.tolist() == ["Count", "Median"] * len(periods),
)

area_labels = observations.iloc[:, 1].dropna()
detail_labels = area_labels[area_labels != "Group Total"]

print("\nRental-area rows:", len(detail_labels))
print("Regional total rows:", int(area_labels.eq("Group Total").sum()))
print("Repeated detail labels:", int(detail_labels.duplicated().sum()))

values = observations.iloc[:, 2:]
print("\nBlank metric cells:", int(values.isna().sum().sum()))
print("Dash metric cells:", int(values.eq("-").sum().sum()))

flattened = pd.Series(values.to_numpy().ravel()).dropna()
text_values = flattened[
    flattened.map(lambda value: isinstance(value, str))
]

print("\nText markers found:")
print(text_values.value_counts().to_string())
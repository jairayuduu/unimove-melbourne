\# Population source and processing



Source: Australian Bureau of Statistics, 2021 Census

General Community Profile for Victorian Suburbs and Localities.



Source page:

https://www.abs.gov.au/census/find-census-data/datapacks



Raw archive:

2021\_GCP\_SAL\_for\_VIC\_short-header.zip



\## Fields and calculations



\- Total population: G01, Tot\_P\_P.

\- Population aged 18–24: sum of G04A persons columns

&#x20; Age\_yr\_18\_P through Age\_yr\_24\_P.

\- Age share: 100 × population aged 18–24 / total population.

\- Census year: 2021.



The SAL prefix is removed from Census identifiers before

joining to the geography master. Codes are stored as strings.



\## Checks and results



\- Population and age tables have matching, unique SAL codes.

\- Selected source counts contain no missing or negative values.

\- All 572 selected suburbs matched Census records.

\- One-to-one joins prevent duplicate suburb observations.



Calder Park, Cocoroc and Fernshaw have published total

populations of zero. Their age percentages remain unavailable.



\## Interpretation



These figures describe the 2021 Census population.

The 18–24 count is derived from published single-year counts.



Age composition is descriptive. It does not directly measure

student population, sociability or suitability for an individual.



For boundary-crossing suburbs, population refers to the whole

SAL area; it has not been apportioned to Greater Melbourne.



\## Output



data/processed/melbourne\_suburb\_population\_2021.csv


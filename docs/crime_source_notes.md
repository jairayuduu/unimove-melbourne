\# Recorded-offence sources and methodology



\## Source



Crime Statistics Agency, Recorded offences by LGA,

year ending June 2026, Table 03.



Source page:

https://discover.data.vic.gov.au/dataset/data-tables-recorded-offences



Downloaded on 8 October 2026.

Local file: data/raw/crime/recorded\_offences\_jun2026.xlsx.



Reporting period: 1 July 2025 to 30 June 2026.



\## Cleaning and validation



The latest-year table contains:

\- 38,860 offence observations.

\- 2,605 LGA/postcode/suburb combinations.

\- 620,140 recorded offences.



Full observation keys are unique.

Counts are numeric, non-negative integers.

Database row counts and offence totals match the cleaned source CSV.



Publisher offence categories are retained, including combined groups.



\## Geographic matching



Source LGA, postcode and suburb are preserved separately.



Normalised names and four configured aliases produce:

\- 646 candidate links.

\- 569 matched ABS suburbs out of 572.

\- 67 ABS suburbs with multiple source combinations.



No source area is linked to multiple ABS suburbs.

Boundary equivalence remains unverified.



Bend Of Islands, Gilderoy and Tonimbuk have no candidate coverage.

Their absence is not interpreted as zero offences.



Carlton has two source combinations: postcodes 3000 and 3053,

both in Melbourne LGA. Their combined candidate total is 3,174.



\## App interpretation



The app sums offence observations across linked source combinations

and displays the number of contributing source areas.



It shows total offences, crimes against the person, and property

and deception offences. The two category columns are parts of the

total; other offence divisions also contribute to the total.



Missing category records remain missing.



These counts are not a safety ranking or an estimate of personal risk.

Area size, visitors, reporting and policing affect comparisons.



No rate is calculated using the older 2021 Census population.



\## Publisher exclusions



Table 03 excludes offences recorded at:

\- Justice institutions.

\- Immigration facilities.

\- Unincorporated Victoria.

\- Unknown geographic locations.



\## Checked examples



| Suburb | Candidate total | Source areas |

|---|---:|---:|

| Carlton | 3,174 | 2 |

| Clayton | 2,298 | 1 |

| Notting Hill | 285 | 1 |

| Parkville | 1,106 | 1 |



Campus filtering and CSV download checks passed.


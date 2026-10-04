\# Geography source and scope



Source: Australian Bureau of Statistics, ASGS Edition 3,

2021 digital boundaries.



Source page:

https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files



Raw files:

\- SAL\_2021\_AUST\_GDA2020\_SHP.zip

\- GCCSA\_2021\_AUST\_SHP\_GDA94.zip



2021 geography was selected to align with 2021 Census data.



\## Inspection



Victoria contains 2,946 SAL records. Two non-spatial records

have no geometry: No usual address and Migratory - Offshore -

Shipping. They are excluded from spatial selection.



All 2,944 present Victorian geometries passed validity checks.



Both datasets were transformed to EPSG:7855 before spatial

comparisons and area calculations.



\## Melbourne selection rule



Include Victorian suburbs/localities whose representative

point lies within Greater Melbourne (GCCSA code 2GMEL).



Selection comparison:

\- Any intersection: 613 records.

\- Full containment: 470 records.

\- Representative point within Melbourne: 572 records.



This is a project scope rule, not an official SAL-to-GCCSA

correspondence. Complete selected suburb polygons are retained.



Heath Hill has 36.11% of its area outside Greater Melbourne;

Lang Lang has 34.72%. Both are flagged for boundary review.

The review threshold is greater than 0.1% outside area.



\## Outputs



\- melbourne\_suburb\_master.csv: attributes and unique SAL codes.

\- melbourne\_suburbs\_2021.geojson: boundaries in EPSG:4326.

\- docs/suburb\_boundary\_review.csv: flagged boundary crossings.



The master contains 572 rows and 572 unique SAL codes.

SAL codes will be used to join compatible Census data.

Rental-area equivalence has not yet been established.


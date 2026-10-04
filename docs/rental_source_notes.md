\# Rental source inspection



\## Source



Publisher: Homes Victoria.

Workbook: Moving annual median rent by suburb and town,

September quarter 2025.



Official download:

https://www.dffh.vic.gov.au/moving-annual-rent-suburb-september-quarter-2025-excel



Local copy: data/raw/rent\_sep2025.xlsx



\## Observed structure



\- Seven worksheets: six dwelling categories and All properties.

\- First row contains the title and reporting-period explanation.

\- Second row contains repeated reporting-period labels.

\- Third row identifies Count and Median columns.

\- Observations begin on the fourth row.

\- Column A contains region labels that continue across blank cells.

\- Column B contains rental areas, including pooled suburb groups.

\- The preview begins with March 2000.



\## Interpretation



The workbook reports moving annual observations.

Pooled rental areas must retain their original geographic meaning.



\## All properties audit results



\- Worksheet dimensions: 162 rows and 208 columns.

\- 103 reporting endpoints, from March 2000 to September 2025.

\- Each endpoint has matching Count and Median headers.

\- 146 rental-area rows and 13 regional total rows.

\- No repeated detail-area labels within this sheet.

\- No blank metric cells; 14 cells contain a dash.

\- The dash is the only text marker found in the metric cells.



\## Transformation decisions



\- Keep regional totals separate from rental-area observations.

\- Preserve dash markers as unavailable values, not zero.

\- Retain pooled rental-area names.

\- Preserve dwelling category and moving annual period definitions.



\## Checks still required



Audit the other six worksheets and confirm the publisher's

meaning of dash markers and rental-area geographic definitions..


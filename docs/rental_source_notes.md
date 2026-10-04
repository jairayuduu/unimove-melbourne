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





\## Full workbook audit



All seven worksheets contain:

\- 103 identical reporting endpoints: March 2000–September 2025.

\- 146 rental-area rows and 13 regional total rows.

\- Correctly paired Count/Median headers.

\- No repeated detail labels within each worksheet.

\- No blank metric cells or unexpected text markers.



Dash-cell counts:

\- 1 bedroom flat: 2,478

\- 2 bedroom flat: 282

\- 3 bedroom flat: 1,572

\- 2 bedroom house: 1,332

\- 3 bedroom house: 650

\- 4 bedroom house: 1,406

\- All properties: 14



Missingness varies by dwelling category. These counts include

regional totals and all reporting periods; they do not measure

latest-period suburb coverage.



The audit does not yet establish identical geographic definitions

across sheets or explain why individual values are unpublished.



\## All properties transformation



Script: src/clean\_rent.py

Output: data/interim/rent\_all\_properties.csv



\- Converted the wide worksheet into 15,038 detail observations.

\- Observation key: source region, source area, dwelling category

&#x20; and moving annual period end.

\- Filled region labels downward.

\- Excluded regional totals from the detail output.

\- Preserved original count and median values in raw-value columns.

\- Converted dash markers to missing numeric values.

\- Recorded rolling annual period start and end dates.

\- Validated key uniqueness, geographic labels and output row count.



Results:

\- 146 rental areas across 103 reporting periods.

\- Seven unavailable lease counts and seven unavailable medians.



Remaining checks:

\- Confirm whether missing counts and medians occur together.

\- Check numeric ranges and compare selected observations directly

&#x20; against the source workbook.









\## All properties validation



\- Seven observations have both count and median unavailable.

\- All seven belong to Docklands, at early reporting endpoints

&#x20; between March 2000 and December 2001.

\- No observation has only one of those values missing.

\- All published lease counts are nonnegative.

\- All published rental medians are positive.

\- Published lease counts range from 10 to 17,354.

\- Published weekly rental medians range from AUD 90 to AUD 868.



Direct workbook comparisons passed for:

\- Armadale, March 2000.

\- Clayton, September 2025.

\- Docklands, March 2000, including missing-value handling.



These spot checks support the selected observations; they do not

verify every source cell or establish geographic equivalence.



Historical summaries mix reporting periods and rental areas.

The average of their medians is not a current market rent estimate.


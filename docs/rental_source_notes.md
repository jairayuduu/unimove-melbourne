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







\## Cleaning pipeline extended to all categories



Refactored the cleaner into a reusable clean\_sheet function.



Output: data/interim/rent\_all\_categories.csv



\- Seven categories, each containing 15,038 detail observations.

\- Combined output contains 105,266 observations.

\- Region/area label sets are identical across categories.

\- No duplicate observation keys.

\- Geographic labels are populated.

\- Published counts are nonnegative and medians are positive.

\- Existing All properties source comparisons still pass.



Unavailable counts and medians per category:

\- 1 bedroom flat: 1,239 each

\- 2 bedroom flat: 141 each

\- 3 bedroom flat: 786 each

\- 2 bedroom house: 666 each

\- 3 bedroom house: 325 each

\- 4 bedroom house: 703 each

\- All properties: 7 each



Equal missing-value totals do not establish row-level alignment.

That alignment remains to be checked for the other six categories.



All properties is an aggregate category. Do not sum its lease

counts alongside the individual dwelling-category counts.

Matching area labels do not establish equivalence with ABS boundaries.







\## Latest-period coverage



Latest endpoint: 30 September 2025.



Across all 146 workbook rental areas:

\- One-bedroom flats have the lowest publication coverage:

&#x20; 131 published medians, or 89.7%.

\- All properties has published medians for all 146 areas.

\- Missing counts and medians align across all categories

&#x20; throughout the complete history.



The source-region breakdown identifies 110 areas in nine

Melbourne-labelled regions and 36 in regional Victoria.

Publisher regions are not yet verified against ABS boundaries.



Publication coverage measures available statistics, not

properties currently available to rent.


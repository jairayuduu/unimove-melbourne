\# Initial rental budget analysis



Question: Which Melbourne publisher rental areas have a

one-bedroom-flat median at or below $400 per week?



Source period: moving year ending 30 September 2025.

Scope: 110 selected Melbourne publisher rental areas.



Results:

\- 99 areas have published medians.

\- 34 have medians at or below $400 per week.

\- 65 have medians above $400 per week.

\- 11 have unavailable medians and remain unclassified.



These are whole-dwelling rental medians, not room rents,

available listings or guarantees of an individual property's

price. Areas may combine multiple suburbs.



Lease counts describe the source observations underlying

the moving-annual median, not current rental availability.



Reproduce using sql/005\_latest\_rental\_view.sql.





\## Budget sensitivity



Moving year ending 30 September 2025.

Counts represent publisher rental areas whose median is

at or below the weekly whole-dwelling budget.



| Weekly budget | 1-bedroom flat areas | 2-bedroom flat areas |

|---|---:|---:|

| $300 | 4 | 0 |

| $350 | 13 | 0 |

| $400 | 34 | 1 |

| $450 | 64 | 13 |

| $500 | 87 | 35 |

| $600 | 99 | 82 |



One-bedroom medians are published for 99 of 110 areas;

two-bedroom medians are published for 109 of 110 areas.



Increasing the example budget from $400 to $450 expands

the qualifying area count from 34 to 64 for one-bedroom

flats, and from 1 to 13 for two-bedroom flats.



These counts do not measure available properties. Each

publisher area receives equal weight regardless of its

lease count or geographic size.



Reproduce using sql/006\_budget\_sensitivity.sql.


\# Rental geography mapping audit



The Melbourne rental snapshot contains 110 distinct publisher

rental areas. These were compared with the 572 selected ABS

2021 Suburbs and Localities.



\## Name matching



Names are normalised by ignoring case, punctuation, repeated

spaces and the trailing Victorian state qualifier.



Results:

\- 57 direct normalised-name candidates.

\- 4 configured directional alias candidates.

\- 49 unresolved rental areas.

\- 0 boundary-equivalence-verified matches.



Aliases are recorded in config/rental\_area\_aliases.csv.

Their target SAL codes and names are checked against the

suburb master.



\## Limitations and next steps



Name and alias matches are candidate links, not evidence

that publisher rental areas equal ABS SAL boundaries.



Unresolved areas include pooled suburb labels and broader

geographic labels. They require further source investigation.



Published pooled medians must retain their source-area label.

They must not be presented as separately measured medians

for each component suburb.



No rental-to-suburb analytical join has been approved by

this audit alone.



\## Publisher methodology review



Reviewed: Homes Victoria Rental Report, September quarter 2025.



Explanatory note 5 states that rental suburbs and towns derive

from Victorian gazetted localities. Adjacent suburbs with

similar housing-market characteristics may be aggregated

into synthetic suburbs to support regular median reporting.



The report explicitly classifies Mornington Peninsula as

metropolitan, supporting its inclusion in our rental scope.



The report does not supply a complete correspondence between

rental areas and ABS 2021 SAL codes. Existing name and alias

links therefore remain candidates.



Source boundaries and pooled-area membership require further

verification before claiming geographic equivalence.



\## Unresolved-area review queue



docs/rental\_area\_review\_queue.csv tracks 49 unresolved areas:

48 hyphenated labels and one broader-area label, Yarra Ranges.



Hyphenated labels are not automatically split into component

suburbs. Membership requires supporting source evidence.



The audit script preserves an existing queue so subsequent

runs do not overwrite manual review notes.


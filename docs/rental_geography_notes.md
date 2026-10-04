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


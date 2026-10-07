\# Campus proximity



Initial campuses:

\- Monash University — Clayton

\- University of Melbourne — Parkville

\- RMIT University — Melbourne City



Campus identities and official university links are maintained

in config/campuses.csv. Approximate campus reference coordinates

and their source links are in config/campus\_locations.csv.



Coordinates come from OpenStreetMap-based Mapcarta pages;

they are not building entrances or verified Google Maps pins.



\## Distance method



Each suburb reference point is calculated using ST\_PointOnSurface

after transforming its polygon to EPSG:7855.



Reference points are transformed to EPSG:4326. PostGIS geography

distance measures straight-line metres between the campus pin

and suburb reference point, then converts them to kilometres.



These distances do not represent travel times or distances

from individual properties. A suburb containing a campus

can have a non-zero reference-point distance.



\## Validation



Each of the three campuses has 572 suburb distance records.



Manual app checks confirmed:

\- Monash Clayton shows Clayton and Notting Hill first.

\- Switching campuses changes nearby-suburb results.

\- Increasing the radius does not reduce the result count.



\## Current limitation



The campus radius filters the nearby-suburb panel.

Rental budget results remain separate and use selected publisher

regions. Campus-based rental filtering is not yet implemented.



\## Campus and rental comparison



Candidate rental links are stored separately from suburb geometry.

There are 57 normalised-name candidates and four alias candidates;

all remain boundary-unverified.



The campus rental view preserves nearby suburbs without rental

links. Missing rental coverage produces an Unknown budget status.



For Monash Clayton, a 5 km radius, one-bedroom flats and a

$400 weekly budget, SQL returned:

\- 2 candidate-linked suburbs at or below budget.

\- 1 candidate-linked suburb above budget.

\- 11 suburbs with unknown rental coverage.



The app supports a campus-specific comparison and CSV export.

The broader regional rental explorer remains separate.




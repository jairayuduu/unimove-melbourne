\# Transport sources and methodology



\## Source



Transport Victoria GTFS Schedule:

https://opendata.transport.vic.gov.au/dataset/gtfs-schedule



Downloaded on 7 October 2026.

Local source: data/raw/transport/gtfs.zip.



Selected feeds:

\- 2: metropolitan rail, excluding labelled replacement-bus routes

\- 3: trams

\- 4: buses



This analysis does not include the other feeds in the source archive.



\## Stop proximity



The cleaned dataset contains 24,735 served boarding stops/platforms:

501 train, 1,623 tram and 22,611 bus records.



Station entrances and internal station nodes are excluded.

Platform records are not counts of distinct stations.



Distances are straight-line distances from suburb reference points.

They are not walking distances or distances from individual properties.



Nearest-stop results are saved in:

unimove.suburb\_transport\_access\_cached.



After updating the stop data, refresh these saved results:

REFRESH MATERIALIZED VIEW unimove.suburb\_transport\_access\_cached;



\## Direct morning service analysis



Analysis date: Thursday, 8 October 2026.

Departure window: 07:00 inclusive to 09:00 exclusive, Melbourne time.

Suburb scope: reference points within 5 km of each campus.



Calendar weekday rules and service-date exceptions are applied.

Labelled train replacement-bus trips are excluded.



Candidate boarding stops are within 800 m straight-line of the

suburb reference point. Candidate arrival stops are within 800 m

straight-line of the campus pin.



A connection requires:

\- Boarding and arrival on the same active trip.

\- Arrival later in the stop sequence and timetable.

\- Regular pickup and drop-off permitted.

\- Different boarding and arrival stops.

\- Boarding outside the campus's 800 m arrival zone.

\- Arrival at least 100 m closer to the campus pin than boarding.



One boarding/arrival pair is retained per suburb and trip,

prioritising the smallest combined access distances.



\## Interpretation and limitations



In-vehicle minutes exclude walking, waiting and transfers.

Straight-line access thresholds do not establish walkable paths.

The analysis uses scheduled services, not live operations.



Trip counts are distinct trips per suburb, not evenly spaced departures.

The same trip can appear for multiple suburbs.

No candidate under these rules does not mean no public transport.



The analysis does not assess transfers, return journeys, walking-only

options or suburbs beyond 5 km.



\## Validation



All four validation issue counts were zero.



Suburbs with direct candidates across all selected modes:

\- Monash Clayton: 11

\- RMIT Melbourne City: 28

\- University of Melbourne Parkville: 19



The saved analysis contains 2,782 suburb-trip options.


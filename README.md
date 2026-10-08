\# UniMove Melbourne



A campus-centred web app helping students compare Melbourne suburbs using rental medians, campus proximity, scheduled direct transport services, age demographics and recorded-offence context.



\*\*\[Launch the live demo](https://unimove-melbourne.streamlit.app/)\*\*



\## What the app does



Start by choosing a university and campus, then set a dwelling category, weekly whole-dwelling budget and approximate distance radius.



The app provides:



\- A suburb shortlist with budget and rental-coverage status.

\- An interactive map showing the campus and suburb reference points.

\- Candidate rental medians, including pooled publisher areas.

\- Scheduled direct morning transport options towards the campus.

\- Nearest bus, train and tram boarding-stop distances.

\- Census population and the share of residents aged 18–24.

\- Recorded-offence counts with geographic coverage information.

\- CSV downloads for further comparison.



Suburbs with unknown rental coverage can remain in the shortlist. Missing data is not treated as evidence that a suburb meets the budget.



\### Supported campuses



| University | Campus |

|---|---|

| Monash University | Clayton |

| University of Melbourne | Parkville |

| RMIT University | Melbourne City |



\## Data coverage



| Dataset | Coverage used |

|---|---|

| Rental history | 105,266 observations across seven dwelling categories and 146 publisher rental areas |

| Rental reporting periods | 103 quarterly endpoints, March 2000 to September 2025 |

| Latest Melbourne rental snapshot | 110 publisher rental areas across seven categories |

| Suburb geography | 572 selected ABS 2021 Suburbs and Localities |

| Population and age | 2021 Census profiles matched to all 572 selected suburbs |

| Transport boarding stops | 24,735 records across metropolitan train, tram and bus feeds |

| Direct transport services | Example service date: 8 October 2026; departures from 7:00 am to before 9:00 am |

| Recorded offences | Year ending 30 June 2026; candidate geographic coverage for 569 of 572 suburbs |



Rental values are moving annual medians for whole dwellings. They are not room rents, current listings or estimates of an individual property's price.



\## Technical implementation



\*\*Python · pandas · GeoPandas · PostgreSQL · PostGIS · Streamlit · PyDeck · Git\*\*



The project combines a reproducible data pipeline with an interactive app:



1\. Inspect source workbooks, geographic archives and nested GTFS feeds.

2\. Clean rental observations, Census profiles, boarding stops and offence records.

3\. Audit geographic name matches and record explicit alias and pooled-area candidates.

4\. Load structured data and suburb geometries into PostgreSQL/PostGIS.

5\. Build SQL views for campus proximity, rental coverage and contextual indicators.

6\. Cache spatial transport results in materialized views.

7\. Export compact snapshots for a public demo that runs independently of the local database.



The public app reads saved CSV snapshots by default. Database mode supports local work against the PostgreSQL pipeline.



\## Validation and example findings



Validation includes source-cell comparisons, duplicate-key checks, missing-value checks, geometry checks, geographic-link audits and reconciliation of source and database totals.



Selected results:



\- All seven rental categories contain 15,038 historical observations.

\- All 572 selected suburbs have Census population matches.

\- Loaded recorded-offence observations total 620,140, matching the cleaned source.

\- Direct-service checks found no departures outside the selected window, nonpositive journey times or stops outside the configured distance thresholds.

\- Across the selected Melbourne rental areas, 34 of 99 published one-bedroom-flat medians were at or below $400 per week at the September 2025 endpoint. Eleven areas had unavailable medians.



The last finding describes publisher rental areas across Melbourne, rather than campus-specific suburb availability.



\## Interpretation and limitations



\### Geographic associations



Rental publisher areas and crime source areas do not have verified boundary equivalence with ABS suburbs. Associations use documented name, alias or explicit label-component candidates.



A pooled rental median can apply to several linked suburbs. It should not be interpreted as a separately measured median for each suburb.



\### Distance and transport



Campus proximity and stop-access distances are straight-line distances from reference points. They are not walking distances or door-to-door commute times.



Direct-service results use a single example timetable date, nearby suburb reference points within 5 km of each campus, and boarding and arrival stops within configured 800-metre thresholds.



Displayed in-vehicle times exclude walking, waiting and transfers. No qualifying direct service means none was found under these rules; it does not establish that public transport is unavailable.



\### Population and recorded offences



Age profiles describe residents counted in the 2021 Census. They do not identify university students.



Recorded-offence counts are contextual information, not personal-risk estimates or safety rankings. Counts are affected by activity levels, visitors, reporting and policing. The app does not calculate crime rates using the older Census population.



\### Snapshot dates



The demo combines sources from different reporting periods. It does not provide live property listings, real-time transport or automatic source updates.



\## Run the demo locally



Python 3.11 was used for local validation.



```powershell

git clone https://github.com/jairayuduu/unimove-melbourne.git

cd unimove-melbourne

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

python -m pip install -r requirements.txt

python -m streamlit run app.py

```



Demo mode is the default and reads the committed `demo\_data/` snapshots. It does not require PostgreSQL or database secrets.



\## Run with PostgreSQL



Install the full pipeline dependencies:



```powershell

python -m pip install -r requirements-pipeline.txt

```



Follow \[database setup](docs/database\_setup.md) and the relevant source notes and SQL scripts to prepare the database.



Create `.streamlit/secrets.toml` with your local database configuration. This file is excluded from Git.



Then run:



```powershell

$env:UNIMOVE\_DATA\_MODE = "database"

python -m streamlit run app.py

```



To return to snapshot mode:



```powershell

$env:UNIMOVE\_DATA\_MODE = "demo"

python -m streamlit run app.py

```



After updating and validating the database, regenerate demo snapshots with:



```powershell

python .\\src\\export\_demo\_data.py

```



\## Repository structure



| Path | Purpose |

|---|---|

| `app.py` | Streamlit application |

| `config/` | Campus configuration and geographic aliases |

| `src/` | Inspection, cleaning, auditing, loading and export scripts |

| `sql/` | Database tables, analytical views and validation queries |

| `docs/` | Source notes, geographic reviews and findings |

| `demo\_data/` | Compact snapshots used by the public app |

| `requirements.txt` | Demo application dependencies |

| `requirements-pipeline.txt` | Full data-processing and database dependencies |



Raw and intermediate datasets are excluded from Git.



\## Sources



\- Homes Victoria rental reporting.

\- Australian Bureau of Statistics 2021 geography and Census data.

\- Victorian public transport GTFS feeds.

\- Crime Statistics Agency Victoria recorded-offence tables.



Source details, transformation methods and geographic limitations are documented in `docs/`.



\## Future improvements



\- Expand campus coverage.

\- Review unresolved geographic associations.

\- Support additional transport dates and transfer journeys.

\- Improve source-refresh automation.

\- Conduct usability testing with students.


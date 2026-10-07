\# UniMove Melbourne



A student housing decision-support project comparing Melbourne

suburbs based on university campus, rental affordability,

commuting accessibility, amenities and community preferences.



\## Project objectives



\- Integrate public housing, geography, transport and Census data.

\- Explore suburb-level patterns using Python and SQL.

\- Develop transparent, preference-based suburb recommendations.

\- Present analysis in Tableau and a student-facing Streamlit app.



\## Planned technology



Python, PostgreSQL/PostGIS, Tableau, Streamlit and Git.



\## Methodology



Preserve original datasets, document cleaning and geographic joins,

validate derived metrics, and explain the limitations of recommendations.

Use machine learning only where it addresses a justified analytical question.



\## Run the local app



With the virtual environment activated and PostgreSQL running:



1\. Follow docs/database\_setup.md to create and load the database.

2\. Create .streamlit/secrets.toml with your local database credentials.

&#x20;  This file is ignored by Git.

3\. Run:



&#x20;   python -m streamlit run app.py



The initial rental explorer supports dwelling-category selection,

a weekly whole-dwelling budget, qualifying rental-area results,

and separate reporting of unavailable medians.



Manual checks matched SQL results:

\- One-bedroom flat at $400: 34 qualifying areas.

\- Two-bedroom flat at $500: 35 qualifying areas.





Users can filter by publisher rental region and download

qualifying results as CSV, including dwelling category and

reporting dates. Clearing all regions prompts users to select

at least one region.



Manual checks confirmed region filtering, empty-selection

handling and CSV agreement with the displayed results.





\## Campus selection



The app starts with university and campus selection.

Initial coverage includes Monash Clayton, University of

Melbourne Parkville and RMIT Melbourne City.



Campus selection currently controls the entry flow.

Distance-based housing filtering is not yet implemented.

Campus records and official source links are maintained

in config/campuses.csv.



\## Current status



\- Python environment and dependencies configured.

\- Official rental workbook inspected and audited.

\- Reproducible cleaning pipeline implemented for seven categories.

\- 105,266 detail observations generated.

\- Selected observations validated against original Excel cells.

\- Latest-period publication coverage analysed.



Melbourne filtering, geographic joins, SQL modelling,

recommendations, Tableau and Streamlit remain planned.



\- Initial Melbourne rental scope configured: 110 publisher rental areas.

\- Latest rental snapshot filtered and publication coverage assessed.







\- 2021 suburb geography foundation generated: 572 unique SAL codes.

\- Melbourne scope rule documented and substantial boundary crossings flagged.



\- 2021 Census population and derived 18–24 age profiles joined to all 572 suburbs.

\- Rental geography audited: 61 candidate name links and 49 unresolved areas.

\- Rental-to-ABS boundary equivalence remains unverified.



\- PostgreSQL/PostGIS configured with a dedicated project login.

\- 572 suburb boundaries and population records loaded and checked with SQL.



\- Full rental history loaded into PostgreSQL: 146 areas and 105,266 observations.

\- SQL rental coverage summaries checked against Python outputs.



\- Local Streamlit rental explorer implemented and checked against SQL results.



\- Three campus reference points loaded into PostGIS.

\- Campus-driven nearby-suburb exploration implemented and checked.

\- Campus proximity and rental budget results remain separate pending geographic linking.


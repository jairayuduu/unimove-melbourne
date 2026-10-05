# Local database setup



Verified environment:

- PostgreSQL 17.11

- PostGIS 3.6.2

- Psycopg 3.3.6

- Host: localhost

- Port: 5432

- Database: unimove

- Project login: unimove_dev

- Project schema: unimove



## Initial setup



Install PostgreSQL and the compatible PostGIS bundle.



Connect as the PostgreSQL administrator and run:



```sql

CREATE DATABASE unimove;

\connect unimove

CREATE EXTENSION postgis;

CREATE ROLE unimove_dev LOGIN;

GRANT CONNECT ON DATABASE unimove TO unimove_dev;

CREATE SCHEMA unimove AUTHORIZATION unimove_dev;

ALTER ROLE unimove_dev IN DATABASE unimove

SET search_path = unimove, public;

\password unimove_dev



Choose a private password at the interactive prompt.
Passwords are not stored in the repository.
Tables and loading
Connect as unimove_dev and execute:
sql/001_create_suburb_tables.sql
Generate the processed geography and population files before
running:
python src/load_suburbs.py
The loader prompts for the password and requires empty tables.
Both datasets load in one transaction. An error rolls back
the transaction.
Suburb polygons are stored as MultiPolygon geometry in
EPSG:4326, with a GiST spatial index.
Population records reference existing suburb codes and use
(sal_code, census_year) as their primary key.
Validation
Execute:
sql/002_validate_suburb_load.sql
Verified results:
- 572 suburb rows and 572 unique SAL codes.
- No invalid geometries or unexpected SRIDs.
- Two boundary review flags.
- 572 population records.
- Three zero-population records.
- Five sample age percentages match the Python output.
Age percentages are derived from counts. NULLIF prevents
division by zero and returns NULL for zero-population suburbs.

## Rental tables and loading

Execute sql/003_create_rental_tables.sql as unimove_dev,
then run python src/load_rent.py.

Inputs:
- data/interim/rent_all_categories.csv
- config/rental_region_scope.csv

The initial loader requires empty rental tables. It loads
publisher areas and observations in one transaction, using
COPY for the observation history.

Rental areas remain separate from ABS suburbs. No geographic
equivalence is assumed.

Unavailable counts and medians are stored as SQL NULL.
Constraints enforce unique observation keys, supported
categories, moving-annual periods and paired missing values.

## Rental validation

Execute sql/004_validate_rental_load.sql.

Verified results:
- 146 publisher rental areas, including 110 in Melbourne scope.
- 105,266 observations across seven dwelling categories.
- Each category contains 15,038 observations and 103 endpoints,
  from March 2000 through September 2025.
- Historical missing-value counts match the Python summaries.
- Latest Melbourne publication coverage matches the CSV report.

Reporting endpoints are quarterly, but rental observations
represent moving annual periods.
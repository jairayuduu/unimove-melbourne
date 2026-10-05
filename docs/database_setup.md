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

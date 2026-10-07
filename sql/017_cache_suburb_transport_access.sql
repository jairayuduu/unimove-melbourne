BEGIN;

CREATE MATERIALIZED VIEW unimove.suburb_transport_access_cached AS
SELECT *
FROM unimove.suburb_transport_access;

CREATE UNIQUE INDEX suburb_transport_access_cached_key
ON unimove.suburb_transport_access_cached (
    sal_code,
    transport_mode
);

COMMIT;

SELECT
    transport_mode,
    count(*) AS suburb_rows
FROM unimove.suburb_transport_access_cached
GROUP BY transport_mode
ORDER BY transport_mode;
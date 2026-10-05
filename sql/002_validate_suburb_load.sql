-- Confirm row counts and spatial properties.
SELECT
    count(*) AS suburb_rows,
    count(DISTINCT sal_code) AS unique_codes,
    count(*) FILTER (
        WHERE NOT public.ST_IsValid(geom)
    ) AS invalid_geometries,
    count(*) FILTER (
        WHERE public.ST_SRID(geom) <> 4326
    ) AS unexpected_srid,
    count(*) FILTER (
        WHERE boundary_review_required
    ) AS boundary_review_flags
FROM unimove.suburb;

-- Confirm population coverage and zero-population handling.
SELECT
    count(*) AS population_rows,
    count(*) FILTER (
        WHERE population_total = 0
    ) AS zero_population_rows
FROM unimove.suburb_population;

-- Derive percentages from stored counts.
SELECT
    s.suburb_name,
    p.population_total,
    p.population_18_24,
    round(
        100.0 * p.population_18_24
        / NULLIF(p.population_total, 0),
        2
    ) AS share_18_24_pct
FROM unimove.suburb AS s
JOIN unimove.suburb_population AS p
    ON p.sal_code = s.sal_code
WHERE p.census_year = 2021
ORDER BY s.sal_code
LIMIT 5;
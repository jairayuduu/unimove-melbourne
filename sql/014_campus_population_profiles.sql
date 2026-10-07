BEGIN;

CREATE OR REPLACE VIEW unimove.campus_population_profiles AS
SELECT
    d.campus_id,
    d.sal_code,
    d.suburb_name,
    d.straight_line_km,
    p.census_year,
    p.population_total,
    p.population_18_24,
    round(
        100.0 * p.population_18_24
        / NULLIF(p.population_total, 0),
        2
    ) AS share_18_24_pct
FROM unimove.campus_suburb_distance AS d
LEFT JOIN unimove.suburb_population AS p
    ON p.sal_code = d.sal_code
   AND p.census_year = 2021;

COMMIT;

-- Every campus should retain all 572 suburbs.
SELECT
    campus_id,
    count(*) AS suburb_rows,
    count(population_total) AS matched_population_rows,
    count(*) FILTER (
        WHERE population_total = 0
    ) AS zero_population_rows
FROM unimove.campus_population_profiles
GROUP BY campus_id
ORDER BY campus_id;

-- Inspect nearby suburbs for the initial campus.
SELECT
    suburb_name,
    round(straight_line_km::numeric, 2) AS straight_line_km,
    population_total,
    population_18_24,
    share_18_24_pct
FROM unimove.campus_population_profiles
WHERE campus_id = 'monash_clayton'
  AND straight_line_km <= 5
ORDER BY straight_line_km, sal_code;
BEGIN;

CREATE OR REPLACE VIEW unimove.campus_rental_candidates AS
WITH categories AS (
    SELECT DISTINCT dwelling_category
    FROM unimove.latest_melbourne_rent
)
SELECT
    d.campus_id,
    d.university_name,
    d.campus_name,
    d.sal_code,
    d.suburb_name,
    d.straight_line_km,
    c.dwelling_category,
    l.rental_area_id,
    l.match_method,
    l.boundary_equivalence_verified,
    r.source_region,
    r.source_area,
    r.period_start,
    r.period_end,
    r.lease_count,
    r.median_weekly_rent_aud,
    CASE
        WHEN l.rental_area_id IS NULL
            THEN 'no_candidate_link'
        WHEN r.rental_area_id IS NULL
            THEN 'no_latest_observation'
        WHEN r.median_weekly_rent_aud IS NULL
            THEN 'median_unavailable'
        ELSE 'published_candidate'
    END AS rental_coverage_status
FROM unimove.campus_suburb_distance AS d
CROSS JOIN categories AS c
LEFT JOIN unimove.rental_suburb_link AS l
    ON l.sal_code = d.sal_code
LEFT JOIN unimove.latest_melbourne_rent AS r
    ON r.rental_area_id = l.rental_area_id
   AND r.dwelling_category = c.dwelling_category;

COMMIT;

-- Example: Monash Clayton, within 5 km, one-bedroom flats.
SELECT
    suburb_name,
    round(straight_line_km::numeric, 2) AS straight_line_km,
    source_area AS publisher_rental_area,
    median_weekly_rent_aud,
    rental_coverage_status,
    CASE
        WHEN median_weekly_rent_aud IS NULL THEN 'unknown'
        WHEN median_weekly_rent_aud <= 400 THEN 'at_or_below_budget'
        ELSE 'above_budget'
    END AS budget_status
FROM unimove.campus_rental_candidates
WHERE campus_id = 'monash_clayton'
  AND dwelling_category = '1 bedroom flat'
  AND straight_line_km <= 5
ORDER BY straight_line_km, sal_code, rental_area_id;

-- Check whether any suburb has multiple candidate rental areas.
SELECT sal_code, count(*) AS candidate_rental_areas
FROM unimove.rental_suburb_link
GROUP BY sal_code
HAVING count(*) > 1;
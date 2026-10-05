BEGIN;

CREATE OR REPLACE VIEW unimove.latest_melbourne_rent AS
SELECT
    a.rental_area_id,
    a.source_region,
    a.source_area,
    o.dwelling_category,
    o.period_start,
    o.period_end,
    o.period_basis,
    o.lease_count,
    o.median_weekly_rent_aud
FROM unimove.rental_observation AS o
JOIN unimove.rental_area AS a
    ON a.rental_area_id = o.rental_area_id
WHERE a.include_in_melbourne_scope
  AND o.period_end = (
      SELECT max(period_end)
      FROM unimove.rental_observation
  );

COMMIT;

-- Confirm the view uses one common reporting endpoint.
SELECT
    period_end,
    count(*) AS observations,
    count(DISTINCT rental_area_id) AS rental_areas
FROM unimove.latest_melbourne_rent
GROUP BY period_end;

-- Example budget: $400 per week for a whole one-bedroom flat.
SELECT
    count(*) AS total_areas,
    count(median_weekly_rent_aud) AS published_areas,
    count(*) FILTER (
        WHERE median_weekly_rent_aud <= 400
    ) AS areas_at_or_below_budget,
    count(*) FILTER (
        WHERE median_weekly_rent_aud > 400
    ) AS areas_above_budget,
    count(*) FILTER (
        WHERE median_weekly_rent_aud IS NULL
    ) AS unavailable_areas
FROM unimove.latest_melbourne_rent
WHERE dwelling_category = '1 bedroom flat';

-- List qualifying areas, preserving the publisher's labels.
SELECT
    source_region,
    source_area,
    median_weekly_rent_aud,
    lease_count
FROM unimove.latest_melbourne_rent
WHERE dwelling_category = '1 bedroom flat'
  AND median_weekly_rent_aud <= 400
ORDER BY median_weekly_rent_aud, source_area;
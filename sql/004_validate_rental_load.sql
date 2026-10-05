-- Historical coverage and unavailable values.
SELECT
    dwelling_category,
    count(*) AS observations,
    count(DISTINCT period_end) AS periods,
    min(period_end) AS first_endpoint,
    max(period_end) AS last_endpoint,
    count(*) FILTER (
        WHERE lease_count IS NULL
    ) AS unavailable_counts,
    count(*) FILTER (
        WHERE median_weekly_rent_aud IS NULL
    ) AS unavailable_medians
FROM unimove.rental_observation
GROUP BY dwelling_category
ORDER BY dwelling_category;

-- Latest coverage within the selected Melbourne scope.
WITH latest AS (
    SELECT max(period_end) AS period_end
    FROM unimove.rental_observation
)
SELECT
    o.dwelling_category,
    count(*) AS area_rows,
    count(o.median_weekly_rent_aud) AS published_medians,
    count(*) FILTER (
        WHERE o.median_weekly_rent_aud IS NULL
    ) AS unavailable_medians,
    round(
        100.0 * count(o.median_weekly_rent_aud) / count(*),
        1
    ) AS published_pct
FROM unimove.rental_observation AS o
JOIN unimove.rental_area AS a
    ON a.rental_area_id = o.rental_area_id
WHERE a.include_in_melbourne_scope
  AND o.period_end = (SELECT period_end FROM latest)
GROUP BY o.dwelling_category
ORDER BY o.dwelling_category;
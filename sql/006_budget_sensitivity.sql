WITH budgets (weekly_budget_aud) AS (
    VALUES (300), (350), (400), (450), (500), (600)
)
SELECT
    r.dwelling_category,
    r.period_end,
    b.weekly_budget_aud,
    count(*) AS total_areas,
    count(r.median_weekly_rent_aud) AS published_areas,
    count(*) FILTER (
        WHERE r.median_weekly_rent_aud <= b.weekly_budget_aud
    ) AS areas_at_or_below_budget,
    count(*) FILTER (
        WHERE r.median_weekly_rent_aud > b.weekly_budget_aud
    ) AS areas_above_budget,
    count(*) FILTER (
        WHERE r.median_weekly_rent_aud IS NULL
    ) AS unavailable_areas,
    round(
        100.0 * count(*) FILTER (
            WHERE r.median_weekly_rent_aud <= b.weekly_budget_aud
        ) / NULLIF(count(r.median_weekly_rent_aud), 0),
        1
    ) AS pct_of_published_areas_at_or_below_budget
FROM unimove.latest_melbourne_rent AS r
CROSS JOIN budgets AS b
WHERE r.dwelling_category IN (
    '1 bedroom flat', '2 bedroom flat'
)
GROUP BY
    r.dwelling_category,
    r.period_end,
    b.weekly_budget_aud
ORDER BY r.dwelling_category, b.weekly_budget_aud;
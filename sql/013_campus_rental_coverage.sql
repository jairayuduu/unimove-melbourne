SELECT
    campus_id,
    count(*) AS nearby_suburbs,
    count(*) FILTER (
        WHERE rental_coverage_status = 'published_candidate'
    ) AS published_candidates,
    count(*) FILTER (
        WHERE rental_coverage_status = 'median_unavailable'
    ) AS unavailable_medians,
    count(*) FILTER (
        WHERE rental_coverage_status IN (
            'no_candidate_link',
            'no_latest_observation'
        )
    ) AS missing_rental_coverage
FROM unimove.campus_rental_candidates
WHERE dwelling_category = '1 bedroom flat'
  AND straight_line_km <= 5
GROUP BY campus_id
ORDER BY campus_id;

SELECT
    sal_code,
    count(*) AS candidate_rental_areas
FROM unimove.rental_suburb_link
GROUP BY sal_code
HAVING count(*) > 1;
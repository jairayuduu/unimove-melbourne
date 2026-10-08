SELECT
    period_start,
    period_end,
    count(*) AS observations,
    sum(offence_count) AS recorded_offences
FROM unimove.crime_observation
GROUP BY period_start, period_end;

SELECT
    count(*) AS suburb_rows,
    count(*) FILTER (
        WHERE EXISTS (
            SELECT 1
            FROM unimove.crime_suburb_link AS link
            WHERE link.sal_code = suburb.sal_code
        )
    ) AS suburbs_with_candidates,
    count(*) FILTER (
        WHERE NOT EXISTS (
            SELECT 1
            FROM unimove.crime_suburb_link AS link
            WHERE link.sal_code = suburb.sal_code
        )
    ) AS suburbs_without_candidates
FROM unimove.suburb AS suburb;

SELECT
    area.source_lga,
    area.source_postcode,
    area.source_suburb,
    count(*) AS observations,
    sum(observation.offence_count) AS recorded_offences
FROM unimove.crime_source_area AS area
JOIN unimove.crime_observation AS observation
    USING (crime_area_id)
WHERE area.source_suburb IN (
    'Carlton', 'Parkville', 'Clayton', 'Notting Hill'
)
GROUP BY
    area.source_lga,
    area.source_postcode,
    area.source_suburb
ORDER BY area.source_suburb, area.source_postcode;

SELECT crime_area_id, count(*) AS linked_abs_suburbs
FROM unimove.crime_suburb_link
GROUP BY crime_area_id
HAVING count(*) > 1;
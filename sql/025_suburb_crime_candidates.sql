BEGIN;

CREATE OR REPLACE VIEW unimove.suburb_crime_candidates AS
WITH latest_period AS (
    SELECT max(period_end) AS period_end
    FROM unimove.crime_observation
),
totals AS (
    SELECT
        link.sal_code,
        min(observation.period_start) AS period_start,
        observation.period_end,
        count(DISTINCT link.crime_area_id) AS source_area_count,
        sum(observation.offence_count) AS recorded_offences,
        sum(observation.offence_count) FILTER (
            WHERE observation.offence_division =
                'A Crimes against the person'
        ) AS crimes_against_person,
        sum(observation.offence_count) FILTER (
            WHERE observation.offence_division =
                'B Property and deception offences'
        ) AS property_and_deception_offences
    FROM unimove.crime_suburb_link AS link
    JOIN unimove.crime_observation AS observation
        USING (crime_area_id)
    JOIN latest_period
        ON observation.period_end = latest_period.period_end
    GROUP BY link.sal_code, observation.period_end
)
SELECT
    suburb.sal_code,
    suburb.suburb_name,
    totals.period_start,
    latest_period.period_end,
    totals.source_area_count,
    totals.recorded_offences,
    totals.crimes_against_person,
    totals.property_and_deception_offences,
    CASE
        WHEN totals.sal_code IS NULL THEN 'no_candidate_coverage'
        ELSE 'unverified_area_candidate'
    END AS crime_coverage_status
FROM unimove.suburb AS suburb
CROSS JOIN latest_period
LEFT JOIN totals
    ON totals.sal_code = suburb.sal_code;

COMMIT;

SELECT
    crime_coverage_status,
    count(*) AS suburb_rows
FROM unimove.suburb_crime_candidates
GROUP BY crime_coverage_status
ORDER BY crime_coverage_status;

SELECT
    suburb_name,
    source_area_count,
    recorded_offences,
    crimes_against_person,
    property_and_deception_offences
FROM unimove.suburb_crime_candidates
WHERE sal_code IN ('20495', '20569', '21974', '22038')
ORDER BY suburb_name;
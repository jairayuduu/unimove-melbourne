BEGIN;

CREATE OR REPLACE VIEW unimove.suburb_boarding_candidates AS
WITH points AS (
    SELECT
        sal_code,
        public.ST_Transform(
            public.ST_PointOnSurface(
                public.ST_Transform(geom, 7855)
            ),
            4326
        ) AS reference_point
    FROM unimove.suburb
)
SELECT
    s.sal_code,
    t.feed_id,
    t.stop_id,
    t.transport_mode,
    t.stop_name,
    public.ST_Distance(
        s.reference_point::public.geography,
        t.geom::public.geography
    ) AS suburb_distance_metres
FROM points AS s
JOIN unimove.transport_stop AS t
    ON public.ST_DWithin(
        t.geom::public.geography,
        s.reference_point::public.geography,
        800
    );

COMMIT;

SELECT
    d.campus_id,
    count(DISTINCT d.sal_code) AS nearby_suburbs,
    count(DISTINCT d.sal_code) FILTER (
        WHERE b.stop_id IS NOT NULL
    ) AS suburbs_with_boarding_candidates,
    count(DISTINCT d.sal_code) FILTER (
        WHERE b.stop_id IS NULL
    ) AS suburbs_without_boarding_candidates
FROM unimove.campus_suburb_distance AS d
LEFT JOIN unimove.suburb_boarding_candidates AS b
    ON b.sal_code = d.sal_code
WHERE d.straight_line_km <= 5
GROUP BY d.campus_id
ORDER BY d.campus_id;
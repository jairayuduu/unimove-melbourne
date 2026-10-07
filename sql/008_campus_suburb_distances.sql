BEGIN;

CREATE OR REPLACE VIEW unimove.campus_suburb_distance AS
WITH suburb_points AS (
    SELECT
        sal_code,
        suburb_name,
        public.ST_Transform(
            public.ST_PointOnSurface(
                public.ST_Transform(geom, 7855)
            ),
            4326
        ) AS reference_point
    FROM unimove.suburb
)
SELECT
    c.campus_id,
    c.university_name,
    c.campus_name,
    s.sal_code,
    s.suburb_name,
    public.ST_Distance(
        c.geom::public.geography,
        s.reference_point::public.geography
    ) / 1000.0 AS straight_line_km
FROM unimove.campus AS c
CROSS JOIN suburb_points AS s;

COMMIT;

-- Every campus should have distances to all 572 suburbs.
SELECT
    campus_id,
    count(*) AS suburb_distances
FROM unimove.campus_suburb_distance
GROUP BY campus_id
ORDER BY campus_id;

-- Inspect the five nearest suburb reference points per campus.
WITH ranked AS (
    SELECT
        *,
        row_number() OVER (
            PARTITION BY campus_id
            ORDER BY straight_line_km, sal_code
        ) AS proximity_rank
    FROM unimove.campus_suburb_distance
)
SELECT
    campus_id,
    suburb_name,
    round(straight_line_km::numeric, 2) AS straight_line_km
FROM ranked
WHERE proximity_rank <= 5
ORDER BY campus_id, proximity_rank;
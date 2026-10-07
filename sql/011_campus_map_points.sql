BEGIN;

CREATE OR REPLACE VIEW unimove.campus_suburb_map_points AS
WITH suburb_points AS (
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
    d.campus_id,
    d.sal_code,
    d.suburb_name,
    d.straight_line_km,
    public.ST_Y(s.reference_point) AS latitude,
    public.ST_X(s.reference_point) AS longitude,
    public.ST_Y(c.geom) AS campus_latitude,
    public.ST_X(c.geom) AS campus_longitude
FROM unimove.campus_suburb_distance AS d
JOIN suburb_points AS s
    ON s.sal_code = d.sal_code
JOIN unimove.campus AS c
    ON c.campus_id = d.campus_id;

COMMIT;

SELECT
    campus_id,
    count(*) AS suburb_points,
    count(*) FILTER (
        WHERE latitude IS NULL OR longitude IS NULL
    ) AS missing_coordinates
FROM unimove.campus_suburb_map_points
GROUP BY campus_id
ORDER BY campus_id;
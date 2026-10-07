BEGIN;

CREATE OR REPLACE VIEW unimove.suburb_transport_access AS
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
),
modes AS (
    SELECT DISTINCT transport_mode
    FROM unimove.transport_stop
)
SELECT
    s.sal_code,
    s.suburb_name,
    m.transport_mode,
    nearest.feed_id,
    nearest.stop_id,
    nearest.stop_name,
    nearest.parent_station,
    nearest.distance_metres
FROM suburb_points AS s
CROSS JOIN modes AS m
LEFT JOIN LATERAL (
    SELECT
        public.ST_Distance(
            s.reference_point::public.geography,
            t.geom::public.geography
        ) AS search_radius
    FROM unimove.transport_stop AS t
    WHERE t.transport_mode = m.transport_mode
    ORDER BY
        t.geom::public.geography
        <-> s.reference_point::public.geography
    LIMIT 1
) AS seed ON true
LEFT JOIN LATERAL (
    SELECT
        t.feed_id,
        t.stop_id,
        t.stop_name,
        t.parent_station,
        public.ST_Distance(
            s.reference_point::public.geography,
            t.geom::public.geography
        ) AS distance_metres
    FROM unimove.transport_stop AS t
    WHERE t.transport_mode = m.transport_mode
      AND public.ST_DWithin(
          t.geom::public.geography,
          s.reference_point::public.geography,
          seed.search_radius + 0.01
      )
    ORDER BY
        distance_metres,
        t.feed_id,
        t.stop_id
    LIMIT 1
) AS nearest ON true;

COMMIT;

SELECT
    transport_mode,
    count(*) AS suburb_rows,
    count(distance_metres) AS matched_stops
FROM unimove.suburb_transport_access
GROUP BY transport_mode
ORDER BY transport_mode;

SELECT
    suburb_name,
    transport_mode,
    stop_name,
    round(distance_metres::numeric) AS distance_metres
FROM unimove.suburb_transport_access
WHERE suburb_name IN ('Clayton', 'Notting Hill', 'Mount Waverley')
ORDER BY suburb_name, transport_mode;
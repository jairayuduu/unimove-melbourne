BEGIN;

CREATE OR REPLACE VIEW unimove.campus_transport_stops AS
SELECT
    c.campus_id,
    t.feed_id,
    t.stop_id,
    t.transport_mode,
    t.stop_name,
    public.ST_Distance(
        c.geom::public.geography,
        t.geom::public.geography
    ) AS campus_distance_metres
FROM unimove.campus AS c
JOIN unimove.transport_stop AS t
    ON public.ST_DWithin(
        t.geom::public.geography,
        c.geom::public.geography,
        800
    );

COMMIT;

SELECT
    campus_id,
    transport_mode,
    count(*) AS boarding_stops_within_800m,
    round(min(campus_distance_metres)::numeric) AS nearest_metres
FROM unimove.campus_transport_stops
GROUP BY campus_id, transport_mode
ORDER BY campus_id, transport_mode;
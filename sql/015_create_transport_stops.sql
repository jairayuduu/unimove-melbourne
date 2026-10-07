BEGIN;

CREATE TABLE unimove.transport_stop (
    feed_id text NOT NULL,
    stop_id text NOT NULL,
    transport_mode text NOT NULL CHECK (
        transport_mode IN (
            'metropolitan_train',
            'tram',
            'bus'
        )
    ),
    stop_name text NOT NULL,
    parent_station text,
    geom public.geometry(Point, 4326) NOT NULL,
    PRIMARY KEY (feed_id, stop_id),
    CONSTRAINT transport_stop_valid_geometry CHECK (
        NOT public.ST_IsEmpty(geom)
        AND public.ST_IsValid(geom)
        AND public.ST_Y(geom) BETWEEN -90 AND 90
        AND public.ST_X(geom) BETWEEN -180 AND 180
    )
);

CREATE INDEX transport_stop_geography_idx
ON unimove.transport_stop
USING gist ((geom::public.geography));

COMMIT;
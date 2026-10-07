BEGIN;

CREATE TABLE unimove.campus (
    campus_id text PRIMARY KEY,
    university_name text NOT NULL,
    campus_name text NOT NULL,
    source_url text NOT NULL,
    coordinate_source_url text NOT NULL,
    location_method text NOT NULL,
    geom public.geometry(Point, 4326) NOT NULL,

    UNIQUE (university_name, campus_name),

    CONSTRAINT campus_geometry_not_empty CHECK (
        NOT public.ST_IsEmpty(geom)
    ),
    CONSTRAINT campus_longitude_range CHECK (
        public.ST_X(geom) BETWEEN -180 AND 180
    ),
    CONSTRAINT campus_latitude_range CHECK (
        public.ST_Y(geom) BETWEEN -90 AND 90
    )
);

COMMIT;
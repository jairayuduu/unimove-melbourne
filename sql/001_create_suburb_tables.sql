BEGIN;

CREATE TABLE unimove.suburb (
    sal_code text PRIMARY KEY,
    suburb_name text NOT NULL,
    geography_year smallint NOT NULL,
    scope_method text NOT NULL,
    outside_melbourne_pct double precision NOT NULL,
    boundary_review_required boolean NOT NULL,
    area_sq_km double precision NOT NULL,
    geom public.geometry(MultiPolygon, 4326) NOT NULL,

    CONSTRAINT suburb_code_format
        CHECK (sal_code ~ '^[0-9]{5}$'),
    CONSTRAINT suburb_outside_pct_range
        CHECK (outside_melbourne_pct BETWEEN 0 AND 100),
    CONSTRAINT suburb_area_positive
        CHECK (area_sq_km > 0),
    CONSTRAINT suburb_geometry_valid
        CHECK (public.ST_IsValid(geom)),
    CONSTRAINT suburb_geometry_not_empty
        CHECK (NOT public.ST_IsEmpty(geom))
);

CREATE INDEX suburb_geom_idx
    ON unimove.suburb USING gist (geom);

CREATE TABLE unimove.suburb_population (
    sal_code text NOT NULL
        REFERENCES unimove.suburb (sal_code),
    census_year smallint NOT NULL,
    population_total integer NOT NULL,
    population_18_24 integer NOT NULL,

    PRIMARY KEY (sal_code, census_year),

    CONSTRAINT population_total_nonnegative
        CHECK (population_total >= 0),
    CONSTRAINT population_18_24_nonnegative
        CHECK (population_18_24 >= 0)
);

COMMIT;
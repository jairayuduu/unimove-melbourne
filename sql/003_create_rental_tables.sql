BEGIN;

CREATE TABLE unimove.rental_area (
    rental_area_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_region text NOT NULL,
    source_area text NOT NULL,
    include_in_melbourne_scope boolean NOT NULL,

    UNIQUE (source_region, source_area)
);

CREATE TABLE unimove.rental_observation (
    rental_area_id bigint NOT NULL
        REFERENCES unimove.rental_area (rental_area_id),
    dwelling_category text NOT NULL,
    period_start date NOT NULL,
    period_end date NOT NULL,
    period_basis text NOT NULL,
    lease_count integer,
    median_weekly_rent_aud numeric(10, 2),

    PRIMARY KEY (
        rental_area_id, dwelling_category, period_end
    ),

    CONSTRAINT rental_category_allowed CHECK (
        dwelling_category IN (
            '1 bedroom flat',
            '2 bedroom flat',
            '3 bedroom flat',
            '2 bedroom house',
            '3 bedroom house',
            '4 bedroom house',
            'All properties'
        )
    ),
    CONSTRAINT rental_period_basis CHECK (
        period_basis = 'moving_annual'
    ),
    CONSTRAINT rental_period_dates CHECK (
        period_start =
        (period_end - INTERVAL '1 year' + INTERVAL '1 day')::date
    ),
    CONSTRAINT rental_count_nonnegative CHECK (
        lease_count >= 0
    ),
    CONSTRAINT rental_median_positive CHECK (
        median_weekly_rent_aud > 0
    ),
    CONSTRAINT rental_missing_values_paired CHECK (
        (lease_count IS NULL) =
        (median_weekly_rent_aud IS NULL)
    )
);

CREATE INDEX rental_observation_period_idx
    ON unimove.rental_observation (
        period_end, dwelling_category
    );

COMMIT;
BEGIN;

CREATE TABLE unimove.crime_source_area (
    crime_area_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_lga text NOT NULL,
    source_postcode text NOT NULL,
    source_suburb text NOT NULL,
    UNIQUE (source_lga, source_postcode, source_suburb)
);

CREATE TABLE unimove.crime_observation (
    crime_area_id bigint NOT NULL
        REFERENCES unimove.crime_source_area (crime_area_id),
    period_start date NOT NULL,
    period_end date NOT NULL,
    offence_division text NOT NULL,
    offence_subdivision text NOT NULL,
    offence_subgroup text NOT NULL,
    offence_count integer NOT NULL CHECK (offence_count >= 0),

    PRIMARY KEY (
        crime_area_id,
        period_end,
        offence_division,
        offence_subdivision,
        offence_subgroup
    ),

    CHECK (period_start <= period_end)
);

CREATE TABLE unimove.crime_suburb_link (
    crime_area_id bigint NOT NULL
        REFERENCES unimove.crime_source_area (crime_area_id),
    sal_code text NOT NULL
        REFERENCES unimove.suburb (sal_code),
    match_method text NOT NULL CHECK (
        match_method IN (
            'name_match_candidate',
            'alias_match_candidate'
        )
    ),
    boundary_equivalence_verified boolean NOT NULL DEFAULT false,
    evidence_reference text NOT NULL,

    PRIMARY KEY (crime_area_id, sal_code),
    CHECK (NOT boundary_equivalence_verified)
);

CREATE INDEX crime_suburb_link_sal_idx
ON unimove.crime_suburb_link (sal_code);

CREATE INDEX crime_observation_period_idx
ON unimove.crime_observation (period_end);

COMMIT;
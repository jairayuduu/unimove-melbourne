BEGIN;

CREATE TABLE unimove.rental_suburb_link (
    rental_area_id bigint NOT NULL
        REFERENCES unimove.rental_area (rental_area_id),
    sal_code text NOT NULL
        REFERENCES unimove.suburb (sal_code),
    match_method text NOT NULL,
    boundary_equivalence_verified boolean NOT NULL DEFAULT false,
    evidence_reference text NOT NULL,

    PRIMARY KEY (rental_area_id, sal_code),

    CONSTRAINT rental_link_method CHECK (
        match_method IN (
            'name_match_candidate',
            'alias_match_candidate'
        )
    ),
    CONSTRAINT candidate_boundary_unverified CHECK (
        NOT boundary_equivalence_verified
    )
);

COMMIT;
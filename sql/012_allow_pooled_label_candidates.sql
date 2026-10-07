BEGIN;

ALTER TABLE unimove.rental_suburb_link
DROP CONSTRAINT rental_link_method;

ALTER TABLE unimove.rental_suburb_link
ADD CONSTRAINT rental_link_method CHECK (
    match_method IN (
        'name_match_candidate',
        'alias_match_candidate',
        'explicit_label_component_candidate'
    )
);

COMMIT;
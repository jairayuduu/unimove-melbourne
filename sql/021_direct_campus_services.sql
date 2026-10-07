BEGIN;

DROP MATERIALIZED VIEW unimove.direct_campus_services;

CREATE MATERIALIZED VIEW unimove.direct_campus_services AS
WITH candidates AS (
    SELECT
        d.campus_id,
        d.sal_code,
        d.suburb_name,
        trip.service_date,
        trip.feed_id,
        trip.trip_id,
        trip.transport_mode,
        trip.route_short_name,
        trip.route_long_name,
        boarding.stop_id AS boarding_stop_id,
        boarding.stop_name AS boarding_stop_name,
        boarding.suburb_distance_metres,
        destination.stop_id AS arrival_stop_id,
        destination.stop_name AS arrival_stop_name,
        destination.campus_distance_metres,
        origin_time.departure_seconds,
        arrival_time.arrival_seconds,
        arrival_time.arrival_seconds
            - origin_time.departure_seconds AS in_vehicle_seconds
    FROM unimove.campus_suburb_distance AS d

    JOIN unimove.suburb_boarding_candidates AS boarding
      ON boarding.sal_code = d.sal_code

    JOIN unimove.transport_connection_stop_time AS origin_time
      ON origin_time.feed_id = boarding.feed_id
     AND origin_time.stop_id = boarding.stop_id

    JOIN unimove.transport_service_trip AS trip
      ON trip.service_date = origin_time.service_date
     AND trip.feed_id = origin_time.feed_id
     AND trip.trip_id = origin_time.trip_id

    JOIN unimove.campus_transport_stops AS destination
      ON destination.campus_id = d.campus_id
     AND destination.feed_id = origin_time.feed_id

    JOIN unimove.transport_connection_stop_time AS arrival_time
      ON arrival_time.service_date = origin_time.service_date
     AND arrival_time.feed_id = origin_time.feed_id
     AND arrival_time.trip_id = origin_time.trip_id
     AND arrival_time.stop_id = destination.stop_id

    WHERE d.straight_line_km <= 5
      AND trip.service_date = DATE '2026-10-08'
      AND origin_time.departure_seconds >= 7 * 3600
      AND origin_time.departure_seconds < 9 * 3600
      AND origin_time.pickup_type = 0
      AND arrival_time.drop_off_type = 0
      AND arrival_time.stop_sequence > origin_time.stop_sequence
      AND arrival_time.stop_id <> origin_time.stop_id
      AND arrival_time.arrival_seconds > origin_time.departure_seconds
      AND public.ST_Distance(
          (
              SELECT c.geom
              FROM unimove.campus AS c
              WHERE c.campus_id = d.campus_id
          )::public.geography,
          (
              SELECT t.geom
              FROM unimove.transport_stop AS t
              WHERE t.feed_id = boarding.feed_id
                AND t.stop_id = boarding.stop_id
          )::public.geography
      ) > destination.campus_distance_metres + 100
      AND NOT EXISTS (
          SELECT 1
          FROM unimove.campus_transport_stops AS campus_stop
          WHERE campus_stop.campus_id = d.campus_id
            AND campus_stop.feed_id = boarding.feed_id
            AND campus_stop.stop_id = boarding.stop_id
      )
)
-- Keep one boarding/alighting combination per suburb and trip.
SELECT DISTINCT ON (
    campus_id, sal_code, service_date, feed_id, trip_id
)
    *
FROM candidates
ORDER BY
    campus_id,
    sal_code,
    service_date,
    feed_id,
    trip_id,
    suburb_distance_metres + campus_distance_metres,
    in_vehicle_seconds,
    boarding_stop_id,
    arrival_stop_id,
    departure_seconds;

CREATE UNIQUE INDEX direct_campus_services_key
ON unimove.direct_campus_services (
    campus_id, sal_code, service_date, feed_id, trip_id
);

COMMIT;

SELECT
    campus_id,
    transport_mode,
    count(DISTINCT sal_code) AS suburbs_with_direct_services,
    count(*) AS suburb_trip_options
FROM unimove.direct_campus_services
GROUP BY campus_id, transport_mode
ORDER BY campus_id, transport_mode;

SELECT
    suburb_name,
    transport_mode,
    route_short_name,
    boarding_stop_name,
    arrival_stop_name,
    round(in_vehicle_seconds / 60.0, 1) AS in_vehicle_minutes
FROM unimove.direct_campus_services
WHERE campus_id = 'monash_clayton'
ORDER BY suburb_name, departure_seconds
LIMIT 15;
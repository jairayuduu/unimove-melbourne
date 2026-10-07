BEGIN;

CREATE TABLE unimove.transport_service_trip (
    service_date date NOT NULL,
    feed_id text NOT NULL,
    trip_id text NOT NULL,
    route_id text NOT NULL,
    transport_mode text NOT NULL,
    route_short_name text NOT NULL,
    route_long_name text NOT NULL,
    PRIMARY KEY (service_date, feed_id, trip_id)
);

CREATE TABLE unimove.transport_connection_stop_time (
    service_date date NOT NULL,
    feed_id text NOT NULL,
    trip_id text NOT NULL,
    stop_sequence integer NOT NULL CHECK (stop_sequence >= 0),
    stop_id text NOT NULL,
    arrival_seconds integer CHECK (arrival_seconds >= 0),
    departure_seconds integer CHECK (departure_seconds >= 0),
    pickup_type smallint NOT NULL CHECK (pickup_type BETWEEN 0 AND 3),
    drop_off_type smallint NOT NULL CHECK (drop_off_type BETWEEN 0 AND 3),

    PRIMARY KEY (
        service_date, feed_id, trip_id, stop_sequence
    ),

    FOREIGN KEY (service_date, feed_id, trip_id)
        REFERENCES unimove.transport_service_trip (
            service_date, feed_id, trip_id
        ),

    FOREIGN KEY (feed_id, stop_id)
        REFERENCES unimove.transport_stop (feed_id, stop_id)
);

CREATE INDEX transport_connection_stop_lookup
ON unimove.transport_connection_stop_time (
    service_date, feed_id, stop_id
);

COMMIT;
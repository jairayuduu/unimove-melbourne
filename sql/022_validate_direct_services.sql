SELECT
    count(*) FILTER (
        WHERE departure_seconds < 7 * 3600
           OR departure_seconds >= 9 * 3600
    ) AS departures_outside_window,
    count(*) FILTER (
        WHERE in_vehicle_seconds <= 0
    ) AS nonpositive_journey_times,
    count(*) FILTER (
        WHERE suburb_distance_metres > 800
           OR campus_distance_metres > 800
    ) AS stops_outside_threshold
FROM unimove.direct_campus_services;

SELECT count(*) AS boarding_stops_inside_campus_zone
FROM unimove.direct_campus_services AS service
JOIN unimove.campus_transport_stops AS campus_stop
  ON campus_stop.campus_id = service.campus_id
 AND campus_stop.feed_id = service.feed_id
 AND campus_stop.stop_id = service.boarding_stop_id;

SELECT
    campus_id,
    count(DISTINCT sal_code) AS suburbs_with_direct_candidates
FROM unimove.direct_campus_services
GROUP BY campus_id
ORDER BY campus_id;
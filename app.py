from pathlib import Path
import pydeck as pdk
import pandas as pd
import psycopg
import streamlit as st
st.set_page_config(page_title="UniMove Melbourne", layout="wide")
PROJECT_ROOT = Path(__file__).resolve().parent
@st.cache_data(ttl=300)
def load_campus_distances(campus_id):
    with psycopg.connect(**dict(st.secrets["database"])) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_code, suburb_name, straight_line_km
                FROM unimove.campus_suburb_distance
                WHERE campus_id = %s
                ORDER BY straight_line_km, sal_code
            """, (campus_id,))
            rows = cursor.fetchall()
            columns = [column.name for column in cursor.description]
    return pd.DataFrame(rows, columns=columns)
@st.cache_data(ttl=300)
def load_campus_rent(campus_id, dwelling_category, radius_km):
    with psycopg.connect(**dict(st.secrets["database"])) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_code, suburb_name, straight_line_km,
                       source_area, median_weekly_rent_aud,
                       rental_coverage_status, match_method,
                       boundary_equivalence_verified,
                       period_start, period_end, lease_count
                FROM unimove.campus_rental_candidates
                WHERE campus_id = %s
                  AND dwelling_category = %s
                  AND straight_line_km <= %s
                ORDER BY straight_line_km, sal_code, rental_area_id
            """, (campus_id, dwelling_category, radius_km))
            rows = cursor.fetchall()
            columns = [column.name for column in cursor.description]
    frame = pd.DataFrame(rows, columns=columns)
    frame["median_weekly_rent_aud"] = pd.to_numeric(
        frame["median_weekly_rent_aud"]
    )
    return frame
@st.cache_data(ttl=300)
def load_rent():
    with psycopg.connect(**dict(st.secrets["database"])) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT source_region, source_area, dwelling_category,
                       period_start, period_end, lease_count,
                       median_weekly_rent_aud
                FROM unimove.latest_melbourne_rent
            """)
            rows = cursor.fetchall()
            columns = [column.name for column in cursor.description]
    frame = pd.DataFrame(rows, columns=columns)
    frame["median_weekly_rent_aud"] = pd.to_numeric(
        frame["median_weekly_rent_aud"]
    )
    return frame
@st.cache_data(ttl=300)
def load_population_profiles(campus_id):
    with psycopg.connect(**dict(st.secrets["database"])) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_code, census_year, population_total,
                       population_18_24, share_18_24_pct
                FROM unimove.campus_population_profiles
                WHERE campus_id = %s
            """, (campus_id,))
            rows = cursor.fetchall()
            columns = [column.name for column in cursor.description]
    frame = pd.DataFrame(rows, columns=columns)
    frame["share_18_24_pct"] = pd.to_numeric(frame["share_18_24_pct"])
    return frame
@st.cache_data(ttl=300)
def load_transport_access():
    with psycopg.connect(**dict(st.secrets["database"])) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_code, transport_mode, stop_name, distance_metres
                FROM unimove.suburb_transport_access_cached
                ORDER BY sal_code, transport_mode
            """)
            rows = cursor.fetchall()
            columns = [column.name for column in cursor.description]
    frame = pd.DataFrame(rows, columns=columns)
    if frame.empty:
        raise ValueError("Cached transport results are empty.")
    if frame.duplicated(["sal_code", "transport_mode"]).any():
        raise ValueError("Duplicate suburb/transport mode keys.")
    frame["distance_metres"] = pd.to_numeric(frame["distance_metres"])
    result = pd.DataFrame({"sal_code": frame["sal_code"].unique()})
    for mode, prefix in (
        ("bus", "bus"),
        ("metropolitan_train", "train"),
        ("tram", "tram"),
    ):
        subset = frame.loc[
            frame["transport_mode"].eq(mode),
            ["sal_code", "stop_name", "distance_metres"],
        ].rename(columns={
            "stop_name": f"nearest_{prefix}_stop",
            "distance_metres": f"nearest_{prefix}_distance_metres",
        })
        result = result.merge(
            subset, on="sal_code", how="left", validate="one_to_one"
        )
    return result
@st.cache_data(ttl=300)
def load_direct_services(campus_id):
    with psycopg.connect(**dict(st.secrets["database"])) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_code, suburb_name, service_date, feed_id, trip_id,
                       transport_mode, route_short_name, route_long_name,
                       boarding_stop_name, arrival_stop_name,
                       suburb_distance_metres, campus_distance_metres,
                       departure_seconds, arrival_seconds, in_vehicle_seconds
                FROM unimove.direct_campus_services
                WHERE campus_id = %s
                ORDER BY service_date, suburb_name, departure_seconds,
                         feed_id, trip_id
            """, (campus_id,))
            rows = cursor.fetchall()
            columns = [column.name for column in cursor.description]
    return pd.DataFrame(rows, columns=columns)
@st.cache_data(ttl=300)
def load_crime_candidates():
    with psycopg.connect(**dict(st.secrets["database"])) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_code, period_start, period_end, source_area_count,
                       recorded_offences, crimes_against_person,
                       property_and_deception_offences, crime_coverage_status
                FROM unimove.suburb_crime_candidates
                ORDER BY sal_code
            """)
            rows = cursor.fetchall()
            columns = [column.name for column in cursor.description]
    frame = pd.DataFrame(rows, columns=columns)
    if frame.empty:
        raise ValueError("Crime candidate view is empty.")
    if frame["sal_code"].duplicated().any():
        raise ValueError("Duplicate crime candidate suburb codes.")
    for column in [
        "source_area_count", "recorded_offences", "crimes_against_person",
        "property_and_deception_offences",
    ]:
        frame[column] = pd.to_numeric(frame[column]).astype("Int64")
    return frame
@st.cache_data(ttl=300)
def load_map_points(campus_id):
    with psycopg.connect(**dict(st.secrets["database"])) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_code, suburb_name, straight_line_km,
                       latitude, longitude,
                       campus_latitude, campus_longitude
                FROM unimove.campus_suburb_map_points
                WHERE campus_id = %s
                ORDER BY sal_code
            """, (campus_id,))
            rows = cursor.fetchall()
            columns = [column.name for column in cursor.description]
    return pd.DataFrame(rows, columns=columns)
st.title("UniMove Melbourne")
st.write("Choose your campus, then explore housing options.")
campuses = pd.read_csv(PROJECT_ROOT / "config" / "campuses.csv")
university = st.selectbox(
    "University",
    options=sorted(campuses["university_name"].unique()),
    index=None,
    placeholder="Select your university",
)
if university is None:
    st.info("Select your university to get started.")
    st.stop()
university_campuses = campuses.loc[
    campuses["university_name"].eq(university)
]
campus_name = st.selectbox(
    "Campus",
    options=university_campuses["campus_name"].tolist(),
    index=None,
    placeholder="Select your campus",
    key=f"campus_selection_{university}",
)
if campus_name is None:
    st.info("Select the campus where you will study.")
    st.stop()
selected_campus = university_campuses.loc[
    university_campuses["campus_name"].eq(campus_name)
].iloc[0]
campus_id = selected_campus["campus_id"]
st.caption(f"Selected campus: {university} — {campus_name}")
try:
    rent = load_rent()
    distances = load_campus_distances(campus_id)
except Exception:
    st.error(
        "Could not load project data. Check that PostgreSQL is running, "
        "your database configuration is correct, and the SQL views exist."
    )
    st.stop()
if rent.empty or distances.empty:
    st.info("Rental data or campus distances are unavailable.")
    st.stop()
endpoint = pd.Timestamp(rent["period_end"].max())
st.subheader("Your housing preferences")
radius = st.slider(
    "Approximate straight-line radius (km)",
    min_value=1,
    max_value=30,
    value=5,
    step=1,
)
category = st.selectbox(
    "Dwelling category",
    [
        "1 bedroom flat",
        "2 bedroom flat",
        "3 bedroom flat",
        "2 bedroom house",
        "3 bedroom house",
        "4 bedroom house",
        "All properties",
    ],
)
budget = st.slider(
    "Weekly whole-dwelling budget (AUD)",
    min_value=200,
    max_value=1200,
    value=400,
    step=10,
)
st.caption(
    f"Moving annual rental medians ending {endpoint:%d %B %Y}. "
    "Whole-dwelling rents, not room rents or current listings."
)
# Combined campus proximity and candidate rental information.
st.header(f"Nearby suburbs for {campus_name}")
try:
    campus_rent = load_campus_rent(campus_id, category, radius)
except Exception:
    st.error(
        "Could not load combined campus and rental results. "
        "Check that the campus_rental_candidates view exists."
    )
    st.stop()
# Current links should yield at most one rental candidate per suburb.
if campus_rent["sal_code"].duplicated().any():
    st.error(
        "A suburb has multiple rental candidates. "
        "The geographic links need review before displaying a shortlist."
    )
    st.stop()
try:
    population = load_population_profiles(campus_id)
except Exception:
    st.error(
        "Could not load population profiles. Check that PostgreSQL "
        "is running and the campus_population_profiles view exists."
    )
    st.stop()
if population["sal_code"].duplicated().any():
    st.error("Population profiles contain duplicate suburb codes.")
    st.stop()
campus_rent = campus_rent.merge(
    population,
    on="sal_code",
    how="left",
    validate="one_to_one",
)
try:
    transport = load_transport_access()
except Exception:
    st.error(
        "Could not load transport access. Check that PostgreSQL is "
        "running and the cached transport results have been created."
    )
    st.stop()
campus_rent = campus_rent.merge(
    transport, on="sal_code", how="left", validate="one_to_one"
)
campus_rent["budget_status"] = "Unknown"
has_median = campus_rent["median_weekly_rent_aud"].notna()
campus_rent.loc[
    has_median & campus_rent["median_weekly_rent_aud"].le(budget),
    "budget_status",
] = "At or below budget"
campus_rent.loc[
    has_median & campus_rent["median_weekly_rent_aud"].gt(budget),
    "budget_status",
] = "Above budget"
campus_rent["rental_basis"] = campus_rent["match_method"].map({
    "name_match_candidate": "Name candidate",
    "alias_match_candidate": "Alias candidate",
    "explicit_label_component_candidate": "Pooled-area proxy",
}).fillna("No candidate link")
try:
    direct_services = load_direct_services(campus_id)
except Exception:
    st.error(
        "Could not load direct-service results. Check that the "
        "direct_campus_services materialized view has been created."
    )
    direct_services = None
try:
    crime_candidates = load_crime_candidates()
except Exception:
    st.error(
        "Could not load recorded-offence data. Check that PostgreSQL is "
        "running and the suburb_crime_candidates view exists."
    )
    crime_candidates = None
if direct_services is not None and not direct_services.empty:
    service_dates = sorted(direct_services["service_date"].unique())
    service_date = st.selectbox(
        "Timetable analysis date",
        service_dates,
        format_func=lambda value: value.strftime("%d %B %Y"),
        key="direct_service_date",
    )
st.subheader("Your student shortlist")
st.caption("Combine your rent preference with campus proximity, demographics and dated direct-service results.")
shortlist = campus_rent.copy()
shortlist["direct_trip_candidates"] = pd.Series(pd.NA, index=shortlist.index, dtype="Int64")
shortlist["median_in_vehicle_minutes"] = float("nan")
shortlist["direct_service_status"] = "Not assessed"
shortlist["transport_analysis_date"] = None
if direct_services is not None and not direct_services.empty:
    day_services = direct_services.loc[direct_services["service_date"].eq(service_date)].copy()
    day_services["minutes"] = day_services["in_vehicle_seconds"] / 60
    day_summary = day_services.groupby("sal_code", as_index=False).agg(
        direct_trip_candidates=("trip_id", "size"),
        median_in_vehicle_minutes=("minutes", "median"),
    )
    shortlist = shortlist.drop(columns=["direct_trip_candidates", "median_in_vehicle_minutes"]).merge(
        day_summary, on="sal_code", how="left", validate="one_to_one"
    )
    assessed_mask = shortlist["straight_line_km"].le(5)
    shortlist["direct_trip_candidates"] = shortlist["direct_trip_candidates"].astype("Int64")
    shortlist.loc[assessed_mask, "direct_trip_candidates"] = shortlist.loc[
        assessed_mask, "direct_trip_candidates"
    ].fillna(0)
    shortlist.loc[assessed_mask, "transport_analysis_date"] = service_date
    shortlist.loc[assessed_mask, "direct_service_status"] = "None found under these rules"
    shortlist.loc[assessed_mask & shortlist["direct_trip_candidates"].gt(0).fillna(False),
                  "direct_service_status"] = "Direct candidates found"
if crime_candidates is not None:
    shortlist = shortlist.merge(
        crime_candidates.rename(columns={
            "period_start": "crime_period_start", "period_end": "crime_period_end"
        }), on="sal_code", how="left", validate="one_to_one"
    )
else:
    shortlist["recorded_offences"] = pd.NA
    shortlist["crime_coverage_status"] = "Unavailable"
rent_filter = st.checkbox("Keep only candidate medians at or below my budget", value=True, key="shortlist_budget")
keep_unknown = st.checkbox("Also retain suburbs with unknown rent", value=True,
                           disabled=not rent_filter, key="shortlist_unknown")
require_direct = st.checkbox("Require a direct morning-service candidate", value=False, key="shortlist_direct")
sort_choice = st.selectbox("Sort shortlist by", [
    "Campus distance", "Median weekly rent", "Share aged 18–24 (highest first)"
], key="shortlist_sort")
if rent_filter:
    keep = shortlist["budget_status"].eq("At or below budget")
    if keep_unknown:
        keep |= shortlist["budget_status"].eq("Unknown")
    shortlist = shortlist.loc[keep].copy()
if require_direct:
    shortlist = shortlist.loc[shortlist["direct_service_status"].eq("Direct candidates found")].copy()
    st.caption("This filter excludes suburbs without a found candidate and suburbs outside the assessed 5 km scope.")
sort_settings = {
    "Campus distance": ("straight_line_km", True),
    "Median weekly rent": ("median_weekly_rent_aud", True),
    "Share aged 18–24 (highest first)": ("share_18_24_pct", False),
}
sort_field, ascending = sort_settings[sort_choice]
shortlist = shortlist.sort_values([sort_field, "suburb_name"], ascending=[ascending, True], na_position="last")
st.metric("Suburbs in your shortlist", len(shortlist))
if shortlist.empty:
    st.info("No suburbs meet these shortlist filters. Try retaining unknown rents or relaxing the direct-service requirement.")
else:
    shortlist_columns = {
        "suburb_name": "Suburb", "straight_line_km": "Campus distance (km)",
        "median_weekly_rent_aud": "Candidate weekly rent (AUD)",
        "budget_status": "Budget status", "rental_basis": "Rental association",
        "direct_service_status": "Direct-service result",
        "direct_trip_candidates": "Trip candidates, 7–9 am",
        "median_in_vehicle_minutes": "Median in-vehicle minutes",
        "share_18_24_pct": "Residents aged 18–24 (%)",
        "recorded_offences": "Candidate-area recorded offences",
    }
    st.dataframe(shortlist[list(shortlist_columns)].rename(columns=shortlist_columns),
        hide_index=True, width="stretch", column_config={
            "Campus distance (km)": st.column_config.NumberColumn(format="%.2f"),
            "Candidate weekly rent (AUD)": st.column_config.NumberColumn(format="$%.2f"),
            "Median in-vehicle minutes": st.column_config.NumberColumn(format="%.1f"),
            "Residents aged 18–24 (%)": st.column_config.NumberColumn(format="%.2f"),
        })
    shortlist_export = shortlist.copy()
    shortlist_export.insert(0, "campus_id", campus_id)
    shortlist_export["dwelling_category"] = category
    shortlist_export["weekly_budget_aud"] = budget
    shortlist_export["radius_km"] = radius
    st.download_button("Download your student shortlist",
        data=shortlist_export.to_csv(index=False).encode("utf-8"),
        file_name=f"unimove_{campus_id}_shortlist.csv", mime="text/csv", key="download_shortlist")
st.caption("Unknown rent is not confirmed affordability. Vehicle minutes exclude walking and waiting. Age shares use the 2021 Census; recorded offences use their separate reporting period and unverified area links. Crime counts are context, not a safety ranking. See the detailed sections above for sources and limitations.")

st.subheader("Suburb map")
map_scope = st.radio("Show on map", ["Your shortlist", "All nearby suburbs"],
                     horizontal=True, key="map_scope")
try:
    map_points = load_map_points(campus_id)
except Exception:
    st.error("Could not load map coordinates.")
    st.stop()
if map_points.empty:
    st.info("Map coordinates are unavailable for this campus.")
else:
    nearby_points = map_points.loc[
        map_points["straight_line_km"].le(radius)
    ].copy()
    if map_scope == "Your shortlist":
        nearby_points = nearby_points.loc[
            nearby_points["sal_code"].isin(shortlist["sal_code"])
        ].copy()
    if nearby_points.empty:
        st.info("No suburb markers match the current map selection; the campus remains visible.")

    nearby_points = nearby_points.merge(
        campus_rent[["sal_code", "budget_status"]],
        on="sal_code",
        how="left",
        validate="one_to_one",
    )
    nearby_points["budget_status"] = (
        nearby_points["budget_status"].fillna("Unknown")
    )
    colours = {
        "At or below budget": [46, 160, 90, 210],
        "Above budget": [220, 80, 70, 210],
        "Unknown": [140, 140, 140, 210],
    }
    nearby_points["colour"] = nearby_points["budget_status"].map(colours)
    nearby_points["map_label"] = nearby_points["suburb_name"]
    nearby_points["distance_label"] = nearby_points[
        "straight_line_km"
    ].map(lambda value: f"{value:.2f} km")
    campus_latitude = float(map_points.iloc[0]["campus_latitude"])
    campus_longitude = float(map_points.iloc[0]["campus_longitude"])
    campus_marker = pd.DataFrame([{
        "latitude": campus_latitude,
        "longitude": campus_longitude,
        "map_label": f"{university} — {campus_name}",
        "budget_status": "Selected campus",
        "distance_label": "Campus reference point",
    }])
    suburb_layer = pdk.Layer(
        "ScatterplotLayer",
        data=nearby_points,
        get_position="[longitude, latitude]",
        get_fill_color="colour",
        get_radius=100,
        radius_min_pixels=5,
        radius_max_pixels=12,
        pickable=True,
    )
    campus_layer = pdk.Layer(
        "ScatterplotLayer",
        data=campus_marker,
        get_position="[longitude, latitude]",
        get_fill_color=[40, 110, 240, 255],
        get_radius=150,
        radius_min_pixels=10,
        radius_max_pixels=18,
        stroked=True,
        get_line_color=[255, 255, 255],
        line_width_min_pixels=2,
        pickable=True,
    )
    zoom = 12 if radius <= 5 else 11 if radius <= 15 else 10
    st.pydeck_chart(
        pdk.Deck(
            layers=[suburb_layer, campus_layer],
            initial_view_state=pdk.ViewState(
                latitude=campus_latitude,
                longitude=campus_longitude,
                zoom=zoom,
                pitch=0,
            ),
            map_style=(
                "https://basemaps.cartocdn.com/gl/"
                "positron-gl-style/style.json"
            ),
            tooltip={
                "text": (
                    "{map_label}\n"
                    "{budget_status}\n"
                    "{distance_label}"
                )
            },
        )
    )
    st.caption(
        "Blue: campus · Green: candidate median within budget · "
        "Red: candidate median above budget · Grey: unknown rent. "
        "Markers represent suburb reference points, not properties."
    )
# Retain broader regional rental exploration separately.
st.divider()

st.header("Explore the supporting data")

with st.expander('Rental, population and nearest-stop details'):
    within_budget, above_budget, unknown = st.columns(3)
    within_budget.metric(
        "Nearby candidates within budget",
        int(campus_rent["budget_status"].eq("At or below budget").sum()),
    )
    above_budget.metric(
        "Nearby candidates above budget",
        int(campus_rent["budget_status"].eq("Above budget").sum()),
    )
    unknown.metric(
        "Nearby suburbs with unknown rent",
        int(campus_rent["budget_status"].eq("Unknown").sum()),
    )
    st.caption(
        "Distances are measured from the campus pin to a reference point "
        "inside each suburb. They are not travel times or distances from "
        "individual properties."
    )
    st.caption(
        "Rental links are unverified candidates. Pooled-area proxies "
        "reuse the publisher's combined-area median, not a separately "
        "measured suburb rent. Unknown rent does not mean above budget."
    )
    campus_display_columns = {
        "suburb_name": "Suburb",
        "straight_line_km": "Approximate distance (km)",
        "source_area": "Publisher rental area",
        "median_weekly_rent_aud": "Median weekly rent (AUD)",
        "budget_status": "Budget status",
        "rental_basis": "Rental association",
        "population_total": "Population (2021)",
        "population_18_24": "Residents aged 18–24 (2021)",
        "share_18_24_pct": "Residents aged 18–24 (%)",
        "nearest_bus_distance_metres": "Nearest bus stop (m)",
        "nearest_train_distance_metres": "Nearest train platform (m)",
        "nearest_tram_distance_metres": "Nearest tram stop (m)",
    }
    if campus_rent.empty:
        st.info("No suburb reference points fall within this radius.")
    else:
        st.dataframe(
            campus_rent[list(campus_display_columns)].rename(
                columns=campus_display_columns
            ),
            hide_index=True,
            width="stretch",
            column_config={
                "Approximate distance (km)": st.column_config.NumberColumn(
                    format="%.2f"
                ),
                "Median weekly rent (AUD)": st.column_config.NumberColumn(
                    format="$%.2f"
                ),
                "Nearest bus stop (m)": st.column_config.NumberColumn(format="%.0f"),
                "Nearest train platform (m)": st.column_config.NumberColumn(
                    format="%.0f"
                ),
                "Nearest tram stop (m)": st.column_config.NumberColumn(format="%.0f"),
                "Population (2021)": st.column_config.NumberColumn(format="%d"),
                "Residents aged 18–24 (2021)": st.column_config.NumberColumn(
                    format="%d"
                ),
                "Residents aged 18–24 (%)": st.column_config.NumberColumn(
                    format="%.2f"
                ),
            },
        )
        st.caption(
            "Demographics are from the 2021 Census. The age percentage "
            "describes residents aged 18–24; it does not measure student "
            "numbers or opportunities to socialise. Percentages are "
            "unavailable for suburbs with zero population."
        )
        st.caption(
            "Transport distances are straight-line distances from the suburb "
            "reference point to the nearest served boarding stop/platform in "
            "the selected feeds. They are not walking distances, service "
            "frequency or campus commute times. Train replacement-bus routes "
            "are excluded; service on a particular date has not been checked."
        )
        with st.container():
            st.dataframe(
                campus_rent[[
                    "suburb_name", "nearest_bus_stop",
                    "nearest_train_stop", "nearest_tram_stop",
                ]].rename(columns={
                    "suburb_name": "Suburb",
                    "nearest_bus_stop": "Bus stop",
                    "nearest_train_stop": "Train platform",
                    "nearest_tram_stop": "Tram stop",
                }),
                hide_index=True,
                width="stretch",
            )
        campus_export = campus_rent.copy()
        campus_export.insert(0, "campus_id", campus_id)
        campus_export.insert(1, "dwelling_category", category)
        campus_export["weekly_budget_aud"] = budget
        campus_export["radius_km"] = radius
        st.download_button(
            label="Download nearby suburb comparison",
            data=campus_export.to_csv(index=False).encode("utf-8"),
            file_name=(
                f"unimove_{campus_id}_{endpoint:%Y%m%d}"
                f"_radius_{radius}_budget_{budget}.csv"
            ),
            mime="text/csv",
            key="download_campus_comparison",
        )
    # Retain broader regional rental exploration separately.

with st.expander('Scheduled direct-service details'):
    st.subheader("Direct morning services towards campus")
    st.caption(
        "Scheduled departures from 7–9 am (Melbourne time). Boarding stops "
        "are within 800 m of suburb reference points; arrival stops are within "
        "800 m of the campus pin. Boarding inside the campus arrival zone is "
        "excluded. This analysis covers suburbs within 5 km of campus."
    )
    if direct_services is not None:
        if direct_services.empty:
            st.info("No direct-service candidates are available for this campus.")
        else:
            assessed = campus_rent.loc[
                campus_rent["straight_line_km"].le(5),
                ["sal_code", "suburb_name"],
            ].copy()
            services = direct_services.loc[
                direct_services["service_date"].eq(service_date)
                & direct_services["sal_code"].isin(assessed["sal_code"])
            ].copy()
            services["in_vehicle_minutes"] = services["in_vehicle_seconds"] / 60
            summary = services.groupby("sal_code", as_index=False).agg(
                direct_trip_candidates=("trip_id", "size"),
                median_in_vehicle_minutes=("in_vehicle_minutes", "median"),
            )
            comparison = assessed.merge(
                summary, on="sal_code", how="left", validate="one_to_one"
            )
            comparison["direct_trip_candidates"] = comparison[
                "direct_trip_candidates"
            ].fillna(0).astype(int)
            comparison["service_result"] = comparison[
                "direct_trip_candidates"
            ].map(lambda count: "Direct candidates found" if count else
                  "None found under these rules")
            st.dataframe(
                comparison.rename(columns={
                    "suburb_name": "Suburb",
                    "direct_trip_candidates": "Trip candidates, 7–9 am",
                    "median_in_vehicle_minutes": "Median in-vehicle minutes",
                    "service_result": "Analysis result",
                }).drop(columns="sal_code"),
                hide_index=True,
                width="stretch",
                column_config={
                    "Median in-vehicle minutes": st.column_config.NumberColumn(
                        format="%.1f"
                    ),
                },
            )
            if radius > 5:
                st.info(
                    "Suburbs beyond 5 km are not assessed in this service analysis."
                )
            st.caption(
                "Minutes cover only time on the vehicle, excluding walking and "
                "waiting. Counts are distinct trips per suburb, not evenly spaced "
                "departures or live service frequency. No candidate does not mean "
                "no public transport: transfers and walking-only options are not "
                "assessed. One boarding/alighting pair is retained per trip, "
                "prioritising shorter combined straight-line access distances."
            )
            if not services.empty:
                with st.container():
                    service_suburb = st.selectbox(
                        "Suburb for timetable details",
                        sorted(services["suburb_name"].unique()),
                        key="service_suburb",
                    )
                    details = services.loc[
                        services["suburb_name"].eq(service_suburb)
                    ].copy()
                    for field, label in (
                        ("departure_seconds", "Departure"),
                        ("arrival_seconds", "Arrival"),
                    ):
                        details[label] = details[field].map(
                            lambda value: f"{int(value) // 3600:02d}:"
                            f"{(int(value) % 3600) // 60:02d}"
                        )
                    st.dataframe(
                        details[[
                            "transport_mode", "route_short_name", "Departure",
                            "Arrival", "boarding_stop_name", "arrival_stop_name",
                            "in_vehicle_minutes", "suburb_distance_metres",
                            "campus_distance_metres",
                        ]].rename(columns={
                            "transport_mode": "Mode",
                            "route_short_name": "Route",
                            "boarding_stop_name": "Boarding stop",
                            "arrival_stop_name": "Arrival stop",
                            "in_vehicle_minutes": "In-vehicle minutes",
                            "suburb_distance_metres": "Suburb-to-stop distance (m)",
                            "campus_distance_metres": "Stop-to-campus distance (m)",
                        }),
                        hide_index=True,
                        width="stretch",
                    )
                service_export = services.copy()
                service_export.insert(0, "campus_id", campus_id)
                st.download_button(
                    "Download scheduled direct-service candidates",
                    data=service_export.to_csv(index=False).encode("utf-8"),
                    file_name=f"unimove_{campus_id}_services_{service_date:%Y%m%d}.csv",
                    mime="text/csv",
                    key="download_direct_services",
                )

with st.expander('Recorded-offence context'):
    st.subheader("Recorded offences near your campus")
    st.caption(
        "Counts describe offences recorded in candidate publisher areas. "
        "They are not a safety ranking or a measure of your personal risk. "
        "Area size, visitors, reporting and policing can affect comparisons."
    )
    if crime_candidates is not None:
        crime_comparison = campus_rent[["sal_code", "suburb_name"]].merge(
            crime_candidates, on="sal_code", how="left", validate="one_to_one"
        )
        crime_endpoint = pd.Timestamp(crime_candidates["period_end"].max())
        starts = crime_candidates["period_start"].dropna()
        if not starts.empty:
            crime_start = pd.Timestamp(starts.min())
            st.caption(
                f"Reporting period: {crime_start:%d %B %Y} to "
                f"{crime_endpoint:%d %B %Y}."
            )
        crime_comparison["coverage_label"] = crime_comparison[
            "crime_coverage_status"
        ].map({
            "unverified_area_candidate": "Unverified area candidate",
            "no_candidate_coverage": "No candidate coverage",
        }).fillna("No candidate coverage")
        if crime_comparison.empty:
            st.info("No nearby suburbs are selected for this radius.")
        else:
            crime_columns = {
                "suburb_name": "Suburb",
                "recorded_offences": "Recorded offences",
                "crimes_against_person": "Crimes against the person",
                "property_and_deception_offences": "Property and deception offences",
                "source_area_count": "Contributing source areas",
                "coverage_label": "Geographic coverage",
            }
            st.dataframe(
                crime_comparison[list(crime_columns)].rename(columns=crime_columns),
                hide_index=True,
                width="stretch",
                column_config={
                    label: st.column_config.NumberColumn(format="%d")
                    for field, label in crime_columns.items()
                    if field not in {"suburb_name", "coverage_label"}
                },
            )
            st.caption(
                "Name and configured alias links have not been verified against "
                "publisher boundaries. Counts sum linked LGA/postcode/suburb "
                "combinations; contributing areas are shown explicitly. "
                "Missing records remain unknown. The two category columns are "
                "parts of the total; other offence divisions are also included "
                "in the total. Source exclusions include justice institutions, "
                "immigration facilities, Unincorporated Victoria and unknown "
                "geographic locations. No population rate is calculated."
            )
            crime_export = crime_comparison.copy()
            crime_export.insert(0, "campus_id", campus_id)
            crime_export["radius_km"] = radius
            crime_export["boundary_equivalence_verified"] = False
            st.download_button(
                "Download nearby recorded-offence comparison",
                data=crime_export.to_csv(index=False).encode("utf-8"),
                file_name=(
                    f"unimove_{campus_id}_crime_{crime_endpoint:%Y%m%d}"
                    f"_radius_{radius}.csv"
                ),
                mime="text/csv",
                key="download_crime_comparison",
            )

with st.expander('Broader Melbourne rental comparison'):
    st.header("Compare broader Melbourne rental regions")
    st.caption(
        "This regional comparison uses your dwelling category and budget, "
        "but is independent of the selected campus radius."
    )
    regions = sorted(rent["source_region"].unique().tolist())
    selected_regions = st.multiselect(
        "Rental regions",
        options=regions,
        default=regions,
    )
    if not selected_regions:
        st.info("Select at least one rental region to see regional results.")
        st.stop()
    selected = rent.loc[
        rent["dwelling_category"].eq(category)
        & rent["source_region"].isin(selected_regions)
    ].copy()
    published = selected["median_weekly_rent_aud"].notna()
    qualifying = selected.loc[
        published & selected["median_weekly_rent_aud"].le(budget)
    ].sort_values(["median_weekly_rent_aud", "source_area"])
    first, second, third = st.columns(3)
    first.metric("Areas at or below budget", len(qualifying))
    second.metric("Areas with published medians", int(published.sum()))
    third.metric("Areas with unavailable medians", int((~published).sum()))
    st.subheader("Rental areas whose median meets your budget")
    st.caption(
        "Publisher areas can combine several suburbs. "
        "A qualifying median does not guarantee an available property."
    )
    display_columns = {
        "source_region": "Region",
        "source_area": "Rental area",
        "median_weekly_rent_aud": "Median weekly rent (AUD)",
        "lease_count": "Leases in reporting year",
    }
    if qualifying.empty:
        st.info("No published area medians meet this budget.")
    else:
        st.dataframe(
            qualifying[list(display_columns)].rename(columns=display_columns),
            hide_index=True,
            width="stretch",
        )
        export_columns = [
            "source_region",
            "source_area",
            "dwelling_category",
            "period_start",
            "period_end",
            "median_weekly_rent_aud",
            "lease_count",
        ]
        st.download_button(
            label="Download qualifying rental areas as CSV",
            data=qualifying[export_columns].to_csv(index=False).encode("utf-8"),
            file_name=(
                f"unimove_rental_areas_{endpoint:%Y%m%d}"
                f"_budget_{budget}.csv"
            ),
            mime="text/csv",
            key="download_regional_results",
        )
    with st.container():
        st.dataframe(
            selected.loc[
                ~published, ["source_region", "source_area"]
            ].rename(columns=display_columns),
            hide_index=True,
            width="stretch",
        )

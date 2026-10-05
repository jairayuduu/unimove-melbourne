import pandas as pd
import psycopg
import streamlit as st

st.set_page_config(page_title="UniMove Melbourne", layout="wide")

st.title("UniMove Melbourne")
st.write("Explore Melbourne rental areas within your weekly budget.")


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


try:
    rent = load_rent()
except Exception:
    st.error(
        "Could not load rental data. Check that PostgreSQL is running "
        "and your local database configuration is correct."
    )
    st.stop()

if rent.empty:
    st.info("No rental data has been loaded yet.")
    st.stop()

endpoint = pd.Timestamp(rent["period_end"].max())
st.caption(
    f"Moving annual rental medians ending {endpoint:%d %B %Y}. "
    "Whole-dwelling rents, not room rents or current listings."
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

selected = rent.loc[rent["dwelling_category"].eq(category)].copy()
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

with st.expander("Areas with unavailable medians"):
    st.dataframe(
        selected.loc[
            ~published, ["source_region", "source_area"]
        ].rename(columns=display_columns),
        hide_index=True,
        width="stretch",
    )
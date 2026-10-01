
import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(
    page_title="Global Budget Analytics Core",
    layout="wide"
)



@st.cache_resource
def get_engine():

    

    engine = create_engine(
        "sqlite:///global_budget_db.db"
    )

    return engine

engine = get_engine()


st.title("🏛️ Global Government Budget Analytics Core")

st.markdown(
"""
Interactive platform exploring public finance trends,
sector allocation, anomaly detection,
volatility analysis and future projections.
"""
)


countries = pd.read_sql_query(
"""
SELECT country_name
FROM countries
ORDER BY country_name
""",
engine
)

selected_country = st.sidebar.selectbox(
    "Select Country",
    countries["country_name"]
)


tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Macro Trends",
    "🧱 Sector Analysis",
    "🔍 Anomalies",
    "🔬 Research Lab"
])


with tab1:

    q = """
    SELECT
        b.year,
        b.Total_Budget_Billions_USD
    FROM budgets b
    JOIN countries c
    ON b.country_id=c.country_id
    WHERE c.country_name=:country_name
    ORDER BY year
    """

    df_macro = pd.read_sql_query(
        q,
        engine,
        params={"country_name": selected_country}
    )

    if df_macro.empty:
        st.warning("No data found.")
    else:

        fig = px.line(
            df_macro,
            x="year",
            y="Total_Budget_Billions_USD",
            template="plotly_dark",
            title=f"{selected_country} Budget Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


with tab2:

    q = """
    SELECT
        b.year,
        sa.sector_name,
        sa.allocated_percentage
    FROM sector_allocations sa
    JOIN budgets b
    ON sa.budget_id=b.budget_id
    JOIN countries c
    ON b.country_id=c.country_id
    WHERE c.country_name=:country_name
    """

    df_sector = pd.read_sql_query(
        q,
        engine,
        params={"country_name": selected_country}
    )

    if not df_sector.empty:

        c1, c2 = st.columns(2)

        with c1:

            fig = px.area(
                df_sector,
                x="year",
                y="allocated_percentage",
                color="sector_name",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with c2:

            fig = px.box(
                df_sector,
                x="sector_name",
                y="allocated_percentage",
                color="sector_name",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


with tab3:

    if not df_macro.empty:

        mean = df_macro["Total_Budget_Billions_USD"].mean()
        std = df_macro["Total_Budget_Billions_USD"].std()

        if std != 0:

            df_macro["z_score"] = (
                df_macro["Total_Budget_Billions_USD"]-mean
            )/std

            outliers = df_macro[
                abs(df_macro["z_score"])>1.96
            ]

            st.dataframe(outliers)

        else:

            st.success("No statistical anomalies detected.")


with tab4:

    q = """
    SELECT
        b.year,
        sa.sector_name,
        sa.allocated_percentage
    FROM sector_allocations sa
    JOIN budgets b
    ON sa.budget_id=b.budget_id
    JOIN countries c
    ON b.country_id=c.country_id
    WHERE c.country_name=:country_name
    """

    corr_df = pd.read_sql_query(
        q,
        engine,
        params={"country_name": selected_country}
    )

    if not corr_df.empty:

        pivot = corr_df.pivot_table(
            index="year",
            columns="sector_name",
            values="allocated_percentage",
            aggfunc="mean"
        )

        corr = pivot.corr()

        fig = px.imshow(
            corr,
            text_auto=".2f",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    if not df_macro.empty:

        degree = st.selectbox(
            "Polynomial Degree",
            [1,2,3],
            index=1
        )

        future = st.slider(
            "Forecast Year",
            2025,
            2050,
            2035
        )

        x = df_macro["year"].values
        y = df_macro["Total_Budget_Billions_USD"].values

        if len(x)>degree:

            poly = np.poly1d(
                np.polyfit(x,y,degree)
            )

            years = np.arange(
                x.max()+1,
                future+1
            )

            pred = poly(years)

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="lines+markers",
                    name="Historical"
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=pred,
                    mode="lines",
                    line=dict(dash="dash"),
                    name="Projection"
                )
            )

            fig.update_layout(
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine, text

import plotly.express as px
import plotly.graph_objects as go

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "global_budget_db.db"
# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Global Budget Analytics",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    .main {
        background-color: #0E1117;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* KPI CARDS */

    .metric-card {
        background: linear-gradient(
            135deg,
            #171B24,
            #1D2330
        );

        border: 1px solid #2A3140;
        border-radius: 14px;

        padding: 20px;

        min-height: 125px;

        box-shadow:
            0 4px 12px rgba(0,0,0,0.25);
    }

    .metric-title {
        color: #94A3B8;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #F8FAFC;
        font-size: 28px;
        font-weight: 700;
    }

    .metric-sub {
        color: #64748B;
        font-size: 12px;
        margin-top: 5px;
    }


    /* SECTION HEADINGS */

    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #F8FAFC;

        margin-top: 25px;
        margin-bottom: 10px;
    }


    /* SIDEBAR */

    section[data-testid="stSidebar"] {
        background-color: #11151D;
    }


    /* DATAFRAME */

    [data-testid="stDataFrame"] {
        border-radius: 10px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# DATABASE
# =========================================================

@st.cache_resource
def get_engine():
    return create_engine(
        f"sqlite:///{DB_PATH}"
    )

engine = get_engine()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def format_number(value):

    if pd.isna(value):
        return "N/A"

    if abs(value) >= 1_000_000:

        return f"{value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:

        return f"{value / 1_000:.2f}K"

    return f"{value:,.2f}"


def format_budget(value):

    if pd.isna(value):
        return "N/A"

    return f"${value:,.2f}B"


def create_metric(title, value, subtitle=""):

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-title">
                {title}
            </div>

            <div class="metric-value">
                {value}
            </div>

            <div class="metric-sub">
                {subtitle}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# HEADER
# =========================================================

st.title("🏛️ Global Government Budget Analytics")

st.markdown(
    """
    **Executive public-finance intelligence platform**

    Explore government budgets, sector allocations,
    statistical anomalies, volatility and future projections.
    """
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ Dashboard Controls")

countries = pd.read_sql_query(
    """
    SELECT
        country_id,
        country_name
    FROM countries
    ORDER BY country_name
    """,
    engine
)


if countries.empty:

    st.error("No countries found in database.")

    st.stop()


selected_country = st.sidebar.selectbox(
    "🌍 Country",
    countries["country_name"].tolist()
)


# =========================================================
# LOAD MACRO DATA
# =========================================================

macro_query = text("""
    SELECT
        b.budget_id,
        b.year,
        b.Total_Budget_Billions_USD
    FROM budgets b

    JOIN countries c
        ON b.country_id = c.country_id

    WHERE c.country_name = :country_name

    ORDER BY b.year
""")


df_macro = pd.read_sql(
    macro_query,
    engine,
    params={
        "country_name": selected_country
    }
)


if df_macro.empty:

    st.warning(
        f"No budget data available for {selected_country}."
    )

    st.stop()


# =========================================================
# DATA PREPARATION
# =========================================================

df_macro["YoY_Growth_%"] = (
    df_macro["Total_Budget_Billions_USD"]
    .pct_change()
    * 100
)


latest = df_macro.iloc[-1]

latest_budget = latest[
    "Total_Budget_Billions_USD"
]

latest_year = int(
    latest["year"]
)


previous_budget = (
    df_macro.iloc[-2]["Total_Budget_Billions_USD"]
    if len(df_macro) > 1
    else np.nan
)


latest_growth = (
    latest_budget / previous_budget - 1
) * 100 if previous_budget else np.nan


average_budget = (
    df_macro[
        "Total_Budget_Billions_USD"
    ].mean()
)


maximum_budget = (
    df_macro[
        "Total_Budget_Billions_USD"
    ].max()
)


minimum_budget = (
    df_macro[
        "Total_Budget_Billions_USD"
    ].min()
)


# =========================================================
# KPI SECTION
# =========================================================

st.markdown(
    '<div class="section-title">📊 Executive Overview</div>',
    unsafe_allow_html=True
)


k1, k2, k3, k4, k5 = st.columns(5)


with k1:

    create_metric(
        "Latest Budget",
        format_budget(latest_budget),
        f"Fiscal year {latest_year}"
    )


with k2:

    growth_text = (
        f"{latest_growth:+.2f}%"
        if not pd.isna(latest_growth)
        else "N/A"
    )

    create_metric(
        "YoY Growth",
        growth_text,
        "vs previous year"
    )


with k3:

    create_metric(
        "Average Budget",
        format_budget(average_budget),
        "Historical average"
    )


with k4:

    create_metric(
        "Maximum Budget",
        format_budget(maximum_budget),
        "Historical maximum"
    )


with k5:

    create_metric(
        "Data Coverage",
        f"{len(df_macro)} Years",
        f"{int(df_macro['year'].min())}–{latest_year}"
    )


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📈 Macro Trends",
        "🧱 Sector Analysis",
        "🚨 Anomalies",
        "🔮 Forecasting",
        "🔬 Research Lab"
    ]
)


# =========================================================
# TAB 1
# MACRO TRENDS
# =========================================================

with tab1:

    st.markdown(
        '<div class="section-title">Government Budget Evolution</div>',
        unsafe_allow_html=True
    )


    c1, c2 = st.columns([2, 1])


    # -----------------------------------------
    # BUDGET TREND
    # -----------------------------------------

    with c1:

        fig = px.line(
            df_macro,
            x="year",
            y="Total_Budget_Billions_USD",
            markers=True,
            template="plotly_dark"
        )

        fig.update_traces(
            line=dict(width=3)
        )

        fig.update_layout(
            title="Annual Government Budget",
            xaxis_title="Year",
            yaxis_title="Budget (Billion USD)",
            hovermode="x unified",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # -----------------------------------------
    # YOY GROWTH
    # -----------------------------------------

    with c2:

        growth_df = df_macro.dropna(
            subset=["YoY_Growth_%"]
        )

        fig = px.bar(
            growth_df,
            x="year",
            y="YoY_Growth_%",
            template="plotly_dark"
        )

        fig.add_hline(
            y=0,
            line_dash="dash"
        )

        fig.update_layout(
            title="Year-over-Year Growth",
            xaxis_title="Year",
            yaxis_title="Growth (%)",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # -----------------------------------------
    # HISTORICAL TABLE
    # -----------------------------------------

    st.markdown(
        '<div class="section-title">Historical Budget Data</div>',
        unsafe_allow_html=True
    )


    display_df = df_macro.copy()

    display_df[
        "Total_Budget_Billions_USD"
    ] = display_df[
        "Total_Budget_Billions_USD"
    ].round(2)


    display_df[
        "YoY_Growth_%"
    ] = display_df[
        "YoY_Growth_%"
    ].round(2)


    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# TAB 2
# SECTOR ANALYSIS
# =========================================================

with tab2:

    sector_query = text("""
        SELECT
            b.year,
            sa.sector_name,
            sa.allocated_percentage

        FROM sector_allocations sa

        JOIN budgets b
            ON sa.budget_id = b.budget_id

        JOIN countries c
            ON b.country_id = c.country_id

        WHERE c.country_name = :country_name

        ORDER BY b.year
    """)


    df_sector = pd.read_sql(
        sector_query,
        engine,
        params={
            "country_name": selected_country
        }
    )


    if df_sector.empty:

        st.warning(
            "No sector allocation data available."
        )

    else:

        # -------------------------------------
        # LATEST YEAR SECTOR DATA
        # -------------------------------------

        latest_sector = df_sector[
            df_sector["year"] == latest_year
        ].copy()


        # -------------------------------------
        # SECTOR KPIs
        # -------------------------------------

        sc1, sc2, sc3 = st.columns(3)


        with sc1:

            top_sector = (
                latest_sector
                .sort_values(
                    "allocated_percentage",
                    ascending=False
                )
                .iloc[0]
            )

            create_metric(
                "Largest Sector",
                top_sector["sector_name"],
                f"{top_sector['allocated_percentage']:.2f}% allocation"
            )


        with sc2:

            create_metric(
                "Number of Sectors",
                len(latest_sector),
                f"Year {latest_year}"
            )


        with sc3:

            create_metric(
                "Average Allocation",
                f"{latest_sector['allocated_percentage'].mean():.2f}%",
                "Across sectors"
            )


        # -------------------------------------
        # CHARTS
        # -------------------------------------

        c1, c2 = st.columns(2)


        with c1:

            fig = px.area(
                df_sector,
                x="year",
                y="allocated_percentage",
                color="sector_name",
                template="plotly_dark"
            )

            fig.update_layout(
                title="Sector Allocation Over Time",
                xaxis_title="Year",
                yaxis_title="Allocation (%)",
                height=450
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        with c2:

            fig = px.bar(
                latest_sector.sort_values(
                    "allocated_percentage",
                    ascending=True
                ),
                x="allocated_percentage",
                y="sector_name",
                orientation="h",
                template="plotly_dark"
            )

            fig.update_layout(
                title=f"Sector Allocation — {latest_year}",
                xaxis_title="Allocation (%)",
                yaxis_title="Sector",
                height=450
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        # -------------------------------------
        # BOX PLOT
        # -------------------------------------

        fig = px.box(
            df_sector,
            x="sector_name",
            y="allocated_percentage",
            template="plotly_dark"
        )

        fig.update_layout(
            title="Sector Allocation Distribution",
            xaxis_title="Sector",
            yaxis_title="Allocation (%)",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# TAB 3
# ANOMALIES
# =========================================================

with tab3:

    st.markdown(
        '<div class="section-title">Statistical Anomaly Detection</div>',
        unsafe_allow_html=True
    )


    anomaly_df = df_macro.copy()


    # -----------------------------------------
    # Z-SCORE
    # -----------------------------------------

    mean_budget = anomaly_df[
        "Total_Budget_Billions_USD"
    ].mean()

    std_budget = anomaly_df[
        "Total_Budget_Billions_USD"
    ].std()


    if std_budget != 0:

        anomaly_df["z_score"] = (
            anomaly_df[
                "Total_Budget_Billions_USD"
            ] - mean_budget
        ) / std_budget


    else:

        anomaly_df["z_score"] = 0


    anomaly_df["Z_Anomaly"] = (
        anomaly_df["z_score"].abs() > 1.96
    )


    # -----------------------------------------
    # IQR
    # -----------------------------------------

    q1 = anomaly_df[
        "Total_Budget_Billions_USD"
    ].quantile(0.25)

    q3 = anomaly_df[
        "Total_Budget_Billions_USD"
    ].quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr

    upper_bound = q3 + 1.5 * iqr


    anomaly_df["IQR_Anomaly"] = (
        (
            anomaly_df[
                "Total_Budget_Billions_USD"
            ] < lower_bound
        )
        |
        (
            anomaly_df[
                "Total_Budget_Billions_USD"
            ] > upper_bound
        )
    )


    anomaly_df["Anomaly"] = (
        anomaly_df["Z_Anomaly"]
        |
        anomaly_df["IQR_Anomaly"]
    )


    # -----------------------------------------
    # KPI
    # -----------------------------------------

    total_anomalies = int(
        anomaly_df["Anomaly"].sum()
    )


    a1, a2, a3 = st.columns(3)


    with a1:

        create_metric(
            "Detected Anomalies",
            total_anomalies,
            "Z-score or IQR"
        )


    with a2:

        create_metric(
            "Z-Score Threshold",
            "±1.96",
            "95% reference threshold"
        )


    with a3:

        create_metric(
            "IQR Range",
            f"{lower_bound:.1f} – {upper_bound:.1f}",
            "Billion USD"
        )


    # -----------------------------------------
    # ANOMALY CHART
    # -----------------------------------------

    fig = go.Figure()


    normal = anomaly_df[
        ~anomaly_df["Anomaly"]
    ]

    abnormal = anomaly_df[
        anomaly_df["Anomaly"]
    ]


    fig.add_trace(
        go.Scatter(
            x=normal["year"],
            y=normal[
                "Total_Budget_Billions_USD"
            ],
            mode="lines+markers",
            name="Normal"
        )
    )


    fig.add_trace(
        go.Scatter(
            x=abnormal["year"],
            y=abnormal[
                "Total_Budget_Billions_USD"
            ],
            mode="markers",
            marker=dict(
                size=12
            ),
            name="Anomaly"
        )
    )


    fig.update_layout(
        template="plotly_dark",
        title="Budget Anomaly Timeline",
        xaxis_title="Year",
        yaxis_title="Budget (Billion USD)",
        height=450
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # -----------------------------------------
    # TABLE
    # -----------------------------------------

    if total_anomalies > 0:

        st.subheader("Detected Anomalies")

        anomaly_display = anomaly_df[
            anomaly_df["Anomaly"]
        ][
            [
                "year",
                "Total_Budget_Billions_USD",
                "z_score",
                "Z_Anomaly",
                "IQR_Anomaly"
            ]
        ]

        st.dataframe(
            anomaly_display.round(3),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No observations crossed the configured anomaly thresholds."
        )


# =========================================================
# TAB 4
# FORECASTING
# =========================================================

with tab4:

    st.markdown(
        '<div class="section-title">Budget Projection Lab</div>',
        unsafe_allow_html=True
    )


    degree = st.selectbox(
        "Polynomial Degree",
        [1, 2, 3],
        index=1
    )


    max_year = int(
        df_macro["year"].max()
    )


    min_forecast_year = max_year + 1


    future_year = st.slider(
        "Forecast Until",
        min_value=min_forecast_year,
        max_value=2050,
        value=min(
            max_year + 10,
            2050
        )
    )


    x = df_macro[
        "year"
    ].values.astype(float)


    y = df_macro[
        "Total_Budget_Billions_USD"
    ].values.astype(float)


    if len(x) > degree:

        # -------------------------------------
        # MODEL
        # -------------------------------------

        coefficients = np.polyfit(
            x,
            y,
            degree
        )

        model = np.poly1d(
            coefficients
        )


        future_years = np.arange(
            max_year + 1,
            future_year + 1
        )


        predictions = model(
            future_years
        )


        # -------------------------------------
        # CHART
        # -------------------------------------

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
                x=future_years,
                y=predictions,
                mode="lines+markers",
                line=dict(
                    dash="dash"
                ),
                name="Projection"
            )
        )


        fig.add_vline(
            x=max_year,
            line_dash="dot"
        )


        fig.update_layout(
            template="plotly_dark",
            title=(
                f"{selected_country} "
                f"Budget Projection"
            ),
            xaxis_title="Year",
            yaxis_title="Budget (Billion USD)",
            height=500
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


        # -------------------------------------
        # FORECAST TABLE
        # -------------------------------------

        forecast_df = pd.DataFrame(
            {
                "Year": future_years,
                "Projected_Budget_Billion_USD":
                    predictions
            }
        )


        forecast_df[
            "Projected_Budget_Billion_USD"
        ] = forecast_df[
            "Projected_Budget_Billion_USD"
        ].round(2)


        st.subheader("Projection Table")


        st.dataframe(
            forecast_df,
            use_container_width=True,
            hide_index=True
        )


        st.info(
            "Polynomial projections are statistical extrapolations "
            "based on historical observations. They should not be "
            "interpreted as official government forecasts."
        )


    else:

        st.warning(
            "Not enough observations for the selected polynomial degree."
        )


# =========================================================
# TAB 5
# RESEARCH LAB
# =========================================================

with tab5:

    st.markdown(
        '<div class="section-title">Research & Statistical Analysis</div>',
        unsafe_allow_html=True
    )


    # =====================================================
    # SECTOR CORRELATION
    # =====================================================

    st.subheader(
        "Sector Allocation Correlation"
    )


    corr_query = text("""
        SELECT
            b.year,
            sa.sector_name,
            sa.allocated_percentage

        FROM sector_allocations sa

        JOIN budgets b
            ON sa.budget_id = b.budget_id

        JOIN countries c
            ON b.country_id = c.country_id

        WHERE c.country_name = :country_name
    """)


    corr_df = pd.read_sql(
        corr_query,
        engine,
        params={
            "country_name": selected_country
        }
    )


    if not corr_df.empty:

        pivot = corr_df.pivot_table(
            index="year",
            columns="sector_name",
            values="allocated_percentage",
            aggfunc="mean"
        )


        correlation = pivot.corr()


        fig = px.imshow(
            correlation,
            text_auto=".2f",
            aspect="auto",
            template="plotly_dark",
            color_continuous_scale="RdBu_r"
        )


        fig.update_layout(
            title="Sector Allocation Correlation Matrix",
            height=600
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # =====================================================
    # VOLATILITY
    # =====================================================

    st.subheader(
        "Budget Volatility"
    )


    volatility = (
        df_macro[
            "Total_Budget_Billions_USD"
        ]
        .pct_change()
        .std()
        * 100
    )


    v1, v2 = st.columns(2)


    with v1:

        create_metric(
            "Budget Volatility",
            f"{volatility:.2f}%",
            "Std. dev. of annual growth"
        )


    with v2:

        budget_std = df_macro[
            "Total_Budget_Billions_USD"
        ].std()


        create_metric(
            "Budget Std. Deviation",
            format_budget(budget_std),
            "Historical variation"
        )


    # =====================================================
    # STATISTICS
    # =====================================================

    st.subheader(
        "Descriptive Statistics"
    )


    statistics = df_macro[
        "Total_Budget_Billions_USD"
    ].describe().to_frame(
        name="Budget (Billion USD)"
    )


    statistics = statistics.round(3)


    st.dataframe(
        statistics,
        use_container_width=True
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Global Government Budget Analytics • "
    "Built with Streamlit, SQLAlchemy, Pandas, NumPy & Plotly"
)
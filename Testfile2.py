from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.io as pio
import requests
import streamlit as st

st.set_page_config(
    page_title="US Manufacturing Energy Classification",
    layout="wide"
)

pio.templates.default = "plotly"

DATA_URL = "https://raw.githubusercontent.com/apatil210/LDRD2/main/Modified%20Data.xlsx"
SHEET_NAME = "Process-level data"

TEXT_COLOR = "#14212B"
PAPER_BG = "rgba(0,0,0,0)"
PLOT_BG = "rgba(0,0,0,0)"
BAR_COLOR = "#0B6E74"

SEC_COLOR_MAP = {
    "SEC Electricity": "#54A24B",
    "SEC Fuels": "#F58518",
    "SEC Steam": "#4C78A8",
}

COL_L2 = "Unit operation Level 2 classification"
COL_L3 = "Unit operation Level 3 classification with details"
COL_PERCENT_ENERGY = "Percent Annual energy demand in 2022"

COL_ANNUAL_PRODUCTION = "Annual production in 2022 based on FU"
COL_ANNUAL_ENERGY = "Annual energy demand in 2022"

COL_SEC_ELECTRICITY = "SEC electricity"
COL_SEC_FUELS = "SEC fuels"
COL_SEC_STEAM = "SEC fuels or electricity for steam or steam from CHP"

COL_EFFICIENCY = "Efficiency"
COL_PROCESS_TEMP = "Process temperature"
COL_INLET_TEMP = "Inlet temperature"
COL_OUTLET_TEMP = "Outlet temperature"
COL_PROCESS_PRESSURE = "Process pressure"
COL_INLET_PRESSURE = "Inlet pressure"
COL_OUTLET_PRESSURE = "Outlet pressure"
COL_RESIDENCE_TIME = "Residence time"


@st.cache_data(show_spinner=False)
def load_excel_data(url: str) -> pd.DataFrame:
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")
    if "text/html" in content_type.lower():
        raise ValueError("The URL returned HTML instead of an Excel file.")

    raw_df = pd.read_excel(
        BytesIO(response.content),
        sheet_name=SHEET_NAME,
        header=None,
        engine="openpyxl"
    )

    header_row_idx = 1
    data_start_row = header_row_idx + 2

    df = raw_df.iloc[data_start_row:].copy()
    df.columns = raw_df.iloc[header_row_idx].astype(str).str.strip()
    df = df.reset_index(drop=True)

    df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]
    return df


def clean_category(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .replace({
            "": "Unknown",
            "nan": "Unknown",
            "None": "Unknown"
        })
    )


def to_numeric_safe(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def prepare_bar_data(df: pd.DataFrame) -> pd.DataFrame:
    working_df = df[[COL_L2, COL_PERCENT_ENERGY]].copy()

    working_df[COL_L2] = clean_category(working_df[COL_L2])
    working_df[COL_PERCENT_ENERGY] = to_numeric_safe(working_df[COL_PERCENT_ENERGY]).fillna(0)

    grouped_df = (
        working_df.groupby(COL_L2, as_index=False)[COL_PERCENT_ENERGY]
        .sum()
        .sort_values(COL_PERCENT_ENERGY, ascending=False)
        .reset_index(drop=True)
    )

    grouped_df = grouped_df[grouped_df[COL_PERCENT_ENERGY] > 0].copy()
    grouped_df["Display Percent"] = grouped_df[COL_PERCENT_ENERGY] * 100
    grouped_df["Rank"] = range(1, len(grouped_df) + 1)

    return grouped_df


def build_fact_sheet(df: pd.DataFrame, selected_l2: str):
    fact_df = df.copy()

    fact_df[COL_L2] = clean_category(fact_df[COL_L2])
    fact_df[COL_L3] = clean_category(fact_df[COL_L3])

    selected_df = fact_df[fact_df[COL_L2] == selected_l2].copy()

    if selected_df.empty:
        return None

    numeric_cols = [
        COL_ANNUAL_PRODUCTION,
        COL_ANNUAL_ENERGY,
        COL_SEC_ELECTRICITY,
        COL_SEC_FUELS,
        COL_SEC_STEAM,
    ]

    for col in numeric_cols:
        selected_df[col] = to_numeric_safe(selected_df[col])

    production_values = (
        selected_df[COL_ANNUAL_PRODUCTION]
        .dropna()
        .loc[lambda s: s != 0]
        .unique()
    )

    annual_production = production_values[0] if len(production_values) > 0 else 0
    annual_energy = selected_df[COL_ANNUAL_ENERGY].fillna(0).sum()

    sec_electricity = selected_df[COL_SEC_ELECTRICITY].fillna(0).sum()
    sec_fuels = selected_df[COL_SEC_FUELS].fillna(0).sum()
    sec_steam = selected_df[COL_SEC_STEAM].fillna(0).sum()

    detail_columns = [
        COL_L3,
        COL_SEC_ELECTRICITY,
        COL_SEC_FUELS,
        COL_SEC_STEAM,
        COL_EFFICIENCY,
        COL_PROCESS_TEMP,
        COL_INLET_TEMP,
        COL_OUTLET_TEMP,
        COL_PROCESS_PRESSURE,
        COL_INLET_PRESSURE,
        COL_OUTLET_PRESSURE,
        COL_RESIDENCE_TIME,
    ]

    detail_df = selected_df[detail_columns].rename(columns={
        COL_L3: "Unit Operations",
        COL_SEC_ELECTRICITY: "SEC Electricity",
        COL_SEC_FUELS: "SEC Fuels",
        COL_SEC_STEAM: "SEC Steam",
        COL_EFFICIENCY: "Efficiency",
        COL_PROCESS_TEMP: "Process temperature",
        COL_INLET_TEMP: "Inlet temperature",
        COL_OUTLET_TEMP: "Outlet temperature",
        COL_PROCESS_PRESSURE: "Process pressure",
        COL_INLET_PRESSURE: "Inlet pressure",
        COL_OUTLET_PRESSURE: "Outlet pressure",
        COL_RESIDENCE_TIME: "Residence time",
    })

    return {
        "Annual Production": annual_production,
        "Annual Energy": annual_energy,
        "SEC Electricity": sec_electricity,
        "SEC Fuels": sec_fuels,
        "SEC Steam": sec_steam,
        "Rows": len(selected_df),
        "Details": detail_df,
    }


def build_bar_chart(df: pd.DataFrame):
    break_start = 8.0
    break_end = 21.0
    compressed_gap = 1.2

    def transform_value(x):
        if x <= break_start:
            return x
        return break_start + compressed_gap + (x - break_end)

    chart_df = df.copy()
    chart_df["Plot Value"] = chart_df["Display Percent"].apply(transform_value)

    fig = px.bar(
        chart_df,
        x="Plot Value",
        y=COL_L2,
        orientation="h",
        text="Display Percent",
        color_discrete_sequence=[BAR_COLOR]
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Percent annual energy: %{text:.2f}%<extra></extra>"
        ),
        marker=dict(line=dict(color="#FCFCFA", width=1.2))
    )

    max_display = chart_df["Display Percent"].max()
    max_plot = transform_value(max_display) + 0.8

    fig.update_layout(
        width=1500,
        height=max(700, 32 * len(chart_df)),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        margin=dict(t=60, l=280, r=120, b=20),
        xaxis_title="Percent Annual Energy Demand in 2022 (%)",
        yaxis_title="Unit Operation (Level 2 Classification)",
        font=dict(
            family="Arial, sans-serif",
            color=TEXT_COLOR,
            size=14
        ),
        shapes=[
            dict(
                type="line",
                x0=break_start + 0.35,
                x1=break_start + 0.55,
                y0=-0.5,
                y1=len(chart_df) - 0.5,
                xref="x",
                yref="y",
                line=dict(color="white", width=6)
            ),
            dict(
                type="line",
                x0=break_start + 0.65,
                x1=break_start + 0.85,
                y0=-0.5,
                y1=len(chart_df) - 0.5,
                xref="x",
                yref="y",
                line=dict(color="white", width=6)
            )
        ]
    )

    fig.update_xaxes(
        range=[0, max_plot + 0.8],
        tickmode="array",
        tickvals=[0, 1, 2, 3, 4, 5, 6, 7, break_start + compressed_gap],
        ticktext=["0%", "1%", "2%", "3%", "4%", "5%", "6%", "7%", "21%"],
        showgrid=True,
        automargin=True
    )

    fig.update_yaxes(
        categoryorder="total ascending",
        automargin=True
    )

    return fig


def build_sec_donut(fact_sheet: dict):
    donut_df = pd.DataFrame({
        "SEC Type": ["SEC Electricity", "SEC Fuels", "SEC Steam"],
        "Value": [
            fact_sheet["SEC Electricity"],
            fact_sheet["SEC Fuels"],
            fact_sheet["SEC Steam"]
        ]
    })

    donut_df = donut_df[donut_df["Value"] > 0].copy()

    if donut_df.empty:
        return None

    fig = px.pie(
        donut_df,
        names="SEC Type",
        values="Value",
        hole=0.62,
        color="SEC Type",
        color_discrete_map=SEC_COLOR_MAP
    )

    total_sec = donut_df["Value"].sum()

    fig.update_traces(
        textposition="outside",
        texttemplate="%{label}<br>%{percent}",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Value: %{value:.3f}<br>"
            "Share: %{percent}<extra></extra>"
        ),
        marker=dict(line=dict(color="#FFFFFF", width=2))
    )

    fig.update_layout(
        height=360,
        margin=dict(t=20, l=20, r=20, b=20),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        showlegend=False,
        font=dict(
            family="Arial, sans-serif",
            color=TEXT_COLOR,
            size=13
        ),
        annotations=[
            dict(
                text=f"<b>Total SEC (GJ/t)</b><br>{total_sec:.2f}",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color=TEXT_COLOR)
            )
        ]
    )

    return fig


st.title("US Manufacturing Energy Classification: Unit Operations")

try:
    df = load_excel_data(DATA_URL)
    bar_df = prepare_bar_data(df)

    left_col, right_col = st.columns([1.1, 1.6], gap="large")

    with left_col:
        selected_l2 = st.selectbox(
            "Select a unit operation (Level 2 classification) to generate a fact sheet",
            bar_df[COL_L2].tolist()
        )

        fact_sheet = build_fact_sheet(df, selected_l2)

        if fact_sheet is not None:
            metric_col1, metric_col2 = st.columns(2)

            metric_col1.metric(
                "Annual Production",
                f"{fact_sheet['Annual Production']:.2f}"
            )

            metric_col2.metric(
                "Annual Energy (PJ/yr)",
                f"{fact_sheet['Annual Energy']:.2f}"
            )

            st.subheader("Specific Energy Consumption (SEC)")
            sec_fig = build_sec_donut(fact_sheet)

            if sec_fig is not None:
                st.plotly_chart(
                    sec_fig,
                    use_container_width=True,
                    theme=None,
                    config={"displayModeBar": False}
                )
            else:
                st.info("No positive SEC values available for this category.")

            st.dataframe(
                fact_sheet["Details"],
                use_container_width=True,
                hide_index=True
            )

    with right_col:
        st.subheader("Percent Annual Energy by Unit Operation (Level 2)")

        with st.container(height=1000):
            st.plotly_chart(
                build_bar_chart(bar_df),
                use_container_width=False,
                theme=None,
                config={
                    "displayModeBar": False,
                    "scrollZoom": False
                }
            )

except Exception as e:
    st.error(f"App error: {e}")

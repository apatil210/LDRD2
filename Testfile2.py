from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import requests
import streamlit as st

# ----------------------------
# App configuration
# ----------------------------
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

# ----------------------------
# Canonical column names
# These match the attached workbook
# ----------------------------
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


# ----------------------------
# Utility functions
# ----------------------------
def normalize_text(value) -> str:
    if pd.isna(value):
        return ""
    return (
        str(value)
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )


def clean_category(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    return s.replace({
        "": "Unknown",
        "nan": "Unknown",
        "None": "Unknown"
    })


def to_numeric_safe(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def find_header_row(raw_df: pd.DataFrame, required_headers: list[str]) -> int:
    normalized_required = {normalize_text(x) for x in required_headers}

    for i in range(min(10, len(raw_df))):
        row_values = {normalize_text(v) for v in raw_df.iloc[i].tolist()}
        if normalized_required.issubset(row_values):
            return i

    raise ValueError(
        "Could not locate the header row containing the expected column names."
    )


def make_unique_columns(columns: list[str]) -> list[str]:
    seen = {}
    result = []

    for col in columns:
        base = normalize_text(col) or "Unnamed"
        if base not in seen:
            seen[base] = 0
            result.append(base)
        else:
            seen[base] += 1
            result.append(f"{base}_{seen[base]}")

    return result


# ----------------------------
# Data loading
# ----------------------------
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

    header_row_idx = find_header_row(
        raw_df,
        required_headers=[
            COL_L2,
            COL_L3,
            COL_PERCENT_ENERGY,
            COL_ANNUAL_PRODUCTION,
            COL_ANNUAL_ENERGY,
            COL_SEC_ELECTRICITY,
            COL_SEC_FUELS,
            COL_SEC_STEAM,
        ]
    )

    df = raw_df.iloc[header_row_idx + 2:].copy()
    df.columns = make_unique_columns(raw_df.iloc[header_row_idx].tolist())
    df = df.reset_index(drop=True)

    df = df.dropna(how="all")
    df.columns = [normalize_text(c) for c in df.columns]

    required_cols = [
        COL_L2,
        COL_L3,
        COL_PERCENT_ENERGY,
        COL_ANNUAL_PRODUCTION,
        COL_ANNUAL_ENERGY,
        COL_SEC_ELECTRICITY,
        COL_SEC_FUELS,
        COL_SEC_STEAM,
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    return df


# ----------------------------
# Data preparation
# ----------------------------
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

    grouped_df["Display Percent"] = grouped_df[COL_PERCENT_ENERGY] * 100
    grouped_df["Abs Display Percent"] = grouped_df["Display Percent"].abs()
    grouped_df["Sign"] = grouped_df["Display Percent"].apply(
        lambda x: "Positive" if x >= 0 else "Negative"
    )
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

    detail_cols = [
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
    detail_cols = [c for c in detail_cols if c in selected_df.columns]

    detail_df = selected_df[detail_cols].rename(columns={
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


# ----------------------------
# Chart builders
# ----------------------------
def build_bar_chart(df: pd.DataFrame):
    chart_df = df.copy()
    chart_df = chart_df.sort_values("Display Percent", ascending=True)

    max_abs = max(chart_df["Display Percent"].abs().max(), 1)

    fig = px.bar(
        chart_df,
        x="Display Percent",
        y=COL_L2,
        orientation="h",
        color="Sign",
        color_discrete_map={
            "Positive": BAR_COLOR,
            "Negative": "#B22222"
        },
        text="Display Percent"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Percent annual energy: %{x:.4f}%<extra></extra>"
        ),
        marker=dict(line=dict(color="#FCFCFA", width=1.0))
    )

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
        legend_title_text="Contribution",
    )

    fig.update_xaxes(
        range=[-max_abs * 1.15, max_abs * 1.15],
        ticksuffix="%",
        zeroline=True,
        zerolinewidth=1.2,
        zerolinecolor="#666",
        showgrid=True,
        automargin=True
    )

    fig.update_yaxes(
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

    donut_df["Abs Value"] = donut_df["Value"].abs()
    donut_df = donut_df[donut_df["Abs Value"] > 0].copy()

    if donut_df.empty:
        fig = go.Figure()
        fig.update_layout(
            height=360,
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            annotations=[dict(
                text="No SEC values available",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color=TEXT_COLOR)
            )]
        )
        return fig

    fig = px.pie(
        donut_df,
        names="SEC Type",
        values="Abs Value",
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
            "Absolute value: %{value:.3f}<extra></extra>"
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
                text=f"<b>Total SEC</b><br>{total_sec:.2f}",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color=TEXT_COLOR)
            )
        ]
    )

    return fig


# ----------------------------
# App UI
# ----------------------------
st.title("US Manufacturing Energy Classification: Unit Operations")

try:
    df = load_excel_data(DATA_URL)
    bar_df = prepare_bar_data(df)

    left_col, right_col = st.columns([1.1, 1.6], gap="large")

    with left_col:
        selected_l2 = st.selectbox(
            "Select a unit operation (Level 2 classification) to generate a fact sheet",
            sorted(bar_df[COL_L2].dropna().unique().tolist())
        )

        fact_sheet = build_fact_sheet(df, selected_l2)

        if fact_sheet is not None:
            metric_col1, metric_col2 = st.columns(2)
            metric_col1.metric(
                "Annual Production (based on FU)",
                f"{fact_sheet['Annual Production']:,.2f}"
            )
            metric_col2.metric(
                "Annual Energy (PJ/yr)",
                f"{fact_sheet['Annual Energy']:,.2f}"
            )

            st.subheader("Specific Energy Consumption (SEC)")
            st.plotly_chart(
                build_sec_donut(fact_sheet),
                use_container_width=True,
                theme=None,
                config={"displayModeBar": False}
            )

            st.dataframe(
                fact_sheet["Details"],
                use_container_width=True,
                hide_index=True
            )

    with right_col:
        st.subheader("Percent Annual Energy by Unit Operation (Level 2)")
        st.caption("Negative values indicate net recovery/export effects in some categories.")

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

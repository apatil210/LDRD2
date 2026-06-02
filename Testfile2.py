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

pio.templates.default = "plotly_white"

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
# Header normalization
# ----------------------------
def normalize_header(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split())
    return text.strip()

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

def find_best_column(columns, candidates, required=True):
    normalized_map = {normalize_header(c).lower(): c for c in columns}

    for candidate in candidates:
        key = normalize_header(candidate).lower()
        if key in normalized_map:
            return normalized_map[key]

    for candidate in candidates:
        candidate_key = normalize_header(candidate).lower()
        for norm_col, original_col in normalized_map.items():
            if candidate_key in norm_col or norm_col in candidate_key:
                return original_col

    if required:
        raise KeyError(
            f"Could not find a matching column for any of: {candidates}"
        )
    return None

# ----------------------------
# Data loading
# ----------------------------
@st.cache_data(show_spinner=False)
def load_excel_data(url: str):
    response = requests.get(url, timeout=60)
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

    # In this workbook, row 0 contains grouped section labels,
    # row 1 contains the real field names, and row 2 contains units.
    header_row_idx = 1
    data_start_idx = 3

    header_values = raw_df.iloc[header_row_idx].tolist()
    columns = [normalize_header(v) for v in header_values]

    df = raw_df.iloc[data_start_idx:].copy()
    df.columns = columns
    df = df.reset_index(drop=True)

    # Drop rows that are fully empty
    df = df.dropna(how="all").reset_index(drop=True)

    return df

# ----------------------------
# Column resolver
# ----------------------------
def resolve_columns(df: pd.DataFrame):
    cols = df.columns.tolist()

    resolved = {
        "L2": find_best_column(cols, [
            "Unit operation Level 2 classification",
            "Unit operation (Level 2 classification)"
        ]),
        "L3": find_best_column(cols, [
            "Unit operation Level 3 classification with details",
            "Unit operation (Level 3 classification; with details)"
        ]),
        "PERCENT_ENERGY": find_best_column(cols, [
            "Percent Annual energy demand in 2022"
        ]),
        "ANNUAL_PRODUCTION": find_best_column(cols, [
            "Annual production in 2022 based on FU",
            "Annual production in 2022"
        ]),
        "ANNUAL_ENERGY": find_best_column(cols, [
            "Annual energy demand in 2022"
        ]),
        "SEC_ELECTRICITY": find_best_column(cols, [
            "SEC electricity",
            "SEC electricty"
        ]),
        "SEC_FUELS": find_best_column(cols, [
            "SEC fuels"
        ]),
        "SEC_STEAM": find_best_column(cols, [
            "SEC fuels or electricity for steam or steam from CHP"
        ]),
        "EFFICIENCY": find_best_column(cols, [
            "Efficiency"
        ], required=False),
        "PROCESS_TEMP": find_best_column(cols, [
            "Process temperature"
        ], required=False),
        "INLET_TEMP": find_best_column(cols, [
            "Inlet temperature"
        ], required=False),
        "OUTLET_TEMP": find_best_column(cols, [
            "Outlet temperature"
        ], required=False),
        "PROCESS_PRESSURE": find_best_column(cols, [
            "Process pressure"
        ], required=False),
        "INLET_PRESSURE": find_best_column(cols, [
            "Inlet pressure"
        ], required=False),
        "OUTLET_PRESSURE": find_best_column(cols, [
            "Outlet pressure"
        ], required=False),
        "RESIDENCE_TIME": find_best_column(cols, [
            "Residence time"
        ], required=False),
    }

    return resolved

# ----------------------------
# Data preparation
# ----------------------------
def prepare_bar_data(df: pd.DataFrame, c: dict) -> pd.DataFrame:
    working_df = df[[c["L2"], c["PERCENT_ENERGY"]]].copy()

    working_df[c["L2"]] = clean_category(working_df[c["L2"]])
    working_df[c["PERCENT_ENERGY"]] = to_numeric_safe(working_df[c["PERCENT_ENERGY"]]).fillna(0)

    grouped_df = (
        working_df.groupby(c["L2"], as_index=False)[c["PERCENT_ENERGY"]]
        .sum()
        .sort_values(c["PERCENT_ENERGY"], ascending=False)
        .reset_index(drop=True)
    )

    grouped_df = grouped_df[grouped_df[c["PERCENT_ENERGY"]] > 0].copy()
    grouped_df["Display Percent"] = grouped_df[c["PERCENT_ENERGY"]] * 100
    grouped_df["Rank"] = range(1, len(grouped_df) + 1)

    return grouped_df

def build_fact_sheet(df: pd.DataFrame, c: dict, selected_l2: str):
    fact_df = df.copy()

    fact_df[c["L2"]] = clean_category(fact_df[c["L2"]])
    fact_df[c["L3"]] = clean_category(fact_df[c["L3"]])

    selected_df = fact_df[fact_df[c["L2"]] == selected_l2].copy()
    if selected_df.empty:
        return None

    numeric_cols = [
        c["ANNUAL_PRODUCTION"],
        c["ANNUAL_ENERGY"],
        c["SEC_ELECTRICITY"],
        c["SEC_FUELS"],
        c["SEC_STEAM"],
    ]

    for col in numeric_cols:
        selected_df[col] = to_numeric_safe(selected_df[col])

    production_values = (
        selected_df[c["ANNUAL_PRODUCTION"]]
        .dropna()
        .loc[lambda s: s != 0]
        .unique()
    )
    annual_production = production_values[0] if len(production_values) > 0 else 0
    annual_energy = selected_df[c["ANNUAL_ENERGY"]].fillna(0).sum()
    sec_electricity = selected_df[c["SEC_ELECTRICITY"]].fillna(0).sum()
    sec_fuels = selected_df[c["SEC_FUELS"]].fillna(0).sum()
    sec_steam = selected_df[c["SEC_STEAM"]].fillna(0).sum()

    detail_cols = [
        c["L3"],
        c["SEC_ELECTRICITY"],
        c["SEC_FUELS"],
        c["SEC_STEAM"],
        c["EFFICIENCY"],
        c["PROCESS_TEMP"],
        c["INLET_TEMP"],
        c["OUTLET_TEMP"],
        c["PROCESS_PRESSURE"],
        c["INLET_PRESSURE"],
        c["OUTLET_PRESSURE"],
        c["RESIDENCE_TIME"],
    ]
    detail_cols = [col for col in detail_cols if col is not None]

    detail_df = selected_df[detail_cols].copy()

    rename_map = {
        c["L3"]: "Unit Operations",
        c["SEC_ELECTRICITY"]: "SEC Electricity",
        c["SEC_FUELS"]: "SEC Fuels",
        c["SEC_STEAM"]: "SEC Steam",
    }

    optional_renames = {
        c["EFFICIENCY"]: "Efficiency",
        c["PROCESS_TEMP"]: "Process temperature",
        c["INLET_TEMP"]: "Inlet temperature",
        c["OUTLET_TEMP"]: "Outlet temperature",
        c["PROCESS_PRESSURE"]: "Process pressure",
        c["INLET_PRESSURE"]: "Inlet pressure",
        c["OUTLET_PRESSURE"]: "Outlet pressure",
        c["RESIDENCE_TIME"]: "Residence time",
    }

    for old, new in optional_renames.items():
        if old is not None:
            rename_map[old] = new

    detail_df = detail_df.rename(columns=rename_map)

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
def build_bar_chart(df: pd.DataFrame, level2_col: str):
    break_start = 8.0
    break_end = 21.0
    compressed_gap = 1.2

    def transform_value(x):
        if x <= break_start:
            return x
        if x <= break_end:
            return break_start + compressed_gap
        return break_start + compressed_gap + (x - break_end)

    chart_df = df.copy()
    chart_df["Plot Value"] = chart_df["Display Percent"].apply(transform_value)

    fig = px.bar(
        chart_df,
        x="Plot Value",
        y=level2_col,
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
    max_plot = transform_value(max_display) + 1.0

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

    tickvals = [0, 1, 2, 3, 4, 5, 6, 7, break_start + compressed_gap]
    ticktext = ["0%", "1%", "2%", "3%", "4%", "5%", "6%", "7%", "21%"]

    if max_display > break_end:
        upper_ticks = list(range(25, int(max_display) + 1, 5))
        for t in upper_ticks:
            tickvals.append(transform_value(t))
            ticktext.append(f"{t}%")

    fig.update_xaxes(
        range=[0, max_plot + 0.8],
        tickmode="array",
        tickvals=tickvals,
        ticktext=ticktext,
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
        fig = go.Figure()
        fig.add_annotation(
            text="No positive SEC values available",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color=TEXT_COLOR)
        )
        fig.update_layout(
            height=360,
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            margin=dict(t=20, l=20, r=20, b=20)
        )
        return fig

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
    c = resolve_columns(df)
    bar_df = prepare_bar_data(df, c)

    left_col, right_col = st.columns([1.1, 1.6], gap="large")

    with left_col:
        selected_l2 = st.selectbox(
            "Select a unit operation (Level 2 classification) to generate a fact sheet",
            bar_df[c["L2"]].tolist()
        )

        fact_sheet = build_fact_sheet(df, c, selected_l2)

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
            st.plotly_chart(
                build_sec_donut(fact_sheet),
                use_container_width=True,
                theme=None,
                config={"displayModeBar": False}
            )

            st.subheader("Unit-operation details")
            st.dataframe(
                fact_sheet["Details"],
                use_container_width=True,
                hide_index=True
            )

    with right_col:
        st.subheader("Percent Annual Energy by Unit Operation (Level 2)")

        with st.container(height=1000):
            st.plotly_chart(
                build_bar_chart(bar_df, c["L2"]),
                use_container_width=False,
                theme=None,
                config={
                    "displayModeBar": False,
                    "scrollZoom": False
                }
            )

except Exception as e:
    st.error(f"App error: {e}")

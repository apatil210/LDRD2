from io import BytesIO
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import requests
import streamlit as st

st.set_page_config(page_title="US Manufacturing Energy Classification", layout="wide")
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


def normalize_label(value: str) -> str:
    if value is None:
        return ""
    value = str(value).strip().lower().replace("\n", " ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def clean_category(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    return s.replace({"": "Unknown", "nan": "Unknown", "None": "Unknown", "none": "Unknown"})


def to_numeric_safe(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


@st.cache_data(show_spinner=False)
def load_excel_data(url: str):
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "")
    if "text/html" in content_type.lower():
        raise ValueError("The URL returned HTML instead of an Excel file.")

    raw_df = pd.read_excel(BytesIO(response.content), sheet_name=SHEET_NAME, header=None, engine="openpyxl")

    normalized_rows = raw_df.fillna("").astype(str).applymap(normalize_label)
    target_header = {
        "unit operation level 2 classification",
        "unit operation level 3 classification with details",
        "annual energy demand in 2022",
        "percent annual energy demand in 2022",
    }

    header_row_idx = None
    for idx in range(len(normalized_rows)):
        row_vals = set(v for v in normalized_rows.iloc[idx].tolist() if v)
        if target_header.issubset(row_vals):
            header_row_idx = idx
            break
    if header_row_idx is None:
        raise ValueError("Could not locate the actual header row in the workbook.")

    columns = raw_df.iloc[header_row_idx].fillna("").astype(str).str.replace("\n", " ", regex=False).str.strip()
    df = raw_df.iloc[header_row_idx + 2 :].copy().reset_index(drop=True)
    df.columns = columns

    df = df.dropna(how="all")
    df = df.loc[:, [str(c).strip() != "" for c in df.columns]]

    normalized_map = {normalize_label(col): col for col in df.columns}

    aliases = {
        "l2": ["unit operation level 2 classification"],
        "l3": ["unit operation level 3 classification with details"],
        "pct_energy": ["percent annual energy demand in 2022"],
        "annual_production": ["annual production in 2022 based on fu"],
        "annual_energy": ["annual energy demand in 2022"],
        "sec_electricity": ["sec electricity"],
        "sec_fuels": ["sec fuels"],
        "sec_steam": ["sec fuels or electricity for steam or steam from chp"],
        "efficiency": ["efficiency"],
        "process_temp": ["process temperature"],
        "inlet_temp": ["inlet temperature"],
        "outlet_temp": ["outlet temperature"],
        "process_pressure": ["process pressure"],
        "inlet_pressure": ["inlet pressure"],
        "outlet_pressure": ["outlet pressure"],
        "residence_time": ["residence time"],
        "industrial_process": ["industrial process"],
        "level1": ["unit operation level 1 classification"],
        "functional_unit": ["functional unit fu"],
        "feedstock": ["feedstock"],
    }

    resolved = {}
    missing = []
    for key, opts in aliases.items():
        match = next((normalized_map[o] for o in opts if o in normalized_map), None)
        resolved[key] = match
        if key in {"l2", "l3", "pct_energy", "annual_production", "annual_energy", "sec_electricity", "sec_fuels", "sec_steam"} and match is None:
            missing.append(key)

    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    return df, resolved


def prepare_bar_data(df: pd.DataFrame, cols: dict) -> pd.DataFrame:
    working_df = df[[cols["l2"], cols["pct_energy"]]].copy()
    working_df[cols["l2"]] = clean_category(working_df[cols["l2"]])
    working_df[cols["pct_energy"]] = to_numeric_safe(working_df[cols["pct_energy"]]).fillna(0)

    grouped_df = (
        working_df.groupby(cols["l2"], as_index=False)[cols["pct_energy"]]
        .sum()
        .sort_values(cols["pct_energy"], ascending=False)
        .reset_index(drop=True)
    )
    grouped_df = grouped_df[grouped_df[cols["pct_energy"]] > 0].copy()
    grouped_df["Display Percent"] = grouped_df[cols["pct_energy"]] * 100
    grouped_df["Rank"] = range(1, len(grouped_df) + 1)
    return grouped_df


def build_fact_sheet(df: pd.DataFrame, cols: dict, selected_l2: str):
    fact_df = df.copy()
    fact_df[cols["l2"]] = clean_category(fact_df[cols["l2"]])
    fact_df[cols["l3"]] = clean_category(fact_df[cols["l3"]])

    selected_df = fact_df[fact_df[cols["l2"]] == selected_l2].copy()
    if selected_df.empty:
        return None

    for key in ["annual_production", "annual_energy", "sec_electricity", "sec_fuels", "sec_steam"]:
        selected_df[cols[key]] = to_numeric_safe(selected_df[cols[key]])

    production_values = selected_df[cols["annual_production"]].dropna().loc[lambda s: s != 0].unique()
    annual_production = production_values[0] if len(production_values) > 0 else None

    detail_candidates = [
        ("Unit Operations", "l3"),
        ("SEC Electricity", "sec_electricity"),
        ("SEC Fuels", "sec_fuels"),
        ("SEC Steam", "sec_steam"),
        ("Efficiency", "efficiency"),
        ("Process temperature", "process_temp"),
        ("Inlet temperature", "inlet_temp"),
        ("Outlet temperature", "outlet_temp"),
        ("Process pressure", "process_pressure"),
        ("Inlet pressure", "inlet_pressure"),
        ("Outlet pressure", "outlet_pressure"),
        ("Residence time", "residence_time"),
        ("Industrial process", "industrial_process"),
        ("Level 1 classification", "level1"),
        ("Functional unit", "functional_unit"),
        ("Feedstock", "feedstock"),
    ]

    detail_cols = [cols[k] for _, k in detail_candidates if cols.get(k)]
    rename_map = {cols[k]: label for label, k in detail_candidates if cols.get(k)}
    detail_df = selected_df[detail_cols].rename(columns=rename_map)

    sec_e = selected_df[cols["sec_electricity"]].fillna(0).sum()
    sec_f = selected_df[cols["sec_fuels"]].fillna(0).sum()
    sec_s = selected_df[cols["sec_steam"]].fillna(0).sum()

    return {
        "Annual Production": annual_production,
        "Annual Energy": selected_df[cols["annual_energy"]].fillna(0).sum(),
        "SEC Electricity": sec_e,
        "SEC Fuels": sec_f,
        "SEC Steam": sec_s,
        "Rows": len(selected_df),
        "Details": detail_df,
    }


def build_bar_chart(df: pd.DataFrame, cols: dict):
    break_start = 8.0
    break_end = 21.0
    compressed_gap = 1.2

    def transform_value(x):
        return x if x <= break_start else break_start + compressed_gap + (x - break_end)

    chart_df = df.copy()
    chart_df["Plot Value"] = chart_df["Display Percent"].apply(transform_value)

    fig = px.bar(
        chart_df,
        x="Plot Value",
        y=cols["l2"],
        orientation="h",
        text="Display Percent",
        color_discrete_sequence=[BAR_COLOR],
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Percent annual energy: %{text:.4f}%<extra></extra>",
        marker=dict(line=dict(color="#FCFCFA", width=1.2)),
    )

    max_display = chart_df["Display Percent"].max() if not chart_df.empty else 0
    max_plot = transform_value(max_display) + 0.8

    fig.update_layout(
        width=1500,
        height=max(700, 32 * len(chart_df)),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        margin=dict(t=60, l=280, r=120, b=20),
        xaxis_title="Percent Annual Energy Demand in 2022 (%)",
        yaxis_title="Unit Operation (Level 2 Classification)",
        font=dict(family="Arial, sans-serif", color=TEXT_COLOR, size=14),
        shapes=[
            dict(type="line", x0=break_start + 0.35, x1=break_start + 0.55, y0=-0.5, y1=len(chart_df) - 0.5, xref="x", yref="y", line=dict(color="white", width=6)),
            dict(type="line", x0=break_start + 0.65, x1=break_start + 0.85, y0=-0.5, y1=len(chart_df) - 0.5, xref="x", yref="y", line=dict(color="white", width=6)),
        ],
    )

    fig.update_xaxes(
        range=[0, max_plot + 0.8],
        tickmode="array",
        tickvals=[0, 1, 2, 3, 4, 5, 6, 7, break_start + compressed_gap],
        ticktext=["0%", "1%", "2%", "3%", "4%", "5%", "6%", "7%", "21%"],
        showgrid=True,
        automargin=True,
    )
    fig.update_yaxes(categoryorder="total ascending", automargin=True)
    return fig


def build_sec_donut(fact_sheet: dict):
    donut_df = pd.DataFrame(
        {
            "SEC Type": ["SEC Electricity", "SEC Fuels", "SEC Steam"],
            "Value": [fact_sheet["SEC Electricity"], fact_sheet["SEC Fuels"], fact_sheet["SEC Steam"]],
        }
    )
    donut_df = donut_df[donut_df["Value"] > 0].copy()

    if 

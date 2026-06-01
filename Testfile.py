from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.io as pio
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Energy Classification: Industrial Process",
    layout="wide"
)

pio.templates.default = "plotly"

DATA_URL = "https://raw.githubusercontent.com/apatil210/LDRD2/main/Modified%20Data.xlsx"

TEXT_COLOR = "#14212B"
PAPER_BG = "rgba(0,0,0,0)"
PLOT_BG = "rgba(0,0,0,0)"
BAR_COLOR = "#0B6E74"


@st.cache_data(show_spinner=False)
def load_excel(url: str) -> pd.DataFrame:
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")
    if "text/html" in content_type.lower():
        raise ValueError("URL returned an HTML page instead of an Excel file.")

    raw_df = pd.read_excel(
        BytesIO(response.content),
        sheet_name="Process-level data",
        header=None,
        engine="openpyxl"
    )

    header_row_idx = 1
    df = raw_df.iloc[header_row_idx + 2:].copy()
    df.columns = raw_df.iloc[header_row_idx].astype(str).str.strip()
    df = df.reset_index(drop=True)

    return df


def clean_category(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
    )


def prepare_bar_data(df: pd.DataFrame) -> pd.DataFrame:
    category_col = "Industrial process"
    value_col = "Percent Annual energy demand in 2022"

    df_work = df[[category_col, value_col]].copy()
    df_work[category_col] = clean_category(df_work[category_col])
    df_work[value_col] = pd.to_numeric(df_work[value_col], errors="coerce").fillna(0)

    df_agg = (
        df_work.groupby(category_col, as_index=False)[value_col]
        .sum()
        .sort_values(value_col, ascending=False)
        .reset_index(drop=True)
    )

    df_agg = df_agg[df_agg[value_col] > 0].copy()
    df_agg["Display Percent"] = df_agg[value_col] * 100
    df_agg["Rank"] = range(1, len(df_agg) + 1)

    return df_agg


def build_bar_chart(df: pd.DataFrame):
    break_start = 7.0
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
        y="Industrial process",
        orientation="h",
        text="Display Percent",
        color_discrete_sequence=[BAR_COLOR]
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Percent annual energy: %{text:.2f}%<extra></extra>"
        ),
        marker=dict(line=dict(color="#FCFCFA", width=1.2))
    )

    max_display = chart_df["Display Percent"].max()
    max_plot = transform_value(max_display) + 1.5

    fig.update_layout(
        title="Percent Annual Energy by Industrial Process",
        width=1400,
        height=max(900, 35 * len(chart_df)),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        margin=dict(t=60, l=10, r=120, b=40),
        xaxis_title="Percent Annual Energy Demand in 2022 (%)",
        yaxis_title="Industrial Process",
        dragmode="pan",
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
        range=[0, max_plot],
        tickmode="array",
        tickvals=[0, 1, 2, 3, 4, 5, 6, 7, break_start + compressed_gap],
        ticktext=["0%", "1%", "2%", "3%", "4%", "5%", "6%", "7%", "21%"],
        showgrid=True,
        fixedrange=False
    )

    fig.update_yaxes(
        categoryorder="total ascending",
        automargin=True,
        fixedrange=False
    )

    return fig


def render_scrollable_chart(fig):
    chart_html = pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs="cdn",
        config={
            "displayModeBar": True,
            "scrollZoom": True,
            "responsive": False
        }
    )

    scrollable_html = f"""
    <div style="
        width: 100%;
        height: 900px;
        overflow: auto;
        border: 1px solid #D9D9D9;
        border-radius: 8px;
        background: white;
        padding: 8px;
    ">
        <div style="width: 1400px; height: {fig.layout.height}px;">
            {chart_html}
        </div>
    </div>
    """

    components.html(scrollable_html, height=920, scrolling=False)


def build_fact_sheet(df: pd.DataFrame, selected_process: str):
    process_col = "Industrial process"
    unit_ops_col = "Unit operation (Level 3 classification; with details)"
    production_col = "Annual production in 2022\n(based on FU)"
    elec_col = "SEC \nelectricity"
    fuel_col = "SEC \nfuels"
    steam_col = "SEC \nfuels or electricity for steam or steam from CHP"

    fact_df = df.copy()
    fact_df[process_col] = clean_category(fact_df[process_col])
    fact_df[unit_ops_col] = clean_category(fact_df[unit_ops_col])

    for col in [production_col, elec_col, fuel_col, steam_col]:
        fact_df[col] = pd.to_numeric(fact_df[col], errors="coerce")

    selected_df = fact_df[fact_df[process_col] == selected_process].copy()

    if selected_df.empty:
        return None

    production_values = (
        selected_df[production_col]
        .dropna()
        .loc[lambda s: s != 0]
        .unique()
    )
    annual_production = production_values[0] if len(production_values) > 0 else 0

    sec_electricity = selected_df[elec_col].fillna(0).sum()
    sec_fuels = selected_df

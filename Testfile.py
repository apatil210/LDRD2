from io import BytesIO
import re

import pandas as pd
import plotly.express as px
import plotly.io as pio
import requests
import streamlit as st

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


def normalize_col_name(col) -> str:
    col = str(col)
    col = col.replace("\n", " ")
    col = re.sub(r"\s+", " ", col).strip().lower()
    return col


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
    df.columns = raw_df.iloc[header_row_idx]
    df = df.reset_index(drop=True)

    df.columns = [normalize_col_name(c) for c in df.columns]

    rename_map = {
        "industrial process": "industrial_process",
        "unit operation (level 1 classification)": "unit_operation_l1",
        "unit operation (level 2 classification)": "unit_operation_l2",
        "unit operation (level 3 classification; with details)": "unit_operation_l3",
        "annual production in 2022 based on fu": "annual_production_2022",
        "sec electricity": "sec_electricity",
        "sec fuels": "sec_fuels",
        "sec fuels or electricity for steam or steam from chp": "sec_steam",
        "percent annual energy demand in 2022": "pct_annual_energy_2022",
    }

    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})

    required = [
        "industrial_process",
        "unit_operation_l3",
        "annual_production_2022",
        "sec_electricity",
        "sec_fuels",
        "sec_steam",
        "pct_annual_energy_2022",
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing expected columns: {missing}. Available columns include: {list(df.columns)}"
        )

    return df


def clean_category(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
    )


def choose_unit_operation(df: pd.DataFrame) -> pd.Series:
    l3 = clean_category(df["unit_operation_l3"])
    l2 = clean_category(df["unit_operation_l2"])
    l1 = clean_category(df["unit_operation_l1"])

    return l3.where(~l3.isin(["Unknown"]), l2).where(~l2.isin(["Unknown"]), l1)


def prepare_bar_data(df: pd.DataFrame) -> pd.DataFrame:
    df_work = df[["industrial_process", "pct_annual_energy_2022"]].copy()
    df_work["industrial_process"] = clean_category(df_work["industrial_process"])
    df_work["pct_annual_energy_2022"] = pd.to_numeric(
        df_work["pct_annual_energy_2022"], errors="coerce"
    ).fillna(0)

    df_agg = (
        df_work.groupby("industrial_process", as_index=False)["pct_annual_energy_2022"]
        .sum()
        .sort_values("pct_annual_energy_2022", ascending=False)
        .reset_index(drop=True)
    )

    df_agg = df_agg[df_agg["pct_annual_energy_2022"] > 0].copy()
    df_agg["display_percent"] = df_agg["pct_annual_energy_2022"] * 100
    df_agg["rank"] = range(1, len(df_agg) + 1)

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
    chart_df["plot_value"] = chart_df["display_percent"].apply(transform_value)

    fig = px.bar(
        chart_df,
        x="plot_value",
        y="industrial_process",
        orientation="h",
        text="display_percent",
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

    max_display = chart_df["display_percent"].max()
    max_plot = transform_value(max_display) + 0.8

    dynamic_height = max(700, len(chart_df) * 38)

    fig.update_layout(
        title="Percent Annual Energy by Industrial Process",
        height=dynamic_height,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        margin=dict(t=60, l=10, r=40, b=20),
        xaxis_title="Percent Annual Energy Demand in 2022 (%)",
        yaxis_title="Industrial Process",
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
        showgrid=True
    )

    fig.update_yaxes(categoryorder="total ascending")

    return fig


def build_fact_sheet(df: pd.DataFrame, selected_process: str):
    fact_df = df.copy()
    fact_df["industrial_process"] = clean_category(fact_df["industrial_process"])
    fact_df["unit_operation_display"] = choose_unit_operation(fact_df)

    for col in [
        "annual_production_2022",
        "sec_electricity",
        "sec_fuels",
        "sec_steam",
    ]:
        fact_df[col] = pd.to_numeric(fact_df[col], errors="coerce")

    selected_df = fact_df[fact_df["industrial_process"] == selected_process].copy()

    if selected_df.empty:
        return None

    production_values = (
        selected_df["annual_production_2022"]
        .dropna()
        .loc[lambda s: s != 0]
        .unique()
    )
    annual_production = production_values[0] if len(production_values) > 0 else 0

    sec_electricity = selected_df["sec_electricity"].fillna(0).sum()
    sec_fuels = selected_df["sec_fuels"].fillna(0).sum()
    sec_steam = selected_df["sec_steam"].fillna(0).sum()

    detail_df = selected_df[
        ["unit_operation_display", "sec_electricity", "sec_fuels", "sec_steam"]
    ].rename(columns={
        "unit_operation_display": "Unit Operations",
        "sec_electricity": "SEC Electricity",
        "sec_fuels": "SEC Fuels",
        "sec_steam": "SEC Steam"
    })

    return {
        "Annual Production": annual_production,
        "SEC Electricity": sec_electricity,
        "SEC Fuels": sec_fuels,
        "SEC Steam": sec_steam,
        "Rows": selected_df.shape[0],
        "Details": detail_df
    }


st.title("Energy Classification: Industrial Process")

try:
    df = load_excel(DATA_URL)
    bar_df = prepare_bar_data(df)

    left_col, right_col = st.columns([1.1, 1.4], gap="large")

    with left_col:
        selected_process = st.selectbox(
            "Select an industrial process to generate a fact sheet",
            bar_df["industrial_process"].tolist()
        )

        fact_sheet = build_fact_sheet(df, selected_process)

        if fact_sheet:
            st.subheader(f"Fact Sheet: {selected_process}")

            c1, c2 = st.columns(2)
            c3, c4 = st.columns(2)

            c1.metric("Annual Production", f"{fact_sheet['Annual Production']:.2f}")
            c2.metric("SEC Electricity", f"{fact_sheet['SEC Electricity']:.2f}")
            c3.metric("SEC Fuels", f"{fact_sheet['SEC Fuels']:.2f}")
            c4.metric("SEC Steam", f"{fact_sheet['SEC Steam']:.2f}")

            st.caption(f"Underlying rows used: {fact_sheet['Rows']}")

            st.dataframe(
                fact_sheet["Details"],
                use_container_width=True,
                hide_index=True
            )

    with right_col:
        st.subheader("Percent Annual Energy by Industrial Process")

        chart_container = st.container(height=700)
        with chart_container:
            st.plotly_chart(
                build_bar_chart(bar_df),
                use_container_width=True,
                theme=None,
                config={
                    "displayModeBar": False,
                    "scrollZoom": False
                }
            )

except Exception as e:
    st.error(f"App error: {e}")

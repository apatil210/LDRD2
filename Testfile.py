from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.io as pio
import requests
import streamlit as st

st.set_page_config(
    page_title="Energy Classification: Unit Operations",
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

    header_row_idx = None
    for i in range(min(len(raw_df), 20)):
        row_values = raw_df.iloc[i].astype(str).str.strip().tolist()
        if "Unit operation Level 2 classification" in row_values:
            header_row_idx = i
            break

    if header_row_idx is None:
        raise ValueError("Could not locate the header row in the Excel sheet.")

    df = raw_df.iloc[header_row_idx + 1:].copy()
    df.columns = raw_df.iloc[header_row_idx].astype(str).str.strip()
    df = df.reset_index(drop=True)

    return df


def clean_category(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
    )


def prepare_bar_data(
    df: pd.DataFrame,
    category_col: str,
    value_col: str
) -> pd.DataFrame:
    required_columns = {category_col, value_col}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

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
    df_agg["Rank"] = range(1, len(df_agg) + 1)

    return df_agg


def build_bar_chart(
    df: pd.DataFrame,
    category_col: str,
    value_col: str,
    title: str
):
    fig = px.bar(
        df,
        x=value_col,
        y=category_col,
        orientation="h",
        text=value_col,
        color_discrete_sequence=[BAR_COLOR]
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Percent annual energy: %{x:.3f}%<extra></extra>"
        ),
        marker=dict(
            line=dict(color="#FCFCFA", width=1.2)
        )
    )

    fig.update_layout(
        title=title,
        height=max(700, 28 * len(df)),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        margin=dict(t=60, l=10, r=40, b=20),
        xaxis_title="Percent Annual Energy Demand in 2022 (%)",
        yaxis_title="Unit Operation Level 2",
        font=dict(
            family="Arial, sans-serif",
            color=TEXT_COLOR,
            size=14
        )
    )

    fig.update_xaxes(
        ticksuffix="%",
        showgrid=True
    )

    fig.update_yaxes(
        categoryorder="total ascending"
    )

    return fig


st.title("Energy Classification: Unit Operations")

try:
    df = load_excel(DATA_URL)

    bar_df = prepare_bar_data(
        df,
        category_col="Unit operation Level 2 classification",
        value_col="Percent Annual energy demand in 2022"
    )

    st.subheader("Percent Annual Energy by Unit Operation Level 2")
    fig_bar = build_bar_chart(
        bar_df,
        "Unit operation Level 2 classification",
        "Percent Annual energy demand in 2022",
        "Percent Annual Energy by Unit Operation Level 2"
    )
    st.plotly_chart(
        fig_bar,
        use_container_width=True,
        theme=None,
        config={
            "displayModeBar": False,
            "scrollZoom": False
        }
    )

    st.subheader("Data Table")
    table_df = bar_df.rename(
        columns={
            "Unit operation Level 2 classification": "Unit Operation Level 2",
            "Percent Annual energy demand in 2022": "Percent Annual Energy (%)"
        }
    )[["Rank", "Unit Operation Level 2", "Percent Annual Energy (%)"]]

    st.dataframe(table_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"App error: {e}")

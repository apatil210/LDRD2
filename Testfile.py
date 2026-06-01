from io import BytesIO

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

    # Convert fraction to displayed percent
    df_agg["Display Percent"] = df_agg[value_col] * 100
    df_agg["Rank"] = range(1, len(df_agg) + 1)

    return df_agg


def build_bar_chart(df: pd.DataFrame):
    fig = px.bar(
        df,
        x="Display Percent",
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
            "Percent annual energy: %{x:.2f}%<extra></extra>"
        ),
        marker=dict(line=dict(color="#FCFCFA", width=1.2))
    )

    fig.update_layout(
        title="Percent Annual Energy by Industrial Process",
        height=max(700, 28 * len(df)),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        margin=dict(t=60, l=10, r=40, b=20),
        xaxis_title="Percent Annual Energy Demand in 2022 (%)",
        yaxis_title="Industrial Process",
        font=dict(
            family="Arial, sans-serif",
            color=TEXT_COLOR,
            size=14
        )
    )

    fig.update_xaxes(ticksuffix="%", showgrid=True)
    fig.update_yaxes(categoryorder="total ascending")

    return fig


st.title("Energy Classification: Industrial Process")

try:
    df = load_excel(DATA_URL)
    bar_df = prepare_bar_data(df)

    st.subheader("Percent Annual Energy by Industrial Process")
    st.plotly_chart(
        build_bar_chart(bar_df),
        use_container_width=True,
        theme=None,
        config={
            "displayModeBar": False,
            "scrollZoom": False
        }
    )

    st.subheader("Data Table")
    table_df = bar_df[["Rank", "Industrial process", "Display Percent"]].rename(
        columns={
            "Industrial process": "Industrial Process",
            "Display Percent": "Percent Annual Energy (%)"
        }
    )

    st.dataframe(
        table_df.style.format({"Percent Annual Energy (%)": "{:.2f}%"}),
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error(f"App error: {e}")

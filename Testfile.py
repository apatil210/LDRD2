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
THRESHOLD_PCT = 1.0

TEXT_COLOR = "#14212B"
PAPER_BG = "rgba(0,0,0,0)"
PLOT_BG = "rgba(0,0,0,0)"

TREEMAP_PALETTE = [
    "#0B6E74",
    "#2D728F",
    "#5B8C5A",
    "#8F5B34",
    "#AA4465",
    "#3A9D90",
    "#6A4C93",
    "#B26E3B",
    "#7A8C2F",
    "#4B6A9B",
]


@st.cache_data(show_spinner=False)
def load_excel(url: str) -> pd.DataFrame:
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")
    if "text/html" in content_type.lower():
        raise ValueError("URL returned an HTML page instead of an Excel file.")

    return pd.read_excel(BytesIO(response.content), engine="openpyxl")


def clean_category(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .fillna("Unknown")
        .str.replace("_", " ", regex=False)
        .str.strip()
        .replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
    )


def aggregate_percent(
    df: pd.DataFrame,
    category_col: str,
    value_col: str
) -> pd.DataFrame:
    required_columns = {category_col, value_col}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df_work = df[[category_col, value_col]].copy()
    df_work[value_col] = pd.to_numeric(df_work[value_col], errors="coerce").fillna(0)
    df_work[category_col] = clean_category(df_work[category_col])

    df_agg = (
        df_work.groupby(category_col, as_index=False)[value_col]
        .sum()
        .query(f"`{value_col}` > 0")
        .sort_values(value_col, ascending=False)
        .reset_index(drop=True)
    )

    if df_agg.empty:
        raise ValueError(f"No positive values found for {value_col}.")

    total = df_agg[value_col].sum()
    df_agg["Share_pct"] = 100 * df_agg[value_col] / total
    df_agg["Rank"] = range(1, len(df_agg) + 1)
    df_agg["Display_text"] = df_agg.apply(
        lambda r: f"<b>{r[category_col]}</b><br>{r['Share_pct']:.1f}%",
        axis=1
    )

    return df_agg


def build_color_map(categories, palette):
    return {
        cat: palette[i % len(palette)]
        for i, cat in enumerate(categories)
    }


def build_treemap(
    df: pd.DataFrame,
    category_col: str,
    value_col: str,
    title: str
):
    color_map = build_color_map(df[category_col], TREEMAP_PALETTE)

    fig = px.treemap(
        df,
        path=[category_col],
        values=value_col,
        color=category_col,
        color_discrete_map=color_map,
        custom_data=[category_col, value_col, "Share_pct", "Rank", "Display_text"]
    )

    fig.update_traces(
        texttemplate="%{customdata[4]}",
        textposition="middle center",
        textfont=dict(
            size=13,
            color="#111111",
            family="Arial, sans-serif"
        ),
        marker=dict(
            line=dict(color="#FCFCFA", width=4),
            cornerradius=10
        ),
        tiling=dict(
            pad=4,
            squarifyratio=1.0
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Annual energy demand: %{customdata[1]:.3f} PJ<br>"
            "Share: %{customdata[2]:.2f}%<br>"
            "Rank: %{customdata[3]}<extra></extra>"
        ),
        pathbar=dict(visible=False)
    )

    fig.update_layout(
        title=title,
        height=820,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        margin=dict(t=50, l=10, r=10, b=10),
        uniformtext=dict(minsize=10, mode="show"),
        font=dict(
            family="Arial, sans-serif",
            color=TEXT_COLOR,
            size=14
        )
    )

    return fig


st.title("Energy Classification: Unit Operations")

try:
    df = load_excel(DATA_URL)

    unit_ops = aggregate_percent(
        df,
        category_col="Unit operation Level 2 classification",
        value_col="Annual energy demand in 2022"
    )

    unit_ops_plot = (
        unit_ops[unit_ops["Share_pct"] > THRESHOLD_PCT]
        .copy()
        .sort_values("Annual energy demand in 2022", ascending=False)
        .reset_index(drop=True)
    )

    st.subheader("Unit Operation Level 2 Categories > 1%")
    fig_tree = build_treemap(
        unit_ops_plot,
        "Unit operation Level 2 classification",
        "Annual energy demand in 2022",
        "Unit Operations - Level 2"
    )
    st.plotly_chart(
        fig_tree,
        use_container_width=True,
        theme=None,
        config={
            "displayModeBar": False,
            "scrollZoom": False
        }
    )

    st.subheader("All Unit Operation Level 2 Categories")
    table_df = unit_ops[
        ["Rank", "Unit operation Level 2 classification", "Annual energy demand in 2022", "Share_pct"]
    ].rename(
        columns={
            "Unit operation Level 2 classification": "Unit Operation Level 2",
            "Annual energy demand in 2022": "Annual Energy (PJ)",
            "Share_pct": "Share (%)"
        }
    )

    st.dataframe(table_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"App error: {e}")

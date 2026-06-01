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

DATA_URL = "https://raw.githubusercontent.com/apatil210/LDRD/main/Figure2Data.xlsx"
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
    return pd.read_excel(BytesIO(response.content), engine="openpyxl")

def clean_category(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace("_", " ", regex=False)
        .str.strip()
    )

def prepare_data(url: str):
    df = load_excel(url)

    required_columns = {"Category", "Data"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_columns}")

    df_agg = (
        df.groupby("Category", as_index=False)["Data"]
        .sum()
        .query("Data > 0")
        .sort_values("Data", ascending=False)
        .reset_index(drop=True)
    )

    if df_agg.empty:
        raise ValueError("No positive data values found.")

    total = df_agg["Data"].sum()
    df_agg["Category_clean"] = clean_category(df_agg["Category"])
    df_agg["Share_pct"] = 100 * df_agg["Data"] / total
    df_agg["Rank"] = range(1, len(df_agg) + 1)
    df_agg["Display_text"] = df_agg.apply(
        lambda r: f"<b>{r['Category_clean']}</b><br>{r['Share_pct']:.1f}%",
        axis=1
    )

    df_treemap = (
        df_agg[df_agg["Share_pct"] > THRESHOLD_PCT]
        .copy()
        .sort_values("Data", ascending=False)
        .reset_index(drop=True)
    )

    return df_agg, df_treemap

def build_color_map(categories, palette):
    return {
        cat: palette[i % len(palette)]
        for i, cat in enumerate(categories)
    }

def build_treemap(df: pd.DataFrame):
    color_map = build_color_map(df["Category_clean"], TREEMAP_PALETTE)

    fig = px.treemap(
        df,
        path=["Category_clean"],
        values="Data",
        color="Category_clean",
        color_discrete_map=color_map,
        custom_data=["Category_clean", "Data", "Share_pct", "Rank", "Display_text"]
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
            "Energy value: %{customdata[1]:.3f}<br>"
            "Share: %{customdata[2]:.2f}%<br>"
            "Rank: %{customdata[3]}<extra></extra>"
        ),
        pathbar=dict(visible=False)
    )

    fig.update_layout(
        height=820,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        margin=dict(t=10, l=10, r=10, b=10),
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
    df_all, df_treemap = prepare_data(DATA_URL)

    st.subheader("Unit Operation Categories > 1%")
    fig_tree = build_treemap(df_treemap)
    st.plotly_chart(
        fig_tree,
        use_container_width=True,
        theme=None,
        config={
            "displayModeBar": False,
            "scrollZoom": False
        }
    )

    st.subheader("All Unit Operation Categories")
    table_df = df_all[["Rank", "Category_clean", "Data", "Share_pct"]].rename(
        columns={
            "Category_clean": "Category",
            "Data": "Value",
            "Share_pct": "Share (%)"
        }
    )

    st.dataframe(table_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"App error: {e}")

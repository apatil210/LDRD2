from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.io as pio
import requests
import streamlit as st

st.set_page_config(
    page_title="Energy Classification Treemaps",
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
def load_excel(uploaded_file=None, url: str | None = None) -> pd.DataFrame:
    if uploaded_file is not None:
        raw = pd.read_excel(uploaded_file, sheet_name="Process-level data", header=None)
    else:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        raw = pd.read_excel(BytesIO(response.content), sheet_name="Process-level data", header=None)

    # First row contains the real headers
    raw.columns = raw.iloc[0]
    df = raw.iloc[1:].reset_index(drop=True)

    # Clean column names
    df.columns = [str(c).strip() for c in df.columns]

    return df

def clean_category(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace("_", " ", regex=False)
        .str.replace("\n", " ", regex=False)
        .str.strip()
    )

def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)

def aggregate_percent(df: pd.DataFrame, category_col: str, value_col: str) -> pd.DataFrame:
    work = df.copy()

    work[category_col] = clean_category(work[category_col])
    work[value_col] = to_numeric(work[value_col])

    agg = (
        work.groupby(category_col, as_index=False)[value_col]
        .sum()
        .query(f"`{value_col}` > 0")
        .sort_values(value_col, ascending=False)
        .reset_index(drop=True)
    )

    if agg.empty:
        raise ValueError(f"No positive values found for {category_col} / {value_col}")

    total = agg[value_col].sum()
    agg["Share_pct"] = 100 * agg[value_col] / total
    agg["Rank"] = range(1, len(agg) + 1)
    agg["Display_text"] = agg.apply(
        lambda r: f"<b>{r[category_col]}</b><br>{r['Share_pct']:.1f}%",
        axis=1
    )

    return agg

def prepare_energy_mix(df: pd.DataFrame) -> pd.DataFrame:
    energy_cols = {
        "Electricity": "Annual electricity demand in 2022",
        "Fuel": "Annual fuels demand in 2022",
        "Steam": "Annual fuels or electricity for steam or steam from CHP demand in 2022",
    }

    totals = []
    for label, col in energy_cols.items():
        value = to_numeric(df[col]).sum()
        totals.append({"Category": label, "Value": value})

    energy_df = pd.DataFrame(totals)
    energy_df = energy_df.query("Value > 0").sort_values("Value", ascending=False).reset_index(drop=True)

    total = energy_df["Value"].sum()
    energy_df["Share_pct"] = 100 * energy_df["Value"] / total
    energy_df["Rank"] = range(1, len(energy_df) + 1)
    energy_df["Display_text"] = energy_df.apply(
        lambda r: f"<b>{r['Category']}</b><br>{r['Share_pct']:.1f}%",
        axis=1
    )

    return energy_df

def filter_threshold(df: pd.DataFrame, threshold_pct: float) -> pd.DataFrame:
    return (
        df[df["Share_pct"] > threshold_pct]
        .copy()
        .reset_index(drop=True)
    )

def build_color_map(categories, palette):
    return {
        cat: palette[i % len(palette)]
        for i, cat in enumerate(categories)
    }

def build_treemap(df: pd.DataFrame, label_col: str, value_col: str, title: str):
    color_map = build_color_map(df[label_col], TREEMAP_PALETTE)

    fig = px.treemap(
        df,
        path=[label_col],
        values=value_col,
        color=label_col,
        color_discrete_map=color_map,
        custom_data=[label_col, value_col, "Share_pct", "Rank", "Display_text"]
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
            "Annual energy: %{customdata[1]:.3f} PJ<br>"
            "Share: %{customdata[2]:.2f}%<br>"
            "Rank: %{customdata[3]}<extra></extra>"
        ),
        pathbar=dict(visible=False)
    )

    fig.update_layout(
        title=title,
        height=700,
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

st.title("Energy Classification Treemaps")

try:
    df = load_excel(uploaded_file=uploaded_file, url=None if uploaded_file else DATA_URL)

    unit_ops = aggregate_percent(
        df,
        category_col="Unit operation (Level 1 classification)",
        value_col="Annual energy demand in 2022"
    )

    industries = aggregate_percent(
        df,
        category_col="Industrial process",
        value_col="Annual energy demand in 2022"
    )

    energy_mix = prepare_energy_mix(df)

    unit_ops_plot = filter_threshold(unit_ops, THRESHOLD_PCT)
    industries_plot = filter_threshold(industries, THRESHOLD_PCT)
    energy_mix_plot = filter_threshold(energy_mix, 0.0)

    st.subheader("Unit Operations by Percent Annual Energy Use")
    st.plotly_chart(
        build_treemap(unit_ops_plot, "Unit operation (Level 1 classification)", "Annual energy demand in 2022",
                      "Unit Operations"),
        use_container_width=True,
        theme=None,
        config={"displayModeBar": False, "scrollZoom": False}
    )

    st.subheader("Industry Types by Percent Annual Energy Use")
    st.plotly_chart(
        build_treemap(industries_plot, "Industrial process", "Annual energy demand in 2022",
                      "Industry Types"),
        use_container_width=True,
        theme=None,
        config={"displayModeBar": False, "scrollZoom": False}
    )

    st.subheader("Energy Use Breakdown by Type")
    st.plotly_chart(
        build_treemap(energy_mix_plot, "Category", "Value",
                      "Electricity vs Fuel vs Steam"),
        use_container_width=True,
        theme=None,
        config={"displayModeBar": False, "scrollZoom": False}
    )

    st.subheader("Underlying Tables")

    tab1, tab2, tab3 = st.tabs(["Unit Operations", "Industry Types", "Energy Types"])

    with tab1:
        st.dataframe(
            unit_ops.rename(columns={
                "Unit operation (Level 1 classification)": "Unit Operation",
                "Annual energy demand in 2022": "Annual Energy (PJ)",
                "Share_pct": "Share (%)"
            })[["Rank", "Unit Operation", "Annual Energy (PJ)", "Share (%)"]],
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        st.dataframe(
            industries.rename(columns={
                "Industrial process": "Industry Type",
                "Annual energy demand in 2022": "Annual Energy (PJ)",
                "Share_pct": "Share (%)"
            })[["Rank", "Industry Type", "Annual Energy (PJ)", "Share (%)"]],
            use_container_width=True,
            hide_index=True
        )

    with tab3:
        st.dataframe(
            energy_mix.rename(columns={
                "Category": "Energy Type",
                "Value": "Annual Energy (PJ)",
                "Share_pct": "Share (%)"
            })[["Rank", "Energy Type", "Annual Energy (PJ)", "Share (%)"]],
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error(f"App error: {e}")

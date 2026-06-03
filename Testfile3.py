import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="US Manufacturing Energy Classification: Unit Operations",
    layout="wide",
)

URL = "https://github.com/apatil210/LDRD2/raw/main/Modified%20Data%20for%20NAICS.xlsx"
SHEET_NAME = "Process-level data"
HEADER_ROW = 1

NAICS_COL = "NAICS Level 1"
BAR_UNIT_COL = "Unit operation Level 2 classification"
BAR_PCT_COL = "Percent Annual energy demand in 2022"
COVERAGE_COL = "Percent Coverage of NAICS 3-digit Sector"
ENERGY_TOTAL_COL = "Annual energy demand in 2022"
ELECTRICITY_COL = "Annual electricity demand in 2022"
FUELS_COL = "Annual fuels demand in 2022"
STEAM_COL = "Annual fuels or electricity for steam or steam from CHP demand in 2022"

REQUIRED_COLUMNS = [
    NAICS_COL,
    BAR_UNIT_COL,
    BAR_PCT_COL,
    ENERGY_TOTAL_COL,
    ELECTRICITY_COL,
    FUELS_COL,
    STEAM_COL,
]


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_excel(URL, sheet_name=SHEET_NAME, header=HEADER_ROW)
    df.columns = [str(col).strip() for col in df.columns]
    return df


def find_column(df: pd.DataFrame, target: str):
    target_norm = str(target).strip().lower()
    exact = [c for c in df.columns if str(c).strip().lower() == target_norm]
    return exact[0] if exact else None


def numeric_series(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.to_numeric(df[col], errors="coerce").fillna(0)


def fmt_pj(value: float) -> str:
    return f"{value:,.2f} PJ"


def fmt_pct(value: float) -> str:
    return f"{value:.2%}"


def build_energy_breakdown(df_filtered: pd.DataFrame) -> pd.DataFrame:
    fuels = numeric_series(df_filtered, FUELS_COL).sum()
    steam = numeric_series(df_filtered, STEAM_COL).sum()
    electricity = numeric_series(df_filtered, ELECTRICITY_COL).sum()

    breakdown = pd.DataFrame(
        {
            "Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
            "Value": [fuels, steam, electricity],
        }
    )
    breakdown = breakdown[breakdown["Value"] > 0].copy()

    if breakdown.empty:
        breakdown = pd.DataFrame(
            {
                "Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
                "Value": [0.0, 0.0, 0.0],
            }
        )

    return breakdown


def build_bar_data(df_filtered: pd.DataFrame) -> pd.DataFrame:
    temp = df_filtered[[BAR_UNIT_COL, BAR_PCT_COL]].copy()
    temp[BAR_PCT_COL] = pd.to_numeric(temp[BAR_PCT_COL], errors="coerce")

    bar_df = (
        temp.dropna(subset=[BAR_UNIT_COL, BAR_PCT_COL])
        .groupby(BAR_UNIT_COL, as_index=False)[BAR_PCT_COL]
        .sum()
        .rename(columns={BAR_UNIT_COL: "Unit Operation", BAR_PCT_COL: "Percent Energy"})
    )

    bar_df = bar_df[bar_df["Percent Energy"] > 0].copy()
    return bar_df


def build_summary(df_filtered: pd.DataFrame, coverage_col_name: str | None) -> dict:
    total_energy = numeric_series(df_filtered, ENERGY_TOTAL_COL).sum()
    total_electricity = numeric_series(df_filtered, ELECTRICITY_COL).sum()
    total_fuels = numeric_series(df_filtered, FUELS_COL).sum()
    total_steam = numeric_series(df_filtered, STEAM_COL).sum()

    coverage = None
    if coverage_col_name is not None:
        coverage_values = pd.to_numeric(df_filtered[coverage_col_name], errors="coerce").dropna()
        if not coverage_values.empty:
            coverage = coverage_values.max()

    return {
        "total_energy": total_energy,
        "total_electricity": total_electricity,
        "total_fuels": total_fuels,
        "total_steam": total_steam,
        "coverage": coverage,
    }


def validate_columns(df: pd.DataFrame):
    missing = [c for c in REQUIRED_COLUMNS if find_column(df, c) is None]
    if missing:
        st.error("Missing required columns: " + ", ".join(missing))
        st.stop()


st.markdown(
    """
    <style>
    .stApp {
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background-color: #f8fafc;
    }
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 1250px;
    }
    h1 {
        font-weight: 700 !important;
        color: #213547 !important;
        letter-spacing: 0.01em;
    }
    h2, h3 {
        color: #213547 !important;
    }
    .card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        margin-bottom: 1rem;
    }
    .metric-label {
        font-size: 0.92rem;
        color: #64748b;
        margin-bottom: 0.15rem;
    }
    .metric-value {
        font-size: 1.35rem;
        font-weight: 700;
        color: #0f172a;
    }
    .coverage-label {
        margin-top: 0.35rem;
        margin-bottom: 1rem;
        font-size: 0.98rem;
        color: #0f172a;
        font-weight: 600;
    }
    .dataframe tbody tr th {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


df = load_data()
validate_columns(df)

NAICS_COL = find_column(df, NAICS_COL)
BAR_UNIT_COL = find_column(df, BAR_UNIT_COL)
BAR_PCT_COL = find_column(df, BAR_PCT_COL)
ENERGY_TOTAL_COL = find_column(df, ENERGY_TOTAL_COL)
ELECTRICITY_COL = find_column(df, ELECTRICITY_COL)
FUELS_COL = find_column(df, FUELS_COL)
STEAM_COL = find_column(df, STEAM_COL)
COVERAGE_COL = find_column(df, COVERAGE_COL)

naics_level1_list = (
    df[NAICS_COL].dropna().astype(str).drop_duplicates().sort_values().tolist()
)

st.markdown(
    "<h1>US Manufacturing Energy Classification: Unit Operations</h1>",
    unsafe_allow_html=True,
)

st.write("Select a NAICS Level 1 sector to generate an energy fact sheet.")

selected_naics1 = st.selectbox("NAICS Level 1", naics_level1_list, index=0)

df_filtered = df[df[NAICS_COL].astype(str) == str(selected_naics1)].copy()
summary = build_summary(df_filtered, COVERAGE_COL)

coverage_text = (
    fmt_pct(summary["coverage"])
    if summary["coverage"] is not None
    else "N/A"
)

st.markdown(
    f'<div class="coverage-label">Total Sector Coverage of {selected_naics1}: {coverage_text}</div>',
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(
        f'<div class="card"><div class="metric-label">Total annual energy</div><div class="metric-value">{fmt_pj(summary["total_energy"])}</div></div>',
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        f'<div class="card"><div class="metric-label">Annual electricity</div><div class="metric-value">{fmt_pj(summary["total_electricity"])}</div></div>',
        unsafe_allow_html=True,
    )
with m3:
    st.markdown(
        f'<div class="card"><div class="metric-label">Annual fuels</div><div class="metric-value">{fmt_pj(summary["total_fuels"])}</div></div>',
        unsafe_allow_html=True,
    )
with m4:
    st.markdown(
        f'<div class="card"><div class="metric-label">Annual steam</div><div class="metric-value">{fmt_pj(summary["total_steam"])}</div></div>',
        unsafe_allow_html=True,
    )

breakdown_df = build_energy_breakdown(df_filtered)
bar_df = build_bar_data(df_filtered)

left_col, right_col = st.columns([1.0, 1.2])

with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Total Annual Energy Breakdown")

    fig_donut = px.pie(
        breakdown_df,
        names="Type",
        values="Value",
        hole=0.62,
        color="Type",
        color_discrete_map={
            "Annual Fuels": "#f7901d",
            "Annual Steam": "#3b82f6",
            "Annual Electricity": "#0f766e",
        },
    )
    fig_donut.update_traces(textinfo="percent+label", textposition="outside")
    fig_donut.update_layout(showlegend=False, margin=dict(t=20, b=10, l=10, r=10))
    st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Percent Annual Energy by Unit Operation")

    if not bar_df.empty:
        bar_df_sorted = bar_df.sort_values("Percent Energy", ascending=True)
        fig_bar = px.bar(
            bar_df_sorted,
            x="Percent Energy",
            y="Unit Operation",
            orientation="h",
            text="Percent Energy",
        )
        fig_bar.update_traces(
            marker_color="#006b6b",
            texttemplate="%{text:.1%}",
            textposition="outside",
            cliponaxis=False,
        )
        fig_bar.update_layout(
            xaxis_title="Percent of Annual Energy",
            yaxis_title="",
            xaxis_tickformat=".0%",
            margin=dict(t=20, b=20, l=80, r=70),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No positive unit-operation energy share data is available for this NAICS Level 1 selection.")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(f"Fact Sheet – {selected_naics1}")
st.dataframe(df_filtered, use_container_width=True, height=500)
st.markdown('</div>', unsafe_allow_html=True)

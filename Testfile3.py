import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="US Manufacturing Energy Classification: Unit Operations",
    layout="wide",
)

FILE_URL = "https://github.com/apatil210/LDRD2/raw/main/Modified%20Data%20for%20NAICS.xlsx"
SHEET_NAME = "Process-level data"
HEADER_ROW = 1


@st.cache_data
def load_data():
    df = pd.read_excel(FILE_URL, sheet_name=SHEET_NAME, header=HEADER_ROW)
    df.columns = [str(col).strip().replace("\n", " ") for col in df.columns]
    return df


def normalize(text):
    return (
        str(text)
        .strip()
        .lower()
        .replace("\n", " ")
        .replace("  ", " ")
        .replace("(3-digit)", "3-digit")
        .replace("level 1 classification", "level 1 classification")
        .replace("level 2 classification", "level 2 classification")
    )


def find_col(df, candidates):
    normalized = {normalize(c): c for c in df.columns}
    for cand in candidates:
        key = normalize(cand)
        if key in normalized:
            return normalized[key]
    return None


def num(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def pct_text(x):
    return f"{x:.2%}"


def pj_text(x):
    return f"{x:,.2f} PJ"


df = load_data()

NAICS_COL = find_col(df, [
    "NAICS Level 1",
])

NAICS2_COL = find_col(df, [
    "NAICS Level 2",
])

PROCESS_COL = find_col(df, [
    "Industrial process",
])

BAR_UNIT_COL = find_col(df, [
    "Unit operation (Level 2 classification)",
    "Unit operation Level 2 classification",
])

BAR_UNIT_L1_COL = find_col(df, [
    "Unit operation (Level 1 classification)",
    "Unit operation Level 1 classification",
])

BAR_PCT_COL = find_col(df, [
    "Percent Annual energy demand in 2022",
])

COVERAGE_COL = find_col(df, [
    "Percent Coverage of NAICS (3-digit) Sector",
    "Percent Coverage of NAICS 3-digit Sector",
])

TOTAL_ENERGY_COL = find_col(df, [
    "Annual energy demand in 2022",
])

ELEC_COL = find_col(df, [
    "Annual electricity demand in 2022",
])

FUELS_COL = find_col(df, [
    "Annual fuels demand in 2022",
])

STEAM_COL = find_col(df, [
    "Annual fuels or electricity for steam or steam from CHP demand in 2022",
])

required = {
    "NAICS Level 1": NAICS_COL,
    "Unit operation Level 2": BAR_UNIT_COL,
    "Percent Annual energy demand in 2022": BAR_PCT_COL,
    "Annual energy demand in 2022": TOTAL_ENERGY_COL,
    "Annual electricity demand in 2022": ELEC_COL,
    "Annual fuels demand in 2022": FUELS_COL,
    "Annual steam-related demand in 2022": STEAM_COL,
}

missing = [k for k, v in required.items() if v is None]
if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.stop()

st.markdown(
    """
    <style>
    .stApp {
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #f8fafc;
    }
    .block-container {
        max-width: 1240px;
        padding-top: 1.25rem;
        padding-bottom: 2rem;
    }
    h1 {
        color: #1e293b !important;
        font-weight: 700 !important;
        letter-spacing: 0.01em;
    }
    h2, h3 {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px 18px;
    }
    .metric-label {
        color: #64748b;
        font-size: 0.92rem;
        margin-bottom: 0.2rem;
    }
    .metric-value {
        color: #0f172a;
        font-size: 1.35rem;
        font-weight: 700;
    }
    .coverage-label {
        margin-top: 0.3rem;
        margin-bottom: 1rem;
        color: #334155;
        font-size: 0.98rem;
        font-weight: 600;
    }
    .dataframe tbody tr th {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h1>US Manufacturing Energy Classification: Unit Operations</h1>",
    unsafe_allow_html=True,
)

st.write("Select a NAICS Level 1 sector to generate a fact sheet.")

naics_level1_list = (
    df[NAICS_COL]
    .dropna()
    .astype(str)
    .drop_duplicates()
    .sort_values()
    .tolist()
)

selected_naics1 = st.selectbox(
    "NAICS Level 1",
    naics_level1_list,
    index=0,
)

df_filtered = df[df[NAICS_COL].astype(str) == str(selected_naics1)].copy()

coverage_value = None
if COVERAGE_COL is not None:
    coverage_series = pd.to_numeric(df_filtered[COVERAGE_COL], errors="coerce").dropna()
    if not coverage_series.empty:
        coverage_value = coverage_series.max()

coverage_text = pct_text(coverage_value) if coverage_value is not None else "N/A"

st.markdown(
    f'<div class="coverage-label">Total Sector Coverage of {selected_naics1}: {coverage_text}</div>',
    unsafe_allow_html=True,
)

total_energy = num(df_filtered[TOTAL_ENERGY_COL]).sum()
total_electricity = num(df_filtered[ELEC_COL]).sum()
total_fuels = num(df_filtered[FUELS_COL]).sum()
total_steam = num(df_filtered[STEAM_COL]).sum()

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Total annual energy</div><div class="metric-value">{pj_text(total_energy)}</div></div>',
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Annual electricity</div><div class="metric-value">{pj_text(total_electricity)}</div></div>',
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Annual fuels</div><div class="metric-value">{pj_text(total_fuels)}</div></div>',
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Annual steam</div><div class="metric-value">{pj_text(total_steam)}</div></div>',
        unsafe_allow_html=True,
    )

bar_tmp = df_filtered[[BAR_UNIT_COL, BAR_PCT_COL]].copy()
bar_tmp[BAR_PCT_COL] = pd.to_numeric(bar_tmp[BAR_PCT_COL], errors="coerce")

bar_df = (
    bar_tmp.dropna(subset=[BAR_UNIT_COL, BAR_PCT_COL])
    .groupby(BAR_UNIT_COL, as_index=False)[BAR_PCT_COL]
    .sum()
    .rename(columns={
        BAR_UNIT_COL: "Unit Operation",
        BAR_PCT_COL: "Percent Energy",
    })
)

bar_df = bar_df[bar_df["Percent Energy"] > 0].sort_values("Percent Energy", ascending=True)

breakdown_df = pd.DataFrame(
    {
        "Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
        "Value": [total_fuels, total_steam, total_electricity],
    }
)
breakdown_df = breakdown_df[breakdown_df["Value"] > 0].copy()

if breakdown_df.empty:
    breakdown_df = pd.DataFrame(
        {
            "Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
            "Value": [0.0, 0.0, 0.0],
        }
    )

left_col, right_col = st.columns([1.0, 1.2])

with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Total Annual Energy Breakdown")

    fig_donut = px.pie(
        breakdown_df,
        names="Type",
        values="Value",
        hole=0.64,
        color="Type",
        color_discrete_map={
            "Annual Fuels": "#f7901d",
            "Annual Steam": "#3b82f6",
            "Annual Electricity": "#006b6b",
        },
    )
    fig_donut.update_traces(
        textinfo="percent+label",
        textposition="outside",
    )
    fig_donut.update_layout(
        showlegend=False,
        margin=dict(t=20, b=10, l=10, r=10),
    )

    st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Percent Annual Energy by Unit Operation")

    if not bar_df.empty:
        fig_bar = px.bar(
            bar_df,
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
            margin=dict(t=20, b=20, l=90, r=70),
        )

        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No positive annual energy data is available for this NAICS Level 1 selection.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(f"Fact Sheet – {selected_naics1}")

preferred_cols = [
    NAICS2_COL,
    NAICS_COL,
    PROCESS_COL,
    BAR_UNIT_L1_COL,
    BAR_UNIT_COL,
    TOTAL_ENERGY_COL,
    ELEC_COL,
    FUELS_COL,
    STEAM_COL,
    BAR_PCT_COL,
    COVERAGE_COL,
]
preferred_cols = [c for c in preferred_cols if c is not None and c in df_filtered.columns]

display_df = df_filtered[preferred_cols].copy() if preferred_cols else df_filtered.copy()

st.dataframe(display_df, use_container_width=True, height=520)

csv_bytes = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered data as CSV",
    data=csv_bytes,
    file_name="naics_filtered_fact_sheet.csv",
    mime="text/csv",
)

st.markdown("</div>", unsafe_allow_html=True)

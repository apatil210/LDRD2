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

NAICS_COL = "NAICS Level 1"
NAICS2_COL = "NAICS Level 2"
PROCESS_COL = "Industrial process"
UNIT_L1_COL = "Unit operation Level 1 classification"
UNIT_L2_COL = "Unit operation Level 2 classification"
ENERGY_PCT_COL = "Percent Annual energy demand in 2022"
COVERAGE_COL = "Percent Coverage of NAICS 3-digit Sector"
TOTAL_ENERGY_COL = "Annual energy demand in 2022"
ELEC_COL = "Annual electricity demand in 2022"
FUELS_COL = "Annual fuels demand in 2022"
STEAM_COL = "Annual fuels or electricity for steam or steam from CHP demand in 2022"

REQUIRED_COLUMNS = [
    NAICS_COL,
    UNIT_L2_COL,
    ENERGY_PCT_COL,
    TOTAL_ENERGY_COL,
    ELEC_COL,
    FUELS_COL,
    STEAM_COL,
]


@st.cache_data
def load_data():
    df = pd.read_excel(FILE_URL, sheet_name=SHEET_NAME, header=HEADER_ROW)
    df.columns = [str(col).strip() for col in df.columns]
    return df


def resolve_column(df, name):
    target = str(name).strip().lower()
    for col in df.columns:
        if str(col).strip().lower() == target:
            return col
    return None


def to_num(series):
    return pd.to_numeric(series, errors="coerce")


def fmt_pct(v):
    return f"{v:.2%}"


def fmt_pj(v):
    return f"{v:,.2f} PJ"


def safe_sum(df, col):
    if col is None or col not in df.columns:
        return 0.0
    return to_num(df[col]).fillna(0).sum()


def safe_max(df, col):
    if col is None or col not in df.columns:
        return None
    s = to_num(df[col]).dropna()
    return None if s.empty else s.max()


def get_bar_df(df_filtered, group_col):
    if group_col is None or ENERGY_PCT_COL not in df_filtered.columns:
        return pd.DataFrame(columns=["Category", "Percent Energy"])

    tmp = df_filtered[[group_col, ENERGY_PCT_COL]].copy()
    tmp[ENERGY_PCT_COL] = to_num(tmp[ENERGY_PCT_COL])

    out = (
        tmp.dropna(subset=[group_col, ENERGY_PCT_COL])
        .groupby(group_col, as_index=False)[ENERGY_PCT_COL]
        .sum()
        .rename(columns={group_col: "Category", ENERGY_PCT_COL: "Percent Energy"})
        .sort_values("Percent Energy", ascending=True)
    )

    return out


def get_breakdown_df(df_filtered):
    fuels = safe_sum(df_filtered, FUELS_COL)
    steam = safe_sum(df_filtered, STEAM_COL)
    elec = safe_sum(df_filtered, ELEC_COL)

    out = pd.DataFrame(
        {
            "Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
            "Value": [fuels, steam, elec],
        }
    )

    out = out[out["Value"] > 0].copy()

    if out.empty:
        out = pd.DataFrame(
            {
                "Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
                "Value": [0.0, 0.0, 0.0],
            }
        )

    return out


st.markdown(
    """
    <style>
    .stApp {
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background-color: #f8fafc;
    }

    .block-container {
        padding-top: 1.25rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }

    h1 {
        font-weight: 700 !important;
        color: #1e293b !important;
        letter-spacing: 0.01em;
    }

    h2, h3 {
        color: #1e293b !important;
        font-weight: 600 !important;
    }

    .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 18px 20px 20px 20px;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 16px 18px;
        margin-bottom: 1rem;
    }

    .metric-label {
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 0.2rem;
    }

    .metric-value {
        color: #0f172a;
        font-size: 1.35rem;
        font-weight: 700;
    }

    .coverage-label {
        margin-top: 0.2rem;
        margin-bottom: 1rem;
        color: #334155;
        font-weight: 600;
        font-size: 0.98rem;
    }

    .stSelectbox > div > div {
        border-radius: 8px;
    }

    .dataframe tbody tr th {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

df = load_data()

resolved = {name: resolve_column(df, name) for name in [
    NAICS_COL,
    NAICS2_COL,
    PROCESS_COL,
    UNIT_L1_COL,
    UNIT_L2_COL,
    ENERGY_PCT_COL,
    COVERAGE_COL,
    TOTAL_ENERGY_COL,
    ELEC_COL,
    FUELS_COL,
    STEAM_COL,
]}

missing = [c for c in REQUIRED_COLUMNS if resolved[c] is None]
if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.stop()

NAICS_COL = resolved[NAICS_COL]
NAICS2_COL = resolved[NAICS2_COL]
PROCESS_COL = resolved[PROCESS_COL]
UNIT_L1_COL = resolved[UNIT_L1_COL]
UNIT_L2_COL = resolved[UNIT_L2_COL]
ENERGY_PCT_COL = resolved[ENERGY_PCT_COL]
COVERAGE_COL = resolved[COVERAGE_COL]
TOTAL_ENERGY_COL = resolved[TOTAL_ENERGY_COL]
ELEC_COL = resolved[ELEC_COL]
FUELS_COL = resolved[FUELS_COL]
STEAM_COL = resolved[STEAM_COL]

st.markdown(
    "<h1>US Manufacturing Energy Classification: Unit Operations</h1>",
    unsafe_allow_html=True,
)

st.write("Select a NAICS Level 1 sector to generate a fact sheet from the process-level workbook.")

naics_options = (
    df[NAICS_COL]
    .dropna()
    .astype(str)
    .drop_duplicates()
    .sort_values()
    .tolist()
)

selected_naics1 = st.selectbox("NAICS Level 1", naics_options, index=0)

df_sector = df[df[NAICS_COL].astype(str) == str(selected_naics1)].copy()

coverage_val = safe_max(df_sector, COVERAGE_COL)
coverage_text = fmt_pct(coverage_val) if coverage_val is not None else "N/A"

st.markdown(
    f'<div class="coverage-label">Total Sector Coverage of {selected_naics1}: {coverage_text}</div>',
    unsafe_allow_html=True,
)

total_energy = safe_sum(df_sector, TOTAL_ENERGY_COL)
total_electricity = safe_sum(df_sector, ELEC_COL)
total_fuels = safe_sum(df_sector, FUELS_COL)
total_steam = safe_sum(df_sector, STEAM_COL)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Total annual energy</div><div class="metric-value">{fmt_pj(total_energy)}</div></div>',
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Annual electricity</div><div class="metric-value">{fmt_pj(total_electricity)}</div></div>',
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Annual fuels</div><div class="metric-value">{fmt_pj(total_fuels)}</div></div>',
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Annual steam</div><div class="metric-value">{fmt_pj(total_steam)}</div></div>',
        unsafe_allow_html=True,
    )

sidebar_col, main_col = st.columns([0.9, 3.1])

with sidebar_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Filters")

    if NAICS2_COL is not None:
        naics2_options = (
            df_sector[NAICS2_COL]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .sort_values()
            .tolist()
        )
        naics2_choice = st.selectbox("NAICS Level 2", ["All"] + naics2_options, index=0)
    else:
        naics2_choice = "All"

    chart_level = st.radio(
        "Bar chart grouping",
        ["Unit operation Level 2", "Unit operation Level 1", "Industrial process"],
        index=0,
    )

    show_raw = st.checkbox("Show raw filtered table", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

if naics2_choice != "All" and NAICS2_COL is not None:
    df_filtered = df_sector[df_sector[NAICS2_COL].astype(str) == str(naics2_choice)].copy()
else:
    df_filtered = df_sector.copy()

if chart_level == "Unit operation Level 1":
    chart_col = UNIT_L1_COL
    chart_title = "Percent Annual Energy by Unit Operation Level 1"
elif chart_level == "Industrial process":
    chart_col = PROCESS_COL
    chart_title = "Percent Annual Energy by Industrial Process"
else:
    chart_col = UNIT_L2_COL
    chart_title = "Percent Annual Energy by Unit Operation"

bar_df = get_bar_df(df_filtered, chart_col)
breakdown_df = get_breakdown_df(df_filtered)

with main_col:
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
        st.subheader(chart_title)

        if not bar_df.empty:
            fig_bar = px.bar(
                bar_df,
                x="Percent Energy",
                y="Category",
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
            st.info("No positive annual energy share data is available for the selected filters.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Filtered Fact Sheet")

    summary_cols = [
        c for c in [
            NAICS2_COL,
            NAICS_COL,
            PROCESS_COL,
            UNIT_L1_COL,
            UNIT_L2_COL,
            TOTAL_ENERGY_COL,
            ELEC_COL,
            FUELS_COL,
            STEAM_COL,
            ENERGY_PCT_COL,
            COVERAGE_COL,
        ] if c is not None and c in df_filtered.columns
    ]

    display_df = df_filtered[summary_cols].copy() if summary_cols else df_filtered.copy()

    st.dataframe(display_df, use_container_width=True, height=520)

    csv_data = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered fact sheet as CSV",
        data=csv_data,
        file_name="filtered_fact_sheet.csv",
        mime="text/csv",
    )

    st.markdown("</div>", unsafe_allow_html=True)
    

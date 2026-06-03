import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------
# Page config
# --------------------------
st.set_page_config(
    page_title="US Manufacturing Energy Classification: Unit Operations",
    layout="wide",
)

# --------------------------
# Load Excel data from GitHub
# --------------------------
@st.cache_data
def load_data():
    url = "https://github.com/apatil210/LDRD2/raw/main/Modified%20Data%20for%20NAICS.xlsx"
    df = pd.read_excel(
        url,
        sheet_name="Process-level data",
        header=1,
    )
    df.columns = [str(col).strip() for col in df.columns]
    return df


df = load_data()

# --------------------------
# Column names
# --------------------------
NAICS_COL = "NAICS Level 1"
BAR_UNIT_COL = "Unit operation Level 2 classification"
BAR_PCT_COL = "Percent Annual energy demand in 2022"

COVERAGE_COL = "Percent Coverage of NAICS 3-digit Sector"
COVERAGE_COL_INDEX = 38  # fallback if exact name is missing

ELEC_COL = "Annual electricity demand in 2022"
FUEL_COL = "Annual fuels demand in 2022"
STEAM_COL = "Annual fuels or electricity for steam or steam from CHP demand in 2022"

# --------------------------
# Validate required columns
# --------------------------
required_cols = [NAICS_COL, BAR_UNIT_COL, BAR_PCT_COL]
missing_required = [col for col in required_cols if col not in df.columns]

if missing_required:
    st.error(
        f"Missing required columns: {missing_required}. Available columns are: {list(df.columns)}"
    )
    st.stop()

# Resolve coverage column
if COVERAGE_COL in df.columns:
    coverage_col_name = COVERAGE_COL
elif len(df.columns) > COVERAGE_COL_INDEX:
    coverage_col_name = df.columns[COVERAGE_COL_INDEX]
else:
    coverage_col_name = None

# --------------------------
# Build dropdown values
# --------------------------
naics_level1_list = (
    df[NAICS_COL]
    .dropna()
    .astype(str)
    .str.strip()
    .drop_duplicates()
    .sort_values()
    .tolist()
)

# --------------------------
# Custom CSS
# --------------------------
st.markdown(
    """
    <style>
    .stApp {
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }

    h1 {
        font-weight: 700 !important;
        color: #2f2a4f !important;
        letter-spacing: 0.02em;
    }

    h2, h3 {
        color: #2f2a4f !important;
        font-weight: 600 !important;
    }

    label[data-baseweb="typography"] {
        color: #5b5873 !important;
        font-weight: 500;
    }

    .card {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 18px 22px 22px 22px;
        box-shadow: 0 1px 8px rgba(0,0,0,0.04);
        border: 1px solid rgba(47, 42, 79, 0.08);
        margin-bottom: 1rem;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .stSelectbox > div > div {
        border-radius: 6px;
    }

    .coverage-label {
        margin-top: 0.25rem;
        margin-bottom: 1rem;
        font-size: 0.98rem;
        color: #2f2a4f;
        font-weight: 600;
    }

    .metric-row {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        margin-bottom: 1rem;
    }

    .metric-box {
        background: #f7f7fb;
        border: 1px solid rgba(47, 42, 79, 0.08);
        border-radius: 14px;
        padding: 12px 16px;
        min-width: 180px;
    }

    .metric-label {
        font-size: 0.86rem;
        color: #5b5873;
        margin-bottom: 4px;
    }

    .metric-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #2f2a4f;
    }

    .dataframe tbody tr th {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------
# Title
# --------------------------
st.markdown(
    "<h1>US Manufacturing Energy Classification: Unit Operations</h1>",
    unsafe_allow_html=True,
)

st.write("Select a NAICS Level 1 sector to generate a fact sheet.")

# --------------------------
# Dropdown
# --------------------------
selected_naics1 = st.selectbox(
    "NAICS Level 1",
    naics_level1_list,
    index=0,
)

df_filtered = df[df[NAICS_COL].astype(str).str.strip() == str(selected_naics1).strip()].copy()

# --------------------------
# Numeric cleanup
# --------------------------
numeric_cols = [BAR_PCT_COL, ELEC_COL, FUEL_COL, STEAM_COL]
if coverage_col_name is not None:
    numeric_cols.append(coverage_col_name)

for col in numeric_cols:
    if col in df_filtered.columns:
        df_filtered[col] = pd.to_numeric(df_filtered[col], errors="coerce")

# --------------------------
# Coverage calculation
# --------------------------
if coverage_col_name is not None and coverage_col_name in df_filtered.columns:
    coverage_series = df_filtered[coverage_col_name].dropna()

    if not coverage_series.empty:
        total_coverage = coverage_series.max()
        coverage_text = f"Total Sector Coverage of {selected_naics1}: {total_coverage:.2%}"
    else:
        coverage_text = f"Total Sector Coverage of {selected_naics1}: N/A"

    st.markdown(
        f'<div class="coverage-label">{coverage_text}</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="coverage-label">Total Sector Coverage of {selected_naics1}: N/A</div>',
        unsafe_allow_html=True,
    )

# --------------------------
# Summary metrics
# --------------------------
total_energy_pct = pd.to_numeric(df_filtered[BAR_PCT_COL], errors="coerce").fillna(0).sum()

total_electricity = (
    pd.to_numeric(df_filtered[ELEC_COL], errors="coerce").fillna(0).sum()
    if ELEC_COL in df_filtered.columns else 0
)
total_fuels = (
    pd.to_numeric(df_filtered[FUEL_COL], errors="coerce").fillna(0).sum()
    if FUEL_COL in df_filtered.columns else 0
)
total_steam = (
    pd.to_numeric(df_filtered[STEAM_COL], errors="coerce").fillna(0).sum()
    if STEAM_COL in df_filtered.columns else 0
)

st.markdown(
    f"""
    <div class="metric-row">
        <div class="metric-box">
            <div class="metric-label">Rows in fact sheet</div>
            <div class="metric-value">{len(df_filtered):,}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Summed energy share</div>
            <div class="metric-value">{total_energy_pct:.2%}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Electricity demand</div>
            <div class="metric-value">{total_electricity:,.2f} PJ</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Fuel demand</div>
            <div class="metric-value">{total_fuels:,.2f} PJ</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Steam / CHP demand</div>
            <div class="metric-value">{total_steam:,.2f} PJ</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------
# Prepare bar chart data
# --------------------------
temp_bar = df_filtered[[BAR_UNIT_COL, BAR_PCT_COL]].copy()
temp_bar[BAR_PCT_COL] = pd.to_numeric(temp_bar[BAR_PCT_COL], errors="coerce")

bar_df = (
    temp_bar.dropna(subset=[BAR_UNIT_COL, BAR_PCT_COL])
    .groupby(BAR_UNIT_COL, as_index=False)[BAR_PCT_COL]
    .sum()
    .rename(
        columns={
            BAR_UNIT_COL: "Unit Operation",
            BAR_PCT_COL: "Percent Energy",
        }
    )
)

# Remove exact zeros for cleaner chart
bar_df = bar_df[bar_df["Percent Energy"].fillna(0) != 0]

# --------------------------
# Prepare donut chart data from real workbook columns
# --------------------------
breakdown_df = pd.DataFrame(
    {
        "Type": ["Annual Fuels", "Annual Steam / CHP", "Annual Electricity"],
        "Value": [total_fuels, total_steam, total_electricity],
    }
)

breakdown_df = breakdown_df[breakdown_df["Value"].fillna(0) > 0]

# --------------------------
# Layout
# --------------------------
left_col, right_col = st.columns([1.0, 1.2])

with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Total Annual Energy Breakdown")

    if not breakdown_df.empty and breakdown_df["Value"].sum() > 0:
        fig_donut = px.pie(
            breakdown_df,
            names="Type",
            values="Value",
            hole=0.65,
        )
        fig_donut.update_traces(
            textinfo="percent+label",
            textposition="outside",
            marker=dict(colors=["#f7901d", "#3b4f9b", "#a3d5a4"]),
        )
        fig_donut.update_layout(
            showlegend=False,
            margin=dict(t=20, b=10, l=10, r=10),
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.write("No annual electricity, fuels, or steam/CHP demand data available for this NAICS Level 1 selection.")

    st.markdown("</div>", unsafe_allow_html=True)

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
        )
        fig_bar.update_traces(
            marker_color="#006b6b",
            text=bar_df_sorted["Percent Energy"],
            texttemplate="%{text:.1%}",
            textposition="outside",
        )
        fig_bar.update_layout(
            xaxis_title="Percent of Annual Energy",
            yaxis_title="",
            xaxis_tickformat=".0%",
            margin=dict(t=20, b=20, l=80, r=60),
            height=max(400, 28 * len(bar_df_sorted)),
        )

        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.write("No energy data available for this NAICS Level 1 selection.")

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------
# Optional top unit operations table
# --------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(f"Top Unit Operations – {selected_naics1}")

if not bar_df.empty:
    top_ops = (
        bar_df.sort_values("Percent Energy", ascending=False)
        .reset_index(drop=True)
        .copy()
    )
    top_ops["Percent Energy"] = top_ops["Percent Energy"].map(
        lambda x: f"{x:.2%}" if pd.notnull(x) else ""
    )
    st.dataframe(top_ops, use_container_width=True, hide_index=True)
else:
    st.write("No unit-operation summary available.")

st.markdown("</div>", unsafe_allow_html=True)

# --------------------------
# Fact sheet table
# --------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(f"Fact Sheet – {selected_naics1}")
st.dataframe(df_filtered, use_container_width=True, hide_index=True)
st.markdown("</div>", unsafe_allow_html=True)

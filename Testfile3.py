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
    # Row 0 is grouping headers; row 1 has actual field names (NAICS Level 1, etc.). [file:54]
    df = pd.read_excel(
        url,
        sheet_name="Process-level data",
        header=1,
    )
    df.columns = df.columns.map(str).str.strip()
    return df

df = load_data()

NAICS_COL = "NAICS Level 1"
BAR_UNIT_COL = "Unit operation Level 2 classification"
BAR_PCT_COL = "Percent Annual energy demand in 2022"
COVERAGE_COL = "Percent Coverage of NAICS 3-digit Sector"

if NAICS_COL not in df.columns:
    st.error(f"Column '{NAICS_COL}' not found. Columns are: {list(df.columns)}")
    st.stop()

# --------------------------
# Build NAICS Level 1 dropdown list
# --------------------------
naics_level1_list = (
    df[NAICS_COL]
    .dropna()
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
        font-weight: 500 !important;
    }

    .card {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 18px 22px 22px 22px;
        box-shadow: none;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .stSelectbox > div > div {
        border-radius: 4px;
    }

    .coverage-tag {
        display: inline-block;
        margin-top: 0.4rem;
        margin-bottom: 0.8rem;
        padding: 0.15rem 0.45rem;
        border-radius: 999px;
        background-color: #eef3ff;
        color: #2f2a4f;
        font-size: 0.8rem;
        font-weight: 500;
    }

    .dataframe tbody tr th {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------
# Title + NAICS filter
# --------------------------
st.markdown(
    "<h1>US Manufacturing Energy Classification: Unit Operations</h1>",
    unsafe_allow_html=True,
)

st.write("Select a NAICS Level 1 sector to generate a fact sheet.")

selected_naics1 = st.selectbox(
    "NAICS Level 1",
    naics_level1_list,
    index=0,
)

df_filtered = df[df[NAICS_COL] == selected_naics1]

# --------------------------
# Compute NAICS coverage tag
# --------------------------
coverage_text = None
if COVERAGE_COL in df_filtered.columns:
    # Use sum here; switch to max() if each NAICS appears once and you prefer that.
    coverage_value = df_filtered[COVERAGE_COL].dropna().sum()
    if pd.notna(coverage_value) and coverage_value != 0:
        coverage_text = f"Total coverage: {coverage_value:.1f}% of NAICS 3‑digit sector"
else:
    coverage_text = None

if coverage_text:
    st.markdown(
        f'<span class="coverage-tag">{coverage_text}</span>',
        unsafe_allow_html=True,
    )

# --------------------------
# Bar data from filtered rows
# --------------------------
if BAR_UNIT_COL in df_filtered.columns and BAR_PCT_COL in df_filtered.columns:
    bar_df = (
        df_filtered[[BAR_UNIT_COL, BAR_PCT_COL]]
        .dropna()
        .groupby(BAR_UNIT_COL, as_index=False)
        .sum()
        .rename(
            columns={
                BAR_UNIT_COL: "Unit Operation",
                BAR_PCT_COL: "Percent Energy",
            }
        )
    )
else:
    bar_df = pd.DataFrame(columns=["Unit Operation", "Percent Energy"])

# Simple placeholder donut data
breakdown_df = pd.DataFrame(
    {
        "Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
        "Value": [0.826, 0.169, 0.0051],
    }
)

# --------------------------
# Layout: donut + bar
# --------------------------
left_col, right_col = st.columns([1.05, 1.15])

with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Total Annual Energy Breakdown")

    fig_donut = px.pie(
        breakdown_df,
        names="Type",
        values="Value",
        hole=0.65,
    )
    fig_donut.update_traces(
        textinfo="percent",
        textposition="outside",
        marker=dict(colors=["#f7901d", "#3b4f9b", "#a3d5a4"]),
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
        bar_df_sorted = bar_df.sort_values("Percent Energy", ascending=True)

        fig_bar = px.bar(
            bar_df_sorted,
            x="Percent Energy",
            y="Unit Operation",
            orientation="h",
        )
        fig_bar.update_traces(
            marker_color="#006b6b",
            text=bar_df_sorted["Percent Energy"] / 100.0,
            texttemplate="%{text:.1%}",
            textposition="outside",
        )
        fig_bar.update_layout(
            xaxis_title="Percent of Annual Energy",
            yaxis_title="",
            xaxis_tickformat=".0%",
            margin=dict(t=20, b=20, l=80, r=60),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.write("No energy data available for this NAICS Level 1 selection.")

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------
# Bottom table – fact sheet
# --------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(f"Fact Sheet – {selected_naics1}")
st.dataframe(df_filtered, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="US Manufacturing Energy Classification: Unit Operations",
    layout="wide",
)

URL = "https://github.com/apatil210/LDRD2/raw/main/Modified%20Data%20for%20NAICS.xlsx"
SHEET_NAME = "Process-level data"

COLS = {
    "naics": "NAICS Level 1",
    "unit_l2": "Unit operation (Level 2 classification)",
    "pct_energy": "Percent Annual energy demand in 2022",
    "coverage": "Percent Coverage of NAICS (3-digit) Sector",
    "annual_energy": "Annual energy demand in 2022",
    "annual_electricity": "Annual electricity demand in 2022",
    "annual_fuels": "Annual fuels demand in 2022",
    "annual_steam": "Annual fuels or electricity for steam or steam from CHP demand in 2022",
}

def norm(x):
    return " ".join(str(x).replace("\n", " ").strip().split()).lower()

@st.cache_data
def load_data():
    df = pd.read_excel(URL, sheet_name=SHEET_NAME, header=1)
    df.columns = [str(c).strip() for c in df.columns]

    if len(df) > 0:
        first_row = " ".join([str(x) for x in df.iloc[0].fillna("").tolist()])
        if "GJ/FU" in first_row or "PJ" in first_row or "bara" in first_row:
            df = df.iloc[1:].copy()

    df = df.dropna(axis=1, how="all")
    return df

def resolve_columns(df):
    norm_map = {norm(c): c for c in df.columns}
    resolved = {}
    missing = []

    for k, expected in COLS.items():
        found = norm_map.get(norm(expected))
        if found is None:
            missing.append(expected)
        else:
            resolved[k] = found

    return resolved, missing

def num(s):
    return pd.to_numeric(s, errors="coerce").fillna(0)

def fmt_pj(x):
    return f"{x:,.2f} PJ"

df = load_data()
cols, missing = resolve_columns(df)

if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.write("Available columns:", list(df.columns))
    st.stop()

naics_col = cols["naics"]
unit_l2_col = cols["unit_l2"]
pct_energy_col = cols["pct_energy"]
coverage_col = cols["coverage"]
annual_energy_col = cols["annual_energy"]
annual_electricity_col = cols["annual_electricity"]
annual_fuels_col = cols["annual_fuels"]
annual_steam_col = cols["annual_steam"]

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
    h1, h2, h3 {
        color: #1e293b !important;
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

st.markdown(
    "<h1>US Manufacturing Energy Classification: Unit Operations</h1>",
    unsafe_allow_html=True,
)
st.write("Select a NAICS Level 1 sector to generate an energy fact sheet.")

naics_options = (
    df[naics_col]
    .dropna()
    .astype(str)
    .drop_duplicates()
    .sort_values()
    .tolist()
)

selected_naics = st.selectbox("NAICS Level 1", naics_options, index=0)

df_filtered = df[df[naics_col].astype(str) == str(selected_naics)].copy()

coverage_values = pd.to_numeric(df_filtered[coverage_col], errors="coerce").dropna()
coverage = coverage_values.max() if not coverage_values.empty else None

st.markdown(
    f'<div class="coverage-label">Total Sector Coverage of {selected_naics}: {coverage:.2%}</div>'
    if coverage is not None
    else f'<div class="coverage-label">Total Sector Coverage of {selected_naics}: N/A</div>',
    unsafe_allow_html=True,
)

total_energy = num(df_filtered[annual_energy_col]).sum()
total_electricity = num(df_filtered[annual_electricity_col]).sum()
total_fuels = num(df_filtered[annual_fuels_col]).sum()
total_steam = num(df_filtered[annual_steam_col]).sum()

m1, m2, m3, m4 = st.columns(4)
for col, label, value in [
    (m1, "Total annual energy", total_energy),
    (m2, "Annual electricity", total_electricity),
    (m3, "Annual fuels", total_fuels),
    (m4, "Annual steam", total_steam),
]:
    with col:
        st.markdown(
            f'<div class="card"><div class="metric-label">{label}</div><div class="metric-value">{fmt_pj(value)}</div></div>',
            unsafe_allow_html=True,
        )

breakdown_df = pd.DataFrame(
    {
        "Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
        "Value": [total_fuels, total_steam, total_electricity],
    }
)
breakdown_df = breakdown_df[breakdown_df["Value"] > 0].copy()

bar_df = df_filtered[[unit_l2_col, pct_energy_col]].copy()
bar_df[pct_energy_col] = pd.to_numeric(bar_df[pct_energy_col], errors="coerce")
bar_df = (
    bar_df.dropna(subset=[unit_l2_col, pct_energy_col])
    .groupby(unit_l2_col, as_index=False)[pct_energy_col]
    .sum()
    .rename(columns={unit_l2_col: "Unit Operation", pct_energy_col: "Percent Energy"})
)
bar_df = bar_df[bar_df["Percent Energy"] > 0].copy()

left_col, right_col = st.columns([1.0, 1.2])

with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Total Annual Energy Breakdown")

    if not breakdown_df.empty:
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
    else:
        st.info("No annual energy breakdown is available for this selection.")

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Percent Annual Energy by Unit Operation")

    if not bar_df.empty:
        bar_df = bar_df.sort_values("Percent Energy", ascending=True)
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
            margin=dict(t=20, b=20, l=80, r=70),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No unit-operation energy data is available for this selection.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(f"Fact Sheet – {selected_naics}")
st.dataframe(df_filtered, use_container_width=True, height=500)
st.markdown("</div>", unsafe_allow_html=True)

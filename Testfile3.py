import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="US Manufacturing Energy Classification: Unit Operations",
    layout="wide",
)

URL = "https://github.com/apatil210/LDRD2/raw/main/Modified%20Data%20for%20NAICS.xlsx"
SHEET_NAME = "Process-level data"

EXPECTED = {
    "naics": "NAICS Level 1",
    "unit_op_l2": "Unit operation Level 2 classification",
    "pct_energy": "Percent Annual energy demand in 2022",
    "coverage": "Percent Coverage of NAICS 3-digit Sector",
    "annual_energy": "Annual energy demand in 2022",
    "annual_electricity": "Annual electricity demand in 2022",
    "annual_fuels": "Annual fuels demand in 2022",
    "annual_steam": "Annual fuels or electricity for steam or steam from CHP demand in 2022",
}

def norm(x):
    return " ".join(str(x).strip().split()).lower()

@st.cache_data
def load_data():
    raw = pd.read_excel(URL, sheet_name=SHEET_NAME, header=None)

    header_row = None
    for i in range(min(10, len(raw))):
        vals = [norm(v) for v in raw.iloc[i].tolist()]
        if norm("NAICS Level 1") in vals and norm("Unit operation Level 2 classification") in vals:
            header_row = i
            break

    if header_row is None:
        st.error("Could not detect the real header row in the Excel sheet.")
        st.stop()

    headers = [str(x).strip() for x in raw.iloc[header_row].tolist()]
    df = raw.iloc[header_row + 1 :].copy()
    df.columns = headers
    df = df.dropna(axis=1, how="all")
    df.columns = [str(c).strip() for c in df.columns]

    return df

def resolve_columns(df):
    norm_map = {norm(c): c for c in df.columns}
    resolved = {}
    missing = []

    for key, label in EXPECTED.items():
        col = norm_map.get(norm(label))
        if col is None:
            missing.append(label)
        else:
            resolved[key] = col

    return resolved, missing

def to_num(s):
    return pd.to_numeric(s, errors="coerce").fillna(0)

def fmt_pj(x):
    return f"{x:,.2f} PJ"

df = load_data()
cols, missing = resolve_columns(df)

if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.write("Detected columns:", list(df.columns))
    st.stop()

naics_col = cols["naics"]
unit_col = cols["unit_op_l2"]
pct_col = cols["pct_energy"]
coverage_col = cols["coverage"]
annual_energy_col = cols["annual_energy"]
electricity_col = cols["annual_electricity"]
fuels_col = cols["annual_fuels"]
steam_col = cols["annual_steam"]

st.markdown(
    """
    <style>
    .stApp { font-family: "Inter", system-ui, sans-serif; background: #f8fafc; }
    .block-container { max-width: 1250px; padding-top: 1.25rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #1e293b !important; }
    .card {
        background: white; border: 1px solid #e2e8f0; border-radius: 16px;
        padding: 18px 20px; margin-bottom: 1rem;
    }
    .metric-label { color: #64748b; font-size: 0.9rem; }
    .metric-value { color: #0f172a; font-size: 1.35rem; font-weight: 700; }
    .coverage-label { margin: 0.4rem 0 1rem 0; font-weight: 600; color: #0f172a; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1>US Manufacturing Energy Classification: Unit Operations</h1>", unsafe_allow_html=True)
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

coverage_vals = pd.to_numeric(df_filtered[coverage_col], errors="coerce").dropna()
coverage = coverage_vals.max() if not coverage_vals.empty else None

st.markdown(
    f'<div class="coverage-label">Total Sector Coverage of {selected_naics}: {coverage:.2%}</div>'
    if coverage is not None else
    f'<div class="coverage-label">Total Sector Coverage of {selected_naics}: N/A</div>',
    unsafe_allow_html=True,
)

total_energy = to_num(df_filtered[annual_energy_col]).sum()
total_electricity = to_num(df_filtered[electricity_col]).sum()
total_fuels = to_num(df_filtered[fuels_col]).sum()
total_steam = to_num(df_filtered[steam_col]).sum()

c1, c2, c3, c4 = st.columns(4)
for c, label, value in [
    (c1, "Total annual energy", total_energy),
    (c2, "Annual electricity", total_electricity),
    (c3, "Annual fuels", total_fuels),
    (c4, "Annual steam", total_steam),
]:
    with c:
        st.markdown(
            f'<div class="card"><div class="metric-label">{label}</div><div class="metric-value">{fmt_pj(value)}</div></div>',
            unsafe_allow_html=True,
        )

breakdown_df = pd.DataFrame({
    "Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
    "Value": [total_fuels, total_steam, total_electricity],
})
breakdown_df = breakdown_df[breakdown_df["Value"] > 0]

bar_df = df_filtered[[unit_col, pct_col]].copy()
bar_df[pct_col] = pd.to_numeric(bar_df[pct_col], errors="coerce")
bar_df = (
    bar_df.dropna(subset=[unit_col, pct_col])
    .groupby(unit_col, as_index=False)[pct_col]
    .sum()
    .rename(columns={unit_col: "Unit Operation", pct_col: "Percent Energy"})
)
bar_df = bar_df[bar_df["Percent Energy"] > 0]

left, right = st.columns([1.0, 1.2])

with left:
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

with right:
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

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="US Manufacturing Energy Classification: Unit Operations", layout="wide")

SHEET_NAME = "Process-level data"
GITHUB_URL = "https://github.com/apatil210/LDRD2/raw/main/Modified%20Data%20for%20NAICS.xlsx"
LOCAL_FILE = "Modified-Data-for-NAICS.xlsx"

EXPECTED = {
    "naics_l1": "NAICS Level 1",
    "naics_l2": "NAICS Level 2",
    "industrial_process": "Industrial process",
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
    source = LOCAL_FILE if Path(LOCAL_FILE).exists() else GITHUB_URL
    df = pd.read_excel(source, sheet_name=SHEET_NAME, header=1)
    df.columns = [str(c).strip() for c in df.columns]

    if len(df) > 0:
        first_row = " ".join([str(x) for x in df.iloc[0].fillna("").tolist()])
        if "GJ/FU" in first_row or "PJ" in first_row or "bara" in first_row:
            df = df.iloc[1:].copy()

    df = df.dropna(axis=1, how="all").reset_index(drop=True)
    return df

def resolve_columns(df):
    norm_map = {norm(c): c for c in df.columns}
    resolved, missing = {}, []

    for k, expected in EXPECTED.items():
        found = norm_map.get(norm(expected))
        if found is None:
            for c in df.columns:
                cn = norm(c)
                if k == "coverage" and "percent coverage of naics" in cn and "sector" in cn:
                    found = c
                    break
                if k == "naics_l2" and cn.startswith("naics level 2"):
                    found = c
                    break
                if k == "naics_l1" and cn.startswith("naics level 1"):
                    found = c
                    break
                if k == "industrial_process" and "industrial process" in cn:
                    found = c
                    break
                if k == "annual_energy" and cn.startswith("annual energy demand in 2022"):
                    found = c
                    break
                if k == "annual_electricity" and cn.startswith("annual electricity demand in 2022"):
                    found = c
                    break
                if k == "annual_fuels" and cn.startswith("annual fuels demand in 2022"):
                    found = c
                    break
                if k == "annual_steam" and "annual fuels or electricity for steam" in cn and "demand in 2022" in cn:
                    found = c
                    break

        if found is None:
            missing.append(expected)
        else:
            resolved[k] = found

    return resolved, missing

def num(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)

def fmt_pj(x):
    return f"{x:,.2f} PJ"

def group_small_slices(df, label_col, value_col, top_n=8):
    df = df.copy()
    df = df[df[value_col] > 0].sort_values(value_col, ascending=False)

    if len(df) <= top_n:
        return df

    top = df.head(top_n).copy()
    other_sum = df.iloc[top_n:][value_col].sum()

    if other_sum > 0:
        top = pd.concat(
            [
                top,
                pd.DataFrame([{label_col: "Other", value_col: other_sum}])
            ],
            ignore_index=True
        )

    return top

df = load_data()
cols, missing = resolve_columns(df)

st.markdown(
    """
    <style>
    .stApp {
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background-color: #f8fafc;
    }
    .block-container {
        padding-top: 1.3rem;
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

st.markdown("<h1>US Manufacturing Energy Classification: NAICS</h1>", unsafe_allow_html=True)
st.write("Select a NAICS Level (3-digit code) sector to generate an energy fact sheet.")

if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.write("Available columns:", list(df.columns))
    st.stop()

naics_l1_col = cols["naics_l1"]
naics_l2_col = cols["naics_l2"]
industrial_process_col = cols["industrial_process"]
coverage_col = cols["coverage"]
annual_energy_col = cols["annual_energy"]
annual_electricity_col = cols["annual_electricity"]
annual_fuels_col = cols["annual_fuels"]
annual_steam_col = cols["annual_steam"]

naics_options = sorted(df[naics_l1_col].dropna().astype(str).drop_duplicates().tolist())
selected_naics = st.selectbox("NAICS Level 1", naics_options, index=0)

df_filtered = df[df[naics_l1_col].astype(str) == str(selected_naics)].copy()

coverage_values = pd.to_numeric(df_filtered[coverage_col], errors="coerce").dropna()
coverage = coverage_values.max() if not coverage_values.empty else None
coverage_text = f"{coverage:.2%}" if coverage is not None else "N/A"

st.markdown(
    f'<div class="coverage-label">Total Sector Coverage of {selected_naics}: {coverage_text}</div>',
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
        "Label": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
        "Value": [total_fuels, total_steam, total_electricity],
    }
)
breakdown_df = breakdown_df[breakdown_df["Value"] > 0].copy()

naics_df = df_filtered[[naics_l2_col, annual_energy_col]].copy()
naics_df[annual_energy_col] = pd.to_numeric(naics_df[annual_energy_col], errors="coerce")
naics_df = (
    naics_df.dropna(subset=[naics_l2_col, annual_energy_col])
    .groupby(naics_l2_col, as_index=False)[annual_energy_col]
    .sum()
    .rename(columns={naics_l2_col: "Label", annual_energy_col: "Value"})
)
naics_df = group_small_slices(naics_df, "Label", "Value", top_n=8)

process_df = df_filtered[[industrial_process_col, annual_energy_col]].copy()
process_df[annual_energy_col] = pd.to_numeric(process_df[annual_energy_col], errors="coerce")
process_df = (
    process_df.dropna(subset=[industrial_process_col, annual_energy_col])
    .groupby(industrial_process_col, as_index=False)[annual_energy_col]
    .sum()
    .rename(columns={industrial_process_col: "Label", annual_energy_col: "Value"})
)
process_df = group_small_slices(process_df, "Label", "Value", top_n=10)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(f"Multi-layer Donut Chart for {selected_naics}")

if not breakdown_df.empty and not naics_df.empty and not process_df.empty:
    fig = go.Figure()

    fig.add_trace(
        go.Pie(
            labels=breakdown_df["Label"],
            values=breakdown_df["Value"],
            name="Energy Type",
            hole=0.25,
            sort=False,
            direction="clockwise",
            domain={"x": [0.22, 0.78], "y": [0.22, 0.78]},
            textinfo="label+percent",
            textposition="inside",
            marker=dict(
                colors=["#f7901d", "#3b82f6", "#0f766e"],
                line=dict(color="white", width=2),
            ),
            showlegend=True,
        )
    )

    fig.add_trace(
        go.Pie(
            labels=naics_df["Label"],
            values=naics_df["Value"],
            name="NAICS Level 2",
            hole=0.55,
            sort=False,
            direction="clockwise",
            domain={"x": [0.12, 0.88], "y": [0.12, 0.88]},
            textinfo="label+percent",
            textposition="inside",
            marker=dict(
                colors=px.colors.qualitative.Set3[:len(naics_df)],
                line=dict(color="white", width=1.5),
            ),
            showlegend=True,
        )
    )

    fig.add_trace(
        go.Pie(
            labels=process_df["Label"],
            values=process_df["Value"],
            name="Industrial Process",
            hole=0.78,
            sort=False,
            direction="clockwise",
            domain={"x": [0.02, 0.98], "y": [0.02, 0.98]},
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value:.2f} PJ<br>%{percent}<extra>Industrial Process</extra>",
            marker=dict(
                colors=(px.colors.qualitative.Pastel + px.colors.qualitative.Safe)[:len(process_df)],
                line=dict(color="white", width=1),
            ),
            showlegend=True,
        )
    )

    fig.update_layout(
        height=850,
        margin=dict(t=40, b=20, l=20, r=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        annotations=[
            dict(
                text=f"<b>{selected_naics}</b><br>Total Energy<br>{total_energy:,.2f} PJ",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color="#0f172a"),
                align="center",
            )
        ],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5,
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption("Inner ring: energy type • Middle ring: NAICS Level 2 • Outer ring: industrial process")
else:
    st.info("Not enough data is available to render the multi-layer donut chart.")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
# st.subheader(f"Fact Sheet – {selected_naics}")
# st.dataframe(df_filtered, use_container_width=True, height=500)
st.markdown("</div>", unsafe_allow_html=True)

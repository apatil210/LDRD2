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

# Prefer exact header name, but fall back to column AM by position if needed.
# Excel column AM = 39th column = zero-based index 38.
COVERAGE_COL = "Percent Coverage of NAICS 3-digit Sector"
COVERAGE_COL_INDEX = 38

# --------------------------
# Validate required columns
# --------------------------
if NAICS_COL not in df.columns:
st.error(f"Column '{NAICS_COL}' not found. Columns are: {list(df.columns)}")
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

   .coverage-label {
       margin-top: 0.25rem;
       margin-bottom: 1rem;
       font-size: 0.98rem;
       color: #2f2a4f;
       font-weight: 600;
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

df_filtered = df[df[NAICS_COL].astype(str) == str(selected_naics1)].copy()

# --------------------------
# Coverage label below dropdown
# --------------------------
if coverage_col_name is not None:
coverage_series = pd.to_numeric(df_filtered[coverage_col_name], errors="coerce").fillna(0)
total_coverage = coverage_series.sum()

st.markdown(
        f'<div class="coverage-label">Total coverage: {total_coverage:.2%}</div>',
        f'<div class="coverage-label">Total Sector Coverage of str(selected_naics1): {total_coverage:.2%}</div>',
unsafe_allow_html=True,
)
else:
st.markdown(
'<div class="coverage-label">Total coverage: N/A</div>',
unsafe_allow_html=True,
)

# --------------------------
# Prepare bar chart data
# --------------------------
if BAR_UNIT_COL in df_filtered.columns and BAR_PCT_COL in df_filtered.columns:
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
else:
bar_df = pd.DataFrame(columns=["Unit Operation", "Percent Energy"])

# --------------------------
# Placeholder donut chart data
# --------------------------
breakdown_df = pd.DataFrame(
{
"Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
"Value": [0.826, 0.169, 0.0051],
}
)

# --------------------------
# Layout
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
text=bar_df_sorted["Percent Energy"],
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
# Fact sheet table
# --------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(f"Fact Sheet – {selected_naics1}")
st.dataframe(df_filtered, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

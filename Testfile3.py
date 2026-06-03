import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------
# Page config and THEME
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
    df = pd.read_excel(url, sheet_name="Process-level data")
    return df

df = load_data()

# Build NAICS Level 1 dropdown list (Column B)
naics_level1_list = (
    df["NAICS Level 1"]
    .dropna()
    .drop_duplicates()
    .sort_values()
    .tolist()
)

# --------------------------
# Custom CSS (no shadows, rectangular selectbox)
# --------------------------
st.markdown(
    """
    <style>
    /* Global font */
    .stApp {
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }

    /* Main title */
    h1 {
        font-weight: 700 !important;
        color: #2f2a4f !important;
        letter-spacing: 0.02em;
    }

    /* Subheaders */
    h2, h3 {
        color: #2f2a4f !important;
        font-weight: 600 !important;
    }

    /* Dropdown label */
    label[data-baseweb="typography"] {
        color: #5b5873 !important;
        font-weight: 500 !important;
    }

    /* Card containers – no shadow */
    .card {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 18px 22px 22px 22px;
        box-shadow: none;
    }

    /* Page padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Make selectbox rectangular */
    .stSelectbox > div > div {
        border-radius: 4px;
    }

    /* Table tweaks */
    .dataframe tbody tr th {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------
# Title + NAICS Level 1 filter
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

# Filter the dataframe by selected NAICS Level 1
df_filtered = df[df["NAICS Level 1"] == selected_naics1]

# --------------------------
# Build bar data from filtered rows
# using Unit operation Level 2 + Percent Annual energy demand in 2022
# --------------------------
if (
    "Unit operation Level 2 classification" in df_filtered.columns
    and "Percent Annual energy demand in 2022" in df_filtered.columns
):
    bar_df = (
        df_filtered[
            [
                "Unit operation Level 2 classification",
                "Percent Annual energy demand in 2022",
            ]
        ]
        .dropna()
        .groupby("Unit operation Level 2 classification", as_index=False)
        .sum()
        .rename(
            columns={
                "Unit operation Level 2 classification": "Unit Operation",
                "Percent Annual energy demand in 2022": "Percent Energy",
            }
        )
    )
else:
    bar_df = pd.DataFrame(columns=["Unit Operation", "Percent Energy"])

# Example donut data (placeholder – adjust fields if you have real ones)
breakdown_df = pd.DataFrame(
    {
        "Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
        "Value": [0.826, 0.169, 0.0051],
    }
)

# --------------------------
# Top row: donut + bar chart
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

st.dataframe(
    df_filtered,
    use_container_width=True,
)
st.markdown("</div>", unsafe_allow_html=True)

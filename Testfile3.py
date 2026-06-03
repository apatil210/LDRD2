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

# Custom CSS (no shadows, rectangular selectbox)
st.markdown(
    """
    <style>
    /* Global font */
    .stApp {
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
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

    /* Make selectbox rectangular (no pill) */
    .stSelectbox > div > div {
        border-radius: 6px;
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
# Mock data – replace this with your real data
# --------------------------
unit_operations = [
    "Cracking", "Reforming", "Distillation", "Drying", "HVAC",
    "Reduction", "Calcination", "Hydrotreating", "Evaporation",
    "Melting", "Blast furnace", "Pulping", "Coking", "Lighting",
    "Electrolysis", "Hydrocracking",
]
percent_energy = [8.6, 8.5, 8.3, 7.7, 4.4, 3.4, 2.7, 2.5, 2.0, 1.9, 1.4, 1.2, 1.2, 1.1, 1.0, 0.9]

bar_df = pd.DataFrame({"Unit Operation": unit_operations, "Percent Energy": percent_energy})

# Example donut-breakdown numbers (PJ/yr)
total_energy = 1424.44
breakdown_df = pd.DataFrame(
    {
        "Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
        "Value": [0.826 * total_energy, 0.169 * total_energy, 0.0051 * total_energy],
    }
)

# Example fact-sheet table
table_df = pd.DataFrame(
    {
        "List of Industry Application": ["Steam cracking-NGL", "Petroleum Refining"],
        "SEC Electricity (GJ/t)": ["None", 0.0011],
        "SEC Fuels (GJ/t)": [17.88, 0.0893],
        "SEC Steam (GJ/t)": [1.1829, 0.0332],
        "Efficiency": [0.9, "75–85%"],
    }
)

# --------------------------
# Title + filter row
# --------------------------
st.markdown(
    "<h1>US Manufacturing Energy Classification: Unit Operations</h1>",
    unsafe_allow_html=True,
)

st.write(
    "Select a unit operation (Level 2 classification) to generate a fact sheet."
)

selected_unit = st.selectbox(
    "",  # empty label to mimic screenshot
    unit_operations,
    index=0,
)

# --------------------------
# Top row: donut + bar chart
# --------------------------
left_col, right_col = st.columns([1.05, 1.15])

with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Total Annual Energy Breakdown")

    # Donut chart (orange ring, white center)
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
    # Center text (total)
    fig_donut.update_layout(
        showlegend=False,
        annotations=[
            dict(
                text=f"Total (PJ/yr)<br><b>{total_energy:.2f}</b>",
                x=0.5,
                y=0.5,
                font=dict(size=16, color="#333333"),
                showarrow=False,
            )
        ],
        margin=dict(t=20, b=10, l=10, r=10),
    )

    st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Percent Annual Energy by Unit Operation Classification")

    # Horizontal bar chart with teal bars, % labels on the right
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

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------
# Bottom table – fact sheet
# --------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Total Annual Energy Breakdown")

st.dataframe(
    table_df,
    use_container_width=True,
)
st.markdown("</div>", unsafe_allow_html=True)

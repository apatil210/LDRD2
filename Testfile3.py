import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NAICS Level 1 Coverage Chart", layout="wide")

st.title("Bar Chart: NAICS Level 1 vs Aggregate Percent Coverage")

github_url = "https://raw.githubusercontent.com/apatil210/LDRD2/main/Modified%20Data%20for%20NAICS.xlsx"

@st.cache_data
def load_data(url):
    df = pd.read_excel(url, sheet_name="Process-level data")
    return df

df = load_data(github_url)

st.subheader("Raw Data Preview")
st.dataframe(df.head())

# Column B = NAICS Level 1
# Column AM = Percent Coverage of NAICS 3-digit Sector
naics_col = df.columns[1]
coverage_col = df.columns[38]

plot_df = df[[naics_col, coverage_col]].copy()
plot_df.columns = ["NAICS Level 1", "Percent Coverage"]

plot_df["Percent Coverage"] = pd.to_numeric(plot_df["Percent Coverage"], errors="coerce")
plot_df = plot_df.dropna(subset=["NAICS Level 1", "Percent Coverage"])

agg_df = (
    plot_df.groupby("NAICS Level 1", as_index=False)["Percent Coverage"]
    .sum()
    .sort_values("Percent Coverage", ascending=False)
)

st.subheader("Aggregated Data")
st.dataframe(agg_df)

fig = px.bar(
    agg_df,
    x="NAICS Level 1",
    y="Percent Coverage",
    title="Aggregate Sum of Percent Coverage by NAICS Level 1",
    labels={
        "NAICS Level 1": "NAICS Level 1",
        "Percent Coverage": "Sum of Percent Coverage"
    },
    text="Percent Coverage"
)

fig.update_traces(
    texttemplate="%{y:.2%}",
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Percent Coverage: %{y:.2%}<extra></extra>"
)

fig.update_layout(
    xaxis_title="NAICS Level 1",
    yaxis_title="Sum of Percent Coverage (%)",
    yaxis_tickformat=".0%",
    xaxis_tickangle=-45,
    height=700
)

st.plotly_chart(fig, use_container_width=True)

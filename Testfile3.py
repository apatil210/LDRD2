import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Column B vs Column AM Bar Chart", layout="wide")

st.title("Bar Chart for Column B vs Column AM")

github_url = "https://raw.githubusercontent.com/apatil210/LDRD2/main/Modified%20Data%20for%20NAICS.xlsx"

@st.cache_data
def get_sheet_names(url):
    return pd.ExcelFile(url).sheet_names

@st.cache_data
def load_sheet(url, sheet_name):
    return pd.read_excel(url, sheet_name=sheet_name)

sheet_names = get_sheet_names(github_url)
sheet_name = st.selectbox("Select sheet", sheet_names)

df = load_sheet(github_url, sheet_name)

st.write("Preview of selected sheet:")
st.dataframe(df.head())

col_b_index = 1    # Excel Column B
col_am_index = 38  # Excel Column AM

if df.shape[1] <= col_am_index:
    st.error("This sheet does not have enough columns to access Column AM.")
else:
    x = df.iloc[:, col_b_index]
    y = pd.to_numeric(df.iloc[:, col_am_index], errors="coerce")

    plot_df = pd.DataFrame({
        "Column_B": x.astype(str),
        "Column_AM": y
    }).dropna()

    if plot_df.empty:
        st.warning("No valid numeric values found in Column AM for this sheet.")
    else:
        fig = px.bar(
            plot_df,
            x="Column_B",
            y="Column_AM",
            title=f"Bar Chart: Column B vs Column AM ({sheet_name})",
            labels={"Column_B": "Column B", "Column_AM": "Column AM"}
        )

        fig.update_layout(
            xaxis_title="Column B",
            yaxis_title="Column AM",
            xaxis_tickangle=-45,
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

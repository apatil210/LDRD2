import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Column B vs Column AM Bar Chart", layout="wide")

st.title("Bar Chart for Column B vs Column AM")

github_url = "https://raw.githubusercontent.com/apatil210/LDRD2/main/Modified%20Data%20for%20NAICS.xlsx"

@st.cache_data
def load_excel_data(url):
    xls = pd.ExcelFile(url)
    return xls

xls = load_excel_data(github_url)

sheet_name = st.selectbox("Select sheet", xls.sheet_names)

@st.cache_data
def load_sheet(url, sheet):
    return pd.read_excel(url, sheet_name=sheet)

df = load_sheet(github_url, sheet_name)

st.write("Preview of selected sheet:")
st.dataframe(df.head())

col_b_index = 1   # Column B
col_am_index = 38 # Column AM

if df.shape[1] <= col_am_index:
    st.error("This sheet does not have enough columns to access Column AM.")
else:
    x = df.iloc[:, col_b_index]
    y = df.iloc[:, col_am_index]

    plot_df = pd.DataFrame({
        "Column_B": x,
        "Column_AM": pd.to_numeric(y, errors="coerce")
    }).dropna()

    st.write("Data used for plotting:")
    st.dataframe(plot_df.head(20))

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

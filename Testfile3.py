import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Column B vs Column AM Bar Chart", layout="wide")

st.title("Bar Chart: Column B vs Column AM")

# Use the RAW GitHub file URL, not the github.com/blob URL
EXCEL_URL = "https://raw.githubusercontent.com/apatil210/LDRD2/main/Modified%20Data%20for%20NAICS.xlsx"


@st.cache_data
def get_excel_file(url):
    return pd.ExcelFile(url)


@st.cache_data
def load_sheet(url, sheet_name):
    return pd.read_excel(url, sheet_name=sheet_name)


try:
    xls = get_excel_file(EXCEL_URL)
    sheet_names = xls.sheet_names
except Exception as e:
    st.error(f"Could not load the Excel file from GitHub: {e}")
    st.stop()

sheet_name = st.selectbox("Select sheet", sheet_names)

try:
    df = load_sheet(EXCEL_URL, sheet_name)
except Exception as e:
    st.error(f"Could not read the selected sheet: {e}")
    st.stop()

st.subheader("Sheet Preview")
st.dataframe(df.head())

# Excel column positions:
# B  = index 1
# AM = index 38
col_b_index = 1
col_am_index = 38

if df.shape[1] <= col_am_index:
    st.error(
        f"The selected sheet '{sheet_name}' does not have enough columns for Column AM. "
        f"It has only {df.shape[1]} columns."
    )
    st.stop()

x_series = df.iloc[:, col_b_index]
y_series = df.iloc[:, col_am_index]

x_name = df.columns[col_b_index]
y_name = df.columns[col_am_index]

plot_df = pd.DataFrame({
    "Column_B": x_series,
    "Column_AM": pd.to_numeric(y_series, errors="coerce")
})

plot_df = plot_df.dropna(subset=["Column_B", "Column_AM"])

# Optional filter for cleaner chart
remove_blank = st.checkbox("Remove blank labels", value=True)
if remove_blank:
    plot_df = plot_df[plot_df["Column_B"].astype(str).str.strip() != ""]

sort_values = st.checkbox("Sort by Column AM", value=False)
if sort_values:
    plot_df = plot_df.sort_values("Column_AM", ascending=False)

st.subheader("Data Used for Chart")
st.dataframe(plot_df)

fig = px.bar(
    plot_df,
    x="Column_B",
    y="Column_AM",
    title=f"Bar Chart for {sheet_name}: Column B vs Column AM",
    labels={
        "Column_B": f"Column B ({x_name})",
        "Column_AM": f"Column AM ({y_name})"
    }
)

fig.update_layout(
    xaxis_title=f"Column B ({x_name})",
    yaxis_title=f"Column AM ({y_name})",
    xaxis_tickangle=-45,
    height=650
)

st.plotly_chart(fig, use_container_width=True)

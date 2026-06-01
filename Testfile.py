from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.io as pio
import requests
import streamlit as st

st.set_page_config(
    page_title="Energy Classification: Industrial Process",
    layout="wide"
)

pio.templates.default = "plotly"

DATA_URL = "https://raw.githubusercontent.com/apatil210/LDRD2/main/Modified%20Data.xlsx"

TEXT_COLOR = "#14212B"
PAPER_BG = "rgba(0,0,0,0)"
PLOT_BG = "rgba(0,0,0,0)"
BAR_COLOR = "#0B6E74"


@st.cache_data(show_spinner=False)
def load_excel(url: str) -> pd.DataFrame:
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")
    if "text/html" in content_type.lower():
        raise ValueError("URL returned an HTML page instead of an Excel file.")

    raw_df = pd.read_excel(
        BytesIO(response.content),
        sheet_name="Process-level data",
        header=None,
        engine="openpyxl"
    )

    header_row_idx = 1
    df = raw_df.iloc[header_row_idx + 2:].copy()
    df.columns = raw_df.iloc[header_row_idx].astype(str).str.strip()
    df = df.reset_index(drop=True)

    return df


def clean_category(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
    )


def prepare_bar_data(df: pd.DataFrame) -> pd.DataFrame:
    category_col = "Industrial process"
    value_col = "Percent Annual energy demand in 2022"

    df_work = df[[category_col, value_col]].copy()
    df_work[category_col] = clean_category(df_work[category_col])
    df_work[value_col] = pd.to_numeric(df_work[value_col], errors="coerce").fillna(0)

    df_agg = (
        df_work.groupby(category_col, as_index=False)[value_col]
        .sum()
        .sort_values(value_col, ascending=False)
        .reset_index(drop=True)
    )

    df_agg = df_agg[df_agg[value_col] > 0].copy()
    df_agg["Display Percent"] = df_agg[value_col] * 100
    df_agg["Rank"] = range(1, len(df_agg) + 1)

    return df_agg


def build_bar_chart(df: pd.DataFrame):
    fig = px.bar(
        df,
        x="Display Percent",
        y="Industrial process",
        orientation="h",
        text="Display Percent",
        color_discrete_sequence=[BAR_COLOR]
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Percent annual energy: %{x:.2f}%<extra></extra>"
        ),
        marker=dict(line=dict(color="#FCFCFA", width=1.2))
    )

    fig.update_layout(
        title="Percent Annual Energy by Industrial Process",
        height=max(700, 28 * len(df)),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        margin=dict(t=60, l=10, r=40, b=20),
        xaxis_title="Percent Annual Energy Demand in 2022 (%)",
        yaxis_title="Industrial Process",
        font=dict(
            family="Arial, sans-serif",
            color=TEXT_COLOR,
            size=14
        )
    )

    fig.update_xaxes(ticksuffix="%", showgrid=True)
    fig.update_yaxes(categoryorder="total ascending")

    return fig


def build_fact_sheet(df: pd.DataFrame, selected_process: str):
    process_col = "Industrial process"
    production_col = "Annual production in 2022\n(based on FU)"
    elec_col = "SEC \nelectricity"
    fuel_col = "SEC \nfuels"
    steam_col = "SEC \nfuels or electricity for steam or steam from CHP"

    fact_df = df.copy()
    fact_df[process_col] = clean_category(fact_df[process_col])

    for col in [production_col, elec_col, fuel_col, steam_col]:
        fact_df[col] = pd.to_numeric(fact_df[col], errors="coerce")

    selected_df = fact_df[fact_df[process_col] == selected_process].copy()

    if selected_df.empty:
        return None

    production_values = (
        selected_df[production_col]
        .dropna()
        .loc[lambda s: s != 0]
        .unique()
    )
    annual_production = production_values[0] if len(production_values) > 0 else 0

    sec_electricity = selected_df[elec_col].fillna(0).sum()
    sec_fuels = selected_df[fuel_col].fillna(0).sum()
    sec_steam = selected_df[steam_col].fillna(0).sum()

    detail_df = selected_df[
        [process_col, production_col, elec_col, fuel_col, steam_col]
    ].rename(columns={
        process_col: "Industrial Process",
        production_col: "Annual Production",
        elec_col: "SEC Electricity",
        fuel_col: "SEC Fuels",
        steam_col: "SEC Steam"
    })

    return {
        "Annual Production": annual_production,
        "SEC Electricity": sec_electricity,
        "SEC Fuels": sec_fuels,
        "SEC Steam": sec_steam,
        "Rows": selected_df.shape[0],
        "Details": detail_df
    }


st.title("Energy Classification: Industrial Process")

try:
    df = load_excel(DATA_URL)
    bar_df = prepare_bar_data(df)

    st.subheader("Percent Annual Energy by Industrial Process")
    st.plotly_chart(
        build_bar_chart(bar_df),
        use_container_width=True,
        theme=None,
        config={
            "displayModeBar": False,
            "scrollZoom": False
        }
    )

    selected_process = st.selectbox(
        "Select an industrial process to generate a fact sheet",
        bar_df["Industrial process"].tolist()
    )

    fact_sheet = build_fact_sheet(df, selected_process)

    if fact_sheet:
        st.subheader(f"Fact Sheet: {selected_process}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Annual Production", f"{fact_sheet['Annual Production']:.2f}")
        c2.metric("SEC Electricity", f"{fact_sheet['SEC Electricity']:.2f}")
        c3.metric("SEC Fuels", f"{fact_sheet['SEC Fuels']:.2f}")
        c4.metric("SEC Steam", f"{fact_sheet['SEC Steam']:.2f}")

        st.caption(f"Underlying rows used: {fact_sheet['Rows']}")

        st.dataframe(
            fact_sheet["Details"],
            use_container_width=True,
            hide_index=True
        )

    st.subheader("Bar Chart Data")
    table_df = bar_df[["Rank", "Industrial process", "Display Percent"]].rename(
        columns={
            "Industrial process": "Industrial Process",
            "Display Percent": "Percent Annual Energy (%)"
        }
    )

    st.dataframe(
        table_df.style.format({"Percent Annual Energy (%)": "{:.2f}%"}),
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error(f"App error: {e}")

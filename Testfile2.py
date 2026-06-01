import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Figure 3", layout="wide")

file_url = "https://raw.githubusercontent.com/apatil210/LDRD/main/Figure3Data.xlsx"
value_cols = ["Electricity", "Fuel", "Steam"]
THRESHOLD_PCT = 5.0

BG_COLOR = "white"
PAPER_BG = "white"
PLOT_BG = "white"
TEXT_COLOR = "#111111"
DIVIDER_COLOR = "#F7F5F1"
LABEL_SIZE = 14

st.markdown(
    f"""
    <style>
    .stApp {{
         background-color: {BG_COLOR};
    }}
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data
def load_data(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return pd.read_excel(BytesIO(response.content), engine="openpyxl")


def make_labels(df_in, value_col, threshold_pct=1.0):
    out = df_in.copy()
    out = out[out[value_col] > 0].copy()

    total = out[value_col].sum()
    if total > 0:
        out["Share_pct"] = 100 * out[value_col] / total
    else:
        out["Share_pct"] = 0

    out["Display_text"] = out.apply(
        lambda r: f"<b>{r['Category_clean']}</b><br>{r['Share_pct']:.1f}%"
        if r["Share_pct"] > threshold_pct else "",
        axis=1
    )

    out_treemap = out[out["Share_pct"] > threshold_pct].copy().reset_index(drop=True)
    out_all = out.sort_values(value_col, ascending=False).reset_index(drop=True)

    return out_treemap, out_all


try:
    df = load_data(file_url)
except Exception as e:
    st.error(f"Failed to load Excel file: {e}")
    st.stop()

required_columns = {"Category", "Electricity", "Fuel", "Steam"}
if not required_columns.issubset(df.columns):
    st.error(f"Excel file must contain these columns: {required_columns}")
    st.write("Columns found:", list(df.columns))
    st.stop()

df_agg = df.groupby("Category", as_index=False)[value_cols].sum()
df_agg["Category_clean"] = (
    df_agg["Category"].astype(str).str.replace("_", " ", regex=False).str.strip()
)
df_agg = df_agg[(df_agg[value_cols] > 0).any(axis=1)].copy()

if df_agg.empty:
    st.warning("No positive values found for Electricity, Fuel, or Steam.")
    st.stop()

base_palette = [
    "#147A7E",
    "#447DA1",
    "#5A9C57",
    "#9B6634",
    "#B22373",
    "#3CA996",
    "#7A38A2",
    "#B87434",
    "#6E9A10",
    "#5D67A8",
]

categories = df_agg["Category_clean"].tolist()
palette = (base_palette * ((len(categories) // len(base_palette)) + 1))[:len(categories)]
color_map = dict(zip(categories, palette))

elec_tree, elec_all = make_labels(df_agg, "Electricity", THRESHOLD_PCT)
fuel_tree, fuel_all = make_labels(df_agg, "Fuel", THRESHOLD_PCT)
steam_tree, steam_all = make_labels(df_agg, "Steam", THRESHOLD_PCT)

fig = make_subplots(
    rows=1,
    cols=3,
    specs=[[{"type": "domain"}, {"type": "domain"}, {"type": "domain"}]],
    subplot_titles=("Electricity (>5%)", "Fuel (>5%)", "Steam (>5%)")
)

common_textfont = dict(
    size=LABEL_SIZE,
    color=TEXT_COLOR,
    family="Arial, sans-serif"
)

common_hovertemplate = (
    "<b>%{label}</b><br>"
    "Value: %{customdata[1]:.3f}<br>"
    "Share: %{customdata[0]:.2f}%"
    "<extra></extra>"
)

fig.add_trace(
    go.Treemap(
        labels=elec_tree["Category_clean"],
        parents=[""] * len(elec_tree),
        values=elec_tree["Electricity"],
        customdata=elec_tree[["Share_pct", "Electricity", "Display_text"]].values,
        texttemplate="%{customdata[2]}",
        textposition="middle center",
        textfont=common_textfont,
        marker=dict(
            colors=[color_map[c] for c in elec_tree["Category_clean"]],
            line=dict(color=DIVIDER_COLOR, width=6),
            cornerradius=10
        ),
        tiling=dict(pad=5, squarifyratio=1.0),
        hovertemplate=common_hovertemplate,
        hoverlabel=dict(
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#D8D2C8",
            font=dict(color="#222222", size=14)
        ),
        branchvalues="total",
        pathbar=dict(visible=False),
        name="Electricity"
    ),
    row=1,
    col=1
)

fig.add_trace(
    go.Treemap(
        labels=fuel_tree["Category_clean"],
        parents=[""] * len(fuel_tree),
        values=fuel_tree["Fuel"],
        customdata=fuel_tree[["Share_pct", "Fuel", "Display_text"]].values,
        texttemplate="%{customdata[2]}",
        textposition="middle center",
        textfont=common_textfont,
        marker=dict(
            colors=[color_map[c] for c in fuel_tree["Category_clean"]],
            line=dict(color=DIVIDER_COLOR, width=6),
            cornerradius=10
        ),
        tiling=dict(pad=5, squarifyratio=1.0),
        hovertemplate=common_hovertemplate,
        hoverlabel=dict(
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#D8D2C8",
            font=dict(color="#222222", size=14)
        ),
        branchvalues="total",
        pathbar=dict(visible=False),
        name="Fuel"
    ),
    row=1,
    col=2
)

fig.add_trace(
    go.Treemap(
        labels=steam_tree["Category_clean"],
        parents=[""] * len(steam_tree),
        values=steam_tree["Steam"],
        customdata=steam_tree[["Share_pct", "Steam", "Display_text"]].values,
        texttemplate="%{customdata[2]}",
        textposition="middle center",
        textfont=common_textfont,
        marker=dict(
            colors=[color_map[c] for c in steam_tree["Category_clean"]],
            line=dict(color=DIVIDER_COLOR, width=6),
            cornerradius=10
        ),
        tiling=dict(pad=5, squarifyratio=1.0),
        hovertemplate=common_hovertemplate,
        hoverlabel=dict(
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#D8D2C8",
            font=dict(color="#222222", size=14)
        ),
        branchvalues="total",
        pathbar=dict(visible=False),
        name="Steam"
    ),
    row=1,
    col=3
)

fig.update_annotations(
    font=dict(size=18, color="#333333", family="Arial, sans-serif")
)

fig.update_layout(
    paper_bgcolor=PAPER_BG,
    plot_bgcolor=PLOT_BG,
    margin=dict(t=50, l=10, r=10, b=10),
    height=760,
    font=dict(color=TEXT_COLOR, family="Arial, sans-serif"),
    uniformtext=dict(minsize=LABEL_SIZE, mode="hide")
)

st.title("Unit Operations by Energy Source")

# st.subheader("For Categories > 1%")
st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displayModeBar": False}
)

st.subheader("Table of All Categories")
table_df = df_agg.copy()

for col in value_cols:
    total = table_df[col].sum()
    share_col = f"{col} Share (%)"
    table_df[share_col] = 100 * table_df[col] / total if total > 0 else 0

table_df = table_df[
    [
        "Category_clean",
        "Electricity", "Electricity Share (%)",
        "Fuel", "Fuel Share (%)",
        "Steam", "Steam Share (%)"
    ]
].rename(columns={"Category_clean": "Category"})

st.dataframe(table_df, use_container_width=True, hide_index=True)

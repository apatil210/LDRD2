import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.graph_objects as go

st.set_page_config(
    page_title="US Manufacturing Energy",
    page_icon="⚙️",
    layout="wide"
)

file_url = "https://raw.githubusercontent.com/apatil210/LDRD/main/Figure1Data.xlsx"

base_color = "#0F766E"
accent_color = "#0B5E55"
stem_color = "#C7D2CF"
bg_color = "#F4F7F6"
card_color = "#FFFFFF"
text_color = "#132A2E"
muted_text = "#5B6B73"
border_color = "rgba(19, 42, 46, 0.08)"

st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(15,118,110,0.06), transparent 28%),
            linear-gradient(180deg, #F7FAF9 0%, #EEF4F2 100%);
    }

    .block-container {
        max-width: 1380px;
        padding-top: 2rem;
        padding-bottom: 2.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    .top-badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        background: rgba(15, 118, 110, 0.10);
        border: 1px solid rgba(15, 118, 110, 0.12);
        color: #0F766E;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        margin-bottom: 0.9rem;
    }

    .hero-shell {
        background: rgba(255,255,255,0.82);
        border: 1px solid rgba(19, 42, 46, 0.07);
        border-radius: 26px;
        padding: 1.6rem 1.7rem 1.3rem 1.7rem;
        box-shadow: 0 12px 30px rgba(16, 24, 40, 0.06);
        backdrop-filter: blur(8px);
        margin-bottom: 1rem;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 1.6fr 0.9fr;
        gap: 1rem;
        align-items: end;
    }

    .hero-title {
        font-size: 2.35rem;
        line-height: 1.05;
        font-weight: 850;
        letter-spacing: -0.03em;
        color: #102A43;
        margin: 0 0 0.45rem 0;
    }

    .hero-subtitle {
        font-size: 1.02rem;
        line-height: 1.55;
        color: #52606D;
        max-width: 62ch;
        margin: 0;
    }

    .hero-note {
        background: linear-gradient(180deg, #FBFDFC 0%, #F5F9F8 100%);
        border: 1px solid rgba(15, 118, 110, 0.10);
        border-radius: 20px;
        padding: 1rem 1rem 0.9rem 1rem;
    }

    .hero-note-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #0F766E;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }

    .hero-note-text {
        font-size: 0.96rem;
        color: #48616A;
        line-height: 1.5;
        margin: 0;
    }

    .section-title {
        font-size: 1.05rem;
        font-weight: 750;
        color: #17354A;
        margin: 0.25rem 0 0.8rem 0.1rem;
        letter-spacing: -0.01em;
    }

    .metric-row {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.9rem;
        margin: 0.35rem 0 1.15rem 0;
    }

    .metric-card {
        background: rgba(255,255,255,0.86);
        border: 1px solid rgba(19, 42, 46, 0.07);
        border-radius: 20px;
        padding: 1rem 1rem 0.95rem 1rem;
        box-shadow: 0 10px 24px rgba(16, 24, 40, 0.045);
    }

    .metric-label {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #6B7C85;
        margin-bottom: 0.45rem;
        font-weight: 700;
    }

    .metric-value {
        font-size: 1.55rem;
        line-height: 1.1;
        font-weight: 800;
        color: #102A43;
        margin-bottom: 0.25rem;
    }

    .metric-sub {
        font-size: 0.92rem;
        color: #5B6B73;
    }

    .chart-card {
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(19, 42, 46, 0.08);
        border-radius: 24px;
        padding: 1rem 1rem 0.7rem 1rem;
        box-shadow: 0 14px 36px rgba(16, 24, 40, 0.055);
    }

    .chart-head {
        display: flex;
        justify-content: space-between;
        align-items: end;
        gap: 1rem;
        padding: 0.25rem 0.25rem 0.8rem 0.25rem;
    }

    .chart-title {
        font-size: 1.08rem;
        font-weight: 800;
        color: #17354A;
        margin: 0;
        letter-spacing: -0.01em;
    }

    .chart-caption {
        font-size: 0.93rem;
        color: #64748B;
        margin: 0.15rem 0 0 0;
    }

    .chart-chip {
        white-space: nowrap;
        padding: 0.45rem 0.7rem;
        border-radius: 999px;
        background: #F2F7F6;
        border: 1px solid rgba(15,118,110,0.08);
        color: #33545B;
        font-size: 0.82rem;
        font-weight: 700;
    }

    [data-testid="stVerticalBlock"] div[style*="overflow"]::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    [data-testid="stVerticalBlock"] div[style*="overflow"]::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #BFD0CC 0%, #8EAAA3 100%);
        border-radius: 999px;
    }

    [data-testid="stVerticalBlock"] div[style*="overflow"]::-webkit-scrollbar-track {
        background: #ECF2F0;
        border-radius: 999px;
    }

    @media (max-width: 900px) {
        .hero-grid {
            grid-template-columns: 1fr;
        }

        .metric-row {
            grid-template-columns: 1fr;
        }

        .hero-title {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return pd.read_excel(BytesIO(response.content), engine="openpyxl")


try:
    df = load_data(file_url)
except Exception as e:
    st.error(f"Failed to load Excel file: {e}")
    st.stop()

required_columns = {"Category", "Data"}
if not required_columns.issubset(df.columns):
    st.error(f"Excel file must contain these columns: {required_columns}")
    st.write("Columns found:", list(df.columns))
    st.stop()

df_agg = (
    df.groupby("Category", as_index=False)["Data"]
      .sum()
)

df_agg = df_agg[df_agg["Data"] > 0].copy()
df_agg = df_agg.sort_values("Data", ascending=True).reset_index(drop=True)

if df_agg.empty:
    st.warning("No positive data values found after aggregation.")
    st.stop()

categories = df_agg["Category"]
values = df_agg["Data"]

top_category = df_agg.iloc[-1]["Category"]
top_value = df_agg.iloc[-1]["Data"]
total_categories = len(df_agg)
avg_share = df_agg["Data"].mean()

st.markdown(f"""
<div class="hero-shell">
    <div class="top-badge">Manufacturing energy profile</div>
    <div class="hero-grid">
        <div>
            <div class="hero-title">US Manufacturing Energy by Unit Operation</div>
            <p class="hero-subtitle">
                A cleaner view of aggregated manufacturing energy use by category,
                presented as a scrollable lollipop chart for easier comparison across
                many unit operations.
            </p>
        </div>
        <div class="hero-note">
            <div class="hero-note-label">Reading guide</div>
            <p class="hero-note-text">
                Larger markers indicate a higher share of total energy use.
                Scroll within the chart panel to explore the full ranked list.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="metric-row">
    <div class="metric-card">
        <div class="metric-label">Categories</div>
        <div class="metric-value">{total_categories}</div>
        <div class="metric-sub">Positive categories included after aggregation</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Largest share</div>
        <div class="metric-value">{top_value:.1%}</div>
        <div class="metric-sub">{top_category}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Average share</div>
        <div class="metric-value">{avg_share:.1%}</div>
        <div class="metric-sub">Mean share across displayed categories</div>
    </div>
</div>
""", unsafe_allow_html=True)

fig = go.Figure()

for cat, val in zip(categories, values):
    fig.add_shape(
        type="line",
        x0=0,
        y0=cat,
        x1=val,
        y1=cat,
        line=dict(color=stem_color, width=4)
    )

fig.add_trace(
    go.Scatter(
        x=values,
        y=categories,
        mode="markers+text",
        text=[f"{v:.1%}" for v in values],
        textposition="middle right",
        textfont=dict(size=13, color=text_color),
        marker=dict(
            size=30,
            color=base_color,
            line=dict(color="white", width=2),
            symbol="circle"
        ),
        hovertemplate="<b>%{y}</b><br>Share: %{x:.1%}<extra></extra>"
    )
)

chart_height = max(880, 38 * len(categories))

fig.update_layout(
    height=chart_height,
    showlegend=False,
    plot_bgcolor=card_color,
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=20, b=30, l=240, r=130),
    font=dict(size=13, color=text_color),
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="rgba(19,42,46,0.12)",
        font=dict(color=text_color, size=13)
    )
)

fig.update_xaxes(
    title_text="Share of manufacturing energy use",
    title_font=dict(size=13, color=muted_text),
    tickformat=".0%",
    tickfont=dict(size=12, color=muted_text),
    showgrid=True,
    gridcolor="#DCE6E3",
    gridwidth=1,
    zeroline=False,
    automargin=True
)

fig.update_yaxes(
    title_text="",
    tickfont=dict(size=12, color=text_color),
    automargin=True
)

st.markdown("""
<div class="chart-card">
    <div class="chart-head">
        <div>
            <div class="chart-title">Category shares</div>
            <div class="chart-caption">
                Ranked lollipop chart of aggregated energy shares by unit-operation category
            </div>
        </div>
        <div class="chart-chip">Scrollable chart panel</div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.container(height=720):
    st.plotly_chart(
        fig,
        width="stretch",
        key="scrollable_lollipop",
        config={
            "scrollZoom": False,
            "displayModeBar": True
        }
    )

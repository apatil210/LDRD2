import streamlit as st

st.set_page_config(page_title="Industrial Energy Modeling", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500&display=swap');

    .stApp {
        background: #f2f2f2;
    }

    .block-container {
        max-width: 1280px;
        padding-top: 3.5rem;
        padding-bottom: 1.2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(1.6rem, 1.1rem + 1.2vw, 2.3rem);
        font-weight: 800;
        line-height: 1.12;
        letter-spacing: -0.03em;
        text-align: center;
        color: #101828;
        margin: 0.5rem 0 1.5rem 0;
    }

    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(1.35rem, 1.05rem + 0.7vw, 1.9rem);
        font-weight: 800;
        line-height: 1.15;
        color: #101828;
        margin: 0 0 0.7rem 0;
    }

    .body-copy {
        font-family: 'Source Serif 4', serif;
        font-size: clamp(1rem, 0.96rem + 0.2vw, 1.15rem);
        line-height: 1.55;
        color: #1f2937;
        margin-bottom: 1.8rem;
    }

    .contributors-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(1.2rem, 1rem + 0.5vw, 1.55rem);
        font-weight: 800;
        color: #101828;
        margin-top: 1.2rem;
        margin-bottom: 0.2rem;
    }

    .contributors-names {
        font-family: 'Inter', sans-serif;
        font-size: clamp(1rem, 0.96rem + 0.2vw, 1.2rem);
        color: #101828;
        margin-bottom: 0.15rem;
    }

    .contributors-affiliation {
        font-family: 'Inter', sans-serif;
        font-size: clamp(0.98rem, 0.94rem + 0.15vw, 1.12rem);
        color: #101828;
        font-style: italic;
    }

    .nav-card {
        background: #2d658f;
        border: 2px solid #1d4868;
        color: white;
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-size: clamp(1rem, 0.95rem + 0.2vw, 1.3rem);
        font-weight: 500;
        line-height: 1.2;
        min-height: 88px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.9rem 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        margin: 0.5rem auto 1rem auto;
        max-width: 240px;
    }

    div[data-testid="column"] {
        display: flex;
        justify-content: center;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 2.2rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero-title {
            margin-top: 0.25rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-title">Industrial Energy Modeling through Mapping Unit Operation Energy Demand</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Project Statement</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="body-copy">
    The term 'industry' refers to a wide range of thermodynamic, mechanical, and chemical processes that transform materials, each involving distinct unit operations. While these processes vary in terms of the number, sequence, and type of unit operations, common operations such as drying, distillation, and compression are shared across sectors. However, the breakdown of industrial energy demand by these unit operations has remained poorly established. Moreover, industrial models at the level of unit operations are scarce. If developed, these models could ultimately serve as fundamental building blocks for system-level industrial process and facility design and optimization. Current frameworks such as the North American Industry Classification System (NAICS) categorize industrial activities based on what they produce (e.g., chemicals, food, metals), not how they use energy, creating silos of subsectors when conducting energy-related analyses. Our work developed a comprehensive analytical framework to analyze energy demand in industrial processes at the unit-operation level. The initial workflow involved gathering data for industrial processes representing nearly two-thirds of U.S. manufacturing and analyzing energy demand profiles by disaggregating these processes into unit operations. Clustering and ranking unit operations by energy demand to identify priority areas for technological advancements that offer the greatest competitive advantage. The overarching goal is to build a novel approach for characterizing US industrial sector, one that is based on unit operations.
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown('<div class="nav-card">Industry Data</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="nav-card">Unit Operation<br>Data</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="nav-card">NAICS Sector<br>Coverage</div>', unsafe_allow_html=True)

st.markdown('<div class="contributors-title">Contributors:</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="contributors-names">Akash Patil, M. Jibran S. Zuberi, Prakash Rao, Unique Karki</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="contributors-affiliation">Lawrence Berkeley National Laboratory, Berkeley, CA 94720</div>',
    unsafe_allow_html=True,
)

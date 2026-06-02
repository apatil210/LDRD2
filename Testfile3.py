import streamlit as st

st.set_page_config(
    page_title="Industrial Energy Modeling",
    layout="wide"
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp {
        background: #ffffff;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 0.8rem;
        padding-bottom: 0.8rem;
        padding-left: 1.6rem;
        padding-right: 1.6rem;
    }

    .page-shell {
        min-height: calc(100vh - 2rem);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        gap: 0.7rem;
    }

    .title-wrap {
        text-align: center;
        padding-top: 0.1rem;
    }

    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(1.45rem, 1rem + 1vw, 2.15rem);
        font-weight: 800;
        line-height: 1.08;
        letter-spacing: -0.03em;
        color: #101828;
        margin: 0;
        text-wrap: balance;
    }

    .content-grid {
        display: grid;
        grid-template-columns: 1.9fr 0.95fr;
        gap: 1.35rem;
        align-items: start;
    }

    .statement-panel {
        padding-right: 0.1rem;
    }

    .eyebrow {
        font-family: 'Inter', sans-serif;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #275d88;
        margin-bottom: 0.35rem;
    }

    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(1.18rem, 1rem + 0.55vw, 1.55rem);
        font-weight: 800;
        line-height: 1.1;
        color: #101828;
        margin: 0 0 0.45rem 0;
    }

    .body-copy {
        font-family: 'Inter', sans-serif;
        font-size: clamp(0.84rem, 0.8rem + 0.12vw, 0.94rem);
        line-height: 1.42;
        color: #344054;
        margin: 0;
        max-width: 82ch;
    }

    .body-copy p {
        margin: 0;
    }

    .body-copy .spacer {
        height: 0.45rem;
    }

    .highlights-panel {
        border-left: 1px solid #e4e7ec;
        padding-left: 1rem;
        display: flex;
        flex-direction: column;
        gap: 0.55rem;
        justify-content: center;
        min-height: 100%;
    }

    .panel-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #667085;
        margin-bottom: 0.05rem;
    }

    .nav-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.7rem;
        align-items: stretch;
    }

    .nav-card {
        background: linear-gradient(180deg, #2f6e9d 0%, #24597e 100%);
        border: 1px solid #1f4f72;
        color: #ffffff;
        border-radius: 10px;
        min-height: 72px;
        padding: 0.75rem 0.8rem;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-size: clamp(0.92rem, 0.88rem + 0.2vw, 1.08rem);
        font-weight: 700;
        line-height: 1.12;
        box-shadow: 0 6px 18px rgba(23, 61, 94, 0.10);
    }

    .contributors {
        border-top: 1px solid #e4e7ec;
        padding-top: 0.65rem;
    }

    .contributors-title {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        font-weight: 800;
        color: #101828;
        margin-bottom: 0.15rem;
    }

    .contributors-names {
        font-family: 'Inter', sans-serif;
        font-size: clamp(0.96rem, 0.92rem + 0.2vw, 1.08rem);
        line-height: 1.25;
        color: #101828;
        margin-bottom: 0.08rem;
    }

    .contributors-affiliation {
        font-family: 'Inter', sans-serif;
        font-size: clamp(0.88rem, 0.85rem + 0.12vw, 0.98rem);
        line-height: 1.22;
        color: #475467;
        font-style: italic;
    }

    @media (max-width: 980px) {
        .page-shell {
            min-height: auto;
        }

        .content-grid {
            grid-template-columns: 1fr;
            gap: 0.9rem;
        }

        .highlights-panel {
            border-left: 0;
            border-top: 1px solid #e4e7ec;
            padding-left: 0;
            padding-top: 0.8rem;
        }

        .nav-grid {
            grid-template-columns: repeat(3, 1fr);
        }
    }

    @media (max-width: 720px) {
        .block-container {
            padding-left: 0.9rem;
            padding-right: 0.9rem;
            padding-top: 0.7rem;
            padding-bottom: 0.7rem;
        }

        .nav-grid {
            grid-template-columns: 1fr;
        }

        .nav-card {
            min-height: 64px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-shell">
        <div class="title-wrap">
            <h1 class="hero-title">Industrial Energy Modeling through Mapping Unit Operation Energy Demand</h1>
        </div>

        <div class="content-grid">
            <section class="statement-panel">
                <div class="eyebrow">Research overview</div>
                <h2 class="section-title">Project Statement</h2>

                <div class="body-copy">
                    <p>The term 'industry' refers to a wide range of thermodynamic, mechanical, and chemical processes that transform materials, each involving distinct unit operations. While these processes vary in number, sequence, and type, common operations such as drying, distillation, and compression are shared across sectors. However, the breakdown of industrial energy demand by these unit operations has remained poorly established, and unit-operation-level industrial models are still scarce.</p>

                    <div class="spacer"></div>

                    <p>If developed, these models could serve as building blocks for system-level industrial process and facility design. Current frameworks such as the North American Industry Classification System (NAICS) categorize industries by what they produce rather than how they use energy, which can create silos in energy-related analysis. This work develops a comprehensive analytical framework to evaluate energy demand in industrial processes at the unit-operation level.</p>

                    <div class="spacer"></div>

                    <p>The initial workflow gathered data for industrial processes representing nearly two-thirds of U.S. manufacturing and analyzed energy demand by disaggregating those processes into unit operations. By clustering and ranking unit operations according to energy demand, the framework identifies priority areas for technological advancement and supports a new approach to characterizing the U.S. industrial sector based on unit operations.</p>
                </div>
            </section>

            <aside class="highlights-panel">
                <div class="panel-label">Core framework</div>
                <div class="nav-grid">
                    <div class="nav-card">Industry Data</div>
                    <div class="nav-card">Unit Operation<br>Data</div>
                    <div class="nav-card">NAICS Sector<br>Coverage</div>
                </div>
            </aside>
        </div>

        <section class="contributors">
            <div class="contributors-title">Contributors</div>
            <div class="contributors-names">Akash Patil, M. Jibran S. Zuberi, Prakash Rao, Unique Karki</div>
            <div class="contributors-affiliation">Lawrence Berkeley National Laboratory, Berkeley, CA 94720</div>
        </section>
    </div>
    """,
    unsafe_allow_html=True,
)

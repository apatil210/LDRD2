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
        background:
            radial-gradient(circle at top right, rgba(53, 101, 146, 0.08), transparent 28%),
            linear-gradient(180deg, #f8fafc 0%, #f4f6f8 100%);
    }

    .block-container {
        max-width: 1220px;
        padding-top: 1.25rem;
        padding-bottom: 1.25rem;
        padding-left: 1.8rem;
        padding-right: 1.8rem;
    }

    .page-shell {
        min-height: calc(100vh - 2rem);
        display: grid;
        grid-template-rows: auto 1fr auto;
        gap: 1rem;
    }

    .hero-panel {
        background: rgba(255, 255, 255, 0.78);
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 22px;
        padding: 1.15rem 1.4rem 1rem;
        box-shadow: 0 18px 50px rgba(15, 23, 42, 0.06);
        backdrop-filter: blur(8px);
    }

    .eyebrow {
        font-family: 'Inter', sans-serif;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #356592;
        text-align: center;
        margin-bottom: 0.45rem;
    }

    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(1.55rem, 1.15rem + 1.15vw, 2.35rem);
        font-weight: 800;
        line-height: 1.08;
        letter-spacing: -0.035em;
        color: #0f172a;
        text-align: center;
        max-width: 15ch;
        margin: 0 auto;
        text-wrap: balance;
    }

    .content-shell {
        display: grid;
        grid-template-columns: minmax(0, 1.55fr) minmax(300px, 0.88fr);
        gap: 1rem;
        align-items: stretch;
    }

    .statement-card,
    .framework-card,
    .contributors-card {
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 22px;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.05);
        backdrop-filter: blur(8px);
    }

    .statement-card {
        padding: 1.25rem 1.35rem 1.15rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .section-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 0.45rem;
    }

    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(1.25rem, 1.02rem + 0.55vw, 1.65rem);
        font-weight: 800;
        line-height: 1.1;
        color: #0f172a;
        margin: 0 0 0.7rem 0;
    }

    .statement-copy {
        font-family: 'Inter', sans-serif;
        font-size: clamp(0.9rem, 0.87rem + 0.14vw, 0.98rem);
        line-height: 1.5;
        color: #334155;
    }

    .statement-copy p {
        margin: 0 0 0.72rem 0;
    }

    .statement-copy p:last-child {
        margin-bottom: 0;
    }

    .framework-card {
        padding: 1.15rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .framework-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.75rem;
        margin-top: 0.3rem;
    }

    .framework-pill {
        position: relative;
        overflow: hidden;
        border-radius: 18px;
        padding: 1rem 1rem;
        min-height: 84px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        background: linear-gradient(180deg, #356592 0%, #264c70 100%);
        border: 1px solid rgba(18, 57, 90, 0.65);
        color: #ffffff;
        font-family: 'Inter', sans-serif;
        font-size: clamp(0.98rem, 0.94rem + 0.2vw, 1.12rem);
        font-weight: 700;
        line-height: 1.16;
        box-shadow: 0 12px 26px rgba(37, 76, 112, 0.18);
    }

    .framework-pill::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.16), transparent 52%);
        pointer-events: none;
    }

    .contributors-card {
        padding: 1rem 1.25rem;
        display: grid;
        grid-template-columns: 180px 1fr;
        gap: 1rem;
        align-items: start;
    }

    .contributors-heading {
        font-family: 'Inter', sans-serif;
        font-size: 0.98rem;
        font-weight: 800;
        color: #0f172a;
    }

    .contributors-meta {
        min-width: 0;
    }

    .contributors-names {
        font-family: 'Inter', sans-serif;
        font-size: clamp(0.98rem, 0.95rem + 0.18vw, 1.12rem);
        line-height: 1.35;
        color: #0f172a;
        margin-bottom: 0.18rem;
    }

    .contributors-affiliation {
        font-family: 'Inter', sans-serif;
        font-size: clamp(0.92rem, 0.9rem + 0.12vw, 1rem);
        line-height: 1.35;
        color: #475569;
        font-style: italic;
    }

    @media (max-width: 980px) {
        .content-shell {
            grid-template-columns: 1fr;
        }

        .framework-grid {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }

        .contributors-card {
            grid-template-columns: 1fr;
            gap: 0.4rem;
        }
    }

    @media (max-width: 760px) {
        .block-container {
            padding-left: 0.9rem;
            padding-right: 0.9rem;
            padding-top: 0.8rem;
            padding-bottom: 0.8rem;
        }

        .page-shell {
            min-height: auto;
        }

        .hero-panel,
        .statement-card,
        .framework-card,
        .contributors-card {
            border-radius: 18px;
        }

        .framework-grid {
            grid-template-columns: 1fr;
        }

        .framework-pill {
            min-height: 76px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-shell">
        <section class="hero-panel">
            <div class="eyebrow">Industrial systems research</div>
            <h1 class="hero-title">Industrial Energy Modeling through Mapping Unit Operation Energy Demand</h1>
        </section>

        <section class="content-shell">
            <article class="statement-card">
                <div>
                    <div class="section-label">Project statement</div>
                    <h2 class="section-title">A unit-operation lens for industrial energy analysis</h2>
                    <div class="statement-copy">
                        <p>The term 'industry' refers to a wide range of thermodynamic, mechanical, and chemical processes that transform materials, each involving distinct unit operations. While these processes vary in number, sequence, and type, common operations such as drying, distillation, and compression are shared across sectors.</p>
                        <p>However, the breakdown of industrial energy demand by these unit operations remains poorly established, and unit-operation-level industrial models are still scarce. Current frameworks such as NAICS categorize industries by what they produce rather than how they use energy, which can create silos in energy-related analysis.</p>
                        <p>This work develops a comprehensive framework to map industrial energy demand at the unit-operation level. By disaggregating processes that represent nearly two-thirds of U.S. manufacturing and ranking unit operations by energy demand, the approach identifies priority areas for technology advancement and supports a more actionable characterization of the industrial sector.</p>
                    </div>
                </div>
            </article>

            <aside class="framework-card">
                <div class="section-label">Core framework</div>
                <h2 class="section-title">Three inputs that shape the model</h2>
                <div class="framework-grid">
                    <div class="framework-pill">Industry Data</div>
                    <div class="framework-pill">Unit Operation<br>Data</div>
                    <div class="framework-pill">NAICS Sector<br>Coverage</div>
                </div>
            </aside>
        </section>

        <section class="contributors-card">
            <div class="contributors-heading">Contributors</div>
            <div class="contributors-meta">
                <div class="contributors-names">Akash Patil, M. Jibran S. Zuberi, Prakash Rao, Unique Karki</div>
                <div class="contributors-affiliation">Lawrence Berkeley National Laboratory, Berkeley, CA 94720</div>
            </div>
        </section>
    </div>
    """,
    unsafe_allow_html=True,
)

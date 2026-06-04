import streamlit as st

st.set_page_config(
    page_title="Industrial Energy Modeling | Berkeley Lab",
    page_icon="⚙️",
    layout="wide",
)

contributors = [
    {
        "name": "Akash Patil",
        "title": "Postdoctoral Researcher, Energy Analysis Division",
        "photo": "https://raw.githubusercontent.com/apatil210/LDRD2/main/Akashpic2.jpg",
    },
    {
        "name": "Jibran Zuberi",
        "title": "Energy/Environmental Policy Research Scientist/Engineer, Energy Analysis Division",
        "photo": "https://raw.githubusercontent.com/apatil210/LDRD2/main/Jibran.jpg",
    },
    {
        "name": "Prakash Rao",
        "title": "Head · Building & Industrial Applications Department",
        "photo": "https://raw.githubusercontent.com/apatil210/LDRD2/main/Prakash.jpg",
    },
    {
        "name": "Unique Karki",
        "title": "Technology Researcher II · Building & Industrial Energy Systems Division",
        "photo": "https://raw.githubusercontent.com/apatil210/LDRD2/main/Unique.jpg",
    },
]

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&display=swap');

    :root {
        --lbl-blue: #00313c;
        --lbl-teal: #007681;
        --lbl-dark-gray: #63666a;
        --lbl-orange: #d57800;
        --bg: #f7f9f9;
        --surface: #ffffff;
        --surface-soft: #eef4f4;
        --text: #0b1f27;
        --muted: #4e5f66;
        --border: rgba(0, 49, 60, 0.12);
        --shadow-sm: 0 8px 24px rgba(0, 49, 60, 0.06);
        --shadow-lg: 0 22px 50px rgba(0, 49, 60, 0.10);
        --max-width: 1240px;
    }

    .stApp {
        background: linear-gradient(180deg, #fbfcfc 0%, #f3f7f7 45%, #eef3f4 100%);
        color: var(--text);
    }

    .block-container {
        max-width: var(--max-width);
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        border-bottom: 1px solid rgba(0, 49, 60, 0.10);
        padding: 0.3rem 0 1rem 0;
        margin-bottom: 1.3rem;
    }

    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 0.95rem;
    }

    .brand-mark {
        width: 52px;
        height: 52px;
        background: linear-gradient(180deg, var(--lbl-blue) 0%, #0a4854 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: var(--shadow-sm);
        flex: 0 0 52px;
        border-radius: 0;
    }

    .brand-svg {
        width: 30px;
        height: 30px;
        color: white;
    }

    .brand-text-top {
        font: 700 0.78rem/1 'Libre Franklin', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--lbl-teal);
        margin-bottom: 0.28rem;
    }

    .brand-text-main {
        font: 800 1.08rem/1.1 'Libre Franklin', sans-serif;
        color: var(--lbl-blue);
        letter-spacing: -0.02em;
    }

    .brand-meta {
        font: 600 0.82rem/1.35 'Libre Franklin', sans-serif;
        color: var(--lbl-dark-gray);
        text-align: right;
    }

    .hero {
        background: linear-gradient(135deg, #ffffff 0%, #f5f9f9 100%);
        border: 1px solid var(--border);
        border-top: 5px solid var(--lbl-teal);
        border-radius: 0;
        padding: 2.4rem 2.4rem 2rem 2.4rem;
        box-shadow: var(--shadow-lg);
        margin-bottom: 1.5rem;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.45fr) minmax(300px, 0.78fr);
        gap: 2rem;
        align-items: start;
    }

    .kicker {
        display: inline-block;
        font: 700 0.82rem/1 'Libre Franklin', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--lbl-teal);
        margin-bottom: 1rem;
    }

    .hero-title {
        font-family: 'Libre Franklin', sans-serif;
        font-size: clamp(2.15rem, 1.55rem + 2vw, 4rem);
        font-weight: 800;
        line-height: 1.02;
        letter-spacing: -0.045em;
        color: var(--lbl-blue);
        max-width: 12ch;
        margin: 0 0 1rem 0;
    }

    .hero-copy {
        font-family: 'Source Serif 4', serif;
        font-size: clamp(1.05rem, 0.98rem + 0.22vw, 1.18rem);
        line-height: 1.72;
        color: #29414b;
        max-width: 68ch;
        margin: 0 0 1.35rem 0;
    }

    .hero-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.7rem;
        margin-top: 1rem;
    }

    .hero-tag {
        background: var(--surface-soft);
        border: 1px solid rgba(0, 118, 129, 0.14);
        color: var(--lbl-blue);
        border-radius: 0;
        padding: 0.7rem 0.9rem;
        min-width: 150px;
    }

    .hero-tag strong {
        display: block;
        font: 800 0.98rem/1.1 'Libre Franklin', sans-serif;
        margin-bottom: 0.18rem;
    }

    .hero-tag span {
        font: 500 0.83rem/1.35 'Libre Franklin', sans-serif;
        color: var(--muted);
    }

    .hero-panel {
        background: var(--lbl-blue);
        color: white;
        border-radius: 0;
        padding: 1.4rem;
        box-shadow: 0 18px 34px rgba(0, 49, 60, 0.18);
    }

    .hero-panel-label {
        font: 700 0.76rem/1 'Libre Franklin', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: rgba(255,255,255,0.7);
        margin-bottom: 0.8rem;
    }

    .hero-panel h3 {
        font: 800 1.4rem/1.15 'Libre Franklin', sans-serif;
        margin: 0 0 0.75rem 0;
        color: white;
    }

    .hero-panel p {
        font: 400 1rem/1.65 'Source Serif 4', serif;
        margin: 0 0 1rem 0;
        color: rgba(255,255,255,0.9);
    }

    .focus-list {
        display: grid;
        gap: 0.65rem;
    }

    .focus-item {
        background: rgba(255,255,255,0.08);
        border-left: 3px solid var(--lbl-orange);
        border-radius: 0;
        padding: 0.8rem 0.9rem;
        font: 500 0.93rem/1.45 'Libre Franklin', sans-serif;
    }

    .section {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 0;
        padding: 1.8rem;
        box-shadow: var(--shadow-sm);
        margin-top: 1.3rem;
    }

    .section-title {
        font: 800 clamp(1.35rem, 1.1rem + 0.75vw, 1.95rem)/1.1 'Libre Franklin', sans-serif;
        color: var(--lbl-blue);
        margin: 0 0 0.75rem 0;
        letter-spacing: -0.03em;
    }

    .section-copy {
        font: 400 1.06rem/1.78 'Source Serif 4', serif;
        color: #334952;
        max-width: 77ch;
        margin: 0;
    }

    .resource-intro {
        margin-top: 0.3rem;
        margin-bottom: 0.3rem;
        font: 500 0.96rem/1.55 'Libre Franklin', sans-serif;
        color: var(--muted);
    }

    .nav-link {
        text-decoration: none;
        display: block;
        width: 100%;
    }

    .nav-card {
        background: #ffffff;
        border: 1px solid rgba(0, 49, 60, 0.12);
        border-top: 4px solid var(--lbl-teal);
        color: var(--text);
        min-height: 215px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 1.35rem;
        box-shadow: var(--shadow-sm);
        margin: 0.2rem 0 0.6rem 0;
        border-radius: 0;
        transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
    }

    .nav-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 18px 36px rgba(0, 49, 60, 0.11);
        border-color: rgba(0, 118, 129, 0.28);
    }

    .nav-kicker {
        font: 700 0.76rem/1 'Libre Franklin', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--lbl-teal);
        margin-bottom: 0.95rem;
    }

    .nav-title {
        font: 800 1.38rem/1.12 'Libre Franklin', sans-serif;
        color: var(--lbl-blue);
        margin-bottom: 0.65rem;
        letter-spacing: -0.03em;
    }

    .nav-copy {
        font: 400 1rem/1.7 'Source Serif 4', serif;
        color: #35505a;
        margin: 0 0 1.1rem 0;
    }

    .nav-footer {
        font: 700 0.92rem/1 'Libre Franklin', sans-serif;
        color: var(--lbl-blue);
    }

    .team-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
        margin-top: 1.2rem;
    }

    .person-card {
        background: #ffffff;
        border: 1px solid rgba(0, 49, 60, 0.10);
        border-radius: 0;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        height: 100%;
        display: flex;
        flex-direction: column;
    }

    .person-photo-wrap {
        background: #e7eff1;
        padding: 0;
    }

    .person-photo-frame {
        width: 100%;
        height: 285px;
        border-bottom: 1px solid rgba(0, 49, 60, 0.10);
        background-color: #dfe8ea;
        background-repeat: no-repeat;
        background-position: center center;
        background-size: 100% 100%;
    }

    .person-body {
        padding: 1rem 1rem 1.15rem 1rem;
    }

    .person-name {
        font: 800 1.02rem/1.2 'Libre Franklin', sans-serif;
        color: var(--lbl-blue);
        margin: 0 0 0.45rem 0;
    }

    .person-title {
        font: 500 0.9rem/1.55 'Libre Franklin', sans-serif;
        color: var(--lbl-dark-gray);
        margin: 0;
        min-height: 4.5rem;
    }

    .hosting-note {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(0, 49, 60, 0.10);
        font: 700 0.92rem/1.45 'Libre Franklin', sans-serif;
        color: var(--lbl-teal);
    }

    .footer-note {
        margin-top: 1.2rem;
        font: 500 0.84rem/1.55 'Libre Franklin', sans-serif;
        color: var(--lbl-dark-gray);
    }

    .funding-copy {
        font: 500 0.98rem/1.6 'Libre Franklin', sans-serif;
        color: var(--lbl-dark-gray);
        margin: 0.2rem 0 0 0;
        letter-spacing: 0.01em;
    }

    .funding-copy strong {
        color: var(--lbl-blue);
        font-weight: 700;
    }

    div[data-testid="column"] {
        display: flex;
    }

    @media (max-width: 1100px) {
        .hero-grid {
            grid-template-columns: 1fr;
        }
        .team-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .hero-title {
            max-width: none;
        }
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 0.8rem;
        }
        .topbar {
            flex-direction: column;
            align-items: flex-start;
        }
        .brand-meta {
            text-align: left;
        }
        .hero,
        .section {
            padding: 1.25rem;
        }
        .team-grid {
            grid-template-columns: 1fr;
        }
        .hero-tags {
            flex-direction: column;
        }
        .hero-tag {
            width: 100%;
        }
        .person-photo-frame {
            height: 320px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="topbar">
        <div class="brand-lockup">
            <div class="brand-mark" aria-hidden="true">
                <svg class="brand-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M4 18V6.5L9.2 4L14.4 6.5V18" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M9.2 18V9.2H14.4V18" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M16.8 18V8.5L20 7V18" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <div>
                <div class="brand-text-top">Berkeley Lab</div>
                <div class="brand-text-main">Industrial Energy Modeling Project</div>
            </div>
        </div>
        <div class="brand-meta">Lawrence Berkeley National Laboratory<br>Energy Technologies Area</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <div class="hero-grid">
            <div>
                <div class="kicker">Research platform</div>
                <h1 class="hero-title">Industrial Energy Modeling through Mapping Unit Operation Energy Demand</h1>
                <p class="hero-copy">
                    This project reframes industrial energy analysis around shared unit operations rather than isolated manufacturing sectors. By organizing process evidence at the operation level, the platform supports a clearer understanding of cross-sector energy demand, stronger prioritization of technology opportunities, and a more transferable foundation for future industrial system models.
                </p>
                <div class="hero-tags">
                    <div class="hero-tag"><strong>Scope</strong><span>Initial process mapping covers nearly two-thirds of U.S. manufacturing.</span></div>
                    <div class="hero-tag"><strong>Method</strong><span>Industrial processes are disaggregated into repeatable unit operations.</span></div>
                    <div class="hero-tag"><strong>Use case</strong><span>Supports technology targeting, modeling, and design optimization.</span></div>
                </div>
            </div>
            <aside class="hero-panel">
                <div class="hero-panel-label">Why it matters</div>
                <h3>Common process steps offer a better basis for energy insight.</h3>
                <p>
                    Existing industrial classifications group facilities by what they produce. This research instead studies how energy is used inside shared operations such as drying, distillation, and compression.
                </p>
                <div class="focus-list">
                    <div class="focus-item">Map industrial energy demand to unit operations that recur across subsectors.</div>
                    <div class="focus-item">Cluster and rank high-demand operations to identify the strongest opportunities for innovation.</div>
                    <div class="focus-item">Create modular building blocks for process-level and facility-level modeling workflows.</div>
                </div>
            </aside>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="section">
        <h2 class="section-title">Project Statement</h2>
        <p class="section-copy">
            Industry comprises thermodynamic, mechanical, and chemical transformations that are built from distinct unit operations. While the number, order, and configuration of these operations differ by subsector, many core operations recur across manufacturing systems. Despite that common structure, industrial energy demand is still rarely analyzed at the unit-operation level. This project develops a framework to disaggregate industrial processes into unit operations, quantify their energy demand profiles, and identify high-priority operations where technological advances can deliver broad system-wide benefit.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="section">
        <h2 class="section-title">Project Resources</h2>
        <p class="resource-intro">Access the core datasets and coverage views that support the analytical framework.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3, gap="large")

cards = [
    (
        col1,
        "Industry data",
        "Process library",
        "Browse industrial process records and the supporting evidence base assembled for the project.",
        "https://testfilepy-adgzkwgrpeml8ungt35ls7.streamlit.app/",
    ),
    (
        col2,
        "Unit operation data",
        "Operation insights",
        "Explore mapped unit operations, their functional role in processes, and their energy-demand structure.",
        "https://testfile2py-ai2jtwn2rdnjkd2nhyuwpi.streamlit.app/",
    ),
    (
        col3,
        "NAICS coverage",
        "Sector representation",
        "Review how the current process dataset maps across manufacturing sectors and coverage boundaries.",
        "https://naicspy-dirbrfux3gcfa7exdkvbbg.streamlit.app/",
    ),
]

for col, kicker, title, copy, url in cards:
    with col:
        st.markdown(
            f'''
            <a class="nav-link" href="{url}" target="_blank" rel="noopener noreferrer">
                <article class="nav-card">
                    <div>
                        <div class="nav-kicker">{kicker}</div>
                        <div class="nav-title">{title}</div>
                        <div class="nav-copy">{copy}</div>
                    </div>
                    <div class="nav-footer">Open resource →</div>
                </article>
            </a>
            ''',
            unsafe_allow_html=True,
        )

cards_html = "".join(
    f'''
    <article class="person-card">
        <div class="person-photo-wrap">
            <div class="person-photo-frame" role="img" aria-label="Portrait of {c["name"]}" style="background-image: url('{c["photo"]}');"></div>
        </div>
        <div class="person-body">
            <h3 class="person-name">{c["name"]}</h3>
            <p class="person-title">{c["title"]}</p>
        </div>
    </article>
    '''
    for c in contributors
)

st.markdown(
    f'''
    <section class="section">
        <h2 class="section-title">Research Team</h2>
        <div class="team-grid">{cards_html}</div>
        
    </section>
    ''',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="section">
        <h2 class="section-title">Funding Acknowledgement</h2>
        <p class="funding-copy">
            Laboratory Directed Research &amp; Development (LDRD) Program (FY 2025-26), Lawrence Berkeley National Laboratory (LBNL).
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

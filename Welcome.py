import streamlit as st

st.set_page_config(
    page_title="Industrial Energy Modeling | LBNL",
    page_icon="⚙️",
    layout="wide",
)

contributors = [
    {
        "name": "Akash Patil",
        "title": "Postdoctoral Researcher · Energy Analysis Division",
        "photo": "https://raw.githubusercontent.com/apatil210/LDRD2/main/Akash_photo.jpg",
    },
    {
        "name": "M. Jibran S. Zuberi",
        "title": "Energy/Environmental Policy Research Scientist/Engineer · Energy Analysis Division",
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&display=swap');

    :root {
        --bg: #f5f7fa;
        --surface: rgba(255,255,255,0.88);
        --surface-strong: #ffffff;
        --text: #10222f;
        --muted: #4e6472;
        --accent: #0b5e8e;
        --accent-dark: #08496d;
        --accent-soft: #e8f1f7;
        --border: rgba(16,34,47,0.10);
        --shadow: 0 20px 50px rgba(10, 36, 56, 0.10);
        --radius: 22px;
        --radius-sm: 16px;
        --max: 1240px;
    }

    .stApp {
        background:
            radial-gradient(circle at top right, rgba(11,94,142,0.10), transparent 28%),
            linear-gradient(180deg, #f7fafc 0%, #eef3f7 100%);
        color: var(--text);
    }

    .block-container {
        max-width: var(--max);
        padding-top: 2.4rem;
        padding-bottom: 3rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(255,255,255,0.78);
        border: 1px solid rgba(11,94,142,0.12);
        color: var(--accent-dark);
        padding: 0.5rem 0.85rem;
        border-radius: 999px;
        font: 600 0.86rem/1 Inter, sans-serif;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 24px rgba(11,94,142,0.08);
        margin-bottom: 1.1rem;
    }

    .hero-wrap {
        background: linear-gradient(145deg, rgba(255,255,255,0.94), rgba(255,255,255,0.80));
        border: 1px solid var(--border);
        border-radius: 32px;
        padding: 3rem 3rem 2.2rem 3rem;
        box-shadow: var(--shadow);
        backdrop-filter: blur(16px);
        margin-bottom: 1.4rem;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.8fr);
        gap: 2rem;
        align-items: center;
    }

    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: clamp(2.2rem, 1.5rem + 2.3vw, 4.2rem);
        font-weight: 800;
        line-height: 1.02;
        letter-spacing: -0.04em;
        color: var(--text);
        margin: 0 0 1rem 0;
        max-width: 12ch;
    }

    .hero-copy {
        font-family: 'Source Serif 4', serif;
        font-size: clamp(1.08rem, 0.98rem + 0.28vw, 1.22rem);
        line-height: 1.72;
        color: var(--muted);
        max-width: 66ch;
        margin: 0 0 1.5rem 0;
    }

    .hero-metrics {
        display: flex;
        flex-wrap: wrap;
        gap: 0.9rem;
        margin-top: 1.25rem;
    }

    .metric-chip {
        background: var(--accent-soft);
        color: var(--accent-dark);
        border: 1px solid rgba(11,94,142,0.10);
        border-radius: 999px;
        padding: 0.75rem 0.95rem;
        min-width: 150px;
    }

    .metric-chip strong {
        display: block;
        font: 800 1rem/1.1 Inter, sans-serif;
        color: var(--text);
        margin-bottom: 0.2rem;
    }

    .metric-chip span {
        font: 500 0.84rem/1.35 Inter, sans-serif;
    }

    .hero-panel {
        background: linear-gradient(180deg, #0d3651 0%, #154f74 100%);
        color: #f8fbfd;
        border-radius: 28px;
        padding: 1.6rem;
        box-shadow: 0 18px 40px rgba(13, 54, 81, 0.24);
    }

    .hero-panel-label {
        font: 700 0.85rem/1 Inter, sans-serif;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: rgba(248,251,253,0.72);
        margin-bottom: 0.9rem;
    }

    .hero-panel h3 {
        font: 800 clamp(1.2rem, 1rem + 0.7vw, 1.65rem)/1.12 Inter, sans-serif;
        margin: 0 0 0.75rem 0;
    }

    .hero-panel p {
        font: 400 1rem/1.65 'Source Serif 4', serif;
        color: rgba(248,251,253,0.88);
        margin: 0 0 1.1rem 0;
    }

    .panel-list {
        display: grid;
        gap: 0.65rem;
    }

    .panel-item {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 0.85rem 0.95rem;
        font: 500 0.94rem/1.45 Inter, sans-serif;
    }

    .section-shell {
        background: rgba(255,255,255,0.72);
        border: 1px solid var(--border);
        border-radius: 28px;
        padding: 2rem;
        box-shadow: 0 14px 34px rgba(16,34,47,0.06);
        margin-top: 1.4rem;
        backdrop-filter: blur(10px);
    }

    .section-title {
        font: 800 clamp(1.35rem, 1.15rem + 0.7vw, 2rem)/1.1 Inter, sans-serif;
        color: var(--text);
        margin: 0 0 0.8rem 0;
        letter-spacing: -0.03em;
    }

    .section-copy {
        font: 400 clamp(1.02rem, 0.98rem + 0.2vw, 1.12rem)/1.75 'Source Serif 4', serif;
        color: var(--muted);
        max-width: 78ch;
        margin: 0;
    }

    .nav-link {
        text-decoration: none;
        display: block;
        width: 100%;
    }

    .nav-card {
        background: linear-gradient(180deg, #ffffff 0%, #f6f9fb 100%);
        border: 1px solid rgba(11,94,142,0.10);
        color: var(--text);
        text-align: left;
        min-height: 212px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 1.45rem;
        box-shadow: 0 18px 35px rgba(16,34,47,0.07);
        margin: 0.2rem 0 0.6rem 0;
        border-radius: 22px;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    }

    .nav-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 24px 42px rgba(16,34,47,0.11);
        border-color: rgba(11,94,142,0.24);
    }

    .nav-kicker {
        color: var(--accent);
        font: 700 0.8rem/1 Inter, sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 1rem;
    }

    .nav-title {
        font: 800 1.45rem/1.1 Inter, sans-serif;
        color: var(--text);
        margin-bottom: 0.7rem;
        letter-spacing: -0.03em;
    }

    .nav-copy {
        font: 400 1rem/1.65 'Source Serif 4', serif;
        color: var(--muted);
        margin-bottom: 1.2rem;
    }

    .nav-footer {
        font: 700 0.95rem/1 Inter, sans-serif;
        color: var(--accent-dark);
    }

    .contributors-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
        margin-top: 1.25rem;
    }

    .person-card {
        background: rgba(255,255,255,0.94);
        border: 1px solid var(--border);
        border-radius: 22px;
        padding: 1.1rem;
        box-shadow: 0 14px 28px rgba(16,34,47,0.06);
        height: 100%;
    }

    .person-photo {
        width: 100%;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        border-radius: 18px;
        border: 1px solid rgba(11,94,142,0.08);
        margin-bottom: 0.95rem;
        background: #eef3f7;
    }

    .person-name {
        font: 800 1.05rem/1.2 Inter, sans-serif;
        color: var(--text);
        margin: 0 0 0.45rem 0;
    }

    .person-title {
        font: 500 0.92rem/1.55 Inter, sans-serif;
        color: var(--muted);
        margin: 0;
        min-height: 4.4rem;
    }

    .institution-bar {
        margin-top: 1.2rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border);
        font: 700 0.95rem/1.4 Inter, sans-serif;
        color: var(--accent-dark);
    }

    div[data-testid="column"] {
        display: flex;
    }

    @media (max-width: 1100px) {
        .hero-grid {
            grid-template-columns: 1fr;
        }
        .contributors-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 1.2rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .hero-wrap,
        .section-shell {
            padding: 1.35rem;
            border-radius: 22px;
        }
        .contributors-grid {
            grid-template-columns: 1fr;
        }
        .hero-title {
            max-width: none;
        }
        .metric-chip {
            width: 100%;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero-wrap">
        <div class="eyebrow">Lawrence Berkeley National Laboratory · Industrial Energy Systems</div>
        <div class="hero-grid">
            <div>
                <h1 class="hero-title">Industrial Energy Modeling through Mapping Unit Operation Energy Demand</h1>
                <p class="hero-copy">
                    A research initiative to characterize industrial energy use through the lens of unit operations rather than sector silos. The platform organizes process-level evidence, identifies high-impact operations such as drying, distillation, and compression, and supports a more transferable framework for industrial system analysis and technology prioritization.
                </p>
                <div class="hero-metrics">
                    <div class="metric-chip"><strong>Nearly two-thirds</strong><span>of U.S. manufacturing represented in the initial workflow</span></div>
                    <div class="metric-chip"><strong>Unit-operation view</strong><span>designed to connect energy demand across subsectors</span></div>
                    <div class="metric-chip"><strong>Research objective</strong><span>build a foundation for process and facility design optimization</span></div>
                </div>
            </div>
            <aside class="hero-panel">
                <div class="hero-panel-label">Project focus</div>
                <h3>From industrial sectors to a common energy language</h3>
                <p>
                    Instead of grouping manufacturing only by what it produces, this work examines how energy is consumed inside shared process steps. That shift makes cross-sector analysis and technology targeting much more actionable.
                </p>
                <div class="panel-list">
                    <div class="panel-item">Disaggregate industrial processes into repeatable unit operations.</div>
                    <div class="panel-item">Rank operations by energy demand to identify high-priority intervention points.</div>
                    <div class="panel-item">Create building blocks for future industrial process and facility models.</div>
                </div>
            </aside>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="section-shell">
        <h2 class="section-title">Project Statement</h2>
        <p class="section-copy">
            Industry encompasses a wide range of thermodynamic, mechanical, and chemical processes that transform materials through distinct unit operations. Although the sequence and composition of these processes vary by subsector, common operations such as drying, distillation, and compression appear repeatedly across manufacturing systems. Yet industrial energy demand is still rarely understood at the level of those shared operations. This project develops an analytical framework that disaggregates industrial processes into unit operations, maps energy demand across them, and clusters high-energy operations to reveal where technology innovation can deliver the strongest system-wide impact.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div style="height:0.35rem"></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

cards = [
    (
        col1,
        "Industry data",
        "Process library",
        "Browse industrial process records and the underlying evidence base used in the project workflow.",
        "https://testfilepy-adgzkwgrpeml8ungt35ls7.streamlit.app/",
    ),
    (
        col2,
        "Unit operation data",
        "Operation insights",
        "Explore mapped unit operations, their roles in industrial processes, and associated energy-demand structure.",
        "https://testfile2py-ai2jtwn2rdnjkd2nhyuwpi.streamlit.app/",
    ),
    (
        col3,
        "NAICS coverage",
        "Sector representation",
        "Review manufacturing coverage and see how the current dataset maps across NAICS sectors.",
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
        <img class="person-photo" src="{c["photo"]}" alt="Portrait of {c["name"]}">
        <h3 class="person-name">{c["name"]}</h3>
        <p class="person-title">{c["title"]}</p>
    </article>
    '''
    for c in contributors
)

st.markdown(
    f'''
    <section class="section-shell">
        <h2 class="section-title">Research Team</h2>
        <p class="section-copy">The project brings together researchers and technical leaders from Lawrence Berkeley National Laboratory working across energy analysis, policy, and industrial systems.</p>
        <div class="contributors-grid">{cards_html}</div>
        <div class="institution-bar">Hosted by Lawrence Berkeley National Laboratory</div>
    </section>
    ''',
    unsafe_allow_html=True,
)

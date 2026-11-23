"""Shared editorial soft-pink theme for the Streamlit dashboard."""

import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #59434D;
            --muted: #927C86;
            --rose: #C9829F;
            --rose-deep: #684B60;
            --rose-light: #F3C5D5;
            --line: #E8C8D6;
            --paper: #FFFFFF;
        }
        html, body, [class*="css"] {
            font-family: Inter, "Aptos", "Segoe UI", sans-serif;
            color: var(--ink);
        }
        .stApp {
            background: linear-gradient(145deg, #FFF5EF 0%, #FFF9FB 48%, #FFF0F5 100%);
            color: var(--ink);
        }
        [data-testid="stHeader"] { background: rgba(255, 245, 239, .88); }
        [data-testid="stMainBlockContainer"] { padding: 1.7rem 2rem 3rem; max-width: 1440px; }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #F3C5D5 0%, #F8E5EC 58%, #F5D7E2 100%);
            border-right: 1px solid #E8C8D6;
        }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.35rem; }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: var(--muted); }
        h1, h2, h3, h4 { color: var(--ink); letter-spacing: -.025em; }
        h2 { margin-top: .45rem; }
        h3 { margin: .45rem 0 .8rem; }
        p, li { color: #77636D; line-height: 1.68; }

        .brand-lockup { padding: .2rem .1rem 1.05rem; border-bottom: 1px solid #EBD4DD; margin-bottom: 1rem; }
        .brand-name { color: var(--rose-deep); font-size: .72rem; font-weight: 800; letter-spacing: .17em; }
        .brand-subtitle { color: var(--muted); font-size: .79rem; margin-top: .28rem; }
        .researcher-card {
            background: linear-gradient(145deg, #FFFDFB 0%, #FFF5EF 100%); border: 1px solid #E8C8D6;
            border-radius: 18px; padding: 1.25rem 1.2rem 1.15rem; margin: .7rem 0 1.2rem;
            box-shadow: 0 10px 25px rgba(104,75,96,.10);
        }
        .researcher-label { color: var(--rose-deep); font-size: .66rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
        .researcher-name { color: var(--ink); font-size: 1.08rem; line-height: 1.3; font-weight: 750; margin: .42rem 0 .68rem; }
        .researcher-meta { color: #806C76; font-size: .78rem; line-height: 1.55; margin-top: .27rem; }
        .sidebar-section-title { color: var(--ink); font-size: .76rem; font-weight: 750; letter-spacing: .035em; margin: 1rem 0 .48rem; }
        .research-fact { border-left: 2px solid #DFA2B7; padding: .06rem 0 .06rem .65rem; margin: .48rem 0; }
        .research-fact-label { color: #9A828D; font-size: .65rem; text-transform: uppercase; letter-spacing: .08em; }
        .research-fact-value { color: #65515B; font-size: .78rem; line-height: 1.45; margin-top: .12rem; }

        [data-testid="stSidebar"] div[role="radiogroup"] { gap: .38rem; }
        [data-testid="stSidebar"] div[role="radiogroup"] > label {
            border: 1px solid transparent; border-radius: 11px; padding: .62rem .78rem;
            margin: 0; transition: background .15s ease, border-color .15s ease;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background: rgba(255,255,255,.58); }
        [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
            background: linear-gradient(100deg, #E6B2C5, #F1D1DC); border-color: #D9A5B8;
            border-left: 3px solid #A96F8B; box-shadow: 0 5px 14px rgba(104,75,96,.10);
        }
        [data-testid="stSidebar"] div[role="radiogroup"] > label [role="radio"] { display: none; }
        [data-testid="stSidebar"] div[role="radiogroup"] > label p { color: #66515C; font-size: .88rem; font-weight: 620; }

        .hero {
            position: relative; overflow: hidden; isolation: isolate;
            padding: 1.45rem 1.8rem 1.55rem; border-radius: 20px;
            border: 1px solid #E8C8D6;
            background: linear-gradient(112deg, #FFFFFF 0%, #FFF5EF 54%, #F3EAF5 100%);
            margin: .15rem 0 1.5rem; box-shadow: 0 12px 28px rgba(104,75,96,.08);
        }
        .hero::after {
            content: ""; position: absolute; z-index: -1; width: 210px; height: 210px;
            right: 5%; top: -112px; border: 1px solid rgba(169,111,139,.3); border-radius: 50%;
            box-shadow: 0 0 0 25px rgba(169,111,139,.055), 0 0 0 52px rgba(169,111,139,.04);
        }
        .hero-kicker { color: #A96F8B; text-transform: uppercase; letter-spacing: .16em; font-size: .68rem; font-weight: 800; }
        .hero-title { color: var(--ink); font-size: clamp(1.65rem, 3vw, 2.25rem); line-height: 1.18; font-weight: 770; margin: .4rem 0 .45rem; max-width: 920px; }
        .hero-copy { color: var(--muted); font-size: .96rem; line-height: 1.6; max-width: 900px; margin: 0; }

        [data-testid="stMetric"] {
            background: #FFFFFF; border: 1px solid #E8C8D6;
            border-radius: 17px; padding: 1.25rem 1.35rem; min-height: 128px;
            box-shadow: 0 9px 21px rgba(104,75,96,.085); border-top: 4px solid #C9829F;
        }
        [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="column"]:nth-child(2) [data-testid="stMetric"] { background:#FFF5EF; border-top-color:#A96F8B; }
        [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="column"]:nth-child(3) [data-testid="stMetric"] { background:#FBF8FC; border-top-color:#9A82A4; }
        [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="column"]:nth-child(4) [data-testid="stMetric"] { background:#FFF9FB; border-top-color:#D89EB4; }
        [data-testid="stMetricLabel"] { color: #806C76; font-size: .77rem; margin-bottom: .35rem; }
        [data-testid="stMetricValue"] { color: #684B60; font-weight: 760; letter-spacing: -.025em; }
        [data-testid="stMetricDelta"] { font-size: .78rem; }

        .parameter-item {
            min-height: 145px; padding: 1.25rem 1.35rem; margin: 0 0 1.5rem;
            border: 1px solid #E8C8D6; border-top: 3px solid #C9829F; border-radius: 16px;
            background: #FFFFFF; box-shadow: 0 6px 15px rgba(104,75,96,.055);
        }
        .parameter-item--mauve { border-top-color:#A96F8B; background:#FFF9F6; }
        .parameter-item--lavender { border-top-color:#9A82A4; background:#FAF7FB; }
        .parameter-item h4 { color: #684B60; font-size: .98rem; margin: .1rem 0 .65rem; }
        .parameter-item p { color: #806C76; font-size: .85rem; margin: 0; line-height: 1.62; }
        /* Keep only each parameter card's own outline on the Dashboard. */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.parameter-item),
        [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stMetric"]) {
            border: 0; border-radius: 0; background: transparent;
            padding: 0; margin: 0; box-shadow: none;
        }
        .section-label { color: var(--rose-deep); font-size: .67rem; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }
        .about-divider { height:1px; background:linear-gradient(90deg,#D9A5B8,rgba(217,165,184,0)); margin:1.65rem 0; }
        .tools-label { margin-top:1.35rem; }
        .tool-list { display: grid; grid-template-columns: 1fr 1fr; gap: .45rem 1rem; margin-top: .65rem; }
        .tool-item { border-bottom: 1px solid #EAD7DF; background: transparent; padding: .5rem .1rem; color: #705A65; font-size: .8rem; }
        .timeline-number { color: #A96F8B; font-size: .66rem; font-weight: 800; letter-spacing: .13em; }
        .timeline-text { color: #66515C; font-size: .83rem; font-weight: 650; line-height: 1.42; margin-top: .5rem; min-height: 2.4rem; }

        [data-testid="stSelectbox"] [data-baseweb="select"] > div { background: #FFFCFD; border-color: #EAD7DF; border-radius: 11px; min-height: 2.8rem; }
        [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within { border-color: #D98DA9; box-shadow: 0 0 0 2px rgba(217,141,169,.14); }
        [data-testid="stTabs"] [data-baseweb="tab-list"] { gap: .35rem; border-bottom: 1px solid #EEDFE5; }
        [data-testid="stTabs"] button[data-baseweb="tab"] { color: #8B737D; border-radius: 10px 10px 0 0; padding: .65rem .9rem; }
        [data-testid="stTabs"] button[aria-selected="true"] { color: var(--rose-deep); border-bottom: 2px solid var(--rose); font-weight: 700; }
        [data-testid="stExpander"] { background: transparent; border: 0; border-radius: 0; }
        [data-testid="stButton"] button { border-radius: 10px; border: 1px solid #EAD5DE; background: white; color: var(--ink); font-weight: 650; }
        [data-testid="stButton"] button:hover { border-color: var(--rose); color: var(--rose-deep); }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid #E8C8D6; border-radius: 17px; background: #FFFFFF;
            padding: 1.25rem 1.4rem; margin: .45rem 0 1.2rem;
            box-shadow: 0 6px 17px rgba(104,75,96,.055);
        }
        /* Tab panels are layout only; keep the bordered wrapper around the chart itself. */
        [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stTabs"]) {
            border: 0; border-radius: 0; background: transparent;
            padding: 0; margin: 0; box-shadow: none;
        }
        /* Keep only the deepest card when Streamlit containers are nested. */
        [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stVerticalBlockBorderWrapper"]) {
            border: 0; border-radius: 0; background: transparent;
            padding: 0; margin: 0; box-shadow: none;
        }
        .st-key-environment-card {
            border: 1px solid #E8C8D6 !important; border-radius: 17px !important;
            background: #FFFFFF !important; padding: 1.25rem 1.4rem !important;
            margin: .45rem 0 1.2rem !important;
            box-shadow: 0 6px 17px rgba(104,75,96,.055) !important;
        }
        .st-key-tools-card { padding-bottom: 2rem !important; }
        .st-key-environment-card [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stVerticalBlockBorderWrapper"].st-key-environment-card {
            border: 1px solid #E8C8D6; border-radius: 17px; background: #FFFFFF;
            padding: 1.25rem 1.4rem; margin: .45rem 0 1.2rem;
            box-shadow: 0 6px 17px rgba(104,75,96,.055);
        }
        [data-testid="stVerticalBlockBorderWrapper"].st-key-tools-card,
        .st-key-tools-card [data-testid="stVerticalBlockBorderWrapper"] {
            padding-bottom: 1.75rem !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stPlotlyChart"]):not(:has([data-testid="stVerticalBlockBorderWrapper"] [data-testid="stPlotlyChart"])),
        [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stVegaLiteChart"]):not(:has([data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVegaLiteChart"])) {
            padding-bottom: 2rem !important;
        }
        [data-testid="stPlotlyChart"], [data-testid="stVegaLiteChart"] { margin: .5rem 0 1.55rem; }
        [data-testid="stHorizontalBlock"] { gap: 1rem !important; }
        [data-testid="stDataFrame"] { border: 0; border-radius: 0; overflow: hidden; }
        [data-testid="stCaptionContainer"] { color: var(--muted); }
        hr { border-color: #EBD9E0; }
        @media (max-width: 760px) {
            [data-testid="stMainBlockContainer"] { padding: 1rem .9rem 2rem; }
            [data-testid="stVerticalBlockBorderWrapper"] { padding: 1rem; }
            .parameter-item { padding: 1.1rem; min-height: auto; }
            .hero { padding: 1.15rem 1.15rem 1.2rem; border-radius: 16px; }
            .hero-title { font-size: 1.6rem; }
            .tool-list { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

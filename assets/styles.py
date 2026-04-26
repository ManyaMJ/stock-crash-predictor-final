"""
assets/styles.py
────────────────
Global CSS injected via st.markdown().
Call inject_css() at the top of every page.
"""

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ─────────────────────────────────────────────────────────────── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #F0F4FF; }

/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1628 0%, #112240 100%);
    border-right: 1px solid #1E3A5F;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: #E8F0FE !important; }

[data-testid="stSidebarNav"] a {
    color: #8BA3C1 !important;
    font-size: 14px;
    padding: 10px 16px;
    border-radius: 8px;
    margin: 3px 8px;
    display: block;
    text-decoration: none;
    transition: all 0.2s ease;
    font-weight: 500;
}
[data-testid="stSidebarNav"] a:hover {
    background-color: #1E3A5F;
    color: #00C9A7 !important;
}
[data-testid="stSidebarNav"] a[aria-selected="true"] {
    background-color: #1E3A5F;
    color: #00C9A7 !important;
    border-left: 3px solid #00C9A7;
    font-weight: 600;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
.stButton > button {
    background-color: #00C9A7 !important;
    color: #0A1628 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 28px !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px;
}
.stButton > button:hover {
    background-color: #009E82 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,201,167,0.35) !important;
}
.stButton > button:active { transform: translateY(0); }

/* Secondary / outline button style via extra class */
.btn-secondary > button {
    background-color: transparent !important;
    color: #00C9A7 !important;
    border: 2px solid #00C9A7 !important;
}
.btn-secondary > button:hover {
    background-color: #E6FFF9 !important;
    box-shadow: none !important;
}

/* ── Tabs ────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background-color: #FFFFFF;
    border-radius: 12px 12px 0 0;
    padding: 8px 8px 0;
    border-bottom: 2px solid #E0E8F5;
    box-shadow: 0 1px 4px rgba(10,22,40,0.06);
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    border-radius: 8px 8px 0 0;
    color: #6B7B8F;
    font-weight: 500;
    font-size: 14px;
    padding: 8px 18px;
    border: none;
    transition: all 0.2s;
}
.stTabs [data-baseweb="tab"]:hover { color: #00C9A7; }
.stTabs [aria-selected="true"] {
    background-color: #F0F4FF !important;
    color: #00C9A7 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #00C9A7 !important;
}

/* ── Metric tiles ────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background-color: #FFFFFF;
    border: 1px solid #E0E8F5;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(10,22,40,0.06);
}
[data-testid="metric-container"] label { color: #8BA3C1 !important; font-size: 12px !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #0A1628 !important; font-weight: 700 !important; }

/* ── File uploader ───────────────────────────────────────────────────────── */
[data-testid="stFileUploadDropzone"] {
    background-color: #FFFFFF;
    border: 2px dashed #00C9A7 !important;
    border-radius: 12px !important;
    padding: 24px !important;
    transition: all 0.2s;
}
[data-testid="stFileUploadDropzone"]:hover {
    background-color: #E6FFF9 !important;
    border-color: #009E82 !important;
}

/* ── Expander ────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background-color: #FFFFFF;
    border: 1px solid #E0E8F5 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px rgba(10,22,40,0.04);
    margin-bottom: 8px;
}

/* ── DataFrames ──────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #E0E8F5;
}

/* ── Selectbox / Slider ──────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background-color: #FFFFFF !important;
    border: 1px solid #D1D9E6 !important;
    border-radius: 8px !important;
}
[data-testid="stSlider"] > div > div > div > div { background-color: #00C9A7; }

/* ── Progress bar ────────────────────────────────────────────────────────── */
[data-testid="stProgress"] > div > div { background-color: #00C9A7 !important; }

/* ── Alert boxes ─────────────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px; }

/* ── Custom component classes ────────────────────────────────────────────── */
.hero-box {
    background: linear-gradient(135deg, #0A1628 0%, #1E3A5F 60%, #0A1628 100%);
    border-radius: 16px;
    padding: 44px 40px;
    margin-bottom: 28px;
    border: 1px solid #1E3A5F;
}
.hero-badge {
    display: inline-block;
    background: rgba(0,201,167,0.15);
    color: #00C9A7;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.5px;
    border: 1px solid rgba(0,201,167,0.3);
    margin-bottom: 16px;
    text-transform: uppercase;
}
.hero-title {
    font-size: 34px;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.25;
    margin-bottom: 10px;
}
.hero-sub {
    font-size: 16px;
    color: #8BA3C1;
    line-height: 1.6;
    max-width: 680px;
    margin-bottom: 24px;
}
.hero-stat {
    display: inline-block;
    margin-right: 32px;
    margin-top: 8px;
}
.hero-stat-val { font-size: 26px; font-weight: 700; color: #00C9A7; }
.hero-stat-lbl { font-size: 12px; color: #8BA3C1; display: block; }

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E0E8F5;
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(10,22,40,0.06);
}
.kpi-val { font-size: 30px; font-weight: 700; color: #00C9A7; }
.kpi-lbl { font-size: 12px; color: #8BA3C1; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
.kpi-sub { font-size: 11px; color: #6B7B8F; margin-top: 3px; }

.step-card {
    background: #FFFFFF;
    border: 1px solid #E0E8F5;
    border-radius: 12px;
    padding: 24px 20px;
    box-shadow: 0 2px 8px rgba(10,22,40,0.05);
    height: 100%;
}
.step-num {
    width: 38px; height: 38px;
    background: #0A1628; color: #00C9A7;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 17px;
    margin: 0 auto 14px;
}
.step-title { font-size: 15px; font-weight: 600; color: #1A2B45; margin-bottom: 8px; text-align: center; }
.step-desc  { font-size: 13px; color: #6B7B8F; line-height: 1.55; text-align: center; }

.section-hdr {
    border-left: 4px solid #00C9A7;
    padding: 2px 0 2px 14px;
    margin-bottom: 18px;
}
.section-hdr h2, .section-hdr h3 { margin: 0; color: #1A2B45; }

.info-banner {
    background: #E6FFF9;
    border: 1px solid #00C9A7;
    border-radius: 10px;
    padding: 14px 18px;
    color: #007A5E;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 16px;
}
.warn-banner {
    background: #FFF8E8;
    border: 1px solid #FFB703;
    border-radius: 10px;
    padding: 14px 18px;
    color: #7A5800;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 16px;
}
.model-tag {
    display: inline-block;
    background: #0A1628;
    color: #00C9A7;
    padding: 3px 10px;
    border-radius: 5px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-right: 6px;
}
.sidebar-logo {
    text-align: center;
    padding: 20px 16px 12px;
    border-bottom: 1px solid #1E3A5F;
    margin-bottom: 8px;
}
.sidebar-logo-title {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: 700;
    margin-top: 8px;
    line-height: 1.3;
}
.sidebar-logo-sub {
    color: #8BA3C1;
    font-size: 11px;
    margin-top: 3px;
}
.status-dot-green::before { content: "●"; color: #00C9A7; margin-right: 6px; }
.status-dot-gray::before  { content: "●"; color: #8BA3C1; margin-right: 6px; }
</style>
"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


def sidebar_header():
    """Render branded sidebar header + data/model status."""
    import streamlit as st
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <div style="font-size:28px;">📈</div>
            <div class="sidebar-logo-title">Crash Predictor</div>
            <div class="sidebar-logo-sub">NIFTY 50 · Explainable ML</div>
        </div>
        """, unsafe_allow_html=True)

        # Status
        data_ok  = 'df_feat' in st.session_state
        model_ok = 'metrics' in st.session_state
        st.markdown(f"""
        <div style="padding:12px 16px; font-size:13px;">
            <div class="{'status-dot-green' if data_ok  else 'status-dot-gray'}">
                {'Data ready' if data_ok  else 'No data uploaded'}
            </div>
            <div style="margin-top:6px" class="{'status-dot-green' if model_ok else 'status-dot-gray'}">
                {'Models trained' if model_ok else 'Models not trained'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

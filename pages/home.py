"""
pages/home.py — Dashboard (Home)
──────────────────────────────────
Landing page: ticker tape · hero · crash event history · how-it-works
· model KPI cards · research context.
CSS + sidebar are injected by app.py before this page runs.
"""

import streamlit as st
from assets.styles import ticker_tape

ticker_tape()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-box">
  <div class="hero-badge"><span class="blink-dot"></span>&nbsp;LIVE RESEARCH TOOL &nbsp;·&nbsp; CHITKARA UNIVERSITY &nbsp;·&nbsp; 2026</div>
  <div class="hero-title">Market <span class="accent">Crash</span><br>Predictor</div>
  <div class="hero-sub">
    An explainable machine-learning framework that identifies pre-crash market conditions
    in any OHLCV equity market — NIFTY 50, S&amp;P 500, Nasdaq, Dow Jones, and beyond.
    Upload your CSV, train five classifiers in seconds, and interrogate every prediction
    with SHAP-based feature attribution.
  </div>
  <div class="hero-stats">
    <div class="hero-stat"><span class="hero-stat-val">0.627</span><span class="hero-stat-lbl">Ensemble ROC-AUC</span></div>
    <div class="hero-stat"><span class="hero-stat-val">79.2%</span><span class="hero-stat-lbl">Crash Recall (RF)</span></div>
    <div class="hero-stat"><span class="hero-stat-val">25</span><span class="hero-stat-lbl">Engineered Features</span></div>
    <div class="hero-stat"><span class="hero-stat-val">5</span><span class="hero-stat-lbl">ML Classifiers</span></div>
    <div class="hero-stat"><span class="hero-stat-val">6,211</span><span class="hero-stat-lbl">Training Records</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Get Started ───────────────────────────────────────────────────────────────
_, btn_col, _ = st.columns([3, 2, 3])
with btn_col:
    if st.button("📂  Upload Data & Get Started", use_container_width=True):
        st.switch_page("pages/1_Upload.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>How It Works</h3></div>', unsafe_allow_html=True)
cols = st.columns(4)
steps = [
    ("01", "Upload CSV",     "Drag & drop any OHLCV CSV — NIFTY 50, S&P 500, Nasdaq, Sensex, or any equity market. Auto-detects columns, validates, and engineers all 25 technical features instantly."),
    ("02", "Train Models",   "One click trains all five classifiers — DT, LR, RF, XGBoost, and the Soft-Voting Ensemble — with SMOTE class balancing."),
    ("03", "Explore Results","Dive into ROC curves, confusion matrices, PR curves, SHAP feature importance, and rolling-window temporal F1 — all interactive."),
    ("04", "Get Predictions","See crash probability on a live timeline. Adjust the decision threshold and download your full prediction CSV."),
]
for col, (num, title, desc) in zip(cols, steps):
    with col:
        st.markdown(f"""
        <div class="step-card">
            <div class="step-num">{num}</div>
            <div class="step-title">{title}</div>
            <div class="step-desc">{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# ── Historical Crash Events ───────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>Historical Crash Events in the Dataset</h3></div>', unsafe_allow_html=True)
st.caption("Five major market dislocations used as crash labels (5-day forward return < −3%). Hover over cards for context.")

crash_events = [
    ("Mar 2000 – Oct 2002", "Dot-Com Bubble Burst",     "NIFTY lost ~55% as tech valuations collapsed. Earnings-driven re-pricing wiped out speculative excess."),
    ("Jan 2008 – Mar 2009", "Global Financial Crisis",  "Sub-prime contagion triggered a ~60% drawdown. Foreign institutional outflows accelerated the decline."),
    ("Jul 2011 – Dec 2011", "European Debt Crisis",     "Sovereign contagion from Greece/Italy elevated risk-off sentiment; NIFTY fell ~25% in six months."),
    ("Jan 2020 – Mar 2020", "COVID-19 Liquidity Shock", "Circuit-breaker events. NIFTY crashed ~38% in 40 trading days — the fastest drawdown in its history."),
    ("Jan 2022 – Jun 2022", "Inflation / Rate-Hike Shock","RBI + Fed tightening cycle. Rising yields repriced growth stocks; NIFTY corrected ~17% over six months."),
]
ev_cols = st.columns(5)
for col, (date, name, desc) in zip(ev_cols, crash_events):
    with col:
        st.markdown(f"""
        <div class="crash-event">
            <div class="crash-event-date">{date}</div>
            <div class="crash-event-name">{name}</div>
            <div class="crash-event-desc">{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# ── Five Classifiers ──────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>Five Classifiers — Test Set ROC-AUC</h3></div>', unsafe_allow_html=True)

models_info = [
    ("Decision Tree",       "0.583", "Max depth 6 · CART · Baseline",              "#8BA3C1"),
    ("Logistic Regression", "0.579", "L2 reg · C=0.5 · Linear baseline",           "#6B7FD4"),
    ("Random Forest",       "0.634", "80 trees · Max depth 8 · Highest Recall",    "#2ECC71"),
    ("XGBoost",             "0.613", "80 estimators · LR 0.05 · Subsample 0.80",   "#FF6B6B"),
    ("Ensemble ★",         "0.627", "Soft-vote LR+RF+XGB · Best overall AUC",      "#00D4AA"),
]
kpi_cols = st.columns(5)
for col, (name, auc, params, color) in zip(kpi_cols, models_info):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:2px solid {color};">
            <div class="kpi-val" style="color:{color};">{auc}</div>
            <div class="kpi-lbl">{name}</div>
            <div class="kpi-sub">{params}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Feature Categories ────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>25 Engineered Features</h3></div>', unsafe_allow_html=True)
feat_col1, feat_col2 = st.columns(2)
with feat_col1:
    st.markdown("""
    <span class="feat-pill">1d Return</span>
    <span class="feat-pill">3d Return</span>
    <span class="feat-pill">5d Return</span>
    <span class="feat-pill">10d Return</span>
    <span class="feat-pill">20d Return</span>
    <span class="feat-pill">MA20 Deviation</span>
    <span class="feat-pill">MA50 Deviation</span>
    <span class="feat-pill">MA5-20 Cross</span>
    <span class="feat-pill">MA20-50 Cross</span>
    <span class="feat-pill">Vol 5d</span>
    <span class="feat-pill">Vol 10d</span>
    <span class="feat-pill">Vol 20d</span>
    <span class="feat-pill">Vol Ratio</span>
    """, unsafe_allow_html=True)
with feat_col2:
    st.markdown("""
    <span class="feat-pill">ATR 14</span>
    <span class="feat-pill">RSI 14</span>
    <span class="feat-pill">MACD</span>
    <span class="feat-pill">MACD Signal</span>
    <span class="feat-pill">MACD Histogram</span>
    <span class="feat-pill">Stochastic %K</span>
    <span class="feat-pill">Stochastic %D</span>
    <span class="feat-pill">BB Width</span>
    <span class="feat-pill">BB Position</span>
    <span class="feat-pill">Volume Ratio 20d</span>
    <span class="feat-pill">OBV Normalised</span>
    <span class="feat-pill">High-Low Range</span>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# ── Research Context ──────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>Research Context</h3></div>', unsafe_allow_html=True)

with st.expander("📄 Abstract", expanded=False):
    st.markdown("""
    The stock market crash is a rare occurrence but can have far-reaching economic impacts.
    Financial markets are nonlinear dynamic systems with multiple structural breaks and persistent
    class imbalances, making accurate crash timing prediction extremely challenging.
    While machine-learning ensembles predict temporal patterns for equities, most operate as
    **black boxes** that do not provide the transparency required by regulators or financial institutions.

    We propose an **optimised soft-voting ensemble** of Decision Tree, Logistic Regression,
    Random Forest, and XGBoost classifiers, augmented with **SHAP** for model interpretability.
    Trained on NIFTY 50 data (2001–2026) with 6,211 daily records and 25 engineered features,
    using SMOTE oversampling to address the ~10.2% crash class imbalance.

    The ensemble achieved **ROC-AUC 0.627** on the 2020–2023 test set — a **7.5% improvement**
    over the standalone Decision Tree. Top SHAP features: **ATR (14-day), 20-day Volatility,
    High-Low Range**. Robustness validated across three market regimes via rolling-window F1.
    """)

with st.expander("🔬 Methodology", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Dataset**")
        st.markdown("""
        - Source: NSE India
        - Period: Jan 2001 – Mar 2026
        - 6,260 records → 6,211 clean observations
        - Crash label: 5-day forward return < −3%
        - Class imbalance: ~10.2% crash days
        """)
        st.markdown("**Train / Test Split**")
        st.markdown("""
        - Train: 2001–2019 (4,675 samples)
        - Test: 2020–2023 (994 samples, 77 crash events)
        - Strictly temporal — no data leakage
        """)
    with col_b:
        st.markdown("**Top-3 SHAP Precursors**")
        for rank, feat, desc in [
            ("#1", "ATR (14-day)",      "Average True Range measures pre-crash volatility expansion"),
            ("#2", "Volatility (20d)",  "Sustained 20-day vol elevation precedes tail-risk events"),
            ("#3", "High-Low Range",    "Wide intra-day spread signals investor indecision"),
        ]:
            st.markdown(f"""
            <div class="insight-panel" style="margin-bottom:8px;">
                <div class="insight-label">{rank} — {feat}</div>
                <div class="insight-text">{desc}</div>
            </div>""", unsafe_allow_html=True)

with st.expander("📚 Key References", expanded=False):
    st.markdown("""
    | Authors | Contribution |
    |---------|-------------|
    | Ozbayoglu et al. (2020) | LSTMs outperform classics but lack interpretability |
    | Sezer et al. (2020) | Only 12% of 150 forecasting studies addressed explainability |
    | Arrieta et al. (2020) | SHAP identified as most theoretically grounded post-hoc method |
    | Bussmann et al. (2021) | XGBoost + SHAP for systemic risk in European banks |
    | Pelletier & Loiseau (2023) | Ensemble methods consistently outperform single estimators |

    **Research gap addressed:** No prior work applies a soft-voting ensemble with SHAP
    to equity market crash prediction with rigorous rolling-window temporal validation.
    """)

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#3D4F63; font-size:11px; padding:12px 0; font-family:'IBM Plex Mono',monospace;">
    Performance Optimisation of Explainable ML Models for Stock Market Crash Prediction &nbsp;·&nbsp;
    Manya Jain & Navdeep Kaur &nbsp;·&nbsp; Chitkara University &nbsp;·&nbsp; IJRAR_333294
</div>
""", unsafe_allow_html=True)

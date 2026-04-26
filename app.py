"""
app.py — Home Page
──────────────────
Landing page: hero, how it works, research context, key stats.
"""

import streamlit as st

st.set_page_config(
    page_title="Stock Market Crash Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

from assets.styles import inject_css, sidebar_header
inject_css()
sidebar_header()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-box">
    <div class="hero-badge">Research Tool · Chitkara University · 2026</div>
    <div class="hero-title">Stock Market Crash Predictor</div>
    <div class="hero-sub">
        An explainable machine learning framework for predicting NIFTY 50 market crashes.
        Upload your market data, train five classifiers in seconds, and explore
        interactive results backed by SHAP-based feature attribution.
    </div>
    <div>
        <div class="hero-stat"><span class="hero-stat-val">0.627</span><span class="hero-stat-lbl">Ensemble ROC-AUC</span></div>
        <div class="hero-stat"><span class="hero-stat-val">79.2%</span><span class="hero-stat-lbl">Crash Recall (RF)</span></div>
        <div class="hero-stat"><span class="hero-stat-val">25</span><span class="hero-stat-lbl">Engineered Features</span></div>
        <div class="hero-stat"><span class="hero-stat-val">5</span><span class="hero-stat-lbl">ML Models</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>How It Works</h3></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

steps = [
    ("01", "Upload CSV", "Drag & drop your NIFTY 50 OHLCV CSV file. The app auto-detects columns, validates the data, and engineers all 25 technical features instantly."),
    ("02", "Train Models", "One click trains all five classifiers — Decision Tree, Logistic Regression, Random Forest, XGBoost, and the Soft-Voting Ensemble — with SMOTE balancing."),
    ("03", "Explore Results", "Dive into ROC curves, confusion matrices, precision-recall curves, SHAP feature importance, and rolling-window temporal validation — all interactive."),
    ("04", "Get Predictions", "See crash probability for every trading day on a timeline. Adjust the threshold slider and download your prediction CSV."),
]

for col, (num, title, desc) in zip([col1, col2, col3, col4], steps):
    with col:
        st.markdown(f"""
        <div class="step-card">
            <div class="step-num">{num}</div>
            <div class="step-title">{title}</div>
            <div class="step-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Get Started button ────────────────────────────────────────────────────────
_, btn_col, _ = st.columns([2, 1, 2])
with btn_col:
    if st.button("📂  Get Started — Upload Data", use_container_width=True):
        st.switch_page("pages/1_Upload.py")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# ── Research Context ──────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>About the Research</h3></div>', unsafe_allow_html=True)

with st.expander("📄 Abstract", expanded=True):
    st.markdown("""
    The stock market crash is a rare occurrence but can have far-reaching economic impacts.
    Financial markets are nonlinear dynamic systems with multiple structural breaks and persistent
    class imbalances, making accurate crash timing prediction extremely challenging.
    While machine-learning ensembles predict temporal patterns for equities, most operate as
    **"black boxes"** that do not provide the transparency required by regulators or financial institutions.

    We propose an **optimised soft-voting ensemble** of Decision Tree, Logistic Regression,
    Random Forest, and XGBoost classifiers, augmented with **SHAP (SHapley Additive exPlanations)**
    for model interpretability. The model was trained on NIFTY 50 stock data (2001–2026) using
    6,211 daily trading records, with 25 engineered technical and volatility indicators across
    five historical crash events, using SMOTE oversampling to address class imbalance.

    The ensemble achieved **ROC-AUC of 0.627** on the 2020–2023 test set — a **7.5% improvement**
    over the standalone Decision Tree. Top crash precursors identified via SHAP:
    **ATR (14-day), 20-day Volatility, and High-Low Range**. Robustness was validated
    across three distinct market regimes using a 10-quarter rolling window.
    """)

with st.expander("🔬 Methodology Overview"):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Dataset**")
        st.markdown("""
        - Source: National Stock Exchange of India (NSE)
        - Period: January 2001 – March 2026
        - 6,260 records → 6,211 clean observations
        - 5 crash events: Dot-com, GFC, Euro Debt Crisis, COVID-19, Inflation Shock
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
        st.markdown("**25 Engineered Features**")
        feature_cats = {
            "Price Returns (5)":    "1/3/5/10/20-day returns",
            "Moving Averages (4)":  "MA deviation, MA cross signals",
            "Volatility (5)":       "Rolling vol, ATR (14-day)",
            "Momentum (6)":         "RSI, MACD, Stochastic %K/%D",
            "Bollinger Bands (2)":  "Band width, price position",
            "Volume (2)":           "Volume ratio, OBV (normalised)",
            "Candlestick (1)":      "High-Low range / close",
        }
        for cat, desc in feature_cats.items():
            st.markdown(f"- **{cat}** — {desc}")

with st.expander("📚 Related Work"):
    st.markdown("""
    | Authors | Contribution |
    |---------|-------------|
    | Ozbayoglu et al. (2020) [14] | LSTMs outperform classical models but lack interpretability |
    | Sezer et al. (2020) [15] | Only 12% of 150 forecasting studies addressed interpretability |
    | Zhang et al. (2022) [2] | LSTM S&P 500 prediction: ROC-AUC 0.85, no explainability |
    | Arrieta et al. (2020) [11] | SHAP identified as most theoretically grounded post-hoc method |
    | Bussmann et al. (2021) [4] | XGBoost + SHAP for systemic risk in European banks |
    | Misheva et al. (2021) [13] | Accuracy-interpretability trade-off as open research challenge |
    | Pelletier & Loiseau (2023) [16] | Ensemble methods consistently outperform single estimators |

    **Research Gap:** No prior work applies a soft-voting ensemble with SHAP explainability
    to NIFTY 50 crash prediction with rigorous rolling-window temporal validation.
    """)

st.markdown("---")

# ── Model overview ────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>Five Classifiers</h3></div>', unsafe_allow_html=True)

models_info = [
    ("Decision Tree",       "0.583", "Max depth 6 · CART · Baseline",                  "#8BA3C1"),
    ("Logistic Regression", "0.579", "L2-reg · C=0.5 · Linear baseline",               "#6B7FD4"),
    ("Random Forest",       "0.634", "80 trees · Max depth 8 · n_jobs=-1",             "#2ECC71"),
    ("XGBoost",             "0.613", "80 estimators · LR 0.05 · Subsample 0.80",       "#FF6B6B"),
    ("Ensemble ★",         "0.627", "Soft-vote: LR + RF + XGB · Best overall AUC",     "#00C9A7"),
]

cols = st.columns(5)
for col, (name, auc, params, color) in zip(cols, models_info):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid {color};">
            <div class="kpi-val" style="color:{color};">{auc}</div>
            <div class="kpi-lbl" style="margin-top:6px;">{name}</div>
            <div class="kpi-sub" style="margin-top:8px;">{params}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#8BA3C1; font-size:12px; padding:16px 0;">
    Performance Optimisation of Explainable ML Models for Stock Market Crash Prediction
    &nbsp;·&nbsp; Manya Jain & Navdeep Kaur &nbsp;·&nbsp; Chitkara University &nbsp;·&nbsp; 2026
    &nbsp;·&nbsp; Published in IJRAR (Registration ID: IJRAR_333294)
</div>
""", unsafe_allow_html=True)

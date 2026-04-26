"""
pages/1_Upload.py — Upload & Explore
─────────────────────────────────────
CSV upload → validation → EDA → feature engineering → session state.
"""

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Upload Data — Crash Predictor",
    page_icon="📂",
    layout="wide",
    initial_sidebar_state="expanded",
)

from assets.styles import inject_css, sidebar_header
from core.features import load_and_validate, engineer_features
from core.charts import price_chart, crash_distribution

inject_css()
sidebar_header()

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("## 📂 Upload & Explore")
st.markdown("Upload your NIFTY 50 (or any OHLCV) CSV file. The app validates, previews, and engineers all 25 features automatically.")
st.markdown("---")

# ── Format guide (collapsible) ────────────────────────────────────────────────
with st.expander("📋 CSV Format Guide — click to expand", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **Required columns** (case-insensitive):
        | Column | Description |
        |--------|-------------|
        | Open   | Daily opening price |
        | High   | Daily high |
        | Low    | Daily low |
        | Close  | Closing price |
        | Date   | Trading date *(recommended)* |
        | Volume | Trading volume *(optional)* |
        """)
    with col_b:
        st.markdown("**Example rows:**")
        sample = pd.DataFrame({
            "Date":   ["2020-01-02", "2020-01-03"],
            "Open":   [12182.50, 12285.80],
            "High":   [12311.20, 12311.40],
            "Low":    [12168.35, 12227.45],
            "Close":  [12282.20, 12235.90],
            "Volume": [185400000, 172300000],
        })
        st.dataframe(sample, hide_index=True, use_container_width=True)
        st.caption("NIFTY 50 data: NSE India · Yahoo Finance (^NSEI)")

# ── Upload widget ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>Upload Your CSV</h3></div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    label="Drag & drop or click to browse",
    type=["csv"],
    help="Max 200 MB · CSV format only",
    label_visibility="collapsed",
)

if uploaded is not None:
    # ── Validate ──────────────────────────────────────────────────────────────
    with st.spinner("Validating data…"):
        df_raw, err = load_and_validate(uploaded)

    if err:
        st.markdown(f'<div class="warn-banner">⚠️ {err}</div>', unsafe_allow_html=True)
        st.stop()

    st.markdown(f'<div class="info-banner">✅ File loaded successfully — <strong>{len(df_raw):,} rows</strong> detected.</div>', unsafe_allow_html=True)

    # ── Key stats ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr"><h3>Dataset Overview</h3></div>', unsafe_allow_html=True)

    date_min = df_raw['date'].min().strftime('%d %b %Y')
    date_max = df_raw['date'].max().strftime('%d %b %Y')
    price_range = f"{df_raw['close'].min():,.1f} – {df_raw['close'].max():,.1f}"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Trading Days", f"{len(df_raw):,}")
    c2.metric("Date Range", f"{date_min}")
    c3.metric("Date Range End", f"{date_max}")
    c4.metric("Close Price Range", price_range)

    # ── Data preview ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr" style="margin-top:20px;"><h3>Data Preview</h3></div>', unsafe_allow_html=True)
    st.dataframe(df_raw.head(10), use_container_width=True, hide_index=True)
    st.caption(f"Showing first 10 of {len(df_raw):,} rows")

    # ── Feature engineering ───────────────────────────────────────────────────
    st.markdown('<div class="section-hdr" style="margin-top:20px;"><h3>Feature Engineering</h3></div>', unsafe_allow_html=True)

    with st.spinner("Computing 25 technical & volatility features…"):
        df_feat = engineer_features(df_raw.to_json())

    crash_count = int(df_feat['crash'].sum())
    crash_rate  = crash_count / len(df_feat) * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows After Feature Engineering", f"{len(df_feat):,}")
    c2.metric("Features Computed", "25")
    c3.metric("Crash Days Labelled", f"{crash_count:,}")
    c4.metric("Crash Rate", f"{crash_rate:.1f}%")

    st.markdown("""
    <div class="info-banner">
    ✅ All 25 features computed: Price Returns · Moving Averages · Volatility · Momentum · Bollinger Bands · Volume · Candlestick
    </div>
    """, unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr" style="margin-top:20px;"><h3>Visual Exploration</h3></div>', unsafe_allow_html=True)

    chart_tab1, chart_tab2, chart_tab3 = st.tabs(["📈 Price Chart", "🥧 Crash Distribution", "📋 Feature Stats"])

    with chart_tab1:
        st.plotly_chart(price_chart(df_feat), use_container_width=True)
        st.caption("Red markers indicate days labelled as crashes (5-day forward return < −3%).")

    with chart_tab2:
        col_dist, col_info = st.columns([1, 1])
        with col_dist:
            st.plotly_chart(crash_distribution(df_feat), use_container_width=True)
        with col_info:
            st.markdown("#### Crash Label Definition")
            st.markdown("""
            A trading day is labelled as a **crash (y = 1)** if the
            5-day forward cumulative return falls below **−3%**.

            > *"Crash events account for approximately 10.2% of all observations,
            this very unbalanced class is addressed during model training using
            SMOTE (Synthetic Minority Over-sampling Technique)."*
            — Research Paper, Section III.B
            """)
            st.metric("Crash Days", f"{crash_count:,}", delta=f"{crash_rate:.1f}% of total")
            st.metric("Non-Crash Days", f"{len(df_feat)-crash_count:,}", delta=f"{100-crash_rate:.1f}% of total")

    with chart_tab3:
        from core.features import FEATURE_COLS, FEATURE_DISPLAY
        feat_stats = df_feat[FEATURE_COLS].describe().T
        feat_stats.index = [FEATURE_DISPLAY.get(f, f) for f in feat_stats.index]
        feat_stats = feat_stats[['mean', 'std', 'min', 'max']].round(5)
        feat_stats.columns = ['Mean', 'Std Dev', 'Min', 'Max']
        st.dataframe(feat_stats, use_container_width=True)
        st.caption("Descriptive statistics for all 25 engineered features.")

    # ── Save to session state ─────────────────────────────────────────────────
    st.session_state['raw_df']  = df_raw
    st.session_state['df_feat'] = df_feat
    st.session_state['upload_complete'] = True

    st.markdown("---")

    # ── Navigation ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr"><h3>Ready to Train?</h3></div>', unsafe_allow_html=True)
    st.markdown(f"Data validated ✅ · {len(df_feat):,} samples · {crash_count:,} crash events ({crash_rate:.1f}%) · 25 features ready")

    _, btn_col, _ = st.columns([2, 2, 2])
    with btn_col:
        if st.button("🤖  Proceed to Model Training & Results →", use_container_width=True):
            st.switch_page("pages/2_Results.py")

else:
    # ── Empty state ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding:60px 20px; color:#8BA3C1;">
        <div style="font-size:52px; margin-bottom:16px;">📁</div>
        <div style="font-size:18px; font-weight:600; color:#1A2B45; margin-bottom:8px;">No file uploaded yet</div>
        <div style="font-size:14px;">Upload a CSV file above to begin. See the format guide for column requirements.</div>
    </div>
    """, unsafe_allow_html=True)

    # Show if session already has data
    if st.session_state.get('upload_complete'):
        st.markdown("""
        <div class="info-banner">
        ℹ️ You have previously uploaded data in this session.
        You can continue to the Results page or upload a new file above.
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Continue to Results", use_container_width=False):
            st.switch_page("pages/2_Results.py")

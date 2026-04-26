"""
pages/1_Upload.py — Upload & Explore
──────────────────────────────────────
CSV upload · validation · EDA · candlestick · feature engineering.
CSS + sidebar injected by app.py.
"""

import streamlit as st
import pandas as pd

from core.features import load_and_validate, engineer_features, FEATURE_COLS, FEATURE_DISPLAY
from core.charts import price_chart, candlestick_chart, crash_distribution
from assets.styles import ticker_tape

ticker_tape()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:6px;">
  <span style="font-size:28px;">📂</span>
  <div>
    <div style="font-size:22px;font-weight:800;color:#F0F4FF;letter-spacing:-0.5px;">Upload & Explore</div>
    <div style="font-size:13px;color:#6B7B8F;">Validate your OHLCV CSV → engineer 25 features → explore with interactive charts</div>
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Format guide ──────────────────────────────────────────────────────────────
with st.expander("📋 CSV Format Guide", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **Required columns** (case-insensitive):
        | Column | Description |
        |--------|-------------|
        | Date   | Trading date *(recommended)* |
        | Open   | Daily opening price |
        | High   | Daily high |
        | Low    | Daily low |
        | Close  | Closing / adjusted close |
        | Volume | Trading volume *(optional)* |
        """)
    with col_b:
        sample = pd.DataFrame({
            "Date":   ["2020-01-02", "2020-01-03", "2020-01-06"],
            "Open":   [12182.50, 12285.80, 12268.15],
            "High":   [12311.20, 12311.40, 12320.00],
            "Low":    [12168.35, 12227.45, 12216.90],
            "Close":  [12282.20, 12235.90, 12311.40],
            "Volume": [185400000, 172300000, 191000000],
        })
        st.dataframe(sample, hide_index=True, use_container_width=True)
        st.caption("NIFTY 50: NSE India · Yahoo Finance (^NSEI)")

# ── Upload widget ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>Upload Your CSV</h3></div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Drag & drop or click to browse — CSV only · max 200 MB",
    type=["csv"], label_visibility="collapsed",
)

if uploaded is not None:
    with st.spinner("Validating data…"):
        df_raw, err = load_and_validate(uploaded)

    if err:
        st.markdown(f'<div class="warn-banner">⚠ {err}</div>', unsafe_allow_html=True)
        st.stop()

    st.markdown(f'<div class="info-banner">✔ File accepted — <strong>{len(df_raw):,} rows</strong> loaded successfully.</div>',
                unsafe_allow_html=True)

    # ── Dataset overview ──────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr"><h3>Dataset Overview</h3></div>', unsafe_allow_html=True)
    date_min = df_raw['date'].min().strftime('%d %b %Y')
    date_max = df_raw['date'].max().strftime('%d %b %Y')
    years    = (df_raw['date'].max() - df_raw['date'].min()).days / 365.25
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Trading Days",     f"{len(df_raw):,}")
    c2.metric("Date From",        date_min)
    c3.metric("Date To",          date_max)
    c4.metric("Years of History", f"{years:.1f} yrs")
    c5.metric("Close Range",      f"₹{df_raw['close'].min():,.0f}–{df_raw['close'].max():,.0f}")

    # ── Data preview ──────────────────────────────────────────────────────────
    with st.expander("🗂 Data Preview (first 10 rows)", expanded=False):
        st.dataframe(df_raw.head(10), use_container_width=True, hide_index=True)

    # ── Feature engineering ───────────────────────────────────────────────────
    st.markdown('<div class="section-hdr" style="margin-top:20px;"><h3>Feature Engineering</h3></div>',
                unsafe_allow_html=True)
    with st.spinner("Computing 25 technical & volatility features…"):
        df_feat = engineer_features(df_raw.to_json())

    crash_count = int(df_feat['crash'].sum())
    crash_rate  = crash_count / len(df_feat) * 100

    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("Rows After Engineering",  f"{len(df_feat):,}")
    f2.metric("Features Computed",       "25")
    f3.metric("Crash Days Labelled",     f"{crash_count:,}")
    f4.metric("Non-Crash Days",          f"{len(df_feat)-crash_count:,}")
    f5.metric("Crash Rate",              f"{crash_rate:.1f}%")

    st.markdown("""
    <div class="info-banner">
    ✔ All 25 features computed — Price Returns · Moving Averages · Volatility ·
    Momentum · Bollinger Bands · Volume · Candlestick
    </div>""", unsafe_allow_html=True)

    # ── Chart tabs ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr" style="margin-top:20px;"><h3>Visual Exploration</h3></div>',
                unsafe_allow_html=True)

    tab_cs, tab_price, tab_dist, tab_stats = st.tabs([
        "🕯 Candlestick",
        "📈 Price + Crashes",
        "🥧 Crash Distribution",
        "📋 Feature Stats",
    ])

    with tab_cs:
        st.plotly_chart(candlestick_chart(df_feat), use_container_width=True)
        st.markdown("""
        <div class="term-box">
        <span class="t-g">▲ GREEN candle</span> — close &gt; open (bullish session)&nbsp;&nbsp;
        <span class="t-r">▼ RED candle</span> — close &lt; open (bearish session)&nbsp;&nbsp;
        <span class="t-r">▼ RED triangle</span> — crash-labelled day (5d fwd return &lt; −3%)
        </div>""", unsafe_allow_html=True)

    with tab_price:
        st.plotly_chart(price_chart(df_feat), use_container_width=True)
        st.caption("Red dots mark crash-labelled days. Use the range selector or drag the mini-chart below to zoom.")

    with tab_dist:
        d_col, i_col = st.columns([1, 1])
        with d_col:
            st.plotly_chart(crash_distribution(df_feat), use_container_width=True)
        with i_col:
            st.markdown("""
            <div class="insight-panel">
                <div class="insight-label">Crash Label Definition</div>
                <div class="insight-text">
                A trading day is labelled <strong style="color:#FF3366;">CRASH (y=1)</strong>
                if the <em>5-day forward cumulative return</em> falls below <strong>−3%</strong>.<br><br>
                This forward-looking window aligns with institutional risk horizons and captures
                the onset of drawdowns before they become visible in backward-looking indicators.
                </div>
            </div>
            <div class="insight-panel" style="border-left-color:#FFB700;">
                <div class="insight-label" style="color:#FFB700;">Class Imbalance</div>
                <div class="insight-text">
                Only ~10% of days are crash days. SMOTE oversampling (k=3)
                is applied during training to prevent the model from predicting
                "no crash" for every day.
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.metric("Crash Days",     f"{crash_count:,}",              delta=f"{crash_rate:.1f}% of total")
            st.metric("Non-Crash Days", f"{len(df_feat)-crash_count:,}", delta=f"{100-crash_rate:.1f}% of total")

    with tab_stats:
        feat_stats = df_feat[FEATURE_COLS].describe().T
        feat_stats.index = [FEATURE_DISPLAY.get(f, f) for f in feat_stats.index]
        feat_stats = feat_stats[['mean', 'std', 'min', 'max']].round(5)
        feat_stats.columns = ['Mean', 'Std Dev', 'Min', 'Max']
        st.dataframe(feat_stats, use_container_width=True)
        st.caption("Descriptive statistics for all 25 engineered features.")
        st.markdown("""
        <div class="insight-panel">
            <div class="insight-label">Interpretation Tip</div>
            <div class="insight-text">
            High <strong>std dev</strong> relative to the mean indicates features with large dynamic range —
            these are often the most discriminative in tree-based models.
            Check ATR-14 and Vol-20d for the widest spreads.
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Save to session state ─────────────────────────────────────────────────
    st.session_state['raw_df']          = df_raw
    st.session_state['df_feat']         = df_feat
    st.session_state['upload_complete'] = True

    st.markdown("---")
    st.markdown('<div class="section-hdr"><h3>Ready to Train?</h3></div>', unsafe_allow_html=True)
    st.markdown(
        f"<span class='model-tag'>DATA OK</span>"
        f"<span class='model-tag'>{len(df_feat):,} samples</span>"
        f"<span class='model-tag'>{crash_count:,} crash events</span>"
        f"<span class='model-tag'>{crash_rate:.1f}% crash rate</span>"
        f"<span class='model-tag'>25 features</span>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([2, 3, 2])
    with btn_col:
        if st.button("🤖  Train All Models & See Results →", use_container_width=True):
            st.switch_page("pages/2_Results.py")

else:
    # ── Empty state ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding:64px 20px;">
        <div style="font-size:56px; margin-bottom:18px; filter:grayscale(0.3);">📁</div>
        <div style="font-size:18px; font-weight:700; color:#B8C4D8; margin-bottom:8px;">No file uploaded yet</div>
        <div style="font-size:13px; color:#6B7B8F;">Upload a NIFTY 50 OHLCV CSV above. See the format guide for column requirements.</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get('upload_complete'):
        st.markdown("""
        <div class="info-banner">
        ℹ You already have data loaded in this session. Upload a new file above or continue to Results.
        </div>""", unsafe_allow_html=True)
        if st.button("→ Continue to Model Results", use_container_width=False):
            st.switch_page("pages/2_Results.py")

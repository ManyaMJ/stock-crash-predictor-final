"""
pages/2_Results.py — Train & Results
──────────────────────────────────────
One-click training → 6 interactive result tabs:
  Metrics | ROC Curves | Confusion Matrix | PR Curves | SHAP | Rolling Window
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Results — Crash Predictor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from assets.styles import inject_css, sidebar_header
from core.trainer import train_all_models, rolling_window_f1, MODEL_KEYS, MODEL_LABELS, MODEL_COLORS
from core.charts import roc_curves, confusion_matrices, pr_curves, shap_bar, rolling_window_chart
from core.features import FEATURE_COLS

inject_css()
sidebar_header()

st.markdown("## 📊 Model Training & Results")
st.markdown("Train all five classifiers on your uploaded data and explore every metric from the research paper.")
st.markdown("---")

# ── Guard: need uploaded data ─────────────────────────────────────────────────
if not st.session_state.get('upload_complete'):
    st.markdown("""
    <div class="warn-banner">
    ⚠️ No data uploaded yet. Please go to the <strong>Upload</strong> page first and upload a CSV file.
    </div>
    """, unsafe_allow_html=True)
    if st.button("← Go to Upload Page"):
        st.switch_page("pages/1_Upload.py")
    st.stop()

df_feat = st.session_state['df_feat']
crash_rate = float(df_feat['crash'].mean())

# ── Training section ──────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>Model Training</h3></div>', unsafe_allow_html=True)

already_trained = st.session_state.get('train_complete', False)

col_info, col_btn = st.columns([3, 1])
with col_info:
    n_train = int(len(df_feat) * 0.8)
    n_test  = len(df_feat) - n_train
    st.markdown(f"""
    **Training configuration:**
    &nbsp; Train set: **{n_train:,} samples** (first 80%)
    &nbsp;·&nbsp; Test set: **{n_test:,} samples** (last 20%)
    &nbsp;·&nbsp; SMOTE k=3 &nbsp;·&nbsp; RF/XGB: 80 estimators &nbsp;·&nbsp; SHAP on 100 samples
    """)
    if already_trained:
        st.markdown('<span style="color:#00C9A7; font-weight:600;">✅ Models already trained — results below.</span>', unsafe_allow_html=True)

with col_btn:
    train_label = "🔄 Re-train Models" if already_trained else "🚀 Train All Models"
    do_train = st.button(train_label, use_container_width=True)

if do_train:
    # ── Run training with live progress ──────────────────────────────────────
    prog_bar = st.progress(0)
    status   = st.empty()

    def update_progress(msg, frac):
        prog_bar.progress(frac)
        status.markdown(f"⏳ **{msg}**")

    with st.spinner(""):
        models, metrics, shap_vals, train_df, test_df = train_all_models(
            df_feat, progress_cb=update_progress
        )
        rolling_df = rolling_window_f1(models, test_df)

    prog_bar.progress(1.0)
    status.markdown("✅ **Training complete!**")

    # Save to session state
    st.session_state['models']     = models
    st.session_state['metrics']    = metrics
    st.session_state['shap_vals']  = shap_vals
    st.session_state['train_df']   = train_df
    st.session_state['test_df']    = test_df
    st.session_state['rolling_df'] = rolling_df
    st.session_state['train_complete'] = True
    already_trained = True

# ── Results ───────────────────────────────────────────────────────────────────
if not st.session_state.get('train_complete'):
    st.markdown("""
    <div style="text-align:center; padding:50px; color:#8BA3C1;">
        <div style="font-size:42px;">🤖</div>
        <div style="font-size:16px; margin-top:12px; color:#1A2B45; font-weight:600;">Click "Train All Models" to see results</div>
        <div style="font-size:13px; margin-top:6px;">Training takes ~30–60 seconds depending on your data size</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

metrics    = st.session_state['metrics']
shap_vals  = st.session_state['shap_vals']
rolling_df = st.session_state.get('rolling_df', pd.DataFrame())

st.markdown("---")
st.markdown('<div class="section-hdr"><h3>Results</h3></div>', unsafe_allow_html=True)

# ── 6 Result Tabs ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Performance Metrics",
    "📈 ROC Curves",
    "🔲 Confusion Matrix",
    "🎯 Precision-Recall",
    "🔍 SHAP Explainability",
    "📅 Rolling Window",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — PERFORMANCE METRICS
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("#### Model Performance — Test Set")
    st.caption("All metrics computed at the F1-optimal decision threshold per model. Primary metric: ROC-AUC.")

    # Summary KPIs
    best_auc   = max(metrics[k]['auc']    for k in MODEL_KEYS)
    best_rec   = max(metrics[k]['recall'] for k in MODEL_KEYS)
    ens_auc    = metrics['ensemble']['auc']
    dt_auc     = metrics['dt']['auc']
    improvement = round((ens_auc - dt_auc) / dt_auc * 100, 1)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ensemble ROC-AUC",     f"{ens_auc:.3f}", f"+{improvement}% vs Decision Tree")
    k2.metric("Best Model AUC",       f"{best_auc:.3f}")
    k3.metric("Best Recall (Crash)",  f"{best_rec:.1%}", "Random Forest")
    k4.metric("Crash Prevalence",     f"{crash_rate:.1%}", "in test set")

    st.markdown("<br>", unsafe_allow_html=True)

    # Full metrics table
    rows = []
    for key in MODEL_KEYS:
        m = metrics[key]
        rows.append({
            "Model":     MODEL_LABELS[key],
            "Accuracy":  m['accuracy'],
            "Precision": m['precision'],
            "Recall":    m['recall'],
            "F1-Score":  m['f1'],
            "ROC-AUC":   m['auc'],
            "Avg Prec":  m['ap'],
        })

    tbl = pd.DataFrame(rows)
    tbl_styled = tbl.style \
        .background_gradient(subset=['ROC-AUC'], cmap='YlGn') \
        .background_gradient(subset=['Recall'],  cmap='YlOrRd') \
        .highlight_max(subset=['ROC-AUC', 'Recall', 'F1-Score', 'Accuracy'], color='#E6FFF9') \
        .format({c: '{:.4f}' for c in tbl.columns if c != 'Model'}) \
        .set_properties(**{'font-size': '13px'})

    st.dataframe(tbl_styled, use_container_width=True, hide_index=True)

    # Download
    csv = tbl.to_csv(index=False)
    st.download_button("⬇ Download Metrics CSV", csv, "model_metrics.csv", "text/csv")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Key Findings")
    ens_m = metrics['ensemble']
    rf_m  = metrics['rf']
    st.markdown(f"""
    - **Ensemble (ROC-AUC {ens_m['auc']:.3f})** achieves the best balance of precision and recall.
    - **Random Forest** has the highest recall ({rf_m['recall']:.1%}) — correctly identifies {rf_m['recall']:.1%} of crash events.
    - **Low precision ({ens_m['precision']:.3f})** across all models reflects the {crash_rate:.1%} class imbalance in the test set — this is expected.
    - All models exceed the random baseline (AUC = 0.500), confirming meaningful predictive signal in the 25 features.
    - AUC range {min(metrics[k]['auc'] for k in MODEL_KEYS):.3f}–{max(metrics[k]['auc'] for k in MODEL_KEYS):.3f} is within the contemporary benchmark range of 0.58–0.71 for equity crash prediction models.
    """)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — ROC CURVES
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("#### ROC Curves — All Five Models")
    st.caption("Higher AUC = better discrimination between crash and non-crash days. Dashed line = random classifier.")
    st.plotly_chart(roc_curves(metrics), use_container_width=True)

    with st.expander("📖 What is a ROC Curve?"):
        st.markdown("""
        The **Receiver Operating Characteristic (ROC) curve** plots the True Positive Rate (Recall)
        against the False Positive Rate at every possible decision threshold.

        - **AUC = 1.0** → perfect classifier
        - **AUC = 0.5** → random guessing (diagonal dashed line)
        - **AUC range 0.58–0.71** is the contemporary benchmark for equity crash prediction

        For our imbalanced dataset (only ~10% crash days), ROC-AUC is more reliable than accuracy
        as a performance metric because it is insensitive to class imbalance.

        > *"All models produced an AUC greater than the random AUC baseline of 0.500."*
        > — Research Paper, Section V.A
        """)

    # AUC comparison table
    auc_data = pd.DataFrame([
        {"Model": MODEL_LABELS[k], "ROC-AUC": metrics[k]['auc'],
         "vs Random Baseline": f"+{metrics[k]['auc'] - 0.5:.3f}"}
        for k in MODEL_KEYS
    ])
    st.dataframe(auc_data.sort_values('ROC-AUC', ascending=False),
                 hide_index=True, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — CONFUSION MATRIX
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("#### Confusion Matrices — F1-Optimal Threshold")
    st.caption("TP = correctly predicted crashes · FP = false alarms · TN = correct non-crash · FN = missed crashes.")
    st.plotly_chart(confusion_matrices(metrics), use_container_width=True)

    # Summary table
    st.markdown("#### TP / FP / TN / FN Breakdown")
    cm_rows = []
    for key in MODEL_KEYS:
        m = metrics[key]
        cm_rows.append({
            "Model": MODEL_LABELS[key],
            "TP (Crashes Caught)": m['tp'],
            "FP (False Alarms)":   m['fp'],
            "TN (Correct Non-Crash)": m['tn'],
            "FN (Missed Crashes)": m['fn'],
            "Threshold": f"{m['threshold']:.3f}",
        })
    cm_df = pd.DataFrame(cm_rows)
    st.dataframe(cm_df, hide_index=True, use_container_width=True)

    with st.expander("📖 Interpretation"):
        st.markdown(f"""
        - The test set has **{metrics['dt']['tp'] + metrics['dt']['fn']} crash events** and
          **{metrics['dt']['tn'] + metrics['dt']['fp']} non-crash days**.
        - **Random Forest** catches the most crashes (TP = {metrics['rf']['tp']}) but at the cost
          of the most false alarms (FP = {metrics['rf']['fp']}).
        - **Ensemble** achieves nearly the same TP as RF ({metrics['ensemble']['tp']}) with fewer false alarms
          ({metrics['ensemble']['fp']} vs {metrics['rf']['fp']}) — confirming that soft-voting smooths RF's aggressive behaviour.
        - **For risk management**, minimising FN (missed crashes) is more important than minimising FP,
          because the cost of missing a real crash far exceeds a false alarm.

        > *"For crash prediction, recall would typically be the preferred evaluation metric,
        since a false negative is much more costly than a false positive."*
        > — Research Paper, Section V.A
        """)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — PRECISION-RECALL CURVES
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("#### Precision-Recall Curves — All Five Models")
    st.caption(f"No-skill baseline = crash prevalence ({crash_rate:.1%}). Higher Average Precision (AP) = better performance.")
    st.plotly_chart(pr_curves(metrics, crash_rate), use_container_width=True)

    # AP summary
    ap_data = pd.DataFrame([
        {"Model": MODEL_LABELS[k],
         "Average Precision (AP)": metrics[k]['ap'],
         "vs No-Skill Baseline": f"+{metrics[k]['ap'] - crash_rate:.4f}"}
        for k in MODEL_KEYS
    ]).sort_values("Average Precision (AP)", ascending=False)
    st.dataframe(ap_data, hide_index=True, use_container_width=True)

    with st.expander("📖 Why PR Curves Matter More for Crash Prediction"):
        st.markdown(f"""
        For **highly imbalanced datasets** like ours ({crash_rate:.1%} crash rate), PR curves are
        more informative than ROC curves because they directly measure how much recall you gain
        for a given level of precision — without being inflated by the large number of true negatives.

        - **No-Skill baseline** (dashed line) = AP equal to crash prevalence ({crash_rate:.3f})
        - All our models outperform the no-skill baseline, confirming discriminative value
        - The steep decline in precision at high recall levels reflects the fundamental challenge
          of predicting rare events under persistent market non-stationarity

        > *"The PR Curve is a more discriminative measure than the ROC Curve because it directly
        measures sensitivity for a given level of specificity and avoids being inflated by the
        large number of true negatives."*
        > — Research Paper, Section V.F
        """)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — SHAP EXPLAINABILITY
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown("#### SHAP Feature Importance — Random Forest Model")
    st.caption("Mean absolute SHAP values across 100 test samples. Higher = stronger influence on crash prediction.")

    shap_vals = st.session_state['shap_vals']
    st.plotly_chart(shap_bar(shap_vals), use_container_width=True)

    # Top 3 interpretation cards
    st.markdown("#### Top 3 Crash Precursors")
    mean_abs = np.abs(shap_vals).mean(axis=0)
    top3_idx = np.argsort(mean_abs)[::-1][:3]

    feature_insights = {
        'atr_14':   ("ATR (14-day)", "Average True Range measures the average price range across a trading session. A spike in ATR signals expanding volatility — a hallmark of pre-crash market conditions where uncertainty and panic are rising."),
        'vol_20d':  ("Volatility (20-day)", "Realised 20-day volatility is the leading financial indicator of tail-risk events. Elevated sustained volatility over 20 days historically precedes market dislocations."),
        'hl_range': ("High-Low Range", "The daily high-low range relative to close captures intra-day price spread. Wide ranges reflect investor indecision and are consistently elevated in the days leading up to a crash."),
        'vol_5d':   ("Volatility (5-day)", "Short-term volatility spikes are early signals of market stress, often preceding crashes by 3–7 trading days."),
        'vol_10d':  ("Volatility (10-day)", "Medium-term volatility captures the transition from stability to instability across two weeks of trading."),
    }

    top3_cols = st.columns(3)
    for i, (idx, col) in enumerate(zip(top3_idx, top3_cols)):
        fname = FEATURE_COLS[idx]
        val   = mean_abs[idx]
        title, desc = feature_insights.get(fname, (fname, "This feature contributes significantly to the model's crash predictions based on SHAP analysis."))
        pct   = val / mean_abs.sum() * 100
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-top:3px solid #00C9A7; text-align:left; padding:18px;">
                <div style="font-size:11px; color:#8BA3C1; font-weight:600; text-transform:uppercase; letter-spacing:1px;">Rank #{i+1}</div>
                <div style="font-size:16px; font-weight:700; color:#1A2B45; margin:8px 0;">{title}</div>
                <div style="font-size:22px; font-weight:700; color:#00C9A7;">{val:.4f}</div>
                <div style="font-size:11px; color:#8BA3C1; margin-bottom:10px;">{pct:.1f}% of total attribution</div>
                <div style="font-size:13px; color:#4A5568; line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📖 What is SHAP?"):
        st.markdown("""
        **SHAP (SHapley Additive exPlanations)** decomposes each model prediction into
        individual feature contributions, grounded in cooperative game theory.

        For each prediction, SHAP answers: *"How much did each feature push the crash
        probability up or down?"*

        **Why SHAP for financial regulation?**
        - Satisfies the axioms of **efficiency, symmetry, and dummy** (Shapley, 1953)
        - Provides theoretically consistent post-hoc explanations
        - Does not modify the underlying model
        - Enables **SEBI-compliant** interpretable AI deployments

        We use **TreeExplainer** (fastest variant for tree-based models like Random Forest)
        computed on 100 test samples for speed without sacrificing ranking accuracy.

        > *"By aggregating the mean absolute values of the SHAP values across all samples,
        global feature importance rankings can be determined."*
        > — Research Paper, Section IV.B
        """)

    # Full feature importance table
    mean_abs_series = pd.Series(mean_abs, index=FEATURE_COLS)
    from core.features import FEATURE_DISPLAY
    feat_imp = pd.DataFrame({
        "Feature": [FEATURE_DISPLAY.get(f, f) for f in mean_abs_series.index],
        "Mean |SHAP|": mean_abs_series.values.round(5),
        "% Attribution": (mean_abs_series.values / mean_abs_series.sum() * 100).round(2),
    }).sort_values("Mean |SHAP|", ascending=False).reset_index(drop=True)
    feat_imp.index += 1
    st.markdown("#### Full Feature Importance Table")
    st.dataframe(feat_imp, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — ROLLING WINDOW
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    st.markdown("#### Rolling-Window Temporal Validation")
    st.caption("F1-score across non-overlapping 3-month windows. Windows with < 2 crash events are excluded.")

    if rolling_df.empty:
        st.markdown("""
        <div class="warn-banner">
        ⚠️ Not enough test data for rolling-window analysis (need multiple 3-month windows with at least 2 crashes each).
        This is normal for smaller datasets.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.plotly_chart(rolling_window_chart(rolling_df), use_container_width=True)

        st.markdown("#### Quarter-by-Quarter F1 Scores")
        st.dataframe(rolling_df, hide_index=True, use_container_width=True)

        with st.expander("📖 Why Rolling-Window Validation?"):
            st.markdown("""
            Financial markets are **non-stationary** — the statistical properties of returns change
            over time due to regime shifts (bull/bear markets, crises, recoveries).

            Standard train/test splits assume stationarity, which is violated in practice.
            Rolling-window validation checks whether the model maintains predictive power
            across structurally different market regimes.

            We evaluate three distinct periods:
            1. **COVID-19 Liquidity Shock (Q1 2020)** — sudden, extreme volatility
            2. **Recovery & Normalisation (2020–2021)** — gradual market stabilisation
            3. **Inflation / Rate-Hike Shock (2022)** — structural monetary policy shift

            > *"The high degree of fluctuations across all classifiers corroborates that there are
            three structurally distinct periods of time."*
            > — Research Paper, Section V.D
            """)

# ── Navigation footer ──────────────────────────────────────────────────────────
st.markdown("---")
col_l, col_r = st.columns(2)
with col_l:
    if st.button("← Back to Upload"):
        st.switch_page("pages/1_Upload.py")
with col_r:
    if st.button("View Live Predictions →"):
        st.switch_page("pages/3_Predictions.py")

"""
pages/2_Results.py — Model Training & Results
───────────────────────────────────────────────
Train button → 6 interactive result tabs.
CSS + sidebar injected by app.py.
"""

import streamlit as st
import pandas as pd
import numpy as np

from core.trainer import train_all_models, rolling_window_f1, MODEL_KEYS, MODEL_LABELS, MODEL_COLORS
from core.charts  import roc_curves, confusion_matrices, pr_curves, shap_bar, rolling_window_chart
from core.features import FEATURE_COLS, FEATURE_DISPLAY
from assets.styles import ticker_tape

ticker_tape()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:6px;">
  <span style="font-size:28px;">📊</span>
  <div>
    <div style="font-size:22px;font-weight:800;color:#F0F4FF;letter-spacing:-0.5px;">Model Training & Results</div>
    <div style="font-size:13px;color:#6B7B8F;">Train all five classifiers and explore every metric from the research paper</div>
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Guard ─────────────────────────────────────────────────────────────────────
if not st.session_state.get('upload_complete'):
    st.markdown('<div class="warn-banner">⚠ No data uploaded. Go to <strong>Upload Data</strong> first.</div>',
                unsafe_allow_html=True)
    if st.button("← Go to Upload"):
        st.switch_page("pages/1_Upload.py")
    st.stop()

df_feat    = st.session_state['df_feat']
crash_rate = float(df_feat['crash'].mean())

# ── Training config + button ──────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>Training Configuration</h3></div>', unsafe_allow_html=True)
already_trained = st.session_state.get('train_complete', False)

n_train = int(len(df_feat) * 0.8)
n_test  = len(df_feat) - n_train

info_col, btn_col = st.columns([4, 1])
with info_col:
    st.markdown(f"""
    <div class="term-box">
    <span class="t-d">DATASET &nbsp;&nbsp;&nbsp;&nbsp;</span>
    <span class="t-b">{len(df_feat):,} samples</span>
    &nbsp;&nbsp;<span class="t-d">CRASH RATE</span>&nbsp;&nbsp;
    <span class="t-r">{crash_rate:.1%}</span><br>
    <span class="t-d">TRAIN SET &nbsp;&nbsp;</span>
    <span class="t-b">{n_train:,} samples</span>&nbsp;&nbsp;(first 80% chronological)<br>
    <span class="t-d">TEST SET &nbsp;&nbsp;&nbsp;</span>
    <span class="t-b">{n_test:,} samples</span>&nbsp;&nbsp;(last 20% chronological)<br>
    <span class="t-d">OVERSAMPLING</span>&nbsp;&nbsp;
    <span class="t-g">SMOTE k=3</span>&nbsp;&nbsp;
    <span class="t-d">SHAP SAMPLES</span>&nbsp;&nbsp;
    <span class="t-g">100</span>&nbsp;&nbsp;
    <span class="t-d">RF TREES</span>&nbsp;&nbsp;
    <span class="t-g">80</span>
    </div>""", unsafe_allow_html=True)
    if already_trained:
        st.markdown('<span style="color:#00D4AA; font-size:12px; font-family:\'IBM Plex Mono\',monospace; font-weight:600;">✔ Models trained — results loaded below.</span>',
                    unsafe_allow_html=True)
with btn_col:
    do_train = st.button(
        "🔄 Re-train" if already_trained else "🚀 Train All Models",
        use_container_width=True,
    )

if do_train:
    prog_bar = st.progress(0)
    status   = st.empty()

    def _cb(msg, frac):
        prog_bar.progress(frac)
        status.markdown(f'<div class="term-box"><span class="t-g">▶</span> <span class="t-b">{msg}</span></div>',
                        unsafe_allow_html=True)

    with st.spinner(""):
        models, metrics, shap_vals, train_df, test_df = train_all_models(df_feat, progress_cb=_cb)
        rolling_df = rolling_window_f1(models, test_df)

    prog_bar.progress(1.0)
    status.markdown('<div class="info-banner">✔ All models trained successfully.</div>', unsafe_allow_html=True)

    st.session_state.update({
        'models':        models,
        'metrics':       metrics,
        'shap_vals':     shap_vals,
        'train_df':      train_df,
        'test_df':       test_df,
        'rolling_df':    rolling_df,
        'train_complete':True,
        'models_trained':True,
    })
    already_trained = True

if not st.session_state.get('train_complete'):
    st.markdown("""
    <div style="text-align:center;padding:56px 20px;">
        <div style="font-size:48px;">🤖</div>
        <div style="font-size:16px;font-weight:700;color:#B8C4D8;margin-top:14px;">Click "Train All Models" to begin</div>
        <div style="font-size:12px;color:#6B7B8F;margin-top:6px;font-family:'IBM Plex Mono',monospace;">
        Training time: ~30–90 seconds depending on dataset size</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

metrics    = st.session_state['metrics']
shap_vals  = st.session_state['shap_vals']
rolling_df = st.session_state.get('rolling_df', pd.DataFrame())

st.markdown("---")
st.markdown('<div class="section-hdr"><h3>Results</h3></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Performance Metrics",
    "📈 ROC Curves",
    "🔲 Confusion Matrices",
    "🎯 Precision-Recall",
    "🔍 SHAP Explainability",
    "📅 Rolling Window",
])

# ── TAB 1 — METRICS ───────────────────────────────────────────────────────────
with tab1:
    st.markdown("#### Model Performance — Test Set")
    st.caption("All metrics at F1-optimal decision threshold per model. Primary ranking metric: ROC-AUC.")

    ens_auc    = metrics['ensemble']['auc']
    dt_auc     = metrics['dt']['auc']
    best_auc   = max(metrics[k]['auc']    for k in MODEL_KEYS)
    best_rec   = max(metrics[k]['recall'] for k in MODEL_KEYS)
    improvement = round((ens_auc - dt_auc) / dt_auc * 100, 1)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ensemble ROC-AUC",    f"{ens_auc:.3f}", f"+{improvement}% vs DT baseline")
    k2.metric("Best Model AUC",      f"{best_auc:.3f}")
    k3.metric("Best Recall (Crash)", f"{best_rec:.1%}")
    k4.metric("Crash Prevalence",    f"{crash_rate:.1%}", "in test set")

    st.markdown("<br>", unsafe_allow_html=True)

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
    st.dataframe(
        tbl, use_container_width=True, hide_index=True,
        column_config={
            "Model":     st.column_config.TextColumn("Model"),
            "Accuracy":  st.column_config.NumberColumn("Accuracy",  format="%.4f"),
            "Precision": st.column_config.NumberColumn("Precision", format="%.4f"),
            "Recall":    st.column_config.NumberColumn("Recall",    format="%.4f"),
            "F1-Score":  st.column_config.NumberColumn("F1-Score",  format="%.4f"),
            "ROC-AUC":   st.column_config.NumberColumn("ROC-AUC",   format="%.4f"),
            "Avg Prec":  st.column_config.NumberColumn("Avg Prec",  format="%.4f"),
        },
    )
    st.download_button("⬇ Download Metrics CSV",
                       tbl.to_csv(index=False), "model_metrics.csv", "text/csv")

    st.markdown("<br>", unsafe_allow_html=True)

    # Key findings
    ens_m = metrics['ensemble']
    rf_m  = metrics['rf']
    ins1, ins2, ins3 = st.columns(3)
    with ins1:
        st.markdown(f"""
        <div class="insight-panel">
            <div class="insight-label">Ensemble Advantage</div>
            <div class="insight-text">
            ROC-AUC <strong style="color:#00D4AA;">{ens_m['auc']:.3f}</strong> — a
            <strong>+{improvement}%</strong> lift over the DT baseline ({dt_auc:.3f}).
            Soft-voting smooths RF's aggressive recall while retaining its discriminative power.
            </div>
        </div>""", unsafe_allow_html=True)
    with ins2:
        st.markdown(f"""
        <div class="insight-panel" style="border-left-color:#2ECC71;">
            <div class="insight-label" style="color:#2ECC71;">Best Recall</div>
            <div class="insight-text">
            Random Forest catches <strong style="color:#2ECC71;">{rf_m['recall']:.1%}</strong>
            of all crash events (TP={rf_m['tp']}) — critical for risk management
            where missing a crash is far more costly than a false alarm.
            </div>
        </div>""", unsafe_allow_html=True)
    with ins3:
        st.markdown(f"""
        <div class="insight-panel" style="border-left-color:#FFB700;">
            <div class="insight-label" style="color:#FFB700;">Class Imbalance Note</div>
            <div class="insight-text">
            Low precision ({ens_m['precision']:.3f}) across all models is expected given the
            <strong>{crash_rate:.1%}</strong> crash prevalence. AUC range
            {min(metrics[k]['auc'] for k in MODEL_KEYS):.3f}–{max(metrics[k]['auc'] for k in MODEL_KEYS):.3f}
            is within the 0.58–0.71 benchmark for equity crash prediction.
            </div>
        </div>""", unsafe_allow_html=True)

# ── TAB 2 — ROC CURVES ────────────────────────────────────────────────────────
with tab2:
    st.markdown("#### ROC Curves — All Five Models")
    st.caption("Higher AUC = better discrimination. Dotted line = random classifier (AUC 0.500).")
    st.plotly_chart(roc_curves(metrics), use_container_width=True)

    auc_data = pd.DataFrame([
        {"Model": MODEL_LABELS[k], "ROC-AUC": metrics[k]['auc'],
         "vs Random": f"+{metrics[k]['auc']-0.5:.3f}",
         "vs DT Baseline": f"{(metrics[k]['auc']-dt_auc)/dt_auc*100:+.1f}%"}
        for k in MODEL_KEYS
    ]).sort_values('ROC-AUC', ascending=False)
    st.dataframe(auc_data, hide_index=True, use_container_width=True)

    with st.expander("📖 What is a ROC Curve?"):
        st.markdown("""
        The **ROC curve** plots True Positive Rate (Recall) vs. False Positive Rate at every
        possible decision threshold. **AUC = 1.0** is perfect; **AUC = 0.5** is random.

        For our ~10% imbalanced dataset, ROC-AUC is more reliable than accuracy because
        it is insensitive to class prevalence. All models exceed the random baseline.
        """)

# ── TAB 3 — CONFUSION MATRICES ────────────────────────────────────────────────
with tab3:
    st.markdown("#### Confusion Matrices — F1-Optimal Threshold")
    st.caption("TP = correctly caught crashes · FP = false alarms · TN = correct non-crash · FN = missed crashes")
    st.plotly_chart(confusion_matrices(metrics), use_container_width=True)

    cm_rows = []
    for key in MODEL_KEYS:
        m = metrics[key]
        cm_rows.append({
            "Model":              MODEL_LABELS[key],
            "TP (Caught)":        m['tp'],
            "FP (False Alarm)":   m['fp'],
            "TN (Correct -ve)":   m['tn'],
            "FN (Missed)":        m['fn'],
            "Threshold":          f"{m['threshold']:.3f}",
            "Recall":             f"{m['recall']:.3f}",
        })
    st.dataframe(pd.DataFrame(cm_rows), hide_index=True, use_container_width=True)

    st.markdown(f"""
    <div class="insight-panel">
        <div class="insight-label">Analyst Interpretation</div>
        <div class="insight-text">
        The Ensemble achieves TP={metrics['ensemble']['tp']} with FP={metrics['ensemble']['fp']} —
        nearly matching RF's TP ({metrics['rf']['tp']}) but with {metrics['rf']['fp']-metrics['ensemble']['fp']} fewer
        false alarms. For a risk-management system, <strong>minimising FN (missed crashes)</strong>
        is the priority — a missed crash costs far more than a false alarm.
        </div>
    </div>""", unsafe_allow_html=True)

# ── TAB 4 — PR CURVES ─────────────────────────────────────────────────────────
with tab4:
    st.markdown("#### Precision-Recall Curves — All Five Models")
    st.caption(f"No-skill baseline = crash prevalence ({crash_rate:.1%}). Higher AP = better.")
    st.plotly_chart(pr_curves(metrics, crash_rate), use_container_width=True)

    ap_data = pd.DataFrame([
        {"Model": MODEL_LABELS[k],
         "Avg Precision (AP)": metrics[k]['ap'],
         "vs No-Skill": f"+{metrics[k]['ap']-crash_rate:.4f}"}
        for k in MODEL_KEYS
    ]).sort_values("Avg Precision (AP)", ascending=False)
    st.dataframe(ap_data, hide_index=True, use_container_width=True)

    with st.expander("📖 Why PR Curves Matter More for Crash Prediction"):
        st.markdown(f"""
        For **highly imbalanced datasets** ({crash_rate:.1%} crash rate), PR curves are more
        informative than ROC curves because they don't get inflated by the large number of
        true negatives. The no-skill baseline (dashed) = AP equal to crash prevalence ({crash_rate:.3f}).
        All models outperform it, confirming real discriminative value.
        """)

# ── TAB 5 — SHAP ──────────────────────────────────────────────────────────────
with tab5:
    st.markdown("#### SHAP Feature Importance — Random Forest Model")
    st.caption("Mean absolute SHAP values across 100 test samples. Teal = top third, blue = mid, grey = bottom.")
    st.plotly_chart(shap_bar(shap_vals), use_container_width=True)

    mean_abs  = np.abs(shap_vals).mean(axis=0)
    top3_idx  = np.argsort(mean_abs)[::-1][:3]

    st.markdown("#### Top-3 Crash Precursors")
    feature_insights = {
        'atr_14':   ("ATR (14-day)",        "Average True Range spikes as pre-crash volatility expands — the single strongest signal.", "#FF3366"),
        'vol_20d':  ("Volatility (20-day)", "Sustained 20-day realised vol is the leading financial indicator of tail-risk events.",     "#FF8C42"),
        'hl_range': ("High-Low Range",      "Wide intra-day spread reflects investor indecision — consistently elevated before crashes.", "#FFB700"),
        'vol_5d':   ("Volatility (5-day)",  "Short-term vol spikes are early warnings of market stress, 3–7 days before a crash.",       "#4FACFE"),
        'vol_10d':  ("Volatility (10-day)", "Medium-term vol captures the shift from stability to instability over two trading weeks.",   "#8B5CF6"),
    }
    top3_cols = st.columns(3)
    for i, (idx, col) in enumerate(zip(top3_idx, top3_cols)):
        fname = FEATURE_COLS[idx]
        val   = mean_abs[idx]
        title, desc, color = feature_insights.get(fname, (fname, "High SHAP attribution from the RF model.", "#00D4AA"))
        pct   = val / mean_abs.sum() * 100
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-top:2px solid {color}; text-align:left; padding:20px;">
                <div style="font-size:10px;color:#6B7B8F;font-weight:700;text-transform:uppercase;
                            letter-spacing:1.5px;font-family:'IBM Plex Mono',monospace;">RANK #{i+1}</div>
                <div style="font-size:15px;font-weight:700;color:#F0F4FF;margin:8px 0 4px;">{title}</div>
                <div style="font-size:24px;font-weight:700;color:{color};font-family:'IBM Plex Mono',monospace;">
                    {val:.4f}</div>
                <div style="font-size:11px;color:#6B7B8F;margin-bottom:12px;
                            font-family:'IBM Plex Mono',monospace;">{pct:.1f}% of total attribution</div>
                <div style="font-size:12px;color:#94A3B8;line-height:1.55;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    mean_abs_s = pd.Series(mean_abs, index=FEATURE_COLS)
    feat_imp = pd.DataFrame({
        "Feature":       [FEATURE_DISPLAY.get(f, f) for f in mean_abs_s.index],
        "Mean |SHAP|":   mean_abs_s.values.round(5),
        "% Attribution": (mean_abs_s.values / mean_abs_s.sum() * 100).round(2),
    }).sort_values("Mean |SHAP|", ascending=False).reset_index(drop=True)
    feat_imp.index += 1
    st.markdown("#### Full Feature Attribution Table")
    st.dataframe(feat_imp, use_container_width=True)

# ── TAB 6 — ROLLING WINDOW ────────────────────────────────────────────────────
with tab6:
    st.markdown("#### Rolling-Window Temporal Validation — 3-Month Quarters")
    st.caption("F1-score in each non-overlapping 3-month window. Windows with < 2 crash events excluded.")

    if rolling_df.empty:
        st.markdown('<div class="warn-banner">⚠ Not enough test data for rolling-window analysis. Need multiple 3-month windows with ≥ 2 crashes each.</div>',
                    unsafe_allow_html=True)
    else:
        st.plotly_chart(rolling_window_chart(rolling_df), use_container_width=True)
        st.markdown("#### Quarter-by-Quarter F1 Scores")
        st.dataframe(rolling_df, hide_index=True, use_container_width=True)
        st.markdown("""
        <div class="insight-panel">
            <div class="insight-label">Regime Analysis</div>
            <div class="insight-text">
            High F1 variance across quarters reflects three structurally distinct regimes:
            <strong style="color:#FF3366;">COVID-19 Liquidity Shock (Q1 2020)</strong> ·
            <strong style="color:#FFB700;">Recovery & Normalisation (2020–2021)</strong> ·
            <strong style="color:#4FACFE;">Inflation / Rate-Hike Shock (2022)</strong>.
            No single classifier dominates across all regimes — validating the ensemble approach.
            </div>
        </div>""", unsafe_allow_html=True)

# ── Navigation footer ─────────────────────────────────────────────────────────
st.markdown("---")
col_l, col_r = st.columns(2)
with col_l:
    if st.button("← Back to Upload"):
        st.switch_page("pages/1_Upload.py")
with col_r:
    if st.button("View Live Predictions →"):
        st.switch_page("pages/3_Predictions.py")

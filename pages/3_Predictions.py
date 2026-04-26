"""
pages/3_Predictions.py — Live Predictions
───────────────────────────────────────────
Risk gauge · threshold slider · crash probability timeline · risk table · CSV.
CSS + sidebar injected by app.py.
"""

import io
import streamlit as st
import pandas as pd
import numpy as np

from core.features import FEATURE_COLS
from core.charts   import prediction_timeline, risk_gauge
from assets.styles import ticker_tape

ticker_tape()

# ── Guard ─────────────────────────────────────────────────────────────────────
if not st.session_state.get('models_trained'):
    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:6px;">
      <span style="font-size:28px;">🔮</span>
      <div>
        <div style="font-size:22px;font-weight:800;color:#F0F4FF;letter-spacing:-0.5px;">Live Predictions</div>
        <div style="font-size:13px;color:#6B7B8F;">Train models first to generate predictions</div>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="warn-banner">⚠ Models not trained yet. Go to <strong>Model Results</strong> and click <em>Train All Models</em>.</div>',
                unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("← Back to Upload", use_container_width=True):
            st.switch_page("pages/1_Upload.py")
    with col_b:
        if st.button("Train Models →", use_container_width=True):
            st.switch_page("pages/2_Results.py")
    st.stop()

# ── Pull session state ────────────────────────────────────────────────────────
models  = st.session_state['models']
metrics = st.session_state['metrics']
df_feat = st.session_state['df_feat']

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:6px;">
  <span style="font-size:28px;">🔮</span>
  <div>
    <div style="font-size:22px;font-weight:800;color:#F0F4FF;letter-spacing:-0.5px;">Live Predictions</div>
    <div style="font-size:13px;color:#6B7B8F;">Adjust threshold · explore the probability timeline · download results</div>
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Controls ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>Prediction Settings</h3></div>', unsafe_allow_html=True)
ctrl1, ctrl2, ctrl3 = st.columns([1, 2, 1])

with ctrl1:
    model_choice = st.selectbox(
        "Model",
        ["Ensemble ★", "Random Forest", "XGBoost", "Logistic Regression", "Decision Tree"],
        index=0,
    )
MODEL_NAME_MAP = {
    "Ensemble ★":         "ensemble",
    "Random Forest":       "rf",
    "XGBoost":             "xgb",
    "Logistic Regression": "lr",
    "Decision Tree":       "dt",
}
model_key     = MODEL_NAME_MAP[model_choice]
chosen_model  = models[model_key]
default_thresh = float(metrics[model_key].get('threshold', 0.50))

with ctrl2:
    threshold = st.slider(
        "Decision Threshold",
        min_value=0.05, max_value=0.95, value=default_thresh, step=0.01,
        help="Lower → higher recall (catch more crashes, more false alarms). "
             "Higher → higher precision (fewer alerts, some crashes missed).",
    )
with ctrl3:
    view_mode = st.selectbox("Table View", ["All Days", "High-Risk Only"], index=0)

st.markdown("<br>", unsafe_allow_html=True)

# ── Build prediction dataframe ────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def build_pred_df(df_json: str, model_key_inner: str) -> pd.DataFrame:
    df = pd.read_json(io.StringIO(df_json))
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    X     = df[FEATURE_COLS].values
    proba = st.session_state['models'][model_key_inner].predict_proba(X)[:, 1]
    return pd.DataFrame({
        'date':         df['date'],
        'close':        df['close'],
        'crash_prob':   proba,
        'actual_crash': df['crash'].astype(int),
    })

with st.spinner("Computing crash probabilities…"):
    pred_df = build_pred_df(df_feat.to_json(), model_key)

pred_df['predicted_crash'] = (pred_df['crash_prob'] >= threshold).astype(int)
pred_df['risk_level'] = pd.cut(
    pred_df['crash_prob'],
    bins=[0, 0.30, 0.50, 0.70, 1.01],
    labels=['🟢 Low', '🟡 Medium', '🟠 High', '🔴 Very High'],
    right=False,
)

# ── Summary KPIs + Risk Gauge ─────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>Prediction Summary</h3></div>', unsafe_allow_html=True)

n_total    = len(pred_df)
n_alerts   = int(pred_df['predicted_crash'].sum())
n_actual   = int(pred_df['actual_crash'].sum())
alert_rate = n_alerts / n_total * 100
correct_caught = int(((pred_df['predicted_crash'] == 1) & (pred_df['actual_crash'] == 1)).sum())
recall_pct = correct_caught / n_actual * 100 if n_actual > 0 else 0.0
avg_prob   = float(pred_df['crash_prob'].mean())
highest    = pred_df.loc[pred_df['crash_prob'].idxmax()]

gauge_col, kpi_col = st.columns([1, 3])

with gauge_col:
    st.plotly_chart(risk_gauge(avg_prob, model_choice), use_container_width=True)

with kpi_col:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Days Analysed",    f"{n_total:,}")
    k2.metric("Crash Alerts",     f"{n_alerts:,}",     delta=f"{alert_rate:.1f}% of days")
    k3.metric("Crashes Caught",   f"{correct_caught:,}", delta=f"{recall_pct:.1f}% recall")
    k4.metric("Actual Crashes",   f"{n_actual:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Risk breakdown mini-bar
    risk_counts = pred_df['risk_level'].value_counts()
    rc1, rc2, rc3, rc4 = st.columns(4)
    for col, label, cls in [
        (rc1, '🟢 Low',       'risk-low'),
        (rc2, '🟡 Medium',    'risk-medium'),
        (rc3, '🟠 High',      'risk-high'),
        (rc4, '🔴 Very High', 'risk-vhigh'),
    ]:
        cnt = int(risk_counts.get(label, 0))
        pct = cnt / n_total * 100
        with col:
            st.markdown(f"""
            <div style="background:#0F1629;border:1px solid rgba(255,255,255,0.06);
                        border-radius:8px;padding:12px 14px;text-align:center;">
                <div class="{cls}" style="font-size:18px;font-weight:700;">{cnt:,}</div>
                <div style="font-size:10px;color:#6B7B8F;margin-top:3px;">{label} · {pct:.1f}%</div>
            </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:10px; font-size:11px; color:#6B7B8F; font-family:'IBM Plex Mono',monospace;">
    ⚡ Highest risk day: <strong style="color:#FF3366;">
    {highest['date'].strftime('%d %b %Y')}</strong>
    &nbsp;·&nbsp; prob = <strong style="color:#FF3366;">{highest['crash_prob']:.4f}</strong>
    &nbsp;·&nbsp; actual crash = <strong>{'YES' if highest['actual_crash'] else 'NO'}</strong>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Timeline ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>Crash Probability Timeline</h3></div>', unsafe_allow_html=True)
st.markdown(
    f'<span class="model-tag">{model_choice}</span>'
    f'<span class="model-tag">THRESHOLD {threshold:.2f}</span>'
    f'<span class="model-tag">F1-OPT {default_thresh:.2f}</span>'
    f'<span style="font-size:12px;color:#6B7B8F;margin-left:6px;">'
    f'Red dots = predicted crash alerts · Bottom panel: probability vs threshold</span>',
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)
st.plotly_chart(prediction_timeline(pred_df, threshold), use_container_width=True)

# ── Risk Table ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr" style="margin-top:20px;"><h3>Prediction Table</h3></div>',
            unsafe_allow_html=True)

display_df = (pred_df[pred_df['predicted_crash'] == 1].copy()
              if view_mode == "High-Risk Only" else pred_df.copy())

if view_mode == "High-Risk Only":
    st.markdown(f'<div class="info-banner">Showing <strong>{len(display_df):,}</strong> high-risk days (threshold ≥ {threshold:.2f}).</div>',
                unsafe_allow_html=True)

table_df = display_df[['date','close','crash_prob','risk_level','actual_crash','predicted_crash']].copy()
table_df.columns = ['Date','Close Price','Crash Probability','Risk Level','Actual Crash','Predicted Crash']
table_df['Date']             = table_df['Date'].dt.strftime('%d %b %Y')
table_df['Close Price']      = table_df['Close Price'].map('₹{:,.2f}'.format)
table_df['Crash Probability']= table_df['Crash Probability'].map('{:.4f}'.format)
table_df['Actual Crash']     = table_df['Actual Crash'].map({0: '✗ No', 1: '✅ Yes'})
table_df['Predicted Crash']  = table_df['Predicted Crash'].map({0: '—', 1: '⚠ Alert'})

st.dataframe(table_df, use_container_width=True, hide_index=True, height=360)
st.caption(f"Showing {len(table_df):,} rows · toggle to High-Risk Only to filter")

# ── Download ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr" style="margin-top:20px;"><h3>Download Results</h3></div>',
            unsafe_allow_html=True)

dl_df = pred_df[['date','close','crash_prob','predicted_crash','actual_crash','risk_level']].copy()
dl_df.columns = ['date','close','crash_probability','predicted_crash','actual_crash','risk_level']
dl_df['threshold_used'] = threshold
dl_df['model']          = model_choice
csv_bytes = dl_df.to_csv(index=False).encode('utf-8')

dl1, dl2 = st.columns([1, 3])
with dl1:
    st.download_button(
        "⬇  Download Predictions CSV",
        data=csv_bytes,
        file_name=f"crash_predictions_{model_key}_t{threshold:.2f}.csv",
        mime="text/csv",
        use_container_width=True,
    )
with dl2:
    st.markdown(
        f"<div style='padding-top:10px;color:#4A5568;font-size:12px;font-family:\"IBM Plex Mono\",monospace;'>"
        f"date · close · crash_probability · predicted_crash · actual_crash · risk_level · threshold ({threshold:.2f}) · model</div>",
        unsafe_allow_html=True,
    )

# ── Threshold guide ───────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📖 Threshold Guide — How to Choose Your Operating Point"):
    st.markdown(f"""
    The **decision threshold** converts a continuous crash probability into a binary alert.

    | Threshold Range | Effect | Use Case |
    |----------------|--------|----------|
    | **0.20 – 0.35** | High recall, many alerts, more false positives | Conservative risk mgmt — catch every possible crash |
    | **0.40 – 0.55** | Balanced · F1-optimal = **{default_thresh:.2f}** | General purpose · research benchmark |
    | **0.65 – 0.85** | High precision, fewer alerts, some crashes missed | Signal-quality-focused trading strategies |

    **Risk Level Bands:**
    - <span class="risk-low">🟢 Low</span> — probability < 0.30 (unlikely crash)
    - <span class="risk-medium">🟡 Medium</span> — 0.30–0.50 (elevated caution)
    - <span class="risk-high">🟠 High</span> — 0.50–0.70 (significant risk signal)
    - <span class="risk-vhigh">🔴 Very High</span> — ≥ 0.70 (strong crash precursor)

    > *The F1-optimal threshold ({default_thresh:.2f}) was chosen to maximise the harmonic mean of
    > precision and recall on the 2020–2023 out-of-sample test set.*
    """, unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
st.markdown("---")
nav1, _, nav3 = st.columns([2, 3, 2])
with nav1:
    if st.button("← Back to Results", use_container_width=True):
        st.switch_page("pages/2_Results.py")
with nav3:
    if st.button("⬆ Upload New Data", use_container_width=True):
        for key in ['raw_df','df_feat','upload_complete','models_trained',
                    'models','metrics','shap_vals','train_df','test_df','train_complete']:
            st.session_state.pop(key, None)
        st.switch_page("pages/1_Upload.py")

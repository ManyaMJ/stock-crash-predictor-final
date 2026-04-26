"""
pages/3_Predictions.py — Live Predictions
──────────────────────────────────────────
Threshold slider · crash probability timeline · risk table · CSV download.
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Predictions — Crash Predictor",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

from assets.styles import inject_css, sidebar_header
from core.features import FEATURE_COLS
from core.charts import prediction_timeline

inject_css()
sidebar_header()

# ── Guard: need models trained ────────────────────────────────────────────────
if not st.session_state.get('models_trained'):
    st.markdown("## 🔮 Predictions")
    st.markdown("""
    <div class="warn-banner">
    ⚠️ Models have not been trained yet. Please go to the <strong>Results</strong> page first
    and click <em>Train All Models</em>.
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("← Back to Upload", use_container_width=True):
            st.switch_page("pages/1_Upload.py")
    with col_b:
        if st.button("Go to Results & Train →", use_container_width=True):
            st.switch_page("pages/2_Results.py")
    st.stop()

# ── Pull data from session state ──────────────────────────────────────────────
models   = st.session_state['models']
metrics  = st.session_state['metrics']
df_feat  = st.session_state['df_feat']
test_df  = st.session_state.get('test_df', None)
train_df = st.session_state.get('train_df', None)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("## 🔮 Live Predictions")
st.markdown(
    "Adjust the decision threshold below to control sensitivity. "
    "The crash probability timeline updates instantly — download your results as CSV when ready."
)
st.markdown("---")

# ── Model selector + threshold slider ────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>Prediction Settings</h3></div>', unsafe_allow_html=True)

ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 2, 1])

with ctrl_col1:
    model_choice = st.selectbox(
        "Select Model",
        options=["Ensemble ★", "Random Forest", "XGBoost", "Logistic Regression", "Decision Tree"],
        index=0,
        help="Ensemble combines LR + RF + XGBoost via soft voting.",
    )

MODEL_NAME_MAP = {
    "Ensemble ★":         "ensemble",
    "Random Forest":       "rf",
    "XGBoost":             "xgb",
    "Logistic Regression": "lr",
    "Decision Tree":       "dt",
}
model_key = MODEL_NAME_MAP[model_choice]
chosen_model = models[model_key]

# Default threshold to the F1-optimal one stored in metrics
default_thresh = float(metrics[model_key].get('threshold', 0.50))

with ctrl_col2:
    threshold = st.slider(
        "Decision Threshold",
        min_value=0.05,
        max_value=0.95,
        value=default_thresh,
        step=0.01,
        help="Lower threshold → higher recall (catch more crashes, more false alarms). "
             "Higher threshold → higher precision (fewer alerts, some crashes missed).",
    )

with ctrl_col3:
    view_mode = st.selectbox(
        "View",
        options=["All Days", "High-Risk Only"],
        index=0,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Build prediction dataframe for the ENTIRE dataset ─────────────────────────
@st.cache_data(show_spinner=False)
def build_pred_df(df_json: str, model_key_inner: str) -> pd.DataFrame:
    """Run chosen model on the full feature set and return prediction df."""
    import json, io
    df = pd.read_json(io.StringIO(df_json))
    # ensure date column is datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])

    X = df[FEATURE_COLS].values
    model_obj = st.session_state['models'][model_key_inner]
    proba = model_obj.predict_proba(X)[:, 1]

    pred_df = pd.DataFrame({
        'date':         df['date'],
        'close':        df['close'],
        'crash_prob':   proba,
        'actual_crash': df['crash'].astype(int),
    })
    return pred_df


with st.spinner("Computing crash probabilities…"):
    df_json = df_feat.to_json()
    pred_df = build_pred_df(df_json, model_key)

# Apply threshold to get predicted labels
pred_df['predicted_crash'] = (pred_df['crash_prob'] >= threshold).astype(int)
pred_df['risk_level'] = pd.cut(
    pred_df['crash_prob'],
    bins=[0, 0.30, 0.50, 0.70, 1.01],
    labels=['🟢 Low', '🟡 Medium', '🟠 High', '🔴 Very High'],
    right=False,
)

# ── KPI summary row ───────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>Prediction Summary</h3></div>', unsafe_allow_html=True)

n_total     = len(pred_df)
n_alerts    = int(pred_df['predicted_crash'].sum())
n_actual    = int(pred_df['actual_crash'].sum())
alert_rate  = n_alerts / n_total * 100
if n_actual > 0:
    correct_caught = int(
        ((pred_df['predicted_crash'] == 1) & (pred_df['actual_crash'] == 1)).sum()
    )
    recall_pct = correct_caught / n_actual * 100
else:
    recall_pct = 0.0

highest_risk_row = pred_df.loc[pred_df['crash_prob'].idxmax()]
highest_risk_date = highest_risk_row['date'].strftime('%d %b %Y')
highest_risk_prob = highest_risk_row['crash_prob']

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Days Analysed",  f"{n_total:,}")
kpi2.metric("Crash Alerts Raised",  f"{n_alerts:,}", delta=f"{alert_rate:.1f}% of days")
kpi3.metric("Actual Crash Days",    f"{n_actual:,}")
kpi4.metric("Crashes Caught",       f"{correct_caught:,}", delta=f"{recall_pct:.1f}% recall")
kpi5.metric("Highest Risk Day",     highest_risk_date, delta=f"Prob {highest_risk_prob:.3f}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Probability Timeline Chart ────────────────────────────────────────────────
st.markdown('<div class="section-hdr"><h3>Crash Probability Timeline</h3></div>', unsafe_allow_html=True)
st.markdown(
    f"Showing probabilities from **{model_choice}** · "
    f"threshold = **{threshold:.2f}** · "
    f"red dots = predicted crash alerts"
)

fig_timeline = prediction_timeline(pred_df, threshold)
st.plotly_chart(fig_timeline, use_container_width=True)
st.caption(
    "Top panel: closing price with red dots on high-risk days. "
    "Bottom panel: crash probability with dashed threshold line. "
    "Zoom / pan with the Plotly toolbar."
)

# ── Risk Table ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr" style="margin-top:24px;"><h3>Prediction Table</h3></div>', unsafe_allow_html=True)

if view_mode == "High-Risk Only":
    display_df = pred_df[pred_df['predicted_crash'] == 1].copy()
    st.markdown(
        f'<div class="info-banner">Showing <strong>{len(display_df):,}</strong> high-risk days '
        f'(threshold ≥ {threshold:.2f}).</div>',
        unsafe_allow_html=True,
    )
else:
    display_df = pred_df.copy()

# Format for display
table_df = display_df[['date', 'close', 'crash_prob', 'risk_level', 'actual_crash', 'predicted_crash']].copy()
table_df.columns = ['Date', 'Close Price', 'Crash Probability', 'Risk Level', 'Actual Crash', 'Predicted Crash']
table_df['Date']             = table_df['Date'].dt.strftime('%d %b %Y')
table_df['Close Price']      = table_df['Close Price'].map('{:,.2f}'.format)
table_df['Crash Probability'] = table_df['Crash Probability'].map('{:.4f}'.format)
table_df['Actual Crash']     = table_df['Actual Crash'].map({0: '✗ No', 1: '✅ Yes'})
table_df['Predicted Crash']  = table_df['Predicted Crash'].map({0: '—', 1: '⚠️ Alert'})

st.dataframe(table_df, use_container_width=True, hide_index=True, height=380)
st.caption(f"Showing {len(table_df):,} rows · use the filter above to switch between All Days and High-Risk Only")

# ── Download CSV ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr" style="margin-top:20px;"><h3>Download Results</h3></div>', unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def make_download_csv(pred_json: str, thresh: float, mkey: str) -> bytes:
    df = pd.read_json(pred_json)
    df['threshold_used'] = thresh
    df['model'] = mkey
    return df.to_csv(index=False).encode('utf-8')

dl_df = pred_df[['date', 'close', 'crash_prob', 'predicted_crash', 'actual_crash', 'risk_level']].copy()
dl_df.columns = ['date', 'close', 'crash_probability', 'predicted_crash', 'actual_crash', 'risk_level']
dl_df['threshold_used'] = threshold
dl_df['model'] = model_choice
csv_bytes = dl_df.to_csv(index=False).encode('utf-8')

dl_col1, dl_col2 = st.columns([1, 3])
with dl_col1:
    st.download_button(
        label="⬇️  Download Predictions CSV",
        data=csv_bytes,
        file_name=f"crash_predictions_{model_key}_thresh{threshold:.2f}.csv",
        mime="text/csv",
        use_container_width=True,
    )
with dl_col2:
    st.markdown(
        f"<div style='padding-top:8px; color:#6B7B8F; font-size:13px;'>"
        f"CSV includes: date · close price · crash probability · predicted crash · actual crash · "
        f"risk level · threshold used ({threshold:.2f}) · model ({model_choice})</div>",
        unsafe_allow_html=True,
    )

# ── Threshold guidance ────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📖 How to Interpret the Threshold", expanded=False):
    st.markdown(f"""
    The **decision threshold** converts a continuous crash probability into a binary alert.

    | Setting | Effect | Best For |
    |---------|--------|----------|
    | **Low (0.20 – 0.35)** | More alerts, higher recall, more false positives | Conservative investors who want to catch every possible crash |
    | **Medium (0.40 – 0.55)** | Balanced precision & recall | General use · current F1-optimal = **{default_thresh:.2f}** |
    | **High (0.65 – 0.80)** | Fewer alerts, higher precision, some crashes missed | Traders who prioritise signal quality over coverage |

    > *The F1-optimal threshold ({default_thresh:.2f}) was computed on the 2020–2023 test set
    > to maximise the harmonic mean of precision and recall for crash detection.*

    **Risk Level bands:**
    - 🟢 **Low** — probability < 0.30 (unlikely crash)
    - 🟡 **Medium** — 0.30 – 0.50 (elevated caution)
    - 🟠 **High** — 0.50 – 0.70 (significant risk)
    - 🔴 **Very High** — ≥ 0.70 (strong crash signal)
    """)

# ── Navigation ────────────────────────────────────────────────────────────────
st.markdown("---")
nav1, nav2, nav3 = st.columns([2, 3, 2])
with nav1:
    if st.button("← Back to Results", use_container_width=True):
        st.switch_page("pages/2_Results.py")
with nav3:
    if st.button("⬆ Upload New Data", use_container_width=True):
        # Clear session state so user can start fresh
        for key in ['raw_df', 'df_feat', 'upload_complete', 'models_trained',
                    'models', 'metrics', 'shap_vals', 'train_df', 'test_df']:
            st.session_state.pop(key, None)
        st.switch_page("pages/1_Upload.py")

"""
core/trainer.py
───────────────
Model training pipeline:
  - 5 classifiers: DT, LR, RF, XGBoost, Soft-Voting Ensemble
  - SMOTE oversampling (optimised: k_neighbors=3)
  - StandardScaler for LR + Ensemble
  - SHAP TreeExplainer on 100 samples (fast)
  - Rolling-window F1 validation
  - All metrics at F1-optimal decision threshold
"""

import numpy as np
import pandas as pd

from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score,
    accuracy_score, roc_curve, precision_recall_curve,
    average_precision_score, confusion_matrix,
)
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import shap

from core.features import FEATURE_COLS

# ── Model display names ───────────────────────────────────────────────────────
MODEL_KEYS   = ['dt', 'lr', 'rf', 'xgb', 'ensemble']
MODEL_LABELS = {
    'dt':       'Decision Tree',
    'lr':       'Logistic Regression',
    'rf':       'Random Forest',
    'xgb':      'XGBoost',
    'ensemble': 'Ensemble (Proposed)',
}
# Chart colors matching the PPT palette
MODEL_COLORS = {
    'dt':       '#8BA3C1',
    'lr':       '#6B7FD4',
    'rf':       '#2ECC71',
    'xgb':      '#FF6B6B',
    'ensemble': '#00C9A7',
}

# Models that require scaled input
NEEDS_SCALING = {'lr', 'ensemble'}


class ScaledModel:
    """Wraps a model + scaler so all models share the same predict_proba interface."""
    def __init__(self, model, scaler):
        self.model  = model
        self.scaler = scaler

    def predict_proba(self, X):
        return self.model.predict_proba(self.scaler.transform(X))

    def predict(self, X):
        return self.model.predict(self.scaler.transform(X))


def temporal_split(df, test_frac=0.2):
    """Chronological train/test split (no shuffling)."""
    n     = len(df)
    split = int(n * (1 - test_frac))
    return df.iloc[:split].copy(), df.iloc[split:].copy()


def train_all_models(df_feat, progress_cb=None):
    """
    Full training pipeline.

    Parameters
    ----------
    df_feat     : pd.DataFrame with FEATURE_COLS + 'crash' + 'date'
    progress_cb : callable(message: str, fraction: float) | None

    Returns
    -------
    models   : dict[str → model]   (all have .predict_proba(X) interface)
    metrics  : dict[str → dict]
    shap_vals: np.ndarray  (n_samples × n_features for RF, class-1)
    train_df : pd.DataFrame
    test_df  : pd.DataFrame
    """

    def _cb(msg, frac):
        if progress_cb:
            progress_cb(msg, frac)

    # ── Split ─────────────────────────────────────────────────────────────────
    train_df, test_df = temporal_split(df_feat)

    X_train = train_df[FEATURE_COLS].values.astype(np.float32)
    y_train = train_df['crash'].values
    X_test  = test_df[FEATURE_COLS].values.astype(np.float32)
    y_test  = test_df['crash'].values

    # ── SMOTE ─────────────────────────────────────────────────────────────────
    _cb("Applying SMOTE oversampling…", 0.05)
    sm = SMOTE(k_neighbors=3, random_state=42)
    X_sm, y_sm = sm.fit_resample(X_train, y_train)

    # ── Scaler ────────────────────────────────────────────────────────────────
    scaler   = StandardScaler()
    X_sm_sc  = scaler.fit_transform(X_sm)
    X_test_sc = scaler.transform(X_test)

    models  = {}
    metrics = {}

    # ── 1. Decision Tree ──────────────────────────────────────────────────────
    _cb("Training Decision Tree…", 0.12)
    dt = DecisionTreeClassifier(max_depth=6, random_state=42)
    dt.fit(X_sm, y_sm)
    models['dt']  = dt
    metrics['dt'] = _evaluate(dt, X_test, y_test)

    # ── 2. Logistic Regression ────────────────────────────────────────────────
    _cb("Training Logistic Regression…", 0.28)
    lr_raw = LogisticRegression(C=0.5, max_iter=1000, random_state=42, n_jobs=-1)
    lr_raw.fit(X_sm_sc, y_sm)
    lr = ScaledModel(lr_raw, scaler)
    models['lr']  = lr
    metrics['lr'] = _evaluate(lr, X_test, y_test)

    # ── 3. Random Forest ─────────────────────────────────────────────────────
    _cb("Training Random Forest…", 0.46)
    rf = RandomForestClassifier(
        n_estimators=80, max_depth=8, n_jobs=-1,
        random_state=42, min_samples_leaf=5,
    )
    rf.fit(X_sm, y_sm)
    models['rf']  = rf
    metrics['rf'] = _evaluate(rf, X_test, y_test)

    # ── 4. XGBoost ───────────────────────────────────────────────────────────
    _cb("Training XGBoost…", 0.64)
    xgb_raw = xgb.XGBClassifier(
        n_estimators=80, learning_rate=0.05, subsample=0.8,
        random_state=42, n_jobs=-1, verbosity=0,
        eval_metric='logloss',
    )
    xgb_raw.fit(X_sm, y_sm)
    models['xgb']  = xgb_raw
    metrics['xgb'] = _evaluate(xgb_raw, X_test, y_test)

    # ── 5. Soft-Voting Ensemble ───────────────────────────────────────────────
    _cb("Building Soft-Voting Ensemble…", 0.80)
    ens_raw = VotingClassifier(
        estimators=[
            ('lr',  LogisticRegression(C=0.5, max_iter=1000, random_state=42, n_jobs=-1)),
            ('rf',  RandomForestClassifier(n_estimators=80, max_depth=8, n_jobs=-1,
                                           random_state=42, min_samples_leaf=5)),
            ('xgb', xgb.XGBClassifier(n_estimators=80, learning_rate=0.05, subsample=0.8,
                                       random_state=42, n_jobs=-1, verbosity=0,
                                       eval_metric='logloss')),
        ],
        voting='soft', n_jobs=-1,
    )
    ens_raw.fit(X_sm_sc, y_sm)
    ens = ScaledModel(ens_raw, scaler)
    models['ensemble']  = ens
    metrics['ensemble'] = _evaluate(ens, X_test, y_test)

    # ── SHAP (on Random Forest, 100 samples) ─────────────────────────────────
    _cb("Computing SHAP explanations…", 0.92)
    n_shap   = min(100, len(X_test))
    explainer = shap.TreeExplainer(rf)
    shap_raw  = explainer.shap_values(X_test[:n_shap])
    # Normalise to 2-D (n_samples, n_features) for class 1
    if isinstance(shap_raw, list):
        shap_vals = np.array(shap_raw[1])          # list → class-1 array
    else:
        shap_vals = np.array(shap_raw)
        if shap_vals.ndim == 3:
            shap_vals = shap_vals[:, :, 1]         # 3-D → class-1 slice

    _cb("Done!", 1.0)

    return models, metrics, shap_vals, train_df, test_df


# ── Evaluation helpers ────────────────────────────────────────────────────────

def _evaluate(model, X_test, y_test):
    """Compute all metrics from a model with .predict_proba(X) interface."""
    proba = model.predict_proba(X_test)[:, 1]

    # F1-optimal threshold
    prec_arr, rec_arr, thresholds = precision_recall_curve(y_test, proba)
    f1_arr   = 2 * prec_arr * rec_arr / (prec_arr + rec_arr + 1e-10)
    best_idx  = int(np.argmax(f1_arr))
    threshold = float(thresholds[best_idx]) if best_idx < len(thresholds) else 0.5

    y_pred = (proba >= threshold).astype(int)
    cm     = confusion_matrix(y_test, y_pred)
    if cm.size == 4:
        tn, fp, fn, tp = cm.ravel()
    else:
        tn = fp = fn = tp = 0

    fpr, tpr, _ = roc_curve(y_test, proba)

    return {
        'auc':       round(float(roc_auc_score(y_test, proba)), 4),
        'accuracy':  round(float(accuracy_score(y_test, y_pred)), 4),
        'precision': round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        'recall':    round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        'f1':        round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        'ap':        round(float(average_precision_score(y_test, proba)), 4),
        'threshold': threshold,
        'tp': int(tp), 'fp': int(fp), 'tn': int(tn), 'fn': int(fn),
        'proba':     proba,
        'fpr':       fpr,
        'tpr':       tpr,
        'pr_prec':   prec_arr,
        'pr_rec':    rec_arr,
    }


def rolling_window_f1(models, test_df, window_months=3):
    """
    Compute per-quarter F1 scores for temporal stability analysis.
    Windows with < 2 crash events are skipped (as in the paper).
    """
    if 'date' not in test_df.columns or len(test_df) < 10:
        return pd.DataFrame()

    df = test_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    start = df['date'].min()
    end   = df['date'].max()
    results = []

    current = start
    while current <= end:
        window_end = current + pd.DateOffset(months=window_months)
        mask = (df['date'] >= current) & (df['date'] < window_end)
        w    = df[mask]

        if len(w) >= 5 and w['crash'].sum() >= 2:
            X_w = w[FEATURE_COLS].values.astype(np.float32)
            y_w = w['crash'].values
            row = {'Quarter': current.strftime('%b %Y')}

            for key in MODEL_KEYS:
                m    = models[key]
                prob = m.predict_proba(X_w)[:, 1]
                pred = (prob >= 0.5).astype(int)
                row[MODEL_LABELS[key]] = round(
                    float(f1_score(y_w, pred, zero_division=0)), 3
                )
            results.append(row)

        current = window_end

    return pd.DataFrame(results)

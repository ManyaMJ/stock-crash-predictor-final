"""
core/charts.py
──────────────
All Plotly interactive chart builders.
Every function returns a plotly.graph_objects.Figure ready for st.plotly_chart().
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from core.trainer import MODEL_KEYS, MODEL_LABELS, MODEL_COLORS
from core.features import FEATURE_COLS, FEATURE_DISPLAY

# ── Shared chart styling ──────────────────────────────────────────────────────
_LAYOUT = dict(
    paper_bgcolor='#FFFFFF',
    plot_bgcolor='#FFFFFF',
    font=dict(family='Inter, sans-serif', color='#1A2B45', size=13),
    margin=dict(l=20, r=20, t=50, b=20),
    legend=dict(bgcolor='#F0F4FF', bordercolor='#E0E8F5', borderwidth=1),
    hoverlabel=dict(bgcolor='#0A1628', font_color='#FFFFFF', bordercolor='#00C9A7'),
)
_AXIS = dict(gridcolor='#E8EEF8', linecolor='#D1D9E6', zerolinecolor='#D1D9E6')


def _base_fig(**kwargs):
    fig = go.Figure()
    fig.update_layout(**_LAYOUT, **kwargs)
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    return fig


# ── 1. Price Chart ────────────────────────────────────────────────────────────
def price_chart(df: pd.DataFrame) -> go.Figure:
    """Interactive close-price line chart with crash periods shaded."""
    fig = _base_fig(
        title=dict(text='Price History with Crash Periods', font_size=16, x=0.01),
        xaxis_title='Date', yaxis_title='Close Price',
    )
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['close'],
        mode='lines', name='Close Price',
        line=dict(color='#0A1628', width=1.5),
        hovertemplate='%{x|%d %b %Y}<br>Close: %{y:,.2f}<extra></extra>',
    ))
    # Shade crash days
    if 'crash' in df.columns:
        crash_days = df[df['crash'] == 1]
        for _, row in crash_days.iterrows():
            fig.add_vrect(
                x0=row['date'], x1=row['date'],
                fillcolor='#FF6B6B', opacity=0.15,
                line_width=0,
            )
        # Add a dummy trace for legend
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode='markers',
            marker=dict(color='#FF6B6B', size=10, symbol='square'),
            name='Crash Day',
        ))
    fig.update_layout(hovermode='x unified', showlegend=True)
    return fig


# ── 2. Crash Distribution ─────────────────────────────────────────────────────
def crash_distribution(df: pd.DataFrame) -> go.Figure:
    """Bar chart: crash vs non-crash day counts."""
    counts = df['crash'].value_counts().sort_index()
    labels = ['No Crash (0)', 'Crash (1)']
    colors = ['#00C9A7', '#FF6B6B']

    fig = _base_fig(title=dict(text='Crash Label Distribution', font_size=16, x=0.01))
    fig.add_trace(go.Bar(
        x=labels,
        y=[counts.get(0, 0), counts.get(1, 0)],
        marker_color=colors,
        text=[f'{counts.get(0,0):,}', f'{counts.get(1,0):,}'],
        textposition='outside',
        hovertemplate='%{x}: %{y:,} days<extra></extra>',
    ))
    fig.update_layout(yaxis_title='Number of Days', showlegend=False, bargap=0.4)
    return fig


# ── 3. ROC Curves ─────────────────────────────────────────────────────────────
def roc_curves(metrics: dict) -> go.Figure:
    """Overlapping ROC curves for all 5 models."""
    fig = _base_fig(
        title=dict(text='ROC Curves — All Models', font_size=16, x=0.01),
        xaxis_title='False Positive Rate',
        yaxis_title='True Positive Rate',
    )
    # Random baseline
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode='lines', name='Random Guess (AUC = 0.500)',
        line=dict(color='#AAAAAA', width=1.5, dash='dash'),
    ))
    for key in MODEL_KEYS:
        m   = metrics[key]
        auc = m['auc']
        fig.add_trace(go.Scatter(
            x=m['fpr'], y=m['tpr'],
            mode='lines',
            name=f"{MODEL_LABELS[key]} (AUC = {auc:.3f})",
            line=dict(color=MODEL_COLORS[key], width=2.5),
            hovertemplate=f"{MODEL_LABELS[key]}<br>FPR: %{{x:.3f}}<br>TPR: %{{y:.3f}}<extra></extra>",
        ))
    fig.update_layout(
        xaxis=dict(range=[0, 1], **_AXIS),
        yaxis=dict(range=[0, 1.02], **_AXIS),
        legend=dict(x=0.55, y=0.08, bgcolor='#F0F4FF', bordercolor='#E0E8F5'),
    )
    return fig


# ── 4. Confusion Matrices ─────────────────────────────────────────────────────
def confusion_matrices(metrics: dict) -> go.Figure:
    """5-panel confusion matrix heatmaps."""
    fig = make_subplots(
        rows=1, cols=5,
        subplot_titles=[MODEL_LABELS[k] for k in MODEL_KEYS],
        horizontal_spacing=0.04,
    )
    for i, key in enumerate(MODEL_KEYS, 1):
        m  = metrics[key]
        tp, fp, tn, fn = m['tp'], m['fp'], m['tn'], m['fn']
        z  = [[tn, fp], [fn, tp]]
        text = [[f'TN\n{tn:,}', f'FP\n{fp:,}'], [f'FN\n{fn:,}', f'TP\n{tp:,}']]
        colors = [
            ['#E6F4F1', '#FFE8E8'],
            ['#FFF3CD', '#E6FFF9'],
        ]
        fig.add_trace(
            go.Heatmap(
                z=z,
                text=text,
                texttemplate='%{text}',
                textfont=dict(size=11, color='#1A2B45'),
                colorscale=[[0, '#EEF5FF'], [1, '#00C9A7']],
                showscale=False,
                xgap=2, ygap=2,
                hovertemplate='Predicted: %{x}<br>Actual: %{y}<br>Count: %{z}<extra></extra>',
            ),
            row=1, col=i,
        )
        fig.update_xaxes(
            tickvals=[0, 1], ticktext=['Pred 0', 'Pred 1'],
            row=1, col=i,
        )
        fig.update_yaxes(
            tickvals=[0, 1], ticktext=['Act 0', 'Act 1'],
            row=1, col=i,
        )

    fig.update_layout(
        **_LAYOUT,
        title=dict(text='Confusion Matrices at F1-Optimal Threshold', font_size=16, x=0.01),
        height=320,
    )
    return fig


# ── 5. Precision-Recall Curves ────────────────────────────────────────────────
def pr_curves(metrics: dict, crash_rate: float) -> go.Figure:
    """Overlapping PR curves with no-skill baseline."""
    fig = _base_fig(
        title=dict(text='Precision-Recall Curves — All Models', font_size=16, x=0.01),
        xaxis_title='Recall',
        yaxis_title='Precision',
    )
    # No-skill baseline
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[crash_rate, crash_rate],
        mode='lines', name=f'No-Skill Baseline (AP = {crash_rate:.3f})',
        line=dict(color='#AAAAAA', width=1.5, dash='dash'),
    ))
    for key in MODEL_KEYS:
        m  = metrics[key]
        ap = m['ap']
        fig.add_trace(go.Scatter(
            x=m['pr_rec'], y=m['pr_prec'],
            mode='lines',
            name=f"{MODEL_LABELS[key]} (AP = {ap:.3f})",
            line=dict(color=MODEL_COLORS[key], width=2.5),
            hovertemplate=f"{MODEL_LABELS[key]}<br>Recall: %{{x:.3f}}<br>Precision: %{{y:.3f}}<extra></extra>",
        ))
    fig.update_layout(
        xaxis=dict(range=[0, 1], **_AXIS),
        yaxis=dict(range=[0, 1.02], **_AXIS),
        legend=dict(x=0.35, y=0.98, bgcolor='#F0F4FF', bordercolor='#E0E8F5'),
    )
    return fig


# ── 6. SHAP Feature Importance ────────────────────────────────────────────────
def shap_bar(shap_vals) -> go.Figure:
    """Horizontal bar chart of mean |SHAP| values for top 15 features.

    Handles both 2-D (n_samples, n_features) and 3-D (n_samples, n_features, n_classes)
    SHAP output, as well as list output from older SHAP versions.
    """
    # Normalise SHAP output to 2-D array (n_samples, n_features) for class 1
    if isinstance(shap_vals, list):
        vals = np.array(shap_vals[1])          # class-1 values from list
    else:
        vals = np.array(shap_vals)
        if vals.ndim == 3:
            vals = vals[:, :, 1]               # class-1 slice of 3-D array

    mean_abs = np.abs(vals).mean(axis=0)
    importance = pd.Series(mean_abs, index=FEATURE_COLS)
    importance = importance.sort_values(ascending=True).tail(15)

    display_names = [FEATURE_DISPLAY.get(f, f) for f in importance.index]
    colors = ['#00C9A7' if v >= importance.quantile(0.67)
              else '#1E3A5F' if v >= importance.quantile(0.33)
              else '#8BA3C1'
              for v in importance.values]

    fig = _base_fig(
        title=dict(text='SHAP Feature Importance — Mean |SHAP| Value', font_size=16, x=0.01),
        xaxis_title='Mean |SHAP Value|',
        height=500,
    )
    fig.add_trace(go.Bar(
        x=importance.values,
        y=display_names,
        orientation='h',
        marker_color=colors,
        text=[f'{v:.4f}' for v in importance.values],
        textposition='outside',
        hovertemplate='%{y}: %{x:.4f}<extra></extra>',
    ))
    fig.update_layout(
        yaxis=dict(autorange=True, **_AXIS),
        xaxis=dict(**_AXIS),
        showlegend=False,
        margin=dict(l=180, r=60, t=50, b=20),
    )
    return fig


# ── 7. Rolling-Window F1 ─────────────────────────────────────────────────────
def rolling_window_chart(rolling_df: pd.DataFrame) -> go.Figure:
    """Line chart of F1 scores across rolling 3-month windows."""
    if rolling_df.empty:
        fig = _base_fig(title=dict(text='Not enough data for rolling-window analysis', font_size=14))
        return fig

    fig = _base_fig(
        title=dict(text='Rolling-Window F1-Score — Temporal Stability (3-Month Windows)', font_size=16, x=0.01),
        xaxis_title='Quarter',
        yaxis_title='F1-Score',
    )
    for key in MODEL_KEYS:
        label = MODEL_LABELS[key]
        if label in rolling_df.columns:
            fig.add_trace(go.Scatter(
                x=rolling_df['Quarter'],
                y=rolling_df[label],
                mode='lines+markers',
                name=label,
                line=dict(color=MODEL_COLORS[key], width=2),
                marker=dict(size=7, color=MODEL_COLORS[key]),
                hovertemplate=f'{label}<br>%{{x}}: F1 = %{{y:.3f}}<extra></extra>',
            ))
    fig.update_layout(
        xaxis=dict(tickangle=-35, **_AXIS),
        yaxis=dict(range=[0, 1], **_AXIS),
        legend=dict(x=0.75, y=0.98, bgcolor='#F0F4FF'),
        hovermode='x unified',
    )
    return fig


# ── 8. Prediction Timeline ────────────────────────────────────────────────────
def prediction_timeline(pred_df: pd.DataFrame, threshold: float) -> go.Figure:
    """
    Crash probability over time.
    pred_df must have columns: date, close, crash_prob, actual_crash (optional)
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.55, 0.45],
        vertical_spacing=0.04,
        subplot_titles=['Close Price', 'Crash Probability'],
    )

    # Price
    fig.add_trace(go.Scatter(
        x=pred_df['date'], y=pred_df['close'],
        mode='lines', name='Close Price',
        line=dict(color='#1A2B45', width=1.5),
        hovertemplate='%{x|%d %b %Y}<br>Price: %{y:,.2f}<extra></extra>',
    ), row=1, col=1)

    # Highlight high-risk in price chart
    high_risk = pred_df[pred_df['crash_prob'] >= threshold]
    if not high_risk.empty:
        fig.add_trace(go.Scatter(
            x=high_risk['date'], y=high_risk['close'],
            mode='markers', name='High-Risk Day',
            marker=dict(color='#FF6B6B', size=5, symbol='circle'),
            hovertemplate='%{x|%d %b %Y}<br>CRASH ALERT<extra></extra>',
        ), row=1, col=1)

    # Probability
    fig.add_trace(go.Scatter(
        x=pred_df['date'], y=pred_df['crash_prob'],
        mode='lines', name='Crash Probability',
        line=dict(color='#00C9A7', width=1.5),
        fill='tozeroy', fillcolor='rgba(0,201,167,0.1)',
        hovertemplate='%{x|%d %b %Y}<br>Prob: %{y:.3f}<extra></extra>',
    ), row=2, col=1)

    # Threshold line
    fig.add_hline(
        y=threshold, row=2, col=1,
        line=dict(color='#FF6B6B', dash='dash', width=1.5),
        annotation_text=f'Threshold {threshold:.2f}',
        annotation_font_color='#FF6B6B',
    )

    fig.update_layout(
        **_LAYOUT,
        height=520,
        title=dict(text='Crash Probability Timeline', font_size=16, x=0.01),
        hovermode='x unified',
        showlegend=True,
    )
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    return fig

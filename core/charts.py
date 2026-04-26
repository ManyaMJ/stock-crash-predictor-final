"""
core/charts.py
──────────────
All Plotly chart builders — dark trading-terminal theme.
Every function returns a go.Figure ready for st.plotly_chart().
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from core.trainer import MODEL_KEYS, MODEL_LABELS, MODEL_COLORS
from core.features import FEATURE_COLS, FEATURE_DISPLAY

# ── Shared dark-theme styling ─────────────────────────────────────────────────
_BG   = '#0A0E1A'
_BG2  = '#0F1629'
_GREEN  = '#00D4AA'
_GREEN2 = '#00FF88'
_RED    = '#FF3366'

_LAYOUT = dict(
    paper_bgcolor=_BG,
    plot_bgcolor=_BG,
    font=dict(family='IBM Plex Mono, Inter, sans-serif', color='#6B7B8F', size=11),
    margin=dict(l=20, r=20, t=52, b=20),
    legend=dict(
        bgcolor='rgba(15,22,41,0.92)',
        bordercolor='rgba(0,212,170,0.18)',
        borderwidth=1,
        font=dict(color='#B8C4D8', size=11),
    ),
    hoverlabel=dict(bgcolor='#141C35', font_color='#E2E8F0',
                    bordercolor=_GREEN, font_size=12),
)
_AXIS = dict(
    gridcolor='rgba(255,255,255,0.04)',
    linecolor='rgba(255,255,255,0.08)',
    zerolinecolor='rgba(255,255,255,0.06)',
    tickfont=dict(color='#4A5568', size=10),
    title_font=dict(color='#94A3B8', size=12),
)


def _base_fig(**kwargs):
    fig = go.Figure()
    fig.update_layout(**_LAYOUT, **kwargs)
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    return fig


# ── 1. Price Chart ────────────────────────────────────────────────────────────
def price_chart(df: pd.DataFrame) -> go.Figure:
    """Close-price line chart with crash day markers and range selector."""
    fig = _base_fig(
        title=dict(text='Price History with Crash Periods', font_size=15,
                   font_color='#B8C4D8', x=0.01),
        xaxis_title='Date', yaxis_title='Close Price',
    )
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['close'],
        mode='lines', name='Close Price',
        line=dict(color=_GREEN, width=1.6),
        hovertemplate='%{x|%d %b %Y}<br>Close: ₹%{y:,.2f}<extra></extra>',
    ))
    if 'crash' in df.columns:
        crash_days = df[df['crash'] == 1]
        fig.add_trace(go.Scatter(
            x=crash_days['date'], y=crash_days['close'],
            mode='markers', name='Crash Day',
            marker=dict(color=_RED, size=6, symbol='circle',
                        line=dict(color='rgba(255,51,102,0.4)', width=1)),
            hovertemplate='%{x|%d %b %Y}<br><b>CRASH DAY</b><br>Close: ₹%{y:,.2f}<extra></extra>',
        ))
    fig.update_layout(
        hovermode='x unified', showlegend=True,
        xaxis=dict(
            rangeslider=dict(visible=True, bgcolor=_BG2, thickness=0.04),
            rangeselector=dict(
                buttons=[
                    dict(count=3,  label='3M',  step='month', stepmode='backward'),
                    dict(count=6,  label='6M',  step='month', stepmode='backward'),
                    dict(count=1,  label='1Y',  step='year',  stepmode='backward'),
                    dict(count=3,  label='3Y',  step='year',  stepmode='backward'),
                    dict(step='all', label='ALL'),
                ],
                bgcolor=_BG2, activecolor=_GREEN,
                font=dict(color='#94A3B8', size=11),
                bordercolor='rgba(0,212,170,0.2)', borderwidth=1,
                x=0, y=1.04,
            ),
            **_AXIS,
        ),
    )
    return fig


# ── 2. Candlestick Chart ──────────────────────────────────────────────────────
def candlestick_chart(df: pd.DataFrame) -> go.Figure:
    """OHLCV candlestick with volume bars — classic trading terminal view."""
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.72, 0.28], vertical_spacing=0.02,
        subplot_titles=['OHLCV Candlestick', 'Volume'],
    )
    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open'], high=df['high'],
        low=df['low'],  close=df['close'],
        name='OHLC',
        increasing=dict(line=dict(color=_GREEN, width=1), fillcolor='rgba(0,212,170,0.7)'),
        decreasing=dict(line=dict(color=_RED,   width=1), fillcolor='rgba(255,51,102,0.7)'),
        hovertext=[
            f"O: {o:,.2f}  H: {h:,.2f}  L: {l:,.2f}  C: {c:,.2f}"
            for o, h, l, c in zip(df['open'], df['high'], df['low'], df['close'])
        ],
        hoverinfo='x+text',
    ), row=1, col=1)
    # Crash markers on candlestick
    if 'crash' in df.columns:
        crash_days = df[df['crash'] == 1]
        fig.add_trace(go.Scatter(
            x=crash_days['date'], y=crash_days['high'] * 1.005,
            mode='markers', name='Crash Day',
            marker=dict(color=_RED, size=7, symbol='triangle-down',
                        line=dict(color='rgba(255,51,102,0.5)', width=1)),
            hovertemplate='%{x|%d %b %Y}<br><b>CRASH FLAG</b><extra></extra>',
        ), row=1, col=1)
    # Volume bars
    colours = [_GREEN if c >= o else _RED
               for c, o in zip(df['close'], df['open'])]
    fig.add_trace(go.Bar(
        x=df['date'], y=df['volume'],
        name='Volume', marker_color=colours,
        opacity=0.65,
        hovertemplate='%{x|%d %b %Y}<br>Vol: %{y:,.0f}<extra></extra>',
    ), row=2, col=1)
    fig.update_layout(
        **_LAYOUT,
        height=560,
        title=dict(text='Candlestick Chart with Volume', font_size=15,
                   font_color='#B8C4D8', x=0.01),
        showlegend=True,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        xaxis2=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=3,  label='3M', step='month', stepmode='backward'),
                    dict(count=6,  label='6M', step='month', stepmode='backward'),
                    dict(count=1,  label='1Y', step='year',  stepmode='backward'),
                    dict(step='all', label='ALL'),
                ],
                bgcolor=_BG2, activecolor=_GREEN,
                font=dict(color='#94A3B8', size=11),
                bordercolor='rgba(0,212,170,0.2)',
            ),
            **_AXIS,
        ),
    )
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    return fig


# ── 3. Crash Distribution ─────────────────────────────────────────────────────
def crash_distribution(df: pd.DataFrame) -> go.Figure:
    counts = df['crash'].value_counts().sort_index()
    fig = _base_fig(
        title=dict(text='Crash Label Distribution', font_size=15,
                   font_color='#B8C4D8', x=0.01),
    )
    fig.add_trace(go.Bar(
        x=['No Crash (0)', 'Crash (1)'],
        y=[counts.get(0, 0), counts.get(1, 0)],
        marker_color=[_GREEN, _RED],
        marker_line=dict(width=0),
        text=[f'{counts.get(0,0):,}', f'{counts.get(1,0):,}'],
        textposition='outside',
        textfont=dict(color='#B8C4D8', size=13, family='IBM Plex Mono'),
        hovertemplate='%{x}: %{y:,} days<extra></extra>',
    ))
    fig.update_layout(
        yaxis_title='Trading Days', showlegend=False, bargap=0.5,
        yaxis=dict(**_AXIS),
    )
    return fig


# ── 4. ROC Curves ─────────────────────────────────────────────────────────────
def roc_curves(metrics: dict) -> go.Figure:
    fig = _base_fig(
        title=dict(text='ROC Curves — All Models', font_size=15,
                   font_color='#B8C4D8', x=0.01),
        xaxis_title='False Positive Rate',
        yaxis_title='True Positive Rate',
    )
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode='lines',
        name='Random (AUC = 0.500)',
        line=dict(color='rgba(255,255,255,0.15)', width=1.5, dash='dot'),
    ))
    for key in MODEL_KEYS:
        m = metrics[key]
        fig.add_trace(go.Scatter(
            x=m['fpr'], y=m['tpr'], mode='lines',
            name=f"{MODEL_LABELS[key]}  AUC {m['auc']:.3f}",
            line=dict(color=MODEL_COLORS[key], width=2.2),
            hovertemplate=f"{MODEL_LABELS[key]}<br>FPR: %{{x:.3f}}<br>TPR: %{{y:.3f}}<extra></extra>",
        ))
    fig.update_layout(
        xaxis=dict(range=[0, 1], **_AXIS),
        yaxis=dict(range=[0, 1.02], **_AXIS),
        legend=dict(x=0.52, y=0.08, bgcolor='rgba(15,22,41,0.9)',
                    bordercolor='rgba(0,212,170,0.18)', borderwidth=1),
        hovermode='x unified',
    )
    return fig


# ── 5. Confusion Matrices ─────────────────────────────────────────────────────
def confusion_matrices(metrics: dict) -> go.Figure:
    fig = make_subplots(
        rows=1, cols=5,
        subplot_titles=[MODEL_LABELS[k] for k in MODEL_KEYS],
        horizontal_spacing=0.04,
    )
    for i, key in enumerate(MODEL_KEYS, 1):
        m = metrics[key]
        tp, fp, tn, fn = m['tp'], m['fp'], m['tn'], m['fn']
        z    = [[tn, fp], [fn, tp]]
        text = [[f'TN\n{tn:,}', f'FP\n{fp:,}'], [f'FN\n{fn:,}', f'TP\n{tp:,}']]
        fig.add_trace(go.Heatmap(
            z=z, text=text, texttemplate='%{text}',
            textfont=dict(size=11, color='#E2E8F0', family='IBM Plex Mono'),
            colorscale=[[0, '#0F1629'], [1, '#006655']],
            showscale=False, xgap=3, ygap=3,
            hovertemplate='Predicted: %{x}<br>Actual: %{y}<br>Count: %{z}<extra></extra>',
        ), row=1, col=i)
        fig.update_xaxes(tickvals=[0, 1], ticktext=['Pred 0', 'Pred 1'],
                         tickfont=dict(color='#6B7B8F', size=10), row=1, col=i)
        fig.update_yaxes(tickvals=[0, 1], ticktext=['Act 0', 'Act 1'],
                         tickfont=dict(color='#6B7B8F', size=10), row=1, col=i)
    fig.update_layout(
        **_LAYOUT,
        title=dict(text='Confusion Matrices at F1-Optimal Threshold',
                   font_size=15, font_color='#B8C4D8', x=0.01),
        height=330,
    )
    return fig


# ── 6. Precision-Recall Curves ────────────────────────────────────────────────
def pr_curves(metrics: dict, crash_rate: float) -> go.Figure:
    fig = _base_fig(
        title=dict(text='Precision-Recall Curves — All Models',
                   font_size=15, font_color='#B8C4D8', x=0.01),
        xaxis_title='Recall',
        yaxis_title='Precision',
    )
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[crash_rate, crash_rate], mode='lines',
        name=f'No-Skill Baseline (AP={crash_rate:.3f})',
        line=dict(color='rgba(255,255,255,0.15)', width=1.5, dash='dot'),
    ))
    for key in MODEL_KEYS:
        m = metrics[key]
        fig.add_trace(go.Scatter(
            x=m['pr_rec'], y=m['pr_prec'], mode='lines',
            name=f"{MODEL_LABELS[key]}  AP {m['ap']:.3f}",
            line=dict(color=MODEL_COLORS[key], width=2.2),
            hovertemplate=f"{MODEL_LABELS[key]}<br>Recall: %{{x:.3f}}<br>Precision: %{{y:.3f}}<extra></extra>",
        ))
    fig.update_layout(
        xaxis=dict(range=[0, 1], **_AXIS),
        yaxis=dict(range=[0, 1.02], **_AXIS),
        legend=dict(x=0.32, y=0.98, bgcolor='rgba(15,22,41,0.9)',
                    bordercolor='rgba(0,212,170,0.18)', borderwidth=1),
        hovermode='x unified',
    )
    return fig


# ── 7. SHAP Feature Importance ────────────────────────────────────────────────
def shap_bar(shap_vals) -> go.Figure:
    if isinstance(shap_vals, list):
        vals = np.array(shap_vals[1])
    else:
        vals = np.array(shap_vals)
        if vals.ndim == 3:
            vals = vals[:, :, 1]

    mean_abs   = np.abs(vals).mean(axis=0)
    importance = pd.Series(mean_abs, index=FEATURE_COLS).sort_values(ascending=True).tail(15)
    display_names = [FEATURE_DISPLAY.get(f, f) for f in importance.index]

    q67 = importance.quantile(0.67)
    q33 = importance.quantile(0.33)
    colours = [_GREEN if v >= q67 else '#4FACFE' if v >= q33 else '#3D4F63'
               for v in importance.values]

    fig = _base_fig(
        title=dict(text='SHAP Feature Importance — Mean |SHAP| Value',
                   font_size=15, font_color='#B8C4D8', x=0.01),
        xaxis_title='Mean |SHAP Value|',
        height=520,
    )
    fig.add_trace(go.Bar(
        x=importance.values, y=display_names,
        orientation='h',
        marker_color=colours,
        marker_line=dict(width=0),
        text=[f'{v:.4f}' for v in importance.values],
        textposition='outside',
        textfont=dict(color='#94A3B8', size=10, family='IBM Plex Mono'),
        hovertemplate='%{y}: %{x:.5f}<extra></extra>',
    ))
    fig.update_layout(
        yaxis=dict(autorange=True, **_AXIS),
        xaxis=dict(**_AXIS),
        showlegend=False,
        margin=dict(l=190, r=70, t=52, b=20),
    )
    return fig


# ── 8. Rolling-Window F1 ─────────────────────────────────────────────────────
def rolling_window_chart(rolling_df: pd.DataFrame) -> go.Figure:
    if rolling_df.empty:
        return _base_fig(title=dict(text='Not enough data for rolling-window analysis',
                                    font_size=14))
    fig = _base_fig(
        title=dict(text='Rolling-Window F1 Score — 3-Month Temporal Windows',
                   font_size=15, font_color='#B8C4D8', x=0.01),
        xaxis_title='Quarter', yaxis_title='F1-Score',
    )
    for key in MODEL_KEYS:
        label = MODEL_LABELS[key]
        if label in rolling_df.columns:
            fig.add_trace(go.Scatter(
                x=rolling_df['Quarter'], y=rolling_df[label],
                mode='lines+markers', name=label,
                line=dict(color=MODEL_COLORS[key], width=2),
                marker=dict(size=8, color=MODEL_COLORS[key],
                            line=dict(color=_BG, width=2)),
                fill='tozeroy' if key == 'ensemble' else None,
                fillcolor='rgba(0,212,170,0.06)' if key == 'ensemble' else None,
                hovertemplate=f'{label}<br>%{{x}}: F1 = %{{y:.3f}}<extra></extra>',
            ))
    fig.update_layout(
        xaxis=dict(tickangle=-35, **_AXIS),
        yaxis=dict(range=[0, 1], **_AXIS),
        legend=dict(x=0.01, y=0.98, bgcolor='rgba(15,22,41,0.9)',
                    bordercolor='rgba(0,212,170,0.18)'),
        hovermode='x unified',
    )
    return fig


# ── 9. Prediction Timeline ────────────────────────────────────────────────────
def prediction_timeline(pred_df: pd.DataFrame, threshold: float) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.52, 0.48], vertical_spacing=0.04,
        subplot_titles=['Close Price', 'Crash Probability'],
    )
    # Price line
    fig.add_trace(go.Scatter(
        x=pred_df['date'], y=pred_df['close'],
        mode='lines', name='Close Price',
        line=dict(color='#4FACFE', width=1.5),
        hovertemplate='%{x|%d %b %Y}<br>₹%{y:,.2f}<extra></extra>',
    ), row=1, col=1)
    # High-risk days on price
    hr = pred_df[pred_df['crash_prob'] >= threshold]
    if not hr.empty:
        fig.add_trace(go.Scatter(
            x=hr['date'], y=hr['close'],
            mode='markers', name='⚠ Crash Alert',
            marker=dict(color=_RED, size=5, symbol='circle',
                        line=dict(color='rgba(255,51,102,0.35)', width=1)),
            hovertemplate='%{x|%d %b %Y}<br><b>CRASH ALERT</b><extra></extra>',
        ), row=1, col=1)
    # Probability area
    fig.add_trace(go.Scatter(
        x=pred_df['date'], y=pred_df['crash_prob'],
        mode='lines', name='Crash Probability',
        line=dict(color=_GREEN, width=1.5),
        fill='tozeroy', fillcolor='rgba(0,212,170,0.08)',
        hovertemplate='%{x|%d %b %Y}<br>Prob: %{y:.3f}<extra></extra>',
    ), row=2, col=1)
    # Red zone above threshold
    fig.add_trace(go.Scatter(
        x=pred_df['date'],
        y=pred_df['crash_prob'].where(pred_df['crash_prob'] >= threshold),
        mode='lines', name=None, showlegend=False,
        line=dict(color=_RED, width=0),
        fill='tozeroy', fillcolor='rgba(255,51,102,0.12)',
        hoverinfo='skip',
    ), row=2, col=1)
    # Threshold line
    fig.add_hline(y=threshold, row=2, col=1,
                  line=dict(color=_RED, dash='dash', width=1.5),
                  annotation_text=f'Threshold {threshold:.2f}',
                  annotation_font_color=_RED,
                  annotation_font_size=11)
    fig.update_layout(
        **_LAYOUT,
        height=540,
        title=dict(text='Crash Probability Timeline', font_size=15,
                   font_color='#B8C4D8', x=0.01),
        hovermode='x unified', showlegend=True,
    )
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    return fig


# ── 10. Risk Gauge ────────────────────────────────────────────────────────────
def risk_gauge(prob: float, model_name: str = '') -> go.Figure:
    """Speedometer gauge showing overall crash probability."""
    pct = prob * 100
    bar_color = (_GREEN if pct < 30 else
                 '#FFB700' if pct < 50 else
                 '#FF8C42' if pct < 70 else _RED)
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title=dict(text=f'Avg Crash Probability<br><span style="font-size:11px;color:#6B7B8F">{model_name}</span>',
                   font=dict(color='#94A3B8', size=13)),
        gauge=dict(
            axis=dict(range=[0, 100],
                      tickwidth=1, tickcolor='#3D4F63',
                      tickfont=dict(color='#4A5568', size=10, family='IBM Plex Mono'),
                      nticks=6),
            bar=dict(color=bar_color, thickness=0.24),
            bgcolor=_BG2,
            borderwidth=1,
            bordercolor='rgba(255,255,255,0.06)',
            steps=[
                dict(range=[0, 30],  color='rgba(0,212,170,0.08)'),
                dict(range=[30, 50], color='rgba(255,183,0,0.08)'),
                dict(range=[50, 70], color='rgba(255,140,66,0.08)'),
                dict(range=[70, 100],color='rgba(255,51,102,0.08)'),
            ],
            threshold=dict(line=dict(color=_RED, width=2),
                           thickness=0.7, value=50),
        ),
        number=dict(suffix='%',
                    font=dict(color=bar_color, size=36,
                              family='IBM Plex Mono'),
                    valueformat='.1f'),
    ))
    fig.update_layout(
        paper_bgcolor=_BG, plot_bgcolor=_BG,
        font=dict(color='#94A3B8'),
        height=260,
        margin=dict(l=24, r=24, t=48, b=16),
    )
    return fig

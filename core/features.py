"""
core/features.py
────────────────
Feature engineering: computes all 25 technical & volatility indicators
from raw OHLCV data and applies the crash label definition from the paper.

Crash label: 5-day forward cumulative return < -3%  →  y = 1
"""

import numpy as np
import pandas as pd
import streamlit as st

# ── Feature column names (exactly 25) ────────────────────────────────────────
FEATURE_COLS = [
    # Price Returns (5)
    'return_1d', 'return_3d', 'return_5d', 'return_10d', 'return_20d',
    # Moving Averages (4)
    'ma20_dev', 'ma50_dev', 'ma5_20_cross', 'ma20_50_cross',
    # Volatility (5)
    'vol_5d', 'vol_10d', 'vol_20d', 'vol_ratio', 'atr_14',
    # Momentum (6)
    'rsi_14', 'macd', 'macd_signal', 'macd_hist', 'stoch_k', 'stoch_d',
    # Bollinger Bands (2)
    'bb_width', 'bb_pos',
    # Volume (2)
    'vol_ratio_20', 'obv_norm',
    # Candlestick (1)
    'hl_range',
]

# Human-readable names for charts / tables
FEATURE_DISPLAY = {
    'return_1d':    '1-Day Return',
    'return_3d':    '3-Day Return',
    'return_5d':    '5-Day Return',
    'return_10d':   '10-Day Return',
    'return_20d':   '20-Day Return',
    'ma20_dev':     'MA20 Deviation',
    'ma50_dev':     'MA50 Deviation',
    'ma5_20_cross': 'MA5-MA20 Cross',
    'ma20_50_cross':'MA20-MA50 Cross',
    'vol_5d':       'Volatility (5-day)',
    'vol_10d':      'Volatility (10-day)',
    'vol_20d':      'Volatility (20-day)',
    'vol_ratio':    'Volatility Ratio',
    'atr_14':       'ATR (14-day)',
    'rsi_14':       'RSI (14)',
    'macd':         'MACD',
    'macd_signal':  'MACD Signal',
    'macd_hist':    'MACD Histogram',
    'stoch_k':      'Stochastic %K',
    'stoch_d':      'Stochastic %D',
    'bb_width':     'Bollinger Band Width',
    'bb_pos':       'Bollinger Band Position',
    'vol_ratio_20': 'Volume Ratio (20-day)',
    'obv_norm':     'OBV (Normalised)',
    'hl_range':     'High-Low Range',
}


def load_and_validate(uploaded_file):
    """
    Read uploaded CSV, normalise column names, validate required columns.
    Returns (DataFrame, error_message). On success error_message is None.
    """
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        return None, f"Could not read CSV: {e}"

    # Normalise column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    # Accept common column name variants (including NSE India export format)
    aliases = {
        'adj_close': 'close', 'adj_close_price': 'close',
        'closing_price': 'close', 'price': 'close', 'ltp': 'close',
        'vol': 'volume', 'v': 'volume',
        'shares_traded': 'volume', 'quantity': 'volume', 'no_of_shares': 'volume',
        'datetime': 'date', 'time': 'date', 'timestamp': 'date',
        'series': None,            # NSE "Series" column — drop
        'turnover_(₹_cr)': None,  # NSE turnover column (unicode) — drop
        'turnover_(rs_cr)': None,  # NSE turnover column (ascii) — drop
        'turnover': None,
    }
    # Rename known columns; drop columns mapped to None (e.g. NSE "Series", "Turnover")
    df = df.rename(columns=lambda c: aliases.get(c, c))
    cols_to_drop = [c for c in df.columns if c is None]
    df = df.drop(columns=cols_to_drop, errors='ignore')

    # Required columns
    for col in ['open', 'high', 'low', 'close']:
        if col not in df.columns:
            return None, (
                f"Missing column: **{col}**. "
                "Expected columns: Date, Open, High, Low, Close (Volume optional)."
            )

    # Volume placeholder if missing
    if 'volume' not in df.columns:
        df['volume'] = 1.0

    # Parse date
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df = df.sort_values('date').reset_index(drop=True)
    else:
        df['date'] = pd.date_range(start='2001-01-01', periods=len(df), freq='B')

    # Numeric conversion
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=['open', 'high', 'low', 'close']).reset_index(drop=True)

    # Minimum rows needed for longest rolling window (MA-50) + crash label (5-day forward)
    MIN_ROWS = 60
    if len(df) < MIN_ROWS:
        return None, (
            f"Dataset has only **{len(df)} rows** after cleaning. "
            f"At least **{MIN_ROWS} trading days** are needed to compute "
            f"50-day moving averages and 5-day forward crash labels. "
            f"Please upload a longer history — see the sample CSV in the sidebar."
        )

    return df[['date', 'open', 'high', 'low', 'close', 'volume']], None


@st.cache_data(show_spinner=False)
def engineer_features(df_json: str) -> pd.DataFrame:
    """
    Compute all 25 features + crash label from raw OHLCV DataFrame.
    Input is JSON string so Streamlit can cache it by content hash.
    Returns DataFrame with original columns + 25 features + 'crash' label.
    """
    import io as _io
    df = pd.read_json(_io.StringIO(df_json))
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    close  = df['close'].astype(float)
    high   = df['high'].astype(float)
    low    = df['low'].astype(float)
    volume = df['volume'].astype(float)

    # ── Price Returns (5) ────────────────────────────────────────────────────
    for n in [1, 3, 5, 10, 20]:
        df[f'return_{n}d'] = close.pct_change(n)

    # ── Moving Averages (4) ──────────────────────────────────────────────────
    ma5  = close.rolling(5).mean()
    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()
    df['ma20_dev']      = (close - ma20) / (ma20.abs() + 1e-10)
    df['ma50_dev']      = (close - ma50) / (ma50.abs() + 1e-10)
    df['ma5_20_cross']  = (ma5  - ma20)  / (ma20.abs() + 1e-10)
    df['ma20_50_cross'] = (ma20 - ma50)  / (ma50.abs() + 1e-10)

    # ── Volatility (5) ───────────────────────────────────────────────────────
    ret = close.pct_change()
    df['vol_5d']    = ret.rolling(5).std()
    df['vol_10d']   = ret.rolling(10).std()
    df['vol_20d']   = ret.rolling(20).std()
    df['vol_ratio'] = df['vol_5d'] / (df['vol_20d'] + 1e-10)
    # ATR (14-day)
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low  - prev_close).abs(),
    ], axis=1).max(axis=1)
    df['atr_14'] = tr.rolling(14).mean()

    # ── Momentum (6) ─────────────────────────────────────────────────────────
    # RSI-14
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    df['rsi_14'] = 100 - (100 / (1 + gain / (loss + 1e-10)))
    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df['macd']        = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist']   = df['macd'] - df['macd_signal']
    # Stochastic %K / %D
    low14  = low.rolling(14).min()
    high14 = high.rolling(14).max()
    df['stoch_k'] = 100 * (close - low14) / (high14 - low14 + 1e-10)
    df['stoch_d'] = df['stoch_k'].rolling(3).mean()

    # ── Bollinger Bands (2) ──────────────────────────────────────────────────
    bb_mid   = close.rolling(20).mean()
    bb_std   = close.rolling(20).std()
    bb_upper = bb_mid + 2 * bb_std
    bb_lower = bb_mid - 2 * bb_std
    df['bb_width'] = (bb_upper - bb_lower) / (bb_mid.abs() + 1e-10)
    df['bb_pos']   = (close - bb_lower) / (bb_upper - bb_lower + 1e-10)

    # ── Volume (2) ───────────────────────────────────────────────────────────
    vol_ma20 = volume.rolling(20).mean()
    df['vol_ratio_20'] = volume / (vol_ma20 + 1e-10)
    obv     = (np.sign(close.diff()) * volume).cumsum()
    obv_mu  = obv.rolling(20).mean()
    obv_std = obv.rolling(20).std()
    df['obv_norm'] = (obv - obv_mu) / (obv_std + 1e-10)

    # ── Candlestick (1) ──────────────────────────────────────────────────────
    df['hl_range'] = (high - low) / (close.abs() + 1e-10)

    # ── Crash Label ──────────────────────────────────────────────────────────
    # 5-day forward cumulative return < -3%
    df['fwd_5d'] = close.pct_change(5).shift(-5)
    df['crash']  = (df['fwd_5d'] < -0.03).astype(int)

    # Drop rows with any NaN in feature/label columns
    df = df.dropna(subset=FEATURE_COLS + ['crash']).reset_index(drop=True)

    return df

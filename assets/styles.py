"""
assets/styles.py
────────────────
Dark Trading Terminal theme — inject_css() + sidebar_header().
Design: Bloomberg/TradingView inspired dark UI with neon accents.
"""

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── CSS VARIABLES ───────────────────────────────────────────────────────── */
:root {
    --bg-0:   #070B12;
    --bg-1:   #0A0E1A;
    --bg-2:   #0F1629;
    --bg-3:   #141C35;
    --bg-4:   #1A2340;
    --green:  #00D4AA;
    --green2: #00FF88;
    --red:    #FF3366;
    --red2:   #FF6B8A;
    --blue:   #4FACFE;
    --gold:   #FFB700;
    --purple: #8B5CF6;
    --t0:     #F0F4FF;
    --t1:     #B8C4D8;
    --t2:     #6B7B8F;
    --t3:     #3D4F63;
    --bdr:    rgba(255,255,255,0.06);
    --bdr-g:  rgba(0,212,170,0.22);
    --glow:   0 0 24px rgba(0,212,170,0.10);
}

/* ── GLOBAL ──────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}
.stApp { background: var(--bg-1) !important; }
.block-container { padding-top: 1.2rem !important; max-width: 1380px; }

/* ── Hide chrome ─────────────────────────────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── SIDEBAR ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-0) !important;
    border-right: 1px solid var(--bdr);
}
[data-testid="stSidebar"] * { color: var(--t1) !important; }

[data-testid="stSidebarNav"] a {
    color: var(--t2) !important;
    font-size: 12px;
    font-weight: 500;
    padding: 9px 14px;
    border-radius: 6px;
    margin: 2px 8px;
    display: block;
    text-decoration: none;
    transition: all 0.18s;
    border-left: 2px solid transparent;
    letter-spacing: 0.2px;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: var(--bg-3) !important;
    color: var(--green) !important;
    border-left-color: var(--green);
}
[data-testid="stSidebarNav"] a[aria-selected="true"] {
    background: var(--bg-3) !important;
    color: var(--green) !important;
    border-left: 2px solid var(--green);
    font-weight: 600;
}

/* ── BUTTONS ─────────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, var(--green) 0%, #009E82 100%) !important;
    color: #060A10 !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    padding: 10px 22px !important;
    letter-spacing: 1px;
    text-transform: uppercase;
    transition: all 0.2s !important;
    box-shadow: 0 4px 16px rgba(0,212,170,0.28) !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, var(--green2) 0%, var(--green) 100%) !important;
    box-shadow: 0 6px 24px rgba(0,212,170,0.45) !important;
    transform: translateY(-1px);
}
.stButton > button:active { transform: translateY(0) !important; }

[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: var(--green) !important;
    border: 1px solid var(--bdr-g) !important;
    box-shadow: none !important;
    font-weight: 600 !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(0,212,170,0.08) !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── TABS ────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-2) !important;
    border-radius: 8px 8px 0 0;
    padding: 6px 6px 0;
    border-bottom: 1px solid var(--bdr-g);
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--t2) !important;
    font-size: 12px !important;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 6px 6px 0 0;
    border: none;
    transition: all 0.18s;
    white-space: nowrap;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.3px;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--green) !important;
    background: var(--bg-3) !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-3) !important;
    color: var(--green) !important;
    font-weight: 700 !important;
    border-bottom: 2px solid var(--green) !important;
}

/* ── METRICS ─────────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--bg-2) !important;
    border: 1px solid var(--bdr-g);
    border-radius: 8px;
    padding: 14px 18px;
    box-shadow: var(--glow);
    transition: all 0.2s;
}
[data-testid="metric-container"]:hover {
    border-color: var(--green);
    box-shadow: 0 0 32px rgba(0,212,170,0.18);
}
[data-testid="metric-container"] label {
    color: var(--t2) !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-family: 'IBM Plex Mono', monospace !important;
}
[data-testid="stMetricValue"] {
    color: var(--t0) !important;
    font-weight: 700 !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
[data-testid="stMetricDelta"] {
    font-size: 11px !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

/* ── FILE UPLOADER ───────────────────────────────────────────────────────── */
[data-testid="stFileUploadDropzone"] {
    background: var(--bg-2) !important;
    border: 2px dashed var(--green) !important;
    border-radius: 10px !important;
    transition: all 0.2s;
}
[data-testid="stFileUploadDropzone"]:hover {
    background: rgba(0,212,170,0.04) !important;
    box-shadow: 0 0 40px rgba(0,212,170,0.1);
}

/* ── EXPANDER ────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--bg-2) !important;
    border: 1px solid var(--bdr) !important;
    border-radius: 8px !important;
    margin-bottom: 8px;
    transition: border-color 0.2s;
}
[data-testid="stExpander"]:hover { border-color: var(--bdr-g) !important; }

/* ── DATAFRAME ───────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 8px;
    border: 1px solid var(--bdr);
    overflow: hidden;
}

/* ── SELECTBOX ───────────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg-2) !important;
    border: 1px solid var(--bdr-g) !important;
    border-radius: 6px !important;
    color: var(--t0) !important;
}

/* ── SLIDER ──────────────────────────────────────────────────────────────── */
[data-testid="stSlider"] > div > div > div > div { background: var(--green) !important; }

/* ── PROGRESS ────────────────────────────────────────────────────────────── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, var(--green), var(--green2)) !important;
}

/* ── SCROLLBAR ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-1); }
::-webkit-scrollbar-thumb { background: var(--bg-4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--green); }

/* ── HR ──────────────────────────────────────────────────────────────────── */
hr { border: none; border-top: 1px solid var(--bdr); margin: 16px 0; }

/* ══════════════════════════════════════════════════════════════════════════
   CUSTOM COMPONENT CLASSES
   ══════════════════════════════════════════════════════════════════════════ */

/* ── TICKER TAPE ─────────────────────────────────────────────────────────── */
@keyframes ticker { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
@keyframes blink  { 0%,100% { opacity:1; } 50% { opacity:0.15; } }
@keyframes fadeUp { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }
@keyframes pulseGlow {
    0%,100% { box-shadow: 0 0 20px rgba(0,212,170,0.10); }
    50%      { box-shadow: 0 0 40px rgba(0,212,170,0.25); }
}

.ticker-wrap {
    overflow: hidden;
    background: var(--bg-0);
    border-top: 1px solid var(--bdr-g);
    border-bottom: 1px solid var(--bdr-g);
    padding: 9px 0;
    margin-bottom: 20px;
    user-select: none;
}
.ticker { display: inline-flex; white-space: nowrap; animation: ticker 52s linear infinite; }
.ticker:hover { animation-play-state: paused; }
.t-item { display: inline-block; padding: 0 24px; font-family: 'IBM Plex Mono', monospace; font-size: 12px; font-weight: 500; color: var(--t2); }
.t-sym  { color: var(--t0); font-weight: 700; margin-right: 8px; }
.t-pos  { color: var(--green); }
.t-neg  { color: var(--red); }
.t-div  { color: var(--t3); padding: 0 8px; }

/* ── HERO ────────────────────────────────────────────────────────────────── */
.hero-box {
    background: linear-gradient(135deg, #06080F 0%, #0A1120 50%, #0E1C34 100%);
    border: 1px solid var(--bdr-g);
    border-radius: 14px;
    padding: 52px 48px 44px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    animation: fadeUp 0.45s ease;
}
.hero-box::before {
    content: '';
    position: absolute; top: -100px; right: -60px;
    width: 520px; height: 520px;
    background: radial-gradient(circle, rgba(0,212,170,0.07) 0%, transparent 65%);
    pointer-events: none;
}
.hero-box::after {
    content: '';
    position: absolute; bottom: -80px; left: 5%;
    width: 380px; height: 380px;
    background: radial-gradient(circle, rgba(79,172,254,0.04) 0%, transparent 65%);
    pointer-events: none;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(0,212,170,0.09);
    color: var(--green);
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 10px; font-weight: 700; letter-spacing: 2px;
    border: 1px solid rgba(0,212,170,0.28);
    margin-bottom: 22px; text-transform: uppercase;
    font-family: 'IBM Plex Mono', monospace;
}
.blink-dot {
    width: 7px; height: 7px;
    background: var(--green2); border-radius: 50%;
    display: inline-block;
    animation: blink 1.6s infinite;
    flex-shrink: 0;
}
.hero-title {
    font-size: 46px; font-weight: 900; color: var(--t0);
    line-height: 1.1; margin-bottom: 14px; letter-spacing: -1.5px;
}
.hero-title .accent { color: var(--green); }
.hero-sub {
    font-size: 15px; color: var(--t2); line-height: 1.75;
    max-width: 620px; margin-bottom: 36px;
}
.hero-stats { display: flex; gap: 44px; flex-wrap: wrap; }
.hero-stat  { display: flex; flex-direction: column; gap: 4px; }
.hero-stat-val {
    font-size: 30px; font-weight: 700; color: var(--green);
    font-family: 'IBM Plex Mono', monospace; line-height: 1;
}
.hero-stat-lbl {
    font-size: 10px; color: var(--t2); text-transform: uppercase;
    letter-spacing: 1.5px; font-weight: 600;
}

/* ── KPI CARD ────────────────────────────────────────────────────────────── */
.kpi-card {
    background: var(--bg-2); border: 1px solid var(--bdr); border-radius: 10px;
    padding: 20px 16px; text-align: center;
    transition: all 0.22s ease; position: relative; overflow: hidden; cursor: default;
}
.kpi-card:hover {
    border-color: var(--bdr-g); transform: translateY(-3px);
    box-shadow: 0 14px 40px rgba(0,0,0,0.45), var(--glow);
}
.kpi-card::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--green), transparent);
    opacity: 0; transition: opacity 0.22s;
}
.kpi-card:hover::after { opacity: 1; }
.kpi-val  { font-size: 26px; font-weight: 700; font-family: 'IBM Plex Mono', monospace; line-height: 1.15; margin-bottom: 6px; }
.kpi-lbl  { font-size: 10px; color: var(--t2); font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; }
.kpi-sub  { font-size: 11px; color: var(--t2); margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--bdr); line-height: 1.4; }

/* ── STEP CARD ───────────────────────────────────────────────────────────── */
.step-card {
    background: var(--bg-2); border: 1px solid var(--bdr); border-radius: 10px;
    padding: 24px 18px; transition: all 0.22s ease; height: 100%;
}
.step-card:hover { border-color: rgba(0,212,170,0.35); transform: translateY(-3px); box-shadow: 0 12px 32px rgba(0,0,0,0.4); }
.step-num {
    width: 34px; height: 34px;
    background: rgba(0,212,170,0.12); color: var(--green);
    border: 1px solid rgba(0,212,170,0.35); border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 13px; font-family: 'IBM Plex Mono', monospace;
    margin: 0 auto 16px;
}
.step-title { font-size: 12px; font-weight: 700; color: var(--t0); margin-bottom: 10px; text-align: center; text-transform: uppercase; letter-spacing: 1px; }
.step-desc  { font-size: 12px; color: var(--t2); line-height: 1.65; text-align: center; }

/* ── SECTION HEADER ──────────────────────────────────────────────────────── */
.section-hdr {
    display: flex; align-items: center; gap: 12px;
    margin: 22px 0 16px; padding-bottom: 10px; border-bottom: 1px solid var(--bdr);
}
.section-hdr h2, .section-hdr h3 { margin: 0; color: var(--t0); font-weight: 700; letter-spacing: -0.3px; }

/* ── BANNERS ─────────────────────────────────────────────────────────────── */
.info-banner {
    background: rgba(0,212,170,0.07); border: 1px solid rgba(0,212,170,0.25);
    border-left: 3px solid var(--green); border-radius: 8px;
    padding: 12px 16px; color: #6EDEC8; font-size: 13px; font-weight: 500; margin-bottom: 16px;
}
.warn-banner {
    background: rgba(255,51,102,0.07); border: 1px solid rgba(255,51,102,0.25);
    border-left: 3px solid var(--red); border-radius: 8px;
    padding: 12px 16px; color: var(--red2); font-size: 13px; font-weight: 500; margin-bottom: 16px;
}

/* ── SIDEBAR STATUS ──────────────────────────────────────────────────────── */
.sidebar-logo { padding: 20px 14px 16px; border-bottom: 1px solid var(--bdr); margin-bottom: 8px; text-align: center; }
.sidebar-logo-title { color: var(--t0); font-size: 14px; font-weight: 700; margin-top: 8px; letter-spacing: -0.3px; }
.sidebar-logo-sub   { color: var(--t2); font-size: 10px; margin-top: 3px; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase; letter-spacing: 1.5px; }
.status-row { padding: 10px 14px; font-size: 11px; font-family: 'IBM Plex Mono', monospace; color: var(--t2); line-height: 2.0; }
.s-on  { color: var(--green); font-weight: 600; }
.s-off { color: var(--t3); }

/* ── TERMINAL BOX ────────────────────────────────────────────────────────── */
.term-box {
    background: var(--bg-0); border: 1px solid var(--bdr-g); border-radius: 8px;
    padding: 18px 20px; font-family: 'IBM Plex Mono', monospace; font-size: 12px;
    color: var(--t1); line-height: 1.9;
}
.t-g { color: var(--green); } .t-r { color: var(--red); }
.t-d { color: var(--t2); }   .t-b { color: var(--t0); font-weight: 600; }
.t-gold { color: var(--gold); }

/* ── INSIGHT PANEL ───────────────────────────────────────────────────────── */
.insight-panel {
    background: var(--bg-2); border: 1px solid var(--bdr);
    border-left: 3px solid var(--green); border-radius: 10px;
    padding: 18px 20px; margin-bottom: 12px;
}
.insight-label {
    font-size: 10px; font-weight: 700; color: var(--green);
    text-transform: uppercase; letter-spacing: 2px; margin-bottom: 7px;
    font-family: 'IBM Plex Mono', monospace;
}
.insight-text { font-size: 13px; color: var(--t1); line-height: 1.65; }

/* ── CRASH EVENT ─────────────────────────────────────────────────────────── */
.crash-event {
    background: var(--bg-2); border: 1px solid var(--bdr);
    border-left: 3px solid var(--red); border-radius: 8px;
    padding: 14px 16px; margin-bottom: 8px; transition: all 0.2s;
}
.crash-event:hover { border-color: rgba(255,51,102,0.45); }
.crash-event-date { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: var(--red); font-weight: 600; }
.crash-event-name { font-size: 13px; font-weight: 700; color: var(--t0); margin: 4px 0 2px; }
.crash-event-desc { font-size: 12px; color: var(--t2); }

/* ── FEATURE PILL ────────────────────────────────────────────────────────── */
.feat-pill {
    display: inline-block; background: rgba(0,212,170,0.08); color: var(--green);
    border: 1px solid rgba(0,212,170,0.2); padding: 3px 10px; border-radius: 12px;
    font-size: 11px; font-weight: 600; font-family: 'IBM Plex Mono', monospace; margin: 2px;
}

/* ── MODEL TAG ───────────────────────────────────────────────────────────── */
.model-tag {
    display: inline-block; background: rgba(0,212,170,0.09); color: var(--green);
    border: 1px solid rgba(0,212,170,0.25); padding: 2px 8px; border-radius: 4px;
    font-size: 10px; font-weight: 700; font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.8px; margin-right: 4px;
}

/* ── STATUS BADGE ────────────────────────────────────────────────────────── */
.badge-live {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,255,136,0.09); color: var(--green2);
    border: 1px solid rgba(0,255,136,0.25); padding: 3px 10px; border-radius: 12px;
    font-size: 10px; font-weight: 700; font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 1px; text-transform: uppercase;
}

/* ── RISK LEVEL COLOURS ──────────────────────────────────────────────────── */
.risk-vhigh  { color: #FF3366; font-weight: 700; font-family: 'IBM Plex Mono', monospace; }
.risk-high   { color: #FF8C42; font-weight: 700; font-family: 'IBM Plex Mono', monospace; }
.risk-medium { color: #FFB700; font-weight: 600; font-family: 'IBM Plex Mono', monospace; }
.risk-low    { color: var(--green); font-weight: 600; font-family: 'IBM Plex Mono', monospace; }
</style>
"""

# ── Live market data ─────────────────────────────────────────────────────────
_TICKER_SYMBOLS = [
    ("^GSPC",  "S&P 500",   "{:,.2f}"),
    ("^IXIC",  "NASDAQ",    "{:,.2f}"),
    ("^DJI",   "DOW JONES", "{:,.2f}"),
    ("^NSEI",  "NIFTY 50",  "{:,.2f}"),
    ("^BSESN", "SENSEX",    "{:,.2f}"),
    ("CL=F",   "CRUDE OIL", "${:.2f}"),
    ("GC=F",   "GOLD",      "${:,.2f}"),
    ("SI=F",   "SILVER",    "${:.3f}"),
]

# Fallback values shown when yfinance is unreachable
_FALLBACK = {
    "^GSPC":  (5_248.49,  0.32),
    "^IXIC":  (16_399.95, 0.18),
    "^DJI":   (39_512.84, 0.40),
    "^NSEI":  (22_345.60, 0.62),
    "^BSESN": (73_428.10, 0.55),
    "CL=F":   (83.18,    -0.61),
    "GC=F":   (2_338.60,  0.43),
    "SI=F":   (27.485,    0.71),
}


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_market_data() -> dict:
    """Fetch latest price + daily % change for all ticker symbols. TTL = 5 min."""
    try:
        import yfinance as yf
        tickers = [s for s, _, _ in _TICKER_SYMBOLS]
        raw = yf.download(tickers, period="2d", interval="1d",
                          progress=False, auto_adjust=True)
        result = {}
        for sym, _, _ in _TICKER_SYMBOLS:
            try:
                closes = raw["Close"][sym].dropna()
                if len(closes) >= 2:
                    price = float(closes.iloc[-1])
                    prev  = float(closes.iloc[-2])
                    pct   = (price - prev) / prev * 100
                else:
                    price, pct = _FALLBACK[sym]
            except Exception:
                price, pct = _FALLBACK[sym]
            result[sym] = (price, pct)
        return result
    except Exception:
        return {sym: _FALLBACK[sym] for sym, _, _ in _TICKER_SYMBOLS}


def _build_ticker_html(data: dict) -> str:
    items = []
    for sym, label, fmt in _TICKER_SYMBOLS:
        price, pct = data.get(sym, _FALLBACK[sym])
        arrow = "▲" if pct >= 0 else "▼"
        css   = "t-pos" if pct >= 0 else "t-neg"
        sign  = "+" if pct >= 0 else ""
        price_str = fmt.format(price)
        items.append(
            f'<span class="t-item"><span class="t-sym">{label}</span>'
            f'<span class="{css}">{arrow} {price_str} &nbsp;{sign}{pct:.2f}%</span></span>'
            f'<span class="t-item t-div">│</span>'
        )
    inner = "\n    ".join(items)
    # duplicate for seamless CSS loop
    return f"""<div class="ticker-wrap">
  <div class="ticker">
    {inner}
    {inner}
  </div>
</div>"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


def ticker_tape():
    data = _fetch_market_data()
    st.markdown(_build_ticker_html(data), unsafe_allow_html=True)


def sidebar_header():
    import os, pathlib
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <div style="font-size:26px;">📈</div>
            <div class="sidebar-logo-title">Market Crash Predictor</div>
            <div class="sidebar-logo-sub">Global Markets · XAI · 2026</div>
        </div>
        """, unsafe_allow_html=True)

        data_ok  = 'df_feat'  in st.session_state
        model_ok = 'metrics'  in st.session_state

        st.markdown(f"""
        <div class="status-row">
            <div><span class="{'s-on' if data_ok  else 's-off'}">{'● DATA LOADED' if data_ok  else '○ NO DATA'}</span></div>
            <div><span class="{'s-on' if model_ok else 's-off'}">{'● MODELS READY' if model_ok else '○ NOT TRAINED'}</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        # Sample CSV download — file lives at project_root/sample_data/
        _sample = pathlib.Path(__file__).parent.parent / "sample_data" / "NIFTY50_sample_2022_2024.csv"
        if _sample.exists():
            st.download_button(
                label="⬇ Download Sample CSV",
                data=_sample.read_bytes(),
                file_name="NIFTY50_sample_2022_2024.csv",
                mime="text/csv",
                use_container_width=True,
                help="500-day NIFTY 50 sample in NSE format — ready to upload",
            )
            st.markdown(
                "<div style='font-size:10px;color:#3D4F63;text-align:center;margin-top:4px;'>"
                "NSE format · 500 trading days · 2022–2024</div>",
                unsafe_allow_html=True,
            )
            st.markdown("---")

"""
app.py — Navigation Controller
────────────────────────────────
Sets page config, injects CSS, renders sidebar, then delegates to the
selected page via st.navigation(). This gives all pages custom sidebar
labels without renaming files.
"""

import streamlit as st

st.set_page_config(
    page_title="Market Crash Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

from assets.styles import inject_css, sidebar_header

inject_css()
sidebar_header()

pg = st.navigation([
    st.Page("pages/home.py",            title="Dashboard",        icon="🏠"),
    st.Page("pages/1_Upload.py",        title="Upload Data",      icon="📂"),
    st.Page("pages/2_Results.py",       title="Model Results",    icon="📊"),
    st.Page("pages/3_Predictions.py",   title="Live Predictions", icon="🔮"),
])
pg.run()

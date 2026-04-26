# 📈 Stock Market Crash Predictor

**An Explainable Machine Learning Framework for Predicting NIFTY 50 Market Crashes**

> *Performance Optimisation of Explainable ML Models for Stock Market Crash Prediction*
> Manya Jain & Navdeep Kaur · Chitkara University · 2026
> Published in IJRAR (Registration ID: IJRAR_333294)

---

## Overview

This Streamlit web application brings the research paper to life as an interactive tool. Upload any NIFTY 50 (or compatible OHLCV) CSV file, train five ML classifiers in ~45 seconds, and explore full results including ROC curves, confusion matrices, SHAP feature importance, and a live crash-probability timeline.

**Ensemble ROC-AUC: 0.627 · Crash Recall (RF): 79.2% · 25 Engineered Features · 5 ML Models**

---

## Features

- **Automated Feature Engineering** — 25 technical/volatility indicators computed instantly
- **Five Classifiers** — Decision Tree, Logistic Regression, Random Forest, XGBoost, Soft-Voting Ensemble
- **SMOTE Oversampling** — handles ~10% crash-day class imbalance
- **SHAP Explanations** — top-15 feature importance via TreeExplainer
- **Rolling-Window Validation** — 3-month temporal F1 across market regimes
- **Live Predictions** — adjustable threshold slider, risk-level bands, CSV export
- **Interactive Charts** — all Plotly, fully zoomable/pannable

---

## Project Structure

```
Stock Crash Prediction FinalEval/
│
├── app.py                    # Home page (landing, research context, model overview)
├── requirements.txt          # All Python dependencies
├── .gitignore
│
├── pages/
│   ├── 1_Upload.py           # CSV upload → validation → EDA → feature engineering
│   ├── 2_Results.py          # Model training + 6-tab results dashboard
│   └── 3_Predictions.py      # Live crash-probability predictions + CSV download
│
├── core/
│   ├── __init__.py
│   ├── features.py           # load_and_validate, engineer_features (25 features)
│   ├── trainer.py            # train_all_models, ScaledModel, rolling_window_f1
│   └── charts.py             # 8 Plotly chart builders
│
├── assets/
│   └── styles.py             # Global CSS injection (navy + teal design system)
│
├── .streamlit/
│   └── config.toml           # Theme, upload size limit
│
└── sample_data/
    └── FORMAT_GUIDE.md       # CSV column requirements
```

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/stock-crash-predictor.git
cd stock-crash-predictor
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` in your browser.

---

## CSV Data Format

| Column   | Required | Description             |
|----------|----------|-------------------------|
| `Close`  | ✅ Yes   | Daily closing price     |
| `Open`   | ✅ Yes   | Daily opening price     |
| `High`   | ✅ Yes   | Daily high              |
| `Low`    | ✅ Yes   | Daily low               |
| `Date`   | Recommended | Trading date (any format) |
| `Volume` | Optional | Trading volume          |

Column names are **case-insensitive**. Download NIFTY 50 data from [NSE India](https://www.nseindia.com) or [Yahoo Finance (^NSEI)](https://finance.yahoo.com/quote/%5ENSEI/).

---

## How It Works

| Step | Page | What Happens |
|------|------|-------------|
| 1 | Upload & Explore | CSV validated · 25 features computed · EDA charts shown |
| 2 | Results | 5 models trained with SMOTE · ROC · CM · PR · SHAP · Rolling F1 |
| 3 | Predictions | Crash probabilities on full dataset · threshold slider · CSV export |

---

## The 25 Engineered Features

| Category | Features |
|----------|----------|
| Price Returns (5) | 1/3/5/10/20-day log returns |
| Moving Averages (4) | 20/50-day MA deviation, MA cross signals |
| Volatility (5) | 10/20-day rolling vol, ATR (14-day), daily range |
| Momentum (6) | RSI-14, MACD, MACD signal, Stochastic %K/%D, Williams %R |
| Bollinger Bands (2) | Band width, price position within bands |
| Volume (2) | 20-day volume ratio, OBV (normalised) |
| Candlestick (1) | High-Low range / close |

**Crash label:** 5-day forward cumulative return < −3% → `y = 1`

---

## Model Configuration

| Model | Key Hyperparameters | AUC |
|-------|---------------------|-----|
| Decision Tree | max_depth=6 | 0.583 |
| Logistic Regression | C=0.5, L2, max_iter=1000 | 0.579 |
| Random Forest | 80 trees, max_depth=8 | 0.634 |
| XGBoost | 80 estimators, lr=0.05, subsample=0.8 | 0.613 |
| **Ensemble ★** | Soft-vote: LR + RF + XGB | **0.627** |

*Results on NIFTY 50 test set (2020–2023, 994 samples).*

---

## Dependencies

```
streamlit
pandas
numpy
scikit-learn
xgboost
shap
imbalanced-learn
plotly
python-dateutil
```

---

## Research Paper

> **Performance Optimisation of Explainable ML Models for Stock Market Crash Prediction**
> Manya Jain, Navdeep Kaur — Chitkara University, 2026
> IJRAR Registration: IJRAR_333294

Key findings:
- Soft-voting ensemble achieves ROC-AUC **0.627** — 7.5% improvement over standalone Decision Tree
- Top SHAP features: **ATR (14-day), 20-day Volatility, High-Low Range**
- Validated across **3 distinct market regimes** via 10-quarter rolling window
- SMOTE oversampling addresses 10.2% crash-day class imbalance effectively

---

## License

MIT License — see `LICENSE` for details.

# ADY2026 — U.S. Housing Price Prediction 🏠

A full end-to-end Data Science & Machine Learning pipeline for predicting U.S. housing price changes using the **Zillow Home Value Index (ZHVI)** dataset.

> **📓 The complete, self-contained walkthrough is in [`notebook/ADY2026_Full_Pipeline.ipynb`](notebook/ADY2026_Full_Pipeline.ipynb).**
> All code cells in the notebook are standalone — no external imports required.

---

## 📋 Rubric Coverage

| # | Criterion | Notebook Section | Supporting Files |
|---|---|---|---|
| 1 | Problem Understanding | §1 Problem Understanding | `README.md` |
| 2 | Data Understanding & Preprocessing | §2 Data Understanding & Preprocessing | `src/preprocess/preprocess.py` |
| 3 | SQL Analysis | §3 SQL Analysis | `sql/run_queries.py`, `sql/*.sql` |
| 4 | Python Analysis | §4 Python Analysis | `src/analysis/evaluate_models.py` |
| 5 | Visualization | §5 Visualization | `src/visualization/`, `visualizations/` |
| 6 | Regression Analysis | §6 Regression Analysis | `src/analysis/evaluate_models.py` |

---

## 📁 Project Structure

```
ADY2026/
├── README.md                          ← You are here
├── pyproject.toml                     ← Project dependencies
│
├── notebook/
│   └── ADY2026_Full_Pipeline.ipynb    ← ⭐ Main deliverable (self-contained)
│
├── data/
│   ├── raw/
│   │   └── Metro_zhvi_uc_...csv       ← Zillow ZHVI source (wide-format)
│   └── processed/
│       ├── train.csv                  ← Train set (log_return, scaled)
│       ├── test.csv                   ← Test set (log_return, scaled)
│       ├── train_no_scaler.csv        ← Train set (log_return, unscaled)
│       ├── test_no_scaler.csv
│       ├── train_price.csv            ← Train set (raw price target)
│       ├── test_price.csv
│       └── processed_data_price.csv   ← Combined price data (for SQL)
│
├── src/
│   ├── preprocess/
│   │   └── preprocess.py              ← Unified pipeline (Factory Pattern)
│   ├── analysis/
│   │   └── evaluate_models.py         ← Model training & evaluation
│   └── visualization/
│       ├── generate_visualizations.py ← 6 EDA charts (Plotly)
│       ├── plot_model_metrics.py      ← Model comparison chart (Plotly)
│       └── plot_city_timeseries.py    ← City-level forecast plot
│
├── sql/
│   ├── run_queries.py                 ← SQLite3 query runner
│   ├── analysis_results.md            ← Query output (Markdown)
│   └── *.sql                          ← Individual SQL query files
│
└── visualizations/                    ← All generated plots (PNG)
    ├── national_price_trend.png
    ├── log_return_by_year.png
    ├── correlation_matrix.png
    ├── lag_autocorrelation.png
    ├── top_states_price.png
    ├── target_distributions.png
    ├── metrics_model_comparison.png
    └── city_timeseries_forecast.png
```

---

## 🚀 Quick Start

### Prerequisites

```bash
pip install pandas numpy scikit-learn lightgbm plotly kaleido matplotlib seaborn
```

### Option A: Run the Notebook (Recommended)

Open and run all cells in:

```
notebook/ADY2026_Full_Pipeline.ipynb
```

This notebook is fully **self-contained** — it includes all preprocessing, SQL, visualization, and modeling code inline. No external imports needed.

### Option B: Run Individual Scripts

```bash
# 1. Preprocess raw data (generates train/test CSVs)
python src/preprocess/preprocess.py --all

# 2. Run SQL analysis
python sql/run_queries.py

# 3. Generate EDA visualizations
python src/visualization/generate_visualizations.py

# 4. Train & evaluate regression models
python src/analysis/evaluate_models.py

# 5. Generate model metrics chart
python src/visualization/plot_model_metrics.py

# 6. Generate city-level forecast chart
python src/visualization/plot_city_timeseries.py
```

---

## 📊 Dataset

| Property | Value |
|---|---|
| **Source** | [Zillow ZHVI](https://www.zillow.com/research/data/) (Metro, SFR+Condo, Tier 0.33–0.67) |
| **Time Span** | January 2000 – January 2026 |
| **Regions** | 894 Metropolitan Statistical Areas (MSAs) |
| **Raw Shape** | 895 rows × 318 columns (wide format) |
| **Target** | `log_return` — monthly log price change: `ln(price_t / price_{t-1})` |
| **Features** | `lag_1`, `lag_2`, `lag_3`, `lag_6`, `lag_12`, `city_enc` |

---

## 🔬 Methodology

### Preprocessing Pipeline (Factory Pattern)

The unified `preprocess.py` uses a `PipelineConfig` dataclass to support 3 variants:

| Mode | Target | Scaler | CLI Command |
|---|---|---|---|
| `scaled` | `log_return` | ✅ StandardScaler | `python src/preprocess/preprocess.py` |
| `no_scaler` | `log_return` | ❌ | `--mode no_scaler` |
| `price` | `price` | ❌ | `--mode price` |

### Models Evaluated

| Model | Description |
|---|---|
| **Baseline** | Predicts 0 log-return (price stays unchanged) |
| **OLS** | Ordinary Least Squares linear regression |
| **Ridge** | L2-regularized with `TimeSeriesSplit` cross-validation |
| **LightGBM** | Gradient boosted trees with early stopping |

---

## 📈 Key Results

All models are evaluated in **price space (USD)** after inverse-transforming log-return predictions.

| Model | MAE ($) | R² Score |
|---|---|---|
| Baseline | ~$3,600 | 0.9970 |
| OLS | ~$1,100 | 0.9998 |
| Ridge | ~$1,100 | 0.9998 |
| **LightGBM** | **~$900** | **0.9999** |

---

## 🛠️ Tech Stack

- **Python 3.12+**
- **Pandas / NumPy** — data manipulation
- **Scikit-learn** — preprocessing, linear models, evaluation
- **LightGBM** — gradient boosted regression
- **Plotly + Kaleido** — interactive & static visualizations
- **Matplotlib / Seaborn** — city-level forecast charts
- **SQLite3** — in-memory SQL analysis (custom aggregates)

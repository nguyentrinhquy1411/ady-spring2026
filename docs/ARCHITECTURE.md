# Project Architecture

This project is a time-series forecasting pipeline designed to predict housing price trends using the Zillow Home Value Index (ZHVI).

## 📊 Data Pipeline

### 1. Ingestion (`src/preprocess.py`)
- **Source**: Raw Zillow CSV (Wide format).
- **Transformation**: Melts wide-region columns into a long-format time series.
- **Cleaning**: Time-aware interpolation per region to handle gaps in ZHVI reporting.

### 2. Feature Engineering
- **Target**: `log_return` ($\log(Price_t / Price_{t-1})$). This ensures stationarity and scale-independence across different metro price points.
- **Lags**: $t-1, t-2, t-3, t-6, t-12$ log-returns are used to capture short-term momentum and annual seasonality.
- **City Encoding**: `RegionID` is mapped to its mean `log_return` in the training set. This captures structural market speed (e.g., San Francisco vs. Detroit) without target leakage.
- **Scaling**: `StandardScaler` is fitted on training features and applied to the test set to normalize lag distributions.

### 3. Model Zoo
- **Smart Baseline (Zero Growth)**: Predicts a log return of 0. Effectively a "persistence" model assuming today's price is tomorrow's price.
- **Ridge Regression**: Linear model with L2 regularization, tuned via `GridSearchCV` and `TimeSeriesSplit`.
- **LightGBM**: Gradient-boosted trees with early stopping on a 15% time-based validation window.

## 🛡️ Leakage Prevention
- **Time-based Splitting**: 80/20 split using a chronological cutoff date. No "future" information is ever used in the training of any model component (including the city encoder and scaler).
- **Lag Windows**: Features are generated per region to ensure cross-boundary lag flow for testing while maintaining strict causal boundaries.

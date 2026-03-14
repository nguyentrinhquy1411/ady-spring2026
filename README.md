# Housing Price Predictor 🏠📈

A professional ML pipeline for predicting housing price trends (ZHVI) across all US Metropolitan Statistical Areas (MSAs). It leverages stationary log-returns and momentum-based features to achieve high-precision forecasts.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### 2. Setup
```bash
uv sync
```

### 3. Run Pipeline
To run the full preprocessing and model evaluation suite:
```bash
# Preprocess raw data (generates data/processed/train.csv)
uv run src/preprocess.py

# Run the standardized training and evaluation suite
uv run src/train_v2.py
```

## 📁 Project Structure

- `src/`
  - `preprocess.py`: Wide-to-long transformation, time-interpolation, and feature engineering.
  - `train_v2.py`: Main training script with leakage audits and standardized metrics.
- `notebooks/`
  - `02_baseline.ipynb`: Exploratory modeling and Ridge baseline.
  - `03_lightgbm.ipynb`: Gradient Boosting implementation and feature importance.
- `assets/`: Exported models (`.pkl`), charts (`.png`), and evaluation logs.
- `docs/`: In-depth documentation on [Architecture](docs/ARCHITECTURE.md) and [Results](docs/RESULTS.md).

## 📊 Performance at a Glance
The current **Ridge Regression** model achieves:
- **Price MAE**: ~$495 (Average error on house value)
- **Price R²**: 0.9999+
- **Baseline Improvement**: >70% reduction in error vs. the Zero Growth baseline ($1,795 MAE).

## 🛠 Features
- **Stationary Target**: Predicts `log_return` instead of absolute price levels.
- **Leakage-Proof Encoding**: Target encoding of cities fitted strictly on training data.
- **Smart Baselines**: Benchmark against "Zero Growth" persistence models.
- **Production Ready**: Full pipeline with `StandardScaler` and model serialization.

---
*Developed for the ADY-2026 Housing Project.*

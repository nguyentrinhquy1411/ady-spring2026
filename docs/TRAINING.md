# Modeling & Training Pipeline

This document details the training logic, model selection, and evaluation methodology implemented in `src/train_v2.py`.

## ⚙️ Pipeline Overview

The training script is designed as an end-to-end evaluation suite. It compares three different approaches to ensure that any complexity added (like Gradient Boosting) is actually yielding performance gains over simple baselines.

---

## 🔬 Model Selection

### 1. Zero-Growth (Baseline)
A persistence model that assumes the `log_return` is always `0`. 
- **Rationale**: Real estate markets have high inertia. The most rigorous test for any model is whether it can outperform the assumption that "nothing changes."

### 2. Ridge Regression
A linear model with L2 regularization.
- **Cross-Validation**: Uses `TimeSeriesSplit` with 5 folds. This is an "expanding window" approach that ensures we never train on future data to predict the past.
- **Hyperparameters**: `alpha` is tuned via `GridSearchCV` to find the optimal balance between bias and variance.

### 3. LightGBM
A gradient-boosted decision tree framework.
- **Validation Strategy**: Uses a fixed 15% time-based validation window (the most recent dates in the training set).
- **Early Stopping**: The model stops training once performance on the validation set stops improving for 50 rounds, preventing overfitting.

---

## 🛡️ Leakage Audit & Prevention

To ensure the validity of our results, `train_v2.py` performs several safety checks:

- **Correlation Check**: Validates that no single feature is too highly correlated ($|r| > 0.9$) with the target, which would suggest look-ahead bias or redundant target encoding.
- **Standardization**: Features are scaled using `StandardScaler` fitted **only** on the training data. This prevents statistics from the test set from leaking into the training process.
- **Strict Chronology**: Both training and testing data are sorted by date per region to ensure no temporal shuffling occurs.

---

## 📊 Performance Metrics

We evaluate models in two distinct dimensions:

### log_return Space (Statistical Accuracy)
- **MAE**: Mean Absolute Error of the log return. Useful for comparing model precision on the stationary target.
- **RMSE**: Root Mean Squared Error. Penalizes larger misses in return prediction.

### Price Space (Business Impact)
Predictions are inverse-transformed back to absolute currency ($):
$$\hat{P}_t = P_{t-1} \cdot e^{\hat{y}_t}$$

- **MAE ($)**: The average dollar amount the prediction is off by. This is the most interpretable metric for stakeholders.
- **R²**: Measures the proportion of variance explained. While typically very high for price levels ($>0.99$), it verifies that the model is correctly tracking the underlying trend.

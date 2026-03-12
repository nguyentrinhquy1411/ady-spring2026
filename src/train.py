"""
train.py  (v2 — Q3 journal submission)
=======================================
Machine Learning pipeline for multi-region ZHVI log-return prediction.
Extends: "Spatiotemporal patterns and prediction of multi-region house
prices via functional mixed effects model" (Chen & Zheng, IJSPM 2025).

Models:  Linear Regression | Random Forest | XGBoost | LightGBM | LSTM
Metrics: RMSE · MAE · MAPE · R²   (log_return domain + USD price domain)
"""

from __future__ import annotations

import json
import pathlib
import pickle
import time
import warnings

import lightgbm as lgb
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR     = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR  = PROJECT_ROOT / "results"
FIGURES_DIR  = PROJECT_ROOT / "figures"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_FILE   = DATA_DIR / "train.csv"
TEST_FILE    = DATA_DIR / "test.csv"
FEATURE_COLS = ["lag_1", "lag_2", "lag_3", "lag_6", "lag_12", "city_enc"]
TARGET_COL   = "log_return"


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def compute_metrics(name: str, y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """All metrics in log_return domain."""
    eps = 1e-8
    return {
        "model": name,
        "rmse":  float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae":   float(mean_absolute_error(y_true, y_pred)),
        "mape":  float(np.mean(np.abs((y_true - y_pred) / (np.abs(y_true) + eps))) * 100),
        "r2":    float(r2_score(y_true, y_pred)),
    }


def compute_price_metrics(
    name: str,
    price_prev: np.ndarray,
    y_true_lr: np.ndarray,
    y_pred_lr: np.ndarray,
) -> dict:
    """Inverse-transform log_return → price, then compute USD metrics."""
    eps = 1e-8
    pt = price_prev * np.exp(y_true_lr)
    pp = price_prev * np.exp(y_pred_lr)
    return {
        "model":      name,
        "rmse_price": float(np.sqrt(mean_squared_error(pt, pp))),
        "mae_price":  float(mean_absolute_error(pt, pp)),
        "mape_price": float(np.mean(np.abs((pt - pp) / (np.abs(pt) + eps))) * 100),
        "r2_price":   float(r2_score(pt, pp)),
        "price_true": pt,
        "price_pred": pp,
    }


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    print("[DATA] Loading train / test …")
    train = pd.read_csv(TRAIN_FILE, parse_dates=["date"])
    test  = pd.read_csv(TEST_FILE,  parse_dates=["date"])
    print(f"  Train : {len(train):,} rows   Test : {len(test):,} rows")
    print(f"  Regions train/test : {train['RegionID'].nunique()} / {test['RegionID'].nunique()}")
    return train, test


# ---------------------------------------------------------------------------
# Classical ML models
# ---------------------------------------------------------------------------
def get_classical_models() -> dict:
    return {
        "Linear Regression": Ridge(alpha=1.0),
        "Random Forest": RandomForestRegressor(
            n_estimators=200, max_depth=10, min_samples_leaf=5,
            n_jobs=-1, random_state=42,
        ),
        "XGBoost": xgb.XGBRegressor(
            n_estimators=400, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            reg_alpha=0.1, reg_lambda=1.0,
            tree_method="hist", random_state=42, verbosity=0,
        ),
        "LightGBM": lgb.LGBMRegressor(
            n_estimators=400, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            reg_alpha=0.1, reg_lambda=1.0,
            random_state=42, verbose=-1, n_jobs=-1,
        ),
    }


# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------
def train_and_evaluate(train: pd.DataFrame, test: pd.DataFrame):

    X_train = train[FEATURE_COLS].values
    y_train = train[TARGET_COL].values

    # Sort test by (region, date) for price inverse-transform
    test_s = test.sort_values(["RegionID", "date"]).copy()
    test_s["price_prev"] = (
        test_s.groupby("RegionID")["price"].shift(1).fillna(test_s["price"])
    )
    sort_idx    = test_s.index
    X_test_s   = test.loc[sort_idx, FEATURE_COLS].values
    y_test_s   = test.loc[sort_idx, TARGET_COL].values
    price_prev  = test_s["price_prev"].values

    metrics_lr    = {}
    metrics_price = {}
    predictions   = {}
    feature_imps  = {}

    print("\n" + "=" * 60)
    print("  MODEL TRAINING & EVALUATION")
    print("=" * 60)

    # ---- Classical models ------------------------------------------------
    for name, model in get_classical_models().items():
        print(f"\n[{name}]")
        t0 = time.time()
        model.fit(X_train, y_train)
        print(f"  Training time : {time.time()-t0:.2f}s")

        y_pred = model.predict(X_test_s)
        m_lr   = compute_metrics(name, y_test_s, y_pred)
        m_p    = compute_price_metrics(name, price_prev, y_test_s, y_pred)
        metrics_lr[name]    = m_lr
        metrics_price[name] = m_p

        print(f"  log_return  RMSE={m_lr['rmse']:.6f}  MAE={m_lr['mae']:.6f}  "
              f"MAPE={m_lr['mape']:.2f}%  R²={m_lr['r2']:.4f}")
        print(f"  Price USD   RMSE=${m_p['rmse_price']:,.0f}  MAE=${m_p['mae_price']:,.0f}  "
              f"MAPE={m_p['mape_price']:.4f}%  R²={m_p['r2_price']:.4f}")

        predictions[name] = {
            "y_true_lr":  y_test_s,
            "y_pred_lr":  y_pred,
            "price_true": m_p["price_true"],
            "price_pred": m_p["price_pred"],
            "dates":      test.loc[sort_idx, "date"].values,
            "regions":    test.loc[sort_idx, "RegionName"].values,
        }
        if hasattr(model, "feature_importances_"):
            feature_imps[name] = dict(zip(FEATURE_COLS, model.feature_importances_))
        elif hasattr(model, "coef_"):
            feature_imps[name] = dict(zip(FEATURE_COLS, np.abs(model.coef_)))

    # ---- LSTM ------------------------------------------------------------
    try:
        from lstm_model import train_lstm, predict_lstm
        print(f"\n[LSTM]")
        t0 = time.time()
        lstm_net = train_lstm(X_train, y_train, seq_len=12, epochs=60,
                              batch_size=4096, patience=8)
        print(f"  Training time : {time.time()-t0:.2f}s")

        y_pred_lstm = predict_lstm(lstm_net, X_train, X_test_s, y_train, seq_len=12)
        name = "LSTM"
        m_lr  = compute_metrics(name, y_test_s, y_pred_lstm)
        m_p   = compute_price_metrics(name, price_prev, y_test_s, y_pred_lstm)
        metrics_lr[name]    = m_lr
        metrics_price[name] = m_p
        print(f"  log_return  RMSE={m_lr['rmse']:.6f}  MAE={m_lr['mae']:.6f}  "
              f"MAPE={m_lr['mape']:.2f}%  R²={m_lr['r2']:.4f}")
        print(f"  Price USD   RMSE=${m_p['rmse_price']:,.0f}  MAE=${m_p['mae_price']:,.0f}  "
              f"MAPE={m_p['mape_price']:.4f}%  R²={m_p['r2_price']:.4f}")

        predictions[name] = {
            "y_true_lr":  y_test_s,
            "y_pred_lr":  y_pred_lstm,
            "price_true": m_p["price_true"],
            "price_pred": m_p["price_pred"],
            "dates":      test.loc[sort_idx, "date"].values,
            "regions":    test.loc[sort_idx, "RegionName"].values,
        }

    except Exception as ex:
        print(f"  [LSTM] WARNING: skipped — {ex}")

    return metrics_lr, metrics_price, predictions, feature_imps


# ---------------------------------------------------------------------------
# Save results
# ---------------------------------------------------------------------------
def save_results(metrics_lr, metrics_price, feature_imps):

    # Log-return metrics
    rows = []
    for name, m in metrics_lr.items():
        rows.append({"Model": name,
                     "RMSE_logret": m["rmse"], "MAE_logret": m["mae"],
                     "MAPE_logret": m["mape"], "R2_logret": m["r2"]})
    pd.DataFrame(rows).to_csv(RESULTS_DIR / "metrics_log_return.csv", index=False)

    # Price metrics
    rows = []
    for name, m in metrics_price.items():
        rows.append({"Model": name,
                     "RMSE_USD": m["rmse_price"], "MAE_USD": m["mae_price"],
                     "MAPE_%":  m["mape_price"],  "R2":      m["r2_price"]})
    df_price = pd.DataFrame(rows)
    df_price.to_csv(RESULTS_DIR / "metrics_price.csv", index=False)

    # Feature importances
    fi_rows = [{"Model": m, "Feature": f, "Importance": i}
               for m, fi in feature_imps.items()
               for f, i in fi.items()]
    pd.DataFrame(fi_rows).to_csv(RESULTS_DIR / "feature_importances.csv", index=False)

    print(f"\n[RESULTS] Saved to {RESULTS_DIR}/")
    print(df_price.to_string(index=False))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  ZHVI Housing Price Prediction — ML Pipeline v2")
    print("  Extending FMEM paper (Chen & Zheng, IJSPM 2025)")
    print("=" * 60)
    train, test = load_data()
    m_lr, m_p, preds, fi = train_and_evaluate(train, test)
    save_results(m_lr, m_p, fi)

    with open(RESULTS_DIR / "predictions.pkl", "wb") as f:
        pickle.dump(preds, f)
    print(f"\n[DONE] Predictions saved to {RESULTS_DIR}/predictions.pkl")
    return m_lr, m_p, preds, fi


if __name__ == "__main__":
    main()

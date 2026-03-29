"""
plot_city_timeseries.py
=======================
Trains Ridge (CV) and LightGBM side-by-side and visualizes their
time-series forecasting performance for three representative cities
(Highest, Middle, Lowest tier markets).

Layout: 3 rows (cities) x 2 cols (Ridge | LightGBM)

Outputs:
  - visualizations/city_timeseries_forecast.png
"""

import sys
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import lightgbm as lgb
from pathlib import Path

warnings.filterwarnings("ignore")

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Paths ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR     = PROJECT_ROOT / "data" / "processed"
VIZ_DIR      = PROJECT_ROOT / "visualizations"

# ── Colors ────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=1.05)
BLUE   = "#2C7BB6"   # Train history
GREEN  = "#1A9641"   # Test actuals
RIDGE_COLOR  = "#D7191C"   # Ridge predictions (red)
LGB_COLOR    = "#984EA3"   # LightGBM predictions (purple)


def train_ridge(X_train, y_train, X_test):
    scaler = StandardScaler()
    X_tr_sc = scaler.fit_transform(X_train)
    X_te_sc = scaler.transform(X_test)

    tscv = TimeSeriesSplit(n_splits=5)
    grid = GridSearchCV(
        Ridge(random_state=42),
        {"alpha": [0.01, 0.1, 1.0, 10.0, 100.0]},
        cv=tscv, scoring="neg_mean_absolute_error", n_jobs=-1
    )
    grid.fit(X_tr_sc, y_train)
    preds = grid.best_estimator_.predict(X_te_sc)
    return preds, grid.best_params_["alpha"], scaler


def train_lightgbm(X_train, y_train, X_test):
    # 85/15 internal train/val split for early stopping
    dates_train = sorted(X_train.index.map(lambda i: i))  # positional
    split_at = int(len(X_train) * 0.85)

    X_tr   = X_train.iloc[:split_at]
    y_tr   = y_train.iloc[:split_at]
    X_val  = X_train.iloc[split_at:]
    y_val  = y_train.iloc[split_at:]

    scaler = StandardScaler()
    X_tr_sc  = scaler.fit_transform(X_tr)
    X_val_sc = scaler.transform(X_val)
    X_te_sc  = scaler.transform(X_test)

    model = lgb.LGBMRegressor(
        n_estimators=1000, learning_rate=0.05, random_state=42,
        num_leaves=31, subsample=0.8
    )
    model.fit(
        X_tr_sc, y_tr,
        eval_set=[(X_val_sc, y_val)],
        eval_metric="l2",
        callbacks=[lgb.early_stopping(50, verbose=False)]
    )
    preds = model.predict(X_te_sc)
    return preds, model.best_iteration_


def plot_city_forecasts():
    VIZ_DIR.mkdir(parents=True, exist_ok=True)

    print("1. Loading data...")
    train_df = pd.read_csv(DATA_DIR / "train.csv", parse_dates=["date"])
    test_df  = pd.read_csv(DATA_DIR / "test.csv",  parse_dates=["date"])
    train_df = train_df.sort_values(["RegionID", "date"]).reset_index(drop=True)
    test_df  = test_df.sort_values(["RegionID", "date"]).reset_index(drop=True)

    features = ["lag_1", "lag_2", "lag_3", "lag_6", "lag_12", "city_enc"]
    target   = "log_return"

    test_df["price_prev"] = test_df["price"] / np.exp(test_df["log_return"])

    print("2. Training Ridge (TimeSeriesSplit CV)...")
    ridge_preds, best_alpha, _ = train_ridge(
        train_df[features], train_df[target], test_df[features]
    )
    test_df["ridge_price"] = test_df["price_prev"] * np.exp(ridge_preds)
    print(f"   Best alpha: {best_alpha}")

    print("3. Training LightGBM (early stopping)...")
    lgb_preds, best_iter = train_lightgbm(
        train_df[features], train_df[target], test_df[features]
    )
    test_df["lgb_price"] = test_df["price_prev"] * np.exp(lgb_preds)
    print(f"   Best iteration (early stopping): {best_iter}")

    # ── Select 3 representative cities ─────────────────────────────────
    city_avg = (train_df.groupby(["RegionID", "RegionName"])["price"]
                .mean().reset_index()
                .sort_values("price", ascending=False).reset_index(drop=True))

    targets = [
        (city_avg.iloc[0]["RegionID"],                   city_avg.iloc[0]["RegionName"],                   "Highest Tier"),
        (city_avg.iloc[len(city_avg)//2]["RegionID"],    city_avg.iloc[len(city_avg)//2]["RegionName"],    "Middle Tier"),
        (city_avg.iloc[len(city_avg)-1]["RegionID"],     city_avg.iloc[len(city_avg)-1]["RegionName"],     "Lowest Tier"),
    ]

    print("4. Plotting...")

    # ── 3 rows x 2 cols ─────────────────────────────────────────────────
    fig, axes = plt.subplots(3, 2, figsize=(18, 15), sharex=False)

    for row, (rid, rname, tier) in enumerate(targets):
        t_train = train_df[train_df["RegionID"] == rid].copy()
        t_test  = test_df[test_df["RegionID"] == rid].copy()
        t_train = t_train[t_train["date"].dt.year >= 2017]

        for col, (pred_col, model_name, pred_color) in enumerate([
            ("ridge_price", "Ridge", RIDGE_COLOR),
            ("lgb_price",   "LightGBM", LGB_COLOR),
        ]):
            ax = axes[row][col]

            local_mae = mean_absolute_error(t_test["price"], t_test[pred_col])
            local_r2  = r2_score(t_test["price"], t_test[pred_col])

            # Train history
            ax.plot(t_train["date"], t_train["price"],
                    color=BLUE, lw=2.5, alpha=0.5, label="Train History")

            # Test actual
            ax.plot(t_test["date"], t_test["price"],
                    color=GREEN, lw=2.5, alpha=0.9, label="Test Actual")

            # Model prediction
            ax.plot(t_test["date"], t_test[pred_col],
                    color=pred_color, lw=2.0, ls="--",
                    marker="o", markersize=3, label=f"{model_name} Predicted")

            # Residual fill (area between actual and predicted)
            ax.fill_between(
                t_test["date"],
                t_test["price"],
                t_test[pred_col],
                alpha=0.15, color=pred_color, label="Error Area"
            )

            # Train/test split line
            split_date = t_test["date"].min()
            ax.axvline(split_date, color="black", ls=":", alpha=0.6, lw=1.5)

            # Title and labels
            title = f"{rname} ({tier})\n— {model_name} —"
            ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
            ax.set_xlabel("Year", fontsize=10)
            ax.set_ylabel("Housing Price (USD)", fontsize=10)
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))

            # Metrics box
            ax.text(0.04, 0.95,
                    f"MAE: ${local_mae:,.0f}\nR²: {local_r2:.4f}",
                    transform=ax.transAxes, fontsize=10, va="top",
                    bbox=dict(boxstyle="round", facecolor="white", alpha=0.9))

            if row == 0 and col == 0:
                ax.legend(loc="lower right", fontsize=9, ncol=2)

    # ── Column headers ───────────────────────────────────────────────────
    for col_ax, label in zip(axes[0], ["Ridge (Linear, L2-Regularized)", "LightGBM (Non-linear, Gradient Boosting)"]):
        col_ax.set_title(f"{label}\n{col_ax.get_title()}", fontsize=12, fontweight="bold", pad=10)

    fig.suptitle(
        "Model Comparison: Ridge vs LightGBM\nActual vs Predicted Housing Prices (2017–2026)",
        fontsize=15, fontweight="bold", y=1.01
    )

    plt.tight_layout()
    out = VIZ_DIR / "city_timeseries_forecast.png"
    plt.savefig(out, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"\n   Saved: {out}")
    print(f"\n   LightGBM best_iteration: {best_iter}")
    print(f"   → Early stopping fired, longer training would only overfit the val set.")


if __name__ == "__main__":
    plot_city_forecasts()

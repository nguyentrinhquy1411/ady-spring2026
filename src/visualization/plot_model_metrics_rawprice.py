"""
plot_model_metrics_rawprice.py
==============================
Trains all 4 models (Baseline, OLS, Ridge, LightGBM) directly on
RAW PRICE (no log-return transformation) and compares their
MAE, RMSE, and R² performance.

Purpose: Serve as an explicit contrast to the log-return pipeline,
showing that high R² alone does not guarantee good predictions.

Data:
  - data/processed/train_price.csv
  - data/processed/test_price.csv

Features: lag_price_1, lag_price_2, lag_price_3,
          lag_price_6, lag_price_12, city_price_enc
Target  : price (raw USD)

Outputs:
  - visualizations/model_metrics_rawprice.csv
  - visualizations/metrics_model_comparison_rawprice.png
"""

import sys
import warnings
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import lightgbm as lgb
from pathlib import Path
import math

warnings.filterwarnings("ignore")

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Paths ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR     = PROJECT_ROOT / "data" / "processed"
VIZ_DIR      = PROJECT_ROOT / "visualizations"

FEATURES = ["lag_price_1", "lag_price_2", "lag_price_3",
            "lag_price_6", "lag_price_12", "city_price_enc"]
TARGET   = "price"


# ── Model trainers ─────────────────────────────────────────────────────────

def train_baseline(test_df):
    """Zero-growth: predict this month = last month (lag_price_1)."""
    return test_df["lag_price_1"].values


def train_ols(X_train, y_train, X_test):
    scaler   = StandardScaler()
    X_tr_sc  = scaler.fit_transform(X_train)
    X_te_sc  = scaler.transform(X_test)
    model    = LinearRegression()
    model.fit(X_tr_sc, y_train)
    return model.predict(X_te_sc)


def train_ridge(X_train, y_train, X_test):
    scaler = StandardScaler()
    X_tr_sc = scaler.fit_transform(X_train)
    X_te_sc = scaler.transform(X_test)
    tscv = TimeSeriesSplit(n_splits=5)
    grid = GridSearchCV(
        Ridge(random_state=42),
        {"alpha": [0.01, 0.1, 1.0, 10.0, 100.0]},
        cv=tscv, scoring="neg_mean_absolute_error", n_jobs=-1,
    )
    grid.fit(X_tr_sc, y_train)
    preds = grid.best_estimator_.predict(X_te_sc)
    print(f"   Ridge best alpha: {grid.best_params_['alpha']}")
    return preds


def train_lightgbm(X_train, y_train, X_test):
    split_at = int(len(X_train) * 0.85)
    X_tr,  X_val  = X_train.iloc[:split_at],  X_train.iloc[split_at:]
    y_tr,  y_val  = y_train.iloc[:split_at],  y_train.iloc[split_at:]

    scaler   = StandardScaler()
    X_tr_sc  = scaler.fit_transform(X_tr)
    X_val_sc = scaler.transform(X_val)
    X_te_sc  = scaler.transform(X_test)

    model = lgb.LGBMRegressor(
        n_estimators=1000, learning_rate=0.05, random_state=42,
        num_leaves=31, subsample=0.8,
    )
    model.fit(
        X_tr_sc, y_tr,
        eval_set=[(X_val_sc, y_val)],
        eval_metric="l2",
        callbacks=[lgb.early_stopping(50, verbose=False)],
    )
    preds = model.predict(X_te_sc)
    print(f"   LightGBM best iteration: {model.best_iteration_}")
    return preds


# ── Metrics helper ─────────────────────────────────────────────────────────

def compute_metrics(y_true, y_pred):
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = math.sqrt(np.mean((y_true - y_pred) ** 2))
    r2   = r2_score(y_true, y_pred)
    return mae, rmse, r2


# ── Main ───────────────────────────────────────────────────────────────────

def run():
    VIZ_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    print("1. Loading raw-price data...")
    train_df = pd.read_csv(DATA_DIR / "train_price.csv", parse_dates=["date"])
    test_df  = pd.read_csv(DATA_DIR / "test_price.csv",  parse_dates=["date"])
    train_df = train_df.sort_values(["RegionID", "date"]).reset_index(drop=True)
    test_df  = test_df.sort_values(["RegionID", "date"]).reset_index(drop=True)

    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]
    X_test  = test_df[FEATURES]
    y_test  = test_df[TARGET]

    results = []

    # 2. Baseline
    print("\n2. Baseline (Zero-Growth = lag_price_1)...")
    base_preds = train_baseline(test_df)
    mae, rmse, r2 = compute_metrics(y_test, base_preds)
    results.append({"Model": "Baseline\n(Zero-Growth)", "MAE": mae, "RMSE": rmse, "R2": r2})
    print(f"   MAE={mae:,.0f}  RMSE={rmse:,.0f}  R²={r2:.6f}")

    # 3. OLS
    print("\n3. OLS (Linear Regression)...")
    ols_preds = train_ols(X_train, y_train, X_test)
    mae, rmse, r2 = compute_metrics(y_test, ols_preds)
    results.append({"Model": "OLS", "MAE": mae, "RMSE": rmse, "R2": r2})
    print(f"   MAE={mae:,.0f}  RMSE={rmse:,.0f}  R²={r2:.6f}")

    # 4. Ridge
    print("\n4. Ridge (L2, TimeSeriesSplit CV)...")
    ridge_preds = train_ridge(X_train, y_train, X_test)
    mae, rmse, r2 = compute_metrics(y_test, ridge_preds)
    results.append({"Model": "Ridge\n(L2 Reg.)", "MAE": mae, "RMSE": rmse, "R2": r2})
    print(f"   MAE={mae:,.0f}  RMSE={rmse:,.0f}  R²={r2:.6f}")

    # 5. LightGBM
    print("\n5. LightGBM (early stopping)...")
    lgb_preds = train_lightgbm(X_train, y_train, X_test)
    mae, rmse, r2 = compute_metrics(y_test, lgb_preds)
    results.append({"Model": "LightGBM\n(GBDT)", "MAE": mae, "RMSE": rmse, "R2": r2})
    print(f"   MAE={mae:,.0f}  RMSE={rmse:,.0f}  R²={r2:.6f}")

    # 6. Save CSV
    df_results = pd.DataFrame(results)
    csv_out = VIZ_DIR / "model_metrics_rawprice.csv"
    df_results.to_csv(csv_out, index=False)
    print(f"\n6. Metrics saved to: {csv_out}")

    # 7. Plot
    print("7. Plotting...")
    _plot(df_results)


def _plot(df):
    model_labels = df["Model"].tolist()

    COLORS = {
        "bar_mae":  "#2C7BB6",
        "bar_rmse": "#D7191C",
        "line_r2":  "#1A9641",
    }

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # MAE bars
    fig.add_trace(
        go.Bar(
            x=model_labels,
            y=df["MAE"],
            name="MAE ($)",
            marker_color=COLORS["bar_mae"],
            text=df["MAE"].apply(lambda v: f"${v:,.0f}"),
            textposition="auto",
            hovertemplate="Model: %{x}<br>MAE: $%{y:,.2f}<extra></extra>",
        ),
        secondary_y=False,
    )

    # RMSE bars
    fig.add_trace(
        go.Bar(
            x=model_labels,
            y=df["RMSE"],
            name="RMSE ($)",
            marker_color=COLORS["bar_rmse"],
            text=df["RMSE"].apply(lambda v: f"${v:,.0f}"),
            textposition="auto",
            hovertemplate="Model: %{x}<br>RMSE: $%{y:,.2f}<extra></extra>",
        ),
        secondary_y=False,
    )

    # R² line
    fig.add_trace(
        go.Scatter(
            x=model_labels,
            y=df["R2"],
            name="R² Score",
            mode="lines+markers+text",
            marker=dict(size=12, color=COLORS["line_r2"]),
            line=dict(width=3, color=COLORS["line_r2"]),
            text=df["R2"].apply(lambda v: f"{v:.4f}"),
            textposition="top center",
            hovertemplate="Model: %{x}<br>R²: %{y:.6f}<extra></extra>",
        ),
        secondary_y=True,
    )

    # Annotation: "R² is misleading here"
    fig.add_annotation(
        x=0.5, y=-0.18,
        xref="paper", yref="paper",
        text=(
            "⚠️ <b>Raw Price pipeline</b> — R² xấp xỉ 1.0 với mọi mô hình, kể cả Baseline.<br>"
            "Điều này là hệ quả của tính không dừng (non-stationarity) trong dữ liệu giá thô,<br>"
            "<b>không</b> phản ánh khả năng dự báo thực sự. So sánh MAE/RMSE mới có ý nghĩa."
        ),
        showarrow=False,
        font=dict(size=12, color="#555555"),
        align="center",
        bgcolor="#FFF9C4",
        bordercolor="#CCCC00",
        borderwidth=1,
        borderpad=8,
    )

    fig.update_layout(
        title={
            "text": (
                "<b>Performance Metrics by Model — Raw Price Pipeline</b><br>"
                "<sup>Baseline vs OLS vs Ridge vs LightGBM (no log-return transformation)</sup>"
            ),
            "y": 0.95, "x": 0.5,
            "xanchor": "center", "yanchor": "top",
        },
        barmode="group",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
        ),
        plot_bgcolor="white",
        hovermode="x unified",
        font=dict(size=13),
        margin=dict(t=120, b=160),
    )

    fig.update_yaxes(
        title_text="<b>Error Value (USD)</b> (Lower is Better)",
        showgrid=True, gridwidth=1, gridcolor="LightGray",
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text="<b>R² Score</b> (Higher is Better)",
        range=[min(df["R2"]) - 0.05, 1.05],
        showgrid=False,
        secondary_y=True,
    )
    fig.update_xaxes(
        title_text="<b>Regression Model</b>",
        showline=True, linewidth=1, linecolor="black",
    )

    out = VIZ_DIR / "metrics_model_comparison_rawprice.png"
    fig.write_image(str(out), scale=2, width=1200, height=750)
    print(f"   Saved: {out}")


if __name__ == "__main__":
    run()

"""
visualize.py  (v2 — Q3 journal submission)
==========================================
Research-quality figures for the ZHVI housing price prediction study.

Figures generated:
  1. price_trend.png         — National median ZHVI trajectory
  2. log_return_dist.png     — Distribution of monthly log returns
  3. model_comparison.png    — RMSE / MAE / MAPE / R² bar charts (5 models)
  4. feature_importance.png  — Normalised importance (RF, XGBoost, LightGBM)
  5. predicted_vs_actual.png — Best model: price predictions vs actual (6 cities)
"""

from __future__ import annotations

import pathlib
import pickle
import warnings

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

matplotlib.use("Agg")
warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR     = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR  = PROJECT_ROOT / "results"
FIGURES_DIR  = PROJECT_ROOT / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family":       "DejaVu Serif",
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.labelsize":    12,
    "legend.fontsize":   10,
    "xtick.labelsize":   10,
    "ytick.labelsize":   10,
    "figure.dpi":        150,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.alpha":        0.3,
    "lines.linewidth":   1.8,
})

MODEL_COLORS = {
    "Linear Regression": "#4C72B0",
    "Random Forest":     "#DD8452",
    "XGBoost":           "#55A868",
    "LightGBM":          "#C44E52",
    "LSTM":              "#8172B2",
}

SAMPLE_CITIES = [
    "San Jose, CA", "New York, NY", "Austin, TX",
    "Phoenix, AZ",  "Seattle, WA",  "Chicago, IL",
]


# ---------------------------------------------------------------------------
# 1. National Price Trend
# ---------------------------------------------------------------------------
def plot_price_trend() -> None:
    train = pd.read_csv(DATA_DIR / "train.csv", usecols=["date", "price"],
                        parse_dates=["date"])
    test  = pd.read_csv(DATA_DIR / "test.csv",  usecols=["date", "price"],
                        parse_dates=["date"])
    tr = train.groupby("date")["price"].median().reset_index()
    te = test.groupby("date")["price"].median().reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(tr["date"], tr["price"] / 1_000, color="#4C72B0",
            label="Train (2001–2020)", lw=2)
    ax.plot(te["date"], te["price"] / 1_000, color="#C44E52",
            label="Test  (2020–2026)", lw=2, ls="--")
    ax.axvline(pd.Timestamp("2020-11-01"), color="gray", lw=1.5,
               ls=":", alpha=0.8, label="Train/Test Cutoff")
    ax.set_xlabel("Date")
    ax.set_ylabel("Median ZHVI (USD thousands)")
    ax.set_title("National Median House Price Trend — Zillow ZHVI\n"
                 "All Metro Areas Combined",
                 fontweight="bold")
    ax.legend()
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}K"))
    fig.savefig(FIGURES_DIR / "price_trend.png", bbox_inches="tight")
    plt.close(fig)
    print("[FIG] price_trend.png")


# ---------------------------------------------------------------------------
# 2. Log-Return Distribution
# ---------------------------------------------------------------------------
def plot_log_return_distribution() -> None:
    tr = pd.read_csv(DATA_DIR / "train.csv", usecols=["log_return"])
    te = pd.read_csv(DATA_DIR / "test.csv",  usecols=["log_return"])
    bins = np.linspace(-0.08, 0.12, 80)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(tr["log_return"], bins=bins, alpha=0.65, label="Train (2001–2020)",
            color="#4C72B0", density=True, edgecolor="white")
    ax.hist(te["log_return"], bins=bins, alpha=0.65, label="Test  (2020–2026)",
            color="#C44E52", density=True, edgecolor="white")
    ax.axvline(0, color="black", lw=1.2, ls="--", alpha=0.5)
    ax.set_xlabel("Monthly Log Return")
    ax.set_ylabel("Density")
    ax.set_title("Distribution of Monthly Log Returns — ZHVI\n"
                 "All Metro Areas, Train vs Test Period",
                 fontweight="bold")
    ax.legend()
    ax.text(0.98, 0.95,
            f"Train μ={tr.log_return.mean():.4f},  σ={tr.log_return.std():.4f}\n"
            f"Test  μ={te.log_return.mean():.4f},  σ={te.log_return.std():.4f}",
            transform=ax.transAxes, ha="right", va="top", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7))
    fig.savefig(FIGURES_DIR / "log_return_dist.png", bbox_inches="tight")
    plt.close(fig)
    print("[FIG] log_return_dist.png")


# ---------------------------------------------------------------------------
# 3. Model Comparison (4 subplots: RMSE / MAE / MAPE / R²)
# ---------------------------------------------------------------------------
def plot_model_comparison(metrics_price: dict) -> None:
    # Ensure consistent order
    model_order = ["Linear Regression", "Random Forest",
                   "XGBoost", "LightGBM", "LSTM"]
    models = [m for m in model_order if m in metrics_price]

    rmse  = [metrics_price[m]["rmse_price"]  / 1_000 for m in models]
    mae   = [metrics_price[m]["mae_price"]   / 1_000 for m in models]
    mape  = [metrics_price[m]["mape_price"]           for m in models]
    r2    = [metrics_price[m]["r2_price"]             for m in models]

    fig, axes = plt.subplots(1, 4, figsize=(18, 5), constrained_layout=True)
    fig.suptitle(
        "Model Performance Comparison — Housing Price Prediction\n"
        "Evaluation on Held-Out Test Set (Nov 2020 – Jan 2026)",
        fontsize=14, fontweight="bold",
    )

    for ax, vals, ylabel, title, higher_better in [
        (axes[0], rmse,  "RMSE (USD thousands)", "RMSE ↓",  False),
        (axes[1], mae,   "MAE  (USD thousands)", "MAE  ↓",  False),
        (axes[2], mape,  "MAPE (%)",              "MAPE ↓",  False),
        (axes[3], r2,    "R²",                   "R²   ↑",  True),
    ]:
        colors = [MODEL_COLORS.get(m, "#888") for m in models]
        bars   = ax.bar(range(len(models)), vals, color=colors,
                        edgecolor="white", linewidth=1.2, width=0.6)
        ax.set_xticks(range(len(models)))
        ax.set_xticklabels([m.replace(" ", "\n") for m in models], fontsize=9)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontweight="bold")
        # highlight best bar
        best_idx = int(np.argmax(vals) if higher_better else np.argmin(vals))
        bars[best_idx].set_edgecolor("gold")
        bars[best_idx].set_linewidth(2.5)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() * 1.02 if val >= 0 else bar.get_height() * 0.98,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=8.5,
                    fontweight="bold")

    fig.savefig(FIGURES_DIR / "model_comparison.png", bbox_inches="tight")
    plt.close(fig)
    print("[FIG] model_comparison.png")


# ---------------------------------------------------------------------------
# 4. Feature Importance
# ---------------------------------------------------------------------------
def plot_feature_importance(feature_importances: dict) -> None:
    fi_models = {k: v for k, v in feature_importances.items()
                 if k in ("Random Forest", "XGBoost", "LightGBM")}
    if not fi_models:
        return

    FEATURE_LABELS = {
        "lag_1":    "Lag-1\n(1 month)",   "lag_2":  "Lag-2\n(2 months)",
        "lag_3":    "Lag-3\n(3 months)",  "lag_6":  "Lag-6\n(6 months)",
        "lag_12":   "Lag-12\n(12 months)","city_enc":"City\nEncoding",
    }
    n = len(fi_models)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5), constrained_layout=True)
    if n == 1:
        axes = [axes]
    fig.suptitle("Feature Importance — Ensemble & Boosting Models\n"
                 "Input: Lag features of log-return + City encoding",
                 fontsize=14, fontweight="bold")

    for ax, (mname, fi) in zip(axes, fi_models.items()):
        feats  = list(fi.keys())
        imps   = np.array([fi[f] for f in feats])
        norm   = imps / (imps.sum() + 1e-10)
        labels = [FEATURE_LABELS.get(f, f) for f in feats]
        si     = np.argsort(norm)
        ax.barh([labels[i] for i in si], norm[si],
                color=MODEL_COLORS.get(mname, "#888"),
                edgecolor="white", linewidth=1.0)
        ax.set_title(mname, fontweight="bold")
        ax.set_xlabel("Relative Importance")
        for i, (v, lbl) in enumerate(zip(norm[si], [labels[j] for j in si])):
            ax.text(v + 0.003, i, f"{v:.3f}", va="center", fontsize=9)

    fig.savefig(FIGURES_DIR / "feature_importance.png", bbox_inches="tight")
    plt.close(fig)
    print("[FIG] feature_importance.png")


# ---------------------------------------------------------------------------
# 5. Predicted vs Actual (best classical model)
# ---------------------------------------------------------------------------
def plot_predicted_vs_actual(predictions: dict,
                              best_model: str = "Linear Regression") -> None:
    pred    = predictions[best_model]
    dates   = pd.to_datetime(pred["dates"])
    regions = pred["regions"]
    pt      = pred["price_true"]
    pp      = pred["price_pred"]

    cities = [c for c in SAMPLE_CITIES if c in set(regions)]
    if len(cities) < 3:
        cities = list(pd.Series(regions).value_counts().index[:6])

    fig, axes = plt.subplots(3, 2, figsize=(13, 11), constrained_layout=True)
    fig.suptitle(
        f"Predicted vs. Actual House Prices — {best_model}\n"
        "Zillow Home Value Index (ZHVI), Selected Metro Areas",
        fontsize=14, fontweight="bold",
    )
    for ax, city in zip(axes.flat, cities[:6]):
        mask = regions == city
        if not mask.any():
            ax.set_visible(False)
            continue
        d, a, p = dates[mask], pt[mask], pp[mask]
        si = np.argsort(d)
        ax.plot(d[si], a[si] / 1_000, color="black", lw=2.2, label="Actual")
        ax.plot(d[si], p[si] / 1_000, color=MODEL_COLORS[best_model],
                ls="--", lw=1.8, label="Predicted")
        ax.set_title(city, fontsize=11, fontweight="bold")
        ax.set_ylabel("Price (USD thousands)")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.legend(loc="upper left", framealpha=0.7)

    fig.savefig(FIGURES_DIR / "predicted_vs_actual.png", bbox_inches="tight")
    plt.close(fig)
    print("[FIG] predicted_vs_actual.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(predictions=None, metrics_price=None, feature_importances=None):
    print("=" * 60)
    print("  GENERATING RESEARCH FIGURES  (v2)")
    print("=" * 60)

    if predictions is None:
        pkl = RESULTS_DIR / "predictions.pkl"
        if pkl.exists():
            with open(pkl, "rb") as f:
                predictions = pickle.load(f)

    if metrics_price is None:
        mp_csv = RESULTS_DIR / "metrics_price.csv"
        if mp_csv.exists():
            df = pd.read_csv(mp_csv)
            metrics_price = {}
            for _, row in df.iterrows():
                metrics_price[row["Model"]] = {
                    "rmse_price": row["RMSE_USD"],
                    "mae_price":  row["MAE_USD"],
                    "mape_price": row["MAPE_%"],
                    "r2_price":   row.get("R2", 0.0),
                }

    if feature_importances is None:
        fi_csv = RESULTS_DIR / "feature_importances.csv"
        if fi_csv.exists():
            df = pd.read_csv(fi_csv)
            feature_importances = {}
            for model, grp in df.groupby("Model"):
                feature_importances[model] = dict(
                    zip(grp["Feature"], grp["Importance"]))

    plot_price_trend()
    plot_log_return_distribution()
    if metrics_price:
        plot_model_comparison(metrics_price)
    if feature_importances:
        plot_feature_importance(feature_importances)
    if predictions:
        plot_predicted_vs_actual(predictions)

    print(f"\n[FIG] All figures saved to: {FIGURES_DIR}/")


if __name__ == "__main__":
    main()

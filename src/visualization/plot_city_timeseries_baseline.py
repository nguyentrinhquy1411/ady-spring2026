"""
plot_city_timeseries_baseline.py
=================================
Visualizes the Baseline (Zero-Growth) forecast, where the prediction
for this month is simply the price from the previous month.
This demonstrates visually why the Baseline still achieves R² > 0.99 
(it acts like a 1-step moving average), though it simply lags the true market.

Layout: 3 rows (cities) x 1 cols (Baseline)

Outputs:
  - visualizations/city_timeseries_baseline_forecast.png
"""

import sys
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sklearn.metrics import mean_absolute_error, r2_score
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
BLUE          = "#2C7BB6"   # Train history
GREEN         = "#1A9641"   # Test actuals
BASELINE_COL  = "#FD8D3C"   # Baseline prediction (orange)

def plot_baseline_forecasts():
    VIZ_DIR.mkdir(parents=True, exist_ok=True)

    print("1. Loading raw-price data...")
    train_df = pd.read_csv(DATA_DIR / "train.csv", parse_dates=["date"])
    test_df  = pd.read_csv(DATA_DIR / "test.csv",  parse_dates=["date"])
    train_df = train_df.sort_values(["RegionID", "date"]).reset_index(drop=True)
    test_df  = test_df.sort_values(["RegionID", "date"]).reset_index(drop=True)

    # ── Calculate Baseline (Zero-growth prediction = previous month's price) ──
    # Since test.csv contains 'price' and 'log_return', 
    # prev price = price / exp(log_return).
    test_df["baseline_price"] = test_df["price"] / np.exp(test_df["log_return"])

    # ── Select 3 representative cities ─────────────────────────────────
    city_avg = (train_df.groupby(["RegionID", "RegionName"])["price"]
                .mean().reset_index()
                .sort_values("price", ascending=False).reset_index(drop=True))

    targets = [
        (city_avg.iloc[0]["RegionID"],                   city_avg.iloc[0]["RegionName"],                   "Highest Tier"),
        (city_avg.iloc[len(city_avg)//2]["RegionID"],    city_avg.iloc[len(city_avg)//2]["RegionName"],    "Middle Tier"),
        (city_avg.iloc[len(city_avg)-1]["RegionID"],     city_avg.iloc[len(city_avg)-1]["RegionName"],     "Lowest Tier"),
    ]

    print("2. Plotting...")

    fig, axes = plt.subplots(3, 1, figsize=(10, 15), sharex=False)

    for row, (rid, rname, tier) in enumerate(targets):
        t_train = train_df[train_df["RegionID"] == rid].copy()
        t_test  = test_df[test_df["RegionID"] == rid].copy()
        t_train = t_train[t_train["date"].dt.year >= 2017]

        ax = axes[row]
        
        # Calculate local metrics
        local_mae = mean_absolute_error(t_test["price"], t_test["baseline_price"])
        local_r2  = r2_score(t_test["price"], t_test["baseline_price"])

        # Train history
        ax.plot(t_train["date"], t_train["price"],
                color=BLUE, lw=2.5, alpha=0.5, label="Train History")

        # Test actual
        ax.plot(t_test["date"], t_test["price"],
                color=GREEN, lw=2.5, alpha=0.9, label="Test Actual")

        # Baseline prediction
        ax.plot(t_test["date"], t_test["baseline_price"],
                color=BASELINE_COL, lw=2.0, ls="--",
                marker="o", markersize=4, label="Baseline (Zero-Growth)")

        # Residual fill
        ax.fill_between(
            t_test["date"],
            t_test["price"],
            t_test["baseline_price"],
            alpha=0.15, color=BASELINE_COL, label="Error Area"
        )

        # Train/test split line
        split_date = t_test["date"].min()
        ax.axvline(split_date, color="black", ls=":", alpha=0.6, lw=1.5)

        # Title and labels
        title = f"{rname} ({tier})\n— Baseline Model (Previous Month's Price) —"
        ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
        ax.set_xlabel("Year", fontsize=10)
        ax.set_ylabel("Housing Price (USD)", fontsize=10)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
        
        # Zoom out x-axis slightly
        ax.margins(x=0.02)

        # Metrics box
        ax.text(0.04, 0.95,
                f"MAE: ${local_mae:,.0f}\nR²: {local_r2:.4f}",
                transform=ax.transAxes, fontsize=11, va="top",
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.9))

        if row == 0:
            ax.legend(loc="lower right", fontsize=10, ncol=1)

    # ── Note ─────────────────────────────────────────────────────────────
    note = (
        "Baseline (Zero-growth): \n"
        "Mô hình giả định giá tháng này = giá tháng trước (dự báo = giá trị quá khứ gần nhất).\n"
        "Giải thích tại sao R² vẫn xấp xỉ 0.999 dù không sử dụng Machine Learning."
    )
    fig.text(
        0.5, -0.01, note,
        ha="center", va="top", fontsize=11,
        color="#555555", style="italic",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#FFF9C4", alpha=0.85),
    )

    fig.suptitle(
        "Baseline (Zero-Growth) Forecast\nActual vs Predicted Housing Prices (2017–2026)",
        fontsize=15, fontweight="bold", y=1.02
    )

    plt.tight_layout()
    out = VIZ_DIR / "city_timeseries_baseline_forecast.png"
    plt.savefig(out, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"\n   Saved: {out}")

if __name__ == "__main__":
    plot_baseline_forecasts()

"""
preprocess.py
=============
Time-series preprocessing pipeline for the Zillow Metro ZHVI dataset.
Processes ALL metro regions simultaneously.

Target : log_return = log(price[t] / price[t-1])  — stationary, scale-free

Feature engineering decisions
------------------------------
• Lag features of log_return only: lag_1, lag_2, lag_3, lag_6, lag_12
  rolling_mean_* REMOVED — they are exact linear combinations of lag_1/2/3
  (VIF = ∞, perfect collinearity with adjacent lags).
• City target-encoding: mean log_return per RegionID, fitted on train only.
  Captures between-city baseline momentum without leakage.

Steps
-----
1.  Load raw CSV (MSA rows only).
2.  Melt ALL regions: wide → long [RegionID, RegionName, StateName, date, price].
3.  Interpolate missing values per region (time-aware).
4.  Compute log_return per region.
5.  Time-based 80/20 train/test split (shared cutoff).
6.  Engineer lag features of log_return (lag_1, lag_2, lag_3, lag_6, lag_12).
7.  City target-encoding: city_enc = mean(log_return) per RegionID from train.
8.  StandardScaler on lag features (fit on train only).
9.  Save train.csv / test.csv to data/processed/.
10. Report final shapes.
"""

from __future__ import annotations

import pathlib
import warnings

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT  = pathlib.Path(__file__).resolve().parent.parent
RAW_FILE      = PROJECT_ROOT / "data" / "raw" / "Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
META_COLS       = ["RegionID", "SizeRank", "RegionName", "RegionType", "StateName"]
TRAIN_RATIO  = 0.80
LAG_PERIODS  = [1, 2, 3, 6, 12]

# rolling_mean_* dropped — exact linear combo of lag_1/2/3 → VIF = ∞
LAG_COLS     = [f"lag_{l}" for l in LAG_PERIODS]
CITY_ENC_COL = "city_enc"                        # target-encoded city feature
FEATURE_COLS = LAG_COLS + [CITY_ENC_COL]          # all model inputs
TARGET_COL   = "log_return"


# ---------------------------------------------------------------------------
# Step 1 – Load raw data
# ---------------------------------------------------------------------------
def load_raw(path: pathlib.Path = RAW_FILE) -> pd.DataFrame:
    """Load the raw wide-format Zillow ZHVI CSV, keeping MSA rows only."""
    print(f"[1] Loading raw data from: {path}")
    df = pd.read_csv(path, low_memory=False)
    print(f"    Raw shape : {df.shape}")

    before = len(df)
    df = df[df["RegionType"] == "msa"].reset_index(drop=True)
    dropped = before - len(df)
    if dropped:
        print(f"    Dropped {dropped} non-MSA row(s) ('United States' country aggregate)")

    print(f"    MSA regions: {df['RegionName'].nunique()}")
    return df


# ---------------------------------------------------------------------------
# Step 2 – Melt ALL regions → long format
# ---------------------------------------------------------------------------
def melt_all_regions(df: pd.DataFrame) -> pd.DataFrame:
    """Convert wide-format to long format [RegionID, RegionName, StateName, date, price]."""
    print("\n[2] Melting all regions: wide → long format …")

    keep_meta = ["RegionID", "RegionName", "StateName"]
    date_cols = [c for c in df.columns if c not in META_COLS]

    long = df[keep_meta + date_cols].melt(
        id_vars=keep_meta,
        value_vars=date_cols,
        var_name="date",
        value_name="price",
    )
    long["date"]  = pd.to_datetime(long["date"])
    long["price"] = pd.to_numeric(long["price"], errors="coerce")
    long = long.sort_values(["RegionID", "date"]).reset_index(drop=True)

    print(f"    Long shape : {long.shape}")
    print(f"    Regions    : {long['RegionName'].nunique()}")
    print(f"    Date range : {long['date'].min().date()} → {long['date'].max().date()}")
    print(f"    Missing    : {long['price'].isna().sum():,} ({long['price'].isna().mean():.1%})")
    return long


# ---------------------------------------------------------------------------
# Step 3 – Handle missing values per region
# ---------------------------------------------------------------------------
def _interpolate_group(grp: pd.DataFrame) -> pd.DataFrame:
    grp = grp.copy().set_index("date")
    grp["price"] = (
        grp["price"]
        .interpolate(method="time", limit_direction="both")
        .ffill()
        .bfill()
    )
    return grp.reset_index()


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Apply group-wise time interpolation across all regions."""
    print("\n[3] Interpolating missing values per region …")
    before = df["price"].isna().sum()

    df = (
        df.groupby("RegionID", group_keys=False)
        .apply(_interpolate_group)
        .reset_index(drop=True)
    )

    print(f"    Missing before : {before:,}")
    print(f"    Missing after  : {df['price'].isna().sum():,}")
    return df


# ---------------------------------------------------------------------------
# Step 4 – Compute log return per region  ← NEW TARGET
# ---------------------------------------------------------------------------
def compute_log_return(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute log_return[t] = log(price[t] / price[t-1]) per region.

    Properties of log return:
      • Stationary — removes the upward price trend
      • Additive — log returns sum over time (unlike percentage returns)
      • Near-zero centred (~0.003–0.005/month for housing)
      • Breaks the r≈0.999 autocorrelation between price levels

    The original `price` column is retained for inverse-transform reference:
        price[t] = price[t-1] * exp(log_return[t])
    """
    print("\n[4] Computing log return (target) per region …")

    df = df.copy()
    df[TARGET_COL] = (
        df.groupby("RegionID")["price"]
        .transform(lambda s: np.log(s / s.shift(1)))
    )

    # First row per region is NaN (no previous price) — drop it
    before = len(df)
    df = df.dropna(subset=[TARGET_COL]).reset_index(drop=True)
    print(f"    Dropped {before - len(df):,} rows (first obs per region, no prior price)")
    print(f"    log_return stats:  mean={df[TARGET_COL].mean():.5f}  "
          f"std={df[TARGET_COL].std():.5f}  "
          f"min={df[TARGET_COL].min():.4f}  "
          f"max={df[TARGET_COL].max():.4f}")
    return df


# ---------------------------------------------------------------------------
# Step 5 – Time-based train/test split
# ---------------------------------------------------------------------------
def time_split(df: pd.DataFrame, train_ratio: float = TRAIN_RATIO) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Shared cutoff date for all regions (no per-region row-count split).
    """
    print(f"\n[5] Time-based split  (train={train_ratio:.0%} / test={1-train_ratio:.0%})")

    all_dates   = df["date"].sort_values().unique()
    cutoff_date = all_dates[int(len(all_dates) * train_ratio)]

    train = df[df["date"] <  cutoff_date].copy().reset_index(drop=True)
    test  = df[df["date"] >= cutoff_date].copy().reset_index(drop=True)

    print(f"    Cutoff date : {pd.Timestamp(cutoff_date).date()}")
    print(f"    Train       : {len(train):,} rows  ({train['date'].min().date()} → {train['date'].max().date()})")
    print(f"    Test        : {len(test):,} rows   ({test['date'].min().date()} → {test['date'].max().date()})")
    return train, test


# ---------------------------------------------------------------------------
# Steps 6 & 7 – Feature engineering (lag + rolling mean of log_return)
# ---------------------------------------------------------------------------
def _add_lag_group(grp: pd.DataFrame) -> pd.DataFrame:
    """Add lag features of log_return for a single region. No rolling means."""
    grp = grp.copy().sort_values("date")
    for lag in LAG_PERIODS:
        grp[f"lag_{lag}"] = grp[TARGET_COL].shift(lag)
    return grp


def engineer_features(
    train: pd.DataFrame,
    test:  pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compute lag features across the train+test boundary so lag windows
    flow correctly into the test period, then re-split.
    City target-encoding (step 7) is applied separately after the split
    to prevent leakage.
    """
    print("\n[6] Engineering lag features of log_return per region …")
    print("    (rolling_mean_* dropped — VIF=∞, exact linear combo of lag_1/2/3)")

    marker   = len(train)
    combined = pd.concat([train, test], ignore_index=True)

    combined = (
        combined.groupby("RegionID", group_keys=False)
        .apply(_add_lag_group)
        .reset_index(drop=True)
    )

    train_feat = combined.iloc[:marker].copy().reset_index(drop=True)
    test_feat  = combined.iloc[marker:].copy().reset_index(drop=True)

    # Drop warm-up rows (NaN from lag_12) from train only
    n_before   = len(train_feat)
    train_feat = train_feat.dropna(subset=LAG_COLS).reset_index(drop=True)
    dropped    = n_before - len(train_feat)
    print(f"    Dropped {dropped:,} warm-up rows (lag-12 × {train_feat['RegionID'].nunique()} regions)")

    # Fill any edge NaN in test at the region boundary
    n_nan = test_feat[LAG_COLS].isna().sum().sum()
    if n_nan:
        test_feat[LAG_COLS] = (
            test_feat.groupby("RegionID")[LAG_COLS]
            .transform(lambda s: s.ffill().bfill())
        )
        print(f"    Filled {n_nan} NaN(s) in test lag features")

    print(f"    Lag features : {LAG_COLS}")
    return train_feat, test_feat


# ---------------------------------------------------------------------------
# Step 7 – City target-encoding  (fit on train only → no leakage)
# ---------------------------------------------------------------------------
def add_city_encoding(
    train: pd.DataFrame,
    test:  pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Encode each city as its mean log_return computed from the training set.

    Why:
      • Collapses the high-cardinality RegionID into one numeric signal.
      • Captures between-city momentum baseline (fast-appreciating vs stagnant markets).
      • Fitted on train only — no target leakage into test.
      • Unknown cities in test fall back to the global train mean.
    """
    print("\n[7] City target-encoding (mean log_return per city, fit on train) …")

    city_mean = train.groupby("RegionID")[TARGET_COL].mean()
    global_mean = train[TARGET_COL].mean()

    train = train.copy()
    test  = test.copy()

    train[CITY_ENC_COL] = train["RegionID"].map(city_mean)
    test[CITY_ENC_COL]  = test["RegionID"].map(city_mean).fillna(global_mean)

    enc_range = f"{city_mean.min():.5f} → {city_mean.max():.5f}"
    print(f"    city_enc range : {enc_range}  (global mean = {global_mean:.5f})")
    return train, test


# ---------------------------------------------------------------------------
# Step 8 – StandardScaler on features (target NOT scaled)
# ---------------------------------------------------------------------------
def scale_features(
    train: pd.DataFrame,
    test:  pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """
    StandardScaler on FEATURE_COLS = [lag_1..lag_12, city_enc] (train only).
    log_return target is NOT scaled — already near-zero centred.
    """
    print("\n[8] Scaling features with StandardScaler (fit on train only) …")

    scaler = StandardScaler()
    train  = train.copy()
    test   = test.copy()

    train[FEATURE_COLS] = scaler.fit_transform(train[FEATURE_COLS])
    test[FEATURE_COLS]  = scaler.transform(test[FEATURE_COLS])

    print(f"    Scaler fitted on {len(train):,} train rows  ({len(FEATURE_COLS)} features)")
    print(f"    Features : {FEATURE_COLS}")
    return train, test, scaler


# ---------------------------------------------------------------------------
# Step 9 – Save processed data
# ---------------------------------------------------------------------------
def save_processed(
    train: pd.DataFrame,
    test:  pd.DataFrame,
    out_dir: pathlib.Path = PROCESSED_DIR,
) -> None:
    """Write train.csv and test.csv to data/processed/."""
    out_dir.mkdir(parents=True, exist_ok=True)

    train_path = out_dir / "train.csv"
    test_path  = out_dir / "test.csv"

    train.to_csv(train_path, index=False)
    test.to_csv(test_path,  index=False)

    print(f"\n[9] Saved processed files:")
    print(f"    → {train_path}  ({train_path.stat().st_size / 1e6:.1f} MB)")
    print(f"    → {test_path}   ({test_path.stat().st_size / 1e6:.1f} MB)")
    print(f"\n    Columns : {train.columns.tolist()}")


# ---------------------------------------------------------------------------
# Step 10 – Report final shapes
# ---------------------------------------------------------------------------
def report_shapes(
    X_train: pd.DataFrame,
    X_test:  pd.DataFrame,
    y_train: pd.Series,
    y_test:  pd.Series,
) -> None:
    print("\n[10] Final dataset shapes:")
    print(f"     X_train : {X_train.shape}")
    print(f"     X_test  : {X_test.shape}")
    print(f"     y_train : {y_train.shape}  (log_return, unscaled)")
    print(f"     y_test  : {y_test.shape}   (log_return, unscaled)")
    print(f"\n     Feature columns : {X_train.columns.tolist()}")
    print(f"     Target          : '{TARGET_COL}'")
    print(f"\n     y_train stats: mean={y_train.mean():.5f}  std={y_train.std():.5f}")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def run_pipeline() -> dict:
    """
    Full preprocessing pipeline — all metro regions, log return target.

    Returns
    -------
    {
        X_train, X_test  : pd.DataFrame  — scaled lag/rolling features
        y_train, y_test  : pd.Series     — log_return target (unscaled)
        scaler           : StandardScaler — fitted on train features
        feature_cols     : list[str]
        target_col       : str           — 'log_return'
        train_df         : pd.DataFrame  — full train frame
        test_df          : pd.DataFrame  — full test  frame
    }

    Inverse transform to recover price:
        price[t] = price[t-1] * exp(predicted_log_return[t])
    """
    print("=" * 60)
    print("  Preprocessing pipeline — ALL metro regions")
    print(f"  Target: log_return  (stationary, log-price difference)")
    print("=" * 60)

    raw                  = load_raw()
    long_df              = melt_all_regions(raw)
    long_df              = handle_missing(long_df)
    long_df              = compute_log_return(long_df)
    train, test          = time_split(long_df)
    train, test          = engineer_features(train, test)
    train, test          = add_city_encoding(train, test)  # ← after split, no leakage
    train, test, scaler  = scale_features(train, test)

    X_train = train[FEATURE_COLS]
    y_train = train[TARGET_COL]
    X_test  = test[FEATURE_COLS]
    y_test  = test[TARGET_COL]

    save_processed(train, test)
    report_shapes(X_train, X_test, y_train, y_test)

    print(f"\n✅ Pipeline complete.  Features: {FEATURE_COLS}\n")

    return {
        "X_train":      X_train,
        "X_test":       X_test,
        "y_train":      y_train,
        "y_test":       y_test,
        "scaler":       scaler,
        "feature_cols": FEATURE_COLS,
        "target_col":   TARGET_COL,
        "train_df":     train,
        "test_df":      test,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    run_pipeline()

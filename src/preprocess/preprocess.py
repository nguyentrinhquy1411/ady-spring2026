"""
preprocess.py
=============
Unified preprocessing pipeline for the Zillow Metro ZHVI dataset.
Supports multiple output variants via a PipelineConfig factory.

Usage:
    python src/preprocess/preprocess.py                 # default: scaled log_return
    python src/preprocess/preprocess.py --mode price    # raw price target
    python src/preprocess/preprocess.py --mode no_scaler
    python src/preprocess/preprocess.py --all           # run all 3 variants
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# Fix Windows cp1252 terminal encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Paths & Constants
# ---------------------------------------------------------------------------
PROJECT_ROOT  = pathlib.Path(__file__).resolve().parent.parent.parent  # ADY2026/
RAW_FILE      = PROJECT_ROOT / "data" / "raw" / "Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

META_COLS   = ["RegionID", "SizeRank", "RegionName", "RegionType", "StateName"]
TRAIN_RATIO = 0.80
LAG_PERIODS = [1, 2, 3, 6, 12]


# ═══════════════════════════════════════════════════════════════════════════════
# Pipeline Configuration (Strategy Pattern)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PipelineConfig:
    """Describes one variant of the preprocessing pipeline."""
    name:               str
    target_col:         str             # "log_return" or "price"
    lag_source:         str             # column to compute lags from
    lag_prefix:         str             # "lag" or "lag_price"
    city_enc_col:       str             # "city_enc" or "city_price_enc"
    use_scaler:         bool            # apply StandardScaler to features?
    train_filename:     str
    test_filename:      str
    save_combined:      bool  = False   # also save a single combined CSV?
    combined_filename:  str   = ""


# ── Pre-defined configs (Factory) ─────────────────────────────────────────────
CONFIGS: dict[str, PipelineConfig] = {
    "scaled": PipelineConfig(
        name="scaled",
        target_col="log_return",
        lag_source="log_return",
        lag_prefix="lag",
        city_enc_col="city_enc",
        use_scaler=True,
        train_filename="train.csv",
        test_filename="test.csv",
    ),
    "no_scaler": PipelineConfig(
        name="no_scaler",
        target_col="log_return",
        lag_source="log_return",
        lag_prefix="lag",
        city_enc_col="city_enc",
        use_scaler=False,
        train_filename="train_no_scaler.csv",
        test_filename="test_no_scaler.csv",
    ),
    "price": PipelineConfig(
        name="price",
        target_col="price",
        lag_source="price",
        lag_prefix="lag_price",
        city_enc_col="city_price_enc",
        use_scaler=False,
        train_filename="train_price.csv",
        test_filename="test_price.csv",
        save_combined=True,
        combined_filename="processed_data_price.csv",
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# Data Preprocessor
# ═══════════════════════════════════════════════════════════════════════════════

class DataPreprocessor:
    """Unified preprocessing pipeline configurable via PipelineConfig.

    Attributes:
        config (PipelineConfig): Variant configuration.
        raw_path (pathlib.Path): Path to the raw CSV.
        processed_dir (pathlib.Path): Output directory.
        train_ratio (float): Time-based train/test split ratio.
        lag_periods (list[int]): Lag periods for feature generation.
        scaler (StandardScaler | None): Fitted scaler (if use_scaler=True).
        city_mean (pd.Series | None): Target-encoded city means.
        global_mean (float | None): Global fallback for unseen cities.
    """

    def __init__(
        self,
        config:        PipelineConfig,
        raw_path:      pathlib.Path     = RAW_FILE,
        processed_dir: pathlib.Path     = PROCESSED_DIR,
        train_ratio:   float            = TRAIN_RATIO,
        lag_periods:   list[int] | None = None,
    ):
        self.config        = config
        self.raw_path      = raw_path
        self.processed_dir = processed_dir
        self.train_ratio   = train_ratio
        self.lag_periods   = lag_periods or LAG_PERIODS
        self.scaler        = StandardScaler() if config.use_scaler else None
        self.city_mean:  pd.Series | None = None
        self.global_mean: float    | None = None

    # ── helpers ────────────────────────────────────────────────────────────
    @property
    def lag_cols(self) -> list[str]:
        return [f"{self.config.lag_prefix}_{p}" for p in self.lag_periods]

    @property
    def feature_cols(self) -> list[str]:
        return self.lag_cols + [self.config.city_enc_col]

    # ── Step 1: Load ──────────────────────────────────────────────────────
    def load_data(self) -> pd.DataFrame:
        """Load raw CSV and keep only MSA regions."""
        print(f"[1] Loading raw data from: {self.raw_path}")
        df = pd.read_csv(self.raw_path, low_memory=False, skipinitialspace=True)
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(["object"]).columns:
            df[col] = df[col].str.strip()

        print(f"    Raw shape : {df.shape}")
        before = len(df)
        df = df[df["RegionType"] == "msa"].reset_index(drop=True)
        dropped = before - len(df)
        if dropped:
            print(f"    Dropped {dropped} non-MSA row(s)")
        print(f"    MSA regions: {df['RegionName'].nunique()}")
        return df

    # ── Step 2: Melt ──────────────────────────────────────────────────────
    def melt_regions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Melt wide-format date columns into long format."""
        print("\n[2] Melting all regions: wide -> long format ...")
        keep_meta = ["RegionID", "RegionName", "StateName"]
        date_cols = [c for c in df.columns if c not in META_COLS]

        long = df[keep_meta + date_cols].melt(
            id_vars=keep_meta, value_vars=date_cols,
            var_name="date", value_name="price",
        )
        long["date"]  = pd.to_datetime(long["date"])
        long["price"] = pd.to_numeric(long["price"], errors="coerce")
        long = long.sort_values(["RegionID", "date"]).reset_index(drop=True)

        print(f"    Long shape : {long.shape}")
        print(f"    Missing    : {long['price'].isna().sum():,}")
        return long

    # ── Step 3: Missing values ────────────────────────────────────────────
    def handle_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Interpolate missing prices per region."""
        print("\n[3] Interpolating missing values per region ...")
        before = df["price"].isna().sum()

        def _interpolate(grp: pd.DataFrame) -> pd.DataFrame:
            grp = grp.copy().set_index("date")
            grp["price"] = (
                grp["price"]
                .interpolate(method="time", limit_direction="both")
                .ffill().bfill()
            )
            return grp.reset_index()

        df = (
            df.groupby("RegionID", group_keys=False)
            .apply(_interpolate)
            .reset_index(drop=True)
        )
        print(f"    Missing before: {before:,} -> after: {df['price'].isna().sum():,}")
        return df

    # ── Step 4: Target & lag features ─────────────────────────────────────
    def compute_targets_and_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute target column and lag features based on config."""
        cfg = self.config
        print(f"\n[4] Computing target='{cfg.target_col}' and lags from '{cfg.lag_source}' ...")
        df = df.copy()

        # If target is log_return, compute it first
        if cfg.target_col == "log_return":
            df["log_return"] = (
                df.groupby("RegionID")["price"]
                .transform(lambda s: np.log(s / s.shift(1)))
            )
            before = len(df)
            df = df.dropna(subset=["log_return"]).reset_index(drop=True)
            print(f"    Dropped {before - len(df):,} first-observation rows (NaN log_return)")

        # Compute lags from the configured source column
        def _add_lags(grp: pd.DataFrame) -> pd.DataFrame:
            grp = grp.copy().sort_values("date")
            for lag in self.lag_periods:
                grp[f"{cfg.lag_prefix}_{lag}"] = grp[cfg.lag_source].shift(lag)
            return grp

        df = (
            df.groupby("RegionID", group_keys=False)
            .apply(_add_lags)
            .reset_index(drop=True)
        )

        # Drop warm-up NaN rows
        n_before = len(df)
        df = df.dropna(subset=self.lag_cols).reset_index(drop=True)
        print(f"    Dropped {n_before - len(df):,} warm-up rows due to lag generation")
        return df

    # ── Step 5: Time split ────────────────────────────────────────────────
    def time_split(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Split into train/test by time cutoff."""
        print(f"\n[5] Time-based split (train={self.train_ratio:.0%} / test={1 - self.train_ratio:.0%})")
        all_dates = df["date"].sort_values().unique()
        cutoff = all_dates[int(len(all_dates) * self.train_ratio)]

        train = df[df["date"] <  cutoff].copy().reset_index(drop=True)
        test  = df[df["date"] >= cutoff].copy().reset_index(drop=True)
        print(f"    Cutoff date : {pd.Timestamp(cutoff).date()}")
        print(f"    Train size  : {len(train):,} rows")
        print(f"    Test size   : {len(test):,} rows")
        return train, test

    # ── Step 6: Train-dependent transforms ────────────────────────────────
    def apply_train_dependent_transforms(
        self, train: pd.DataFrame, test: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """City target-encoding (always) + StandardScaler (if configured)."""
        cfg = self.config
        label = "City Encoding" + (" & Scaling" if cfg.use_scaler else "")
        print(f"\n[6] Applying train-dependent transforms ({label}) ...")

        # City encoding — fit on train only
        self.city_mean   = train.groupby("RegionID")[cfg.target_col].mean()
        self.global_mean = float(train[cfg.target_col].mean())

        train[cfg.city_enc_col] = train["RegionID"].map(self.city_mean)
        test[cfg.city_enc_col]  = test["RegionID"].map(self.city_mean).fillna(self.global_mean)

        # Optional scaling
        if cfg.use_scaler and self.scaler is not None:
            train[self.feature_cols] = self.scaler.fit_transform(train[self.feature_cols])
            test[self.feature_cols]  = self.scaler.transform(test[self.feature_cols])
            print("    StandardScaler applied to feature columns")

        return train, test

    # ── Step 7: Save ──────────────────────────────────────────────────────
    def save_processed(self, train: pd.DataFrame, test: pd.DataFrame) -> None:
        """Save train/test CSVs and optional combined CSV."""
        cfg = self.config
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        train_path = self.processed_dir / cfg.train_filename
        test_path  = self.processed_dir / cfg.test_filename

        train.to_csv(train_path, index=False)
        test.to_csv(test_path,  index=False)

        print(f"\n[7] Saved to {self.processed_dir}:")
        print(f"    -> {cfg.train_filename} ({train_path.stat().st_size / 1e6:.1f} MB)")
        print(f"    -> {cfg.test_filename}  ({test_path.stat().st_size / 1e6:.1f} MB)")

        if cfg.save_combined:
            combined = pd.concat([train, test], ignore_index=True)
            combined = combined.sort_values(["RegionID", "date"]).reset_index(drop=True)
            combined_path = self.processed_dir / cfg.combined_filename
            combined.to_csv(combined_path, index=False)
            print(f"    -> {cfg.combined_filename} ({combined_path.stat().st_size / 1e6:.1f} MB)")

    # ── Run ───────────────────────────────────────────────────────────────
    def run(self) -> dict:
        """Execute the full pipeline."""
        cfg = self.config
        print("=" * 60)
        print(f"  Preprocessing Pipeline -- mode: {cfg.name}")
        print(f"  target={cfg.target_col}  scaler={cfg.use_scaler}")
        print("=" * 60)

        df = self.load_data()
        df = self.melt_regions(df)
        df = self.handle_missing(df)
        df = self.compute_targets_and_features(df)

        train, test = self.time_split(df)
        train, test = self.apply_train_dependent_transforms(train, test)
        self.save_processed(train, test)

        X_train = train[self.feature_cols]
        X_test  = test[self.feature_cols]
        y_train = train[cfg.target_col]
        y_test  = test[cfg.target_col]

        scale_note = "scaled" if cfg.use_scaler else "unscaled"
        print(f"\n[8] Final shapes:")
        print(f"     X_train : {X_train.shape}")
        print(f"     X_test  : {X_test.shape}")
        print(f"     y_train : {y_train.shape}  ({cfg.target_col}, {scale_note})")
        print(f"     y_test  : {y_test.shape}   ({cfg.target_col}, {scale_note})")
        print(f"\nPipeline complete. Features: {self.feature_cols}\n")

        return {
            "X_train":      X_train,
            "X_test":       X_test,
            "y_train":      y_train,
            "y_test":       y_test,
            "scaler":       self.scaler,
            "feature_cols": self.feature_cols,
            "target_col":   cfg.target_col,
            "train_df":     train,
            "test_df":      test,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CLI Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Zillow ZHVI preprocessing pipeline"
    )
    parser.add_argument(
        "--mode", choices=list(CONFIGS.keys()), default="scaled",
        help="Pipeline variant (default: scaled)",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Run all pipeline variants sequentially",
    )
    args = parser.parse_args()

    if args.all:
        for cfg in CONFIGS.values():
            DataPreprocessor(config=cfg).run()
            print("\n" + "-" * 60 + "\n")
    else:
        DataPreprocessor(config=CONFIGS[args.mode]).run()


if __name__ == "__main__":
    main()

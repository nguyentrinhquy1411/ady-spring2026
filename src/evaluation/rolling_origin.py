"""
evaluation/rolling_origin.py
=============================
Rolling-Origin Cross-Validation for Panel Time-Series Data
-----------------------------------------------------------
Rolling-origin (also called "expanding window" or "walk-forward") evaluation
is the standard validation protocol for time-series forecasting:

    Fold k:
        Train: observations with date ≤ cutoff_k
        Test:  observations with cutoff_k < date ≤ cutoff_{k+1}

    where cutoff_k partitions the available training dates into n_splits
    equal-sized segments.

    This ensures:
      (i)  No look-ahead bias: future data is never used to train.
      (ii) The evaluation reflects real out-of-sample performance.
      (iii) Results are comparable across models on identical folds.

Panel-specific consideration:
  The cutoff date is SHARED across all cities, so all city panels are
  split at the same calendar date. This mirrors production deployment
  where a model is re-trained at fixed intervals with all available data.

Reference:
  Tashman, L. J. (2000). Out-of-sample tests of forecasting accuracy:
  An analysis and review. International Journal of Forecasting, 16(4),
  437–450.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd
from tqdm import tqdm

from .metrics import compute_rmse, compute_mae


@dataclass
class FoldResult:
    fold:         int
    train_cutoff: pd.Timestamp
    test_cutoff:  pd.Timestamp
    n_train:      int
    n_test:       int
    rmse:         float
    mae:          float
    model_name:   str
    predictions:  np.ndarray = field(repr=False)
    actuals:      np.ndarray = field(repr=False)


class RollingOriginEvaluator:
    """
    Rolling-origin (expanding window) cross-validator for panel data.

    Parameters
    ----------
    n_splits   : int   — number of expanding folds
    date_col   : str   — date column name
    target_col : str   — target column name
    entity_col : str   — panel entity column
    feature_cols : list[str] — feature columns to use
    """

    def __init__(
        self,
        n_splits:     int       = 5,
        date_col:     str       = "date",
        target_col:   str       = "log_return",
        entity_col:   str       = "RegionID",
        feature_cols: list[str] = None,
    ) -> None:
        self.n_splits    = n_splits
        self.date_col    = date_col
        self.target_col  = target_col
        self.entity_col  = entity_col
        self.feature_cols = feature_cols or [
            "lag_1", "lag_2", "lag_3", "lag_6", "lag_12", "city_enc"
        ]

    # ------------------------------------------------------------------
    def _date_splits(self, df: pd.DataFrame) -> list[tuple]:
        """Compute (train_cutoff, test_cutoff) pairs for n_splits folds."""
        all_dates = np.sort(df[self.date_col].unique())
        T = len(all_dates)
        # Use dates from 30% → 90% of the timeline as test cutoffs
        start_idx = int(T * 0.30)
        end_idx   = int(T * 0.90)
        split_idxs = np.linspace(start_idx, end_idx, self.n_splits + 1, dtype=int)
        splits = []
        for k in range(self.n_splits):
            train_cutoff = all_dates[split_idxs[k]]
            test_cutoff  = all_dates[split_idxs[k + 1]]
            splits.append((pd.Timestamp(train_cutoff), pd.Timestamp(test_cutoff)))
        return splits

    # ------------------------------------------------------------------
    def evaluate(
        self,
        df:          pd.DataFrame,
        fit_fn:      Callable,
        predict_fn:  Callable,
        model_name:  str = "model",
        verbose:     bool = True,
    ) -> list[FoldResult]:
        """
        Evaluate a model using rolling-origin splits.

        Parameters
        ----------
        df         : full DataFrame (train period)
        fit_fn     : callable(X_tr, y_tr, entity_tr) → fitted model object
        predict_fn : callable(model, X_te, entity_te) → np.ndarray of preds
        model_name : label for the model
        verbose    : show tqdm progress bar

        Returns
        -------
        list[FoldResult]
        """
        splits  = self._date_splits(df)
        results = []

        iterable = tqdm(enumerate(splits, 1), total=self.n_splits, desc=model_name) \
            if verbose else enumerate(splits, 1)

        for fold, (train_cut, test_cut) in iterable:
            train_mask = df[self.date_col] <= train_cut
            test_mask  = (df[self.date_col] > train_cut) & (df[self.date_col] <= test_cut)

            df_tr = df[train_mask].copy()
            df_te = df[test_mask].copy()

            if len(df_te) == 0:
                continue

            X_tr = df_tr[self.feature_cols]
            y_tr = df_tr[self.target_col]
            eid_tr = df_tr[self.entity_col]

            X_te = df_te[self.feature_cols]
            y_te = df_te[self.target_col].values
            eid_te = df_te[self.entity_col]

            try:
                model = fit_fn(X_tr, y_tr, eid_tr)
                preds = predict_fn(model, X_te, eid_te)
            except Exception as exc:
                print(f"    [Fold {fold}] Error: {exc}")
                continue

            rmse = compute_rmse(y_te, preds)
            mae  = compute_mae(y_te, preds)

            results.append(FoldResult(
                fold         = fold,
                train_cutoff = train_cut,
                test_cutoff  = test_cut,
                n_train      = len(df_tr),
                n_test       = len(df_te),
                rmse         = rmse,
                mae          = mae,
                model_name   = model_name,
                predictions  = preds,
                actuals      = y_te,
            ))

        return results

    # ------------------------------------------------------------------
    @staticmethod
    def aggregate(results: list[FoldResult]) -> dict:
        """Aggregate fold results into mean ± std statistics."""
        rmses = [r.rmse for r in results]
        maes  = [r.mae  for r in results]
        return {
            "model":       results[0].model_name if results else "",
            "n_folds":     len(results),
            "rmse_mean":   float(np.mean(rmses)),
            "rmse_std":    float(np.std(rmses)),
            "mae_mean":    float(np.mean(maes)),
            "mae_std":     float(np.std(maes)),
            "avg_n_train": int(np.mean([r.n_train for r in results])),
            "avg_n_test":  int(np.mean([r.n_test  for r in results])),
        }

    @staticmethod
    def to_dataframe(all_results: dict[str, list[FoldResult]]) -> pd.DataFrame:
        """Convert multi-model rolling-origin results to a tidy DataFrame."""
        rows = []
        for model_name, folds in all_results.items():
            for r in folds:
                rows.append({
                    "model":   model_name,
                    "fold":    r.fold,
                    "n_train": r.n_train,
                    "n_test":  r.n_test,
                    "rmse":    r.rmse,
                    "mae":     r.mae,
                })
        return pd.DataFrame(rows)

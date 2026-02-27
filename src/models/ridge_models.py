"""
models/ridge_models.py
======================
Model 4a: Global Ridge Regression
Model 4b: Local Ridge Regression
----------------------------------
Mathematical formulation (Ridge / L2 regularisation):

    β̂_Ridge = argmin_β { ||y − Xβ||² + λ ||β||² }

    Closed form:  β̂ = (XᵀX + λI)⁻¹ Xᵀy

Bias-Variance Interpretation:
  - λ = 0  → OLS (minimum bias, maximum variance)
  - λ → ∞  → β̂ → 0 (maximum bias, minimum variance / shrinkage)
  - Ridge introduces a controlled bias to reduce forecast variance,
    which is beneficial when:
      (a) predictors are highly correlated (lags are autocorrelated)
      (b) N/T ratio is unfavourable in small-T local panels
      (c) OLS overfits within-city samples

  In panel forecasting, Ridge outperforms OLS when:
    σ²_noise / ||β*||² > λ_optimal / (eigenvalues of XᵀX)

Degrees of Freedom:  df(λ) = trace[(XᵀX)(XᵀX + λI)⁻¹] < p
  Each λ > 0 shrinks effective parameters, reducing model complexity.

Global Ridge:
  Single model on pooled data. Exploits cross-sectional sample (N×T rows).

Local Ridge:
  City-specific Ridge with common regularisation strength λ selected
  globally via time-series cross-validation.

Reference:
  Hoerl, A. E., & Kennard, R. W. (1970). Ridge regression: Biased
  estimation for nonorthogonal problems. Technometrics, 12(1), 55–67.

  Baltagi, B. H. (2013). Econometric Analysis of Panel Data (5th ed.).
  Wiley.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.model_selection import TimeSeriesSplit


# ---------------------------------------------------------------------------
# 4a. Global Ridge
# ---------------------------------------------------------------------------
class GlobalRidge:
    """
    Ridge regression trained on all cities combined.

    Alpha is chosen via time-series cross-validation on the pooled training
    data (TimeSeriesSplit with n_splits=5).

    Parameters
    ----------
    alphas     : iterable of candidate λ values
    n_splits   : number of expanding-window CV folds
    """

    name = "Global Ridge"

    def __init__(
        self,
        alphas: tuple = (0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0),
        n_splits: int = 5,
    ) -> None:
        self.alphas   = list(alphas)
        self.n_splits = n_splits
        self._model: Ridge | None = None
        self.best_alpha_: float | None = None
        self._feature_names: list[str] = []

    # ------------------------------------------------------------------
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "GlobalRidge":
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        self._feature_names = list(X.columns)
        X_arr = X.values
        y_arr = y.values

        # Select alpha via CV
        best_alpha, best_mse = None, np.inf
        for alpha in self.alphas:
            mses = []
            for tr_idx, val_idx in tscv.split(X_arr):
                m = Ridge(alpha=alpha, fit_intercept=True)
                m.fit(X_arr[tr_idx], y_arr[tr_idx])
                pred = m.predict(X_arr[val_idx])
                mses.append(np.mean((y_arr[val_idx] - pred) ** 2))
            mean_mse = float(np.mean(mses))
            if mean_mse < best_mse:
                best_mse   = mean_mse
                best_alpha = alpha

        self.best_alpha_ = best_alpha
        self._model = Ridge(alpha=best_alpha, fit_intercept=True)
        self._model.fit(X_arr, y_arr)
        print(f"    GlobalRidge: best α={best_alpha}  (CV-MSE={best_mse:.6f})")
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self._model.predict(X.values)

    def summary(self) -> pd.DataFrame:
        return pd.DataFrame({
            "feature": self._feature_names,
            "coef":    self._model.coef_,
        })


# ---------------------------------------------------------------------------
# 4b. Local Ridge
# ---------------------------------------------------------------------------
class LocalRidge:
    """
    Per-city Ridge regression with globally tuned regularisation strength.

    The optimal alpha is chosen first on the pooled training data (time-series
    CV), then each city's Ridge model is fitted with that shared alpha.

    This is a practical compromise:
      - Avoids per-city CV (infeasible for short T_i)
      - Still adjusts slopes to per-city dynamics
      - Subsumes LocalOLS as λ → 0

    Parameters
    ----------
    alphas     : candidate λ values for global CV
    n_splits   : CV folds
    entity_col : panel entity identifier
    min_obs    : minimum obs per city to fit a local model
    """

    name = "Local Ridge"

    def __init__(
        self,
        alphas:     tuple = (0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0),
        n_splits:   int  = 5,
        entity_col: str  = "RegionID",
        min_obs:    int  = 24,
    ) -> None:
        self.alphas     = list(alphas)
        self.n_splits   = n_splits
        self.entity_col = entity_col
        self.min_obs    = min_obs

        self.best_alpha_: float | None = None
        self._models:      dict = {}
        self._global_mean: float = 0.0
        self._feature_names: list[str] = []

    # ------------------------------------------------------------------
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        entity_ids: pd.Series,
    ) -> "LocalRidge":
        self._feature_names = list(X.columns)
        self._global_mean   = float(y.mean())
        X_arr = X.values
        y_arr = y.values

        # Step 1: tune alpha on pooled data
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        best_alpha, best_mse = None, np.inf
        for alpha in self.alphas:
            mses = []
            for tr_idx, val_idx in tscv.split(X_arr):
                m = Ridge(alpha=alpha, fit_intercept=True)
                m.fit(X_arr[tr_idx], y_arr[tr_idx])
                pred = m.predict(X_arr[val_idx])
                mses.append(np.mean((y_arr[val_idx] - pred) ** 2))
            mean_mse = float(np.mean(mses))
            if mean_mse < best_mse:
                best_mse   = mean_mse
                best_alpha = alpha
        self.best_alpha_ = best_alpha

        # Step 2: fit per-city Ridge with best_alpha
        groups  = entity_ids.values
        skipped = 0
        for city in np.unique(groups):
            mask = groups == city
            Xi, yi = X_arr[mask], y_arr[mask]
            if len(yi) < self.min_obs:
                skipped += 1
                continue
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                m = Ridge(alpha=best_alpha, fit_intercept=True)
                m.fit(Xi, yi)
            self._models[city] = m

        n_cities = len(np.unique(groups))
        print(
            f"    LocalRidge: best α={best_alpha}  | "
            f"fitted {len(self._models)}/{n_cities} cities "
            f"(skipped {skipped})"
        )
        return self

    def predict(self, X: pd.DataFrame, entity_ids: pd.Series) -> np.ndarray:
        preds  = np.full(len(X), self._global_mean, dtype=float)
        groups = entity_ids.values
        X_arr  = X.values
        for city in np.unique(groups):
            mask = groups == city
            if city in self._models:
                preds[mask] = self._models[city].predict(X_arr[mask])
        return preds

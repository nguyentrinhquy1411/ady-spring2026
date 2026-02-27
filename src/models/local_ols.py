"""
models/local_ols.py
===================
Model 2: Local (City-Specific) OLS
------------------------------------
Mathematical formulation:
    y_{i,t} = αᵢ + βᵢ₁ x_{i,t,1} + ... + βᵢₖ x_{i,t,k} + ε_{i,t}

Where:
  - (αᵢ, βᵢ) = city-specific intercept AND slopes, estimated independently
    for each city i from its own T_i time-series observations.

Econometric Interpretation:
  - No information is shared across cities (complete fragmentation).
  - Unbiased under heterogeneous city dynamics, but HIGH VARIANCE when
    T_i is small (short per-city series problem).
  - Susceptible to over-fitting: each city model has p+1 parameters but
    only T_i observations. If T_i ≈ p+1, the model fits within-city
    noise and generalises poorly.
  - Bias-variance trade-off: Local OLS minimises bias but maximises
    variance. Optimal only when cities are truly dynamically independent.

Reference:
  Pesaran, M. H., & Smith, R. (1995). Estimating long-run relationships
  from dynamic panels. Journal of Econometrics, 68(1), 79–113.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class LocalOLS:
    """
    Local OLS: one separate LinearRegression model per city (RegionID).

    Fit is performed independently for each entity. At prediction time,
    cities not seen in training fall back to the global mean.

    Parameters
    ----------
    entity_col    : str  — panel entity identifier column
    min_obs       : int  — minimum training observations per city
    fit_intercept : bool
    """

    name = "Local OLS"

    def __init__(
        self,
        entity_col:    str  = "RegionID",
        min_obs:       int  = 24,
        fit_intercept: bool = True,
    ) -> None:
        self.entity_col    = entity_col
        self.min_obs       = min_obs
        self.fit_intercept = fit_intercept

        self._models:     dict[int, LinearRegression] = {}
        self._global_mean: float = 0.0
        self._feature_names: list[str] = []

    # ------------------------------------------------------------------
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        entity_ids: pd.Series,
    ) -> "LocalOLS":
        """
        Fit one LinearRegression per city.

        Parameters
        ----------
        X          : feature matrix (all cities, stacked)
        y          : log_return target
        entity_ids : city identifier column aligned with X, y
        """
        self._feature_names = list(X.columns)
        self._global_mean   = float(y.mean())

        groups = entity_ids.values
        X_arr  = X.values
        y_arr  = y.values

        skipped = 0
        for city in np.unique(groups):
            mask = groups == city
            Xi, yi = X_arr[mask], y_arr[mask]
            if len(yi) < self.min_obs:
                skipped += 1
                continue
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                m = LinearRegression(fit_intercept=self.fit_intercept)
                m.fit(Xi, yi)
            self._models[city] = m

        n_cities = len(np.unique(groups))
        print(
            f"    LocalOLS: fitted {len(self._models)}/{n_cities} cities "
            f"(skipped {skipped} with < {self.min_obs} obs)"
        )
        return self

    def predict(self, X: pd.DataFrame, entity_ids: pd.Series) -> np.ndarray:
        """
        Predict city-by-city; unknown cities → global mean.
        """
        preds = np.full(len(X), self._global_mean, dtype=float)
        groups = entity_ids.values
        X_arr  = X.values

        for city in np.unique(groups):
            mask = groups == city
            if city in self._models:
                preds[mask] = self._models[city].predict(X_arr[mask])
        return preds

    # ------------------------------------------------------------------
    def coefficient_df(self) -> pd.DataFrame:
        """Return a tidy DataFrame of per-city coefficients."""
        rows = []
        for city, m in self._models.items():
            row = {"city": city, "intercept": m.intercept_}
            for feat, c in zip(self._feature_names, m.coef_):
                row[feat] = c
            rows.append(row)
        return pd.DataFrame(rows).reset_index(drop=True)

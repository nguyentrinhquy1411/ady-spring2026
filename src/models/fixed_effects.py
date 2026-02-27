"""
models/fixed_effects.py
========================
Model 3: Fixed Effects (Within) Panel Model
--------------------------------------------
Mathematical formulation (Least Squares Dummy Variable — LSDV):

    y_{i,t} = αᵢ + β₁ x_{i,t,1} + ... + βₖ x_{i,t,k} + ε_{i,t}

    where αᵢ = city-fixed intercept (N−1 city dummies).
    β = SHARED slopes across all cities (partial pooling of slopes,
        no pooling of intercepts).

Equivalently, the Within estimator de-means:
    ÿ_{i,t} = β₁ ẍ_{i,t,1} + ... + βₖ ẍ_{i,t,k} + ε̈_{i,t}
    where ÿ_{i,t} = y_{i,t} − ȳᵢ  (within-city demeaning)

Econometric Interpretation:
  - Allows each city to have a distinct long-run average return (αᵢ)
    while constraining slope dynamics to be homogeneous.
  - Controls for all time-invariant unobserved city heterogeneity that
    is correlated with regressors (e.g., geographic fundamentals, supply
    elasticity, demographic trends).
  - More efficient than local OLS when slope homogeneity is reasonable.
  - Cannot estimate time-invariant covariates (collinear with αᵢ).
  - N-consistent under sequential exogeneity; Nickell bias is negligible
    for large T (here T≈240 months per city).

Implementation:
  We use the LSDV approach (city dummy columns) via sklearn LinearRegression
  for simplicity and speed. This is numerically equivalent to PanelOLS with
  EntityEffects from linearmodels.

Reference:
  Mundlak, Y. (1978). On the pooling of time series and cross section data.
  Econometrica, 46(1), 69–85.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class FixedEffectsModel:
    """
    Fixed Effects model estimated via LSDV (city dummy variables).

    Parameters
    ----------
    entity_col    : str  — panel entity identifier column
    fit_intercept : bool — set False; dummies absorb the intercept
    drop_first    : bool — True to avoid perfect multicollinearity (N-1 dummies)
    """

    name = "Fixed Effects (LSDV)"

    def __init__(
        self,
        entity_col:    str  = "RegionID",
        drop_first:    bool = True,
    ) -> None:
        self.entity_col = entity_col
        self.drop_first = drop_first
        self._model = LinearRegression(fit_intercept=True)
        self._dummy_cities: list = []
        self._feature_names: list[str] = []
        self._city_fe: dict = {}      # estimated fixed effects

    # ------------------------------------------------------------------
    def _build_X(
        self,
        X: pd.DataFrame,
        entity_ids: pd.Series,
        fit: bool = True,
    ) -> np.ndarray:
        """Append one-hot city dummies to the feature matrix."""
        dummies = pd.get_dummies(
            entity_ids.astype(str),
            prefix="city",
            drop_first=self.drop_first,
        )
        if fit:
            self._dummy_cities = list(dummies.columns)
        else:
            # At test time, align columns to training dummies
            dummies = dummies.reindex(
                columns=self._dummy_cities, fill_value=0
            )
        return np.concatenate([X.values, dummies.values.astype(float)], axis=1)

    # ------------------------------------------------------------------
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        entity_ids: pd.Series,
    ) -> "FixedEffectsModel":
        """
        Fit LSDV: lags + city dummies.

        Parameters
        ----------
        X          : lag feature matrix
        y          : log_return target
        entity_ids : city identifier aligned with X, y
        """
        self._feature_names = list(X.columns)
        X_ext = self._build_X(X, entity_ids, fit=True)
        self._model.fit(X_ext, y.values)

        # Extract city fixed effects for interpretation
        k = len(self._feature_names)
        self.slope_coefs_ = self._model.coef_[:k]
        dummy_coefs = self._model.coef_[k:]
        # FE for dropped category is zero (reference city)
        self._city_fe = dict(zip(self._dummy_cities, dummy_coefs))

        print(
            f"    FixedEffects: {len(self._dummy_cities)} dummy cols "
            f"| global intercept={self._model.intercept_:.5f}"
        )
        return self

    def predict(self, X: pd.DataFrame, entity_ids: pd.Series) -> np.ndarray:
        X_ext = self._build_X(X, entity_ids, fit=False)
        return self._model.predict(X_ext)

    # ------------------------------------------------------------------
    def fixed_effects_df(self) -> pd.DataFrame:
        """Return a DataFrame of estimated city fixed effects."""
        rows = [
            {"city_dummy": k, "fixed_effect": v}
            for k, v in self._city_fe.items()
        ]
        return pd.DataFrame(rows).sort_values("fixed_effect", ascending=False)

    def slope_summary(self) -> pd.DataFrame:
        """Shared slope coefficients across all cities."""
        return pd.DataFrame({
            "feature": self._feature_names,
            "coef":    self.slope_coefs_,
        })

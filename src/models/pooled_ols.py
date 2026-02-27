"""
models/pooled_ols.py
====================
Model 1: Pooled (Global) OLS
----------------------------
Mathematical formulation:
    y_{i,t} = α + β₁ x_{i,t,1} + ... + βₖ x_{i,t,k} + ε_{i,t}

Where:
  - y_{i,t}   = log_return for city i at time t
  - x_{i,t,*} = lag features (lag_1, lag_2, lag_3, lag_6, lag_12, city_enc)
  - α, β       = single set of intercept and slopes shared across ALL cities

Econometric Interpretation:
  - Assumes homogeneous slope structure across all cities (complete pooling).
  - Maximises sample size (all T observations per city are combined).
  - Efficient when cities share the same return dynamics (cross-sectional
    homogeneity assumption holds).
  - Biased when heterogeneity in city dynamics is substantial and correlated
    with regressors (omitted variable bias à la Nickell, 1981).

Reference:
  Hsiao, C. (2014). Analysis of Panel Data. Cambridge University Press.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class PooledOLS:
    """
    Pooled OLS: a single linear regression fitted on all cities jointly.

    Parameters
    ----------
    fit_intercept : bool, default True
    """

    name = "Pooled OLS"

    def __init__(self, fit_intercept: bool = True) -> None:
        self.fit_intercept = fit_intercept
        self._model = LinearRegression(fit_intercept=fit_intercept)

    # ------------------------------------------------------------------
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "PooledOLS":
        """
        Fit on stacked (city × time) observations.

        Parameters
        ----------
        X : pd.DataFrame  — feature matrix (all cities)
        y : pd.Series     — log_return target
        """
        self._model.fit(X.values, y.values)
        self.coef_   = self._model.coef_
        self.intercept_ = self._model.intercept_
        self.feature_names_ = list(X.columns)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self._model.predict(X.values)

    # ------------------------------------------------------------------
    def summary(self) -> pd.DataFrame:
        """Return coefficient table."""
        coefs = {
            "feature":   self.feature_names_,
            "coef":      self.coef_,
        }
        df = pd.DataFrame(coefs)
        df.loc[len(df)] = ["intercept", self.intercept_]
        return df.reset_index(drop=True)

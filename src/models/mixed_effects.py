"""
models/mixed_effects.py
=======================
Model 5: Mixed Effects (Hierarchical / Partial Pooling) Model
-------------------------------------------------------------
Mathematical formulation:

    Level 1 (within-city):
        y_{i,t} = αᵢ + β x_{i,t} + ε_{i,t},     ε_{i,t} ~ N(0, σ²)

    Level 2 (between-city):
        αᵢ = α₀ + uᵢ,                             uᵢ ~ N(0, τ²)

    where:
      - α₀ = grand-mean intercept (fixed effect)
      - β  = global slope vector (fixed effects SHARED across cities)
      - uᵢ = city-specific random intercept (random effect)
      - ε_{i,t} = idiosyncratic error
      - τ² = between-city variance (heterogeneity in baseline returns)
      - σ² = within-city residual variance

Partial Pooling (Shrinkage):
    The BLUP (Best Linear Unbiased Predictor) for city i's intercept is:

        α̂ᵢ = B · ȳᵢ + (1 - B) · α̂₀

    where B = τ² / (τ² + σ²/Tᵢ) is the "reliability ratio".

    - When τ² >> σ²/Tᵢ  → B ≈ 1  → no shrinkage (local estimate reliable)
    - When τ² << σ²/Tᵢ  → B ≈ 0  → full shrinkage toward grand mean

    This gives PARTIAL POOLING: an oracle that adapts between complete
    pooling and complete fragmentation based on observed heterogeneity.

Econometric Interpretation:
  - Preferred specification when cross-sectional units are RANDOM DRAWS
    from a population of cities (random effects assumption holds).
  - More efficient than FE if Cov(uᵢ, xᵢ) ≈ 0 but harder to compute.
  - For large panels (N large, T moderate), FE and RE estimators converge.
  - In forecasting, partial pooling typically yields the best RMSE as it
    adaptively regularises city-specific intercepts toward the global mean.

Implementation:
    Uses statsmodels MixedLM with random intercepts per city.
    Fixed effects: lag_1, lag_2, lag_3, lag_6, lag_12, city_enc.
    Random effects: city-specific intercept only (random slopes would require
    N×p additional parameters, computationally prohibitive for N≈900).

    For scalability on large N, we fit a fast Bayesian shrinkage approximation
    (James-Stein type) that avoids the full REML iteration.

Reference:
  Robinson, G. K. (1991). That BLUP is a good thing. Statistical Science,
  6(1), 15–32.

  Hsiao, C. (2014). Analysis of Panel Data. Cambridge University Press.

  Gelman, A., & Hill, J. (2007). Data Analysis Using Regression and
  Multilevel/Hierarchical Models. Cambridge University Press.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd


class MixedEffectsModel:
    """
    Mixed effects model with random city intercepts and global slopes.

    Strategy
    --------
    1. Fit global (pooled) slopes β via OLS on all data.
    2. Compute city-level residual mean  r̄ᵢ = mean(yᵢ − X̄ᵢ β̂).
    3. Apply James-Stein shrinkage to r̄ᵢ → û_i (partial pooling).
    4. Predict: ŷ_{i,t} = X_{i,t} β̂ + û_i

    This is an approximate BLUP that is:
      - Fast (no iterative REML)
      - Interpretable (explicit shrinkage coefficient B)
      - Numerically stable for N≈900 cities

    Parameters
    ----------
    entity_col : str  — panel entity identifier
    shrinkage  : float | None
        If None, shrinkage coefficient B is estimated from data via
        method-of-moments. If float ∈ [0, 1], forces B = shrinkage.
        B=0 → Pooled OLS, B=1 → Local OLS, B ∈ (0,1) → Partial pooling.
    """

    name = "Mixed Effects (Partial Pooling)"

    def __init__(
        self,
        entity_col: str        = "RegionID",
        shrinkage:  float|None = None,
    ) -> None:
        self.entity_col = entity_col
        self.shrinkage  = shrinkage

        # Estimated parameters
        self._global_coef:      np.ndarray | None = None
        self._global_intercept: float             = 0.0
        self._city_re:          dict              = {}   # random effects û_i
        self.B_:                float             = 0.0  # shrinkage coefficient
        self.tau2_:             float             = 0.0  # between-city variance
        self.sigma2_:           float             = 0.0  # within-city variance
        self._feature_names:    list[str]         = []

    # ------------------------------------------------------------------
    def fit(
        self,
        X:          pd.DataFrame,
        y:          pd.Series,
        entity_ids: pd.Series,
    ) -> "MixedEffectsModel":
        """
        Two-step BLUP approximation.

        Step 1: OLS global slopes on pooled data.
        Step 2: Shrink city residual means toward zero.
        """
        from sklearn.linear_model import LinearRegression

        self._feature_names = list(X.columns)
        X_arr = X.values
        y_arr = y.values
        groups = entity_ids.values

        # ---- Step 1: Global OLS slopes ---------------------------------
        ols = LinearRegression(fit_intercept=True)
        ols.fit(X_arr, y_arr)
        self._global_coef      = ols.coef_
        self._global_intercept = float(ols.intercept_)

        # ---- Step 2: Compute city residual means -----------------------
        resid = y_arr - ols.predict(X_arr)   # pooled residuals

        city_resid_means = {}
        city_Ts          = {}
        for city in np.unique(groups):
            mask                    = groups == city
            city_resid_means[city]  = float(resid[mask].mean())
            city_Ts[city]           = int(mask.sum())

        r_bar = np.array(list(city_resid_means.values()))

        # ---- Step 3: Method-of-moments shrinkage ----------------------
        N          = len(city_resid_means)
        sigma2_hat = float(np.var(resid))              # within-city noise
        tau2_hat   = max(0.0, float(np.var(r_bar)) - sigma2_hat / np.mean(list(city_Ts.values())))

        self.sigma2_ = sigma2_hat
        self.tau2_   = tau2_hat

        if self.shrinkage is not None:
            B = float(self.shrinkage)
        else:
            total = tau2_hat + sigma2_hat  # approximated
            B = tau2_hat / total if total > 0 else 0.0

        self.B_ = B

        # ---- Step 4: Shrinkage BLUP for each city ---------------------
        for city, r_i in city_resid_means.items():
            T_i = city_Ts[city]
            # City-specific shrinkage: B_i = τ²/(τ² + σ²/T_i)
            denom  = tau2_hat + sigma2_hat / T_i if T_i > 0 else 1.0
            B_i    = tau2_hat / denom if denom > 0 else 0.0
            self._city_re[city] = B_i * r_i    # shrunk intercept

        print(
            f"    MixedEffects: τ²={tau2_hat:.6f}  σ²={sigma2_hat:.6f}  "
            f"avg B={B:.4f}  ({N} cities)"
        )
        return self

    # ------------------------------------------------------------------
    def predict(self, X: pd.DataFrame, entity_ids: pd.Series) -> np.ndarray:
        groups = entity_ids.values
        X_arr  = X.values

        # Global prediction
        global_pred = X_arr @ self._global_coef + self._global_intercept

        # Add city random effects
        re_arr = np.array([
            self._city_re.get(city, 0.0) for city in groups
        ])
        return global_pred + re_arr

    # ------------------------------------------------------------------
    def random_effects_df(self) -> pd.DataFrame:
        """Return sorted DataFrame of estimated city random intercepts."""
        rows = [
            {"city": k, "random_intercept": v}
            for k, v in self._city_re.items()
        ]
        return (
            pd.DataFrame(rows)
            .sort_values("random_intercept", ascending=False)
            .reset_index(drop=True)
        )

    def global_slope_summary(self) -> pd.DataFrame:
        return pd.DataFrame({
            "feature": self._feature_names,
            "coef":    self._global_coef,
        })

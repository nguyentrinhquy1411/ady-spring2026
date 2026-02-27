"""
evaluation/metrics.py
=====================
Forecast accuracy metrics for panel return forecasting.

Metrics implemented:
  1. RMSE — Root Mean Squared Error
  2. MAE  — Mean Absolute Error
  3. Diebold-Mariano test — formal statistical comparison of two forecasts

Diebold-Mariano Test (DM, 1995)
--------------------------------
H₀: E[d_t] = 0  (equal predictive accuracy)
H₁: E[d_t] ≠ 0  (unequal predictive accuracy)

    d_t  = L(e₁_t) − L(e₂_t)     loss differential
    L(e) = e²                       (quadratic loss, default)
    DM   = d̄ / √(V̂[d̄])            test statistic

Under H₀, DM ~ N(0,1) asymptotically.
V̂[d̄] is estimated via a Newey-West HAC variance (long-run variance)
to account for autocorrelation in the loss differential series.

For panel data, we stack all city predictions per period and compute
the aggregate loss differential across all (city, time) pairs, then
apply the DM test on the time dimension.

References:
  Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy.
  Journal of Business & Economic Statistics, 13(3), 253–263.

  Harvey, D., Leybourne, S., & Newbold, P. (1997). Testing the equality
  of prediction mean squared errors. International Journal of Forecasting,
  13(2), 281–291.
"""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------------
# Basic metrics
# ---------------------------------------------------------------------------

def compute_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error."""
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def compute_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Error."""
    return float(np.mean(np.abs(y_true - y_pred)))


# ---------------------------------------------------------------------------
# Diebold-Mariano Test
# ---------------------------------------------------------------------------

def _newey_west_variance(d: np.ndarray, max_lag: int | None = None) -> float:
    """
    Newey-West HAC variance estimator for the mean of d.

    V̂_NW = (1/T²) * [Γ(0) + 2 Σ_{j=1}^{m} w_j Γ(j)]
    where w_j = 1 − j/(m+1)  (Bartlett kernel)
          Γ(j) = Σ_{t=j+1}^{T} (d_t − d̄)(d_{t−j} − d̄)
          m = max_lag (auto-selected by Newey-West rule if None)

    Returns the variance of the MEAN (not the series).
    """
    T = len(d)
    d_demeaned = d - np.mean(d)

    if max_lag is None:
        max_lag = int(np.floor(4 * (T / 100) ** (2 / 9)))

    gamma_0 = float(np.dot(d_demeaned, d_demeaned)) / T
    long_run_var = gamma_0

    for j in range(1, max_lag + 1):
        weight  = 1.0 - j / (max_lag + 1)
        gamma_j = float(np.dot(d_demeaned[j:], d_demeaned[:-j])) / T
        long_run_var += 2 * weight * gamma_j

    # Variance of the sample mean
    return max(long_run_var / T, 1e-16)


def diebold_mariano_test(
    e1:       np.ndarray,
    e2:       np.ndarray,
    h:        int = 1,
    loss:     Literal["squared", "absolute"] = "squared",
    max_lag:  int | None = None,
) -> dict:
    """
    Diebold-Mariano test for equal predictive accuracy.

    Parameters
    ----------
    e1, e2   : forecast errors of model 1 and model 2 (same length)
    h        : forecast horizon (use h=1 for one-step-ahead)
    loss     : 'squared' (MSE differential) or 'absolute' (MAE differential)
    max_lag  : Newey-West truncation lag (auto if None)

    Returns
    -------
    dict with keys: dm_stat, p_value, decision(α=0.05),
                    mean_loss_e1, mean_loss_e2, delta_loss
    """
    e1, e2 = np.asarray(e1, dtype=float), np.asarray(e2, dtype=float)
    assert len(e1) == len(e2), "Error vectors must have equal length."

    if loss == "squared":
        L1, L2 = e1 ** 2, e2 ** 2
    else:
        L1, L2 = np.abs(e1), np.abs(e2)

    d   = L1 - L2                    # loss differential
    d_bar = float(np.mean(d))
    var_d = _newey_west_variance(d, max_lag=max_lag)
    dm_stat = d_bar / np.sqrt(var_d)

    # Two-sided p-value (asymptotically N(0,1))
    p_value = float(2 * (1 - stats.norm.cdf(abs(dm_stat))))

    return {
        "dm_stat":      round(dm_stat, 4),
        "p_value":      round(p_value, 4),
        "significant":  p_value < 0.05,
        "better_model": "model_2" if dm_stat > 0 else "model_1",
        "mean_loss_e1": round(float(np.mean(L1)), 6),
        "mean_loss_e2": round(float(np.mean(L2)), 6),
        "delta_loss":   round(d_bar, 6),
    }


# ---------------------------------------------------------------------------
# Summary table builder
# ---------------------------------------------------------------------------

def summarize_results(
    results: dict[str, dict],
    dm_tests: dict[str, dict] | None = None,
) -> pd.DataFrame:
    """
    Build a formatted comparison table from model results.

    Parameters
    ----------
    results  : {model_name: {"rmse": float, "mae": float}}
    dm_tests : {model_name: dm_result_dict} vs. Pooled OLS baseline

    Returns
    -------
    pd.DataFrame sorted by RMSE ascending.
    """
    rows = []
    for model, metrics in results.items():
        row = {
            "Model":      model,
            "RMSE":       round(metrics["rmse"], 6),
            "MAE":        round(metrics["mae"],  6),
        }
        if dm_tests and model in dm_tests:
            dm = dm_tests[model]
            row["DM_stat"]  = dm["dm_stat"]
            row["p_value"]  = dm["p_value"]
            row["Sig(5%)"]  = "✓" if dm["significant"] else ""
            row["Better"]   = dm["better_model"]
        rows.append(row)

    df = pd.DataFrame(rows).sort_values("RMSE").reset_index(drop=True)
    df.index = range(1, len(df) + 1)   # rank 1 = best
    return df

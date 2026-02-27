"""
src/evaluation
==============
Evaluation utilities for panel forecasting comparisons.
"""
from .metrics import compute_rmse, compute_mae, diebold_mariano_test, summarize_results
from .rolling_origin import RollingOriginEvaluator

__all__ = [
    "compute_rmse",
    "compute_mae",
    "diebold_mariano_test",
    "summarize_results",
    "RollingOriginEvaluator",
]

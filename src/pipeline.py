"""
src/pipeline.py
===============
Master Pipeline Orchestrator for Panel Forecasting Comparison
-------------------------------------------------------------
Runs all five pooling strategies end-to-end and produces:
  1. Hold-out test RMSE / MAE comparison table
  2. Rolling-origin CV performance table (mean ± std across folds)
  3. Diebold-Mariano tests (each model vs. Pooled OLS benchmark)
  4. Saved JSON report → reports/panel_results.json

Usage
-----
    cd /Users/nguyenquy1411/Documents/dev/fpt/ady-2026
    uv run python src/pipeline.py
"""

from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Make sure src/ is on PYTHONPATH when run directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from models import (
    PooledOLS,
    LocalOLS,
    FixedEffectsModel,
    GlobalRidge,
    LocalRidge,
    MixedEffectsModel,
)
from evaluation import (
    compute_rmse,
    compute_mae,
    diebold_mariano_test,
    summarize_results,
    RollingOriginEvaluator,
)

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------
PROJECT_ROOT  = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR      = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR   = PROJECT_ROOT / "reports"

LAG_COLS      = ["lag_1", "lag_2", "lag_3", "lag_6", "lag_12"]
CITY_ENC_COL  = "city_enc"
FEATURE_COLS  = LAG_COLS + [CITY_ENC_COL]
TARGET_COL    = "log_return"
ENTITY_COL    = "RegionID"
DATE_COL      = "date"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    print("[Pipeline] Loading processed data …")
    train = pd.read_csv(DATA_DIR / "train.csv", parse_dates=[DATE_COL])
    test  = pd.read_csv(DATA_DIR / "test.csv",  parse_dates=[DATE_COL])
    train = train.sort_values([ENTITY_COL, DATE_COL]).reset_index(drop=True)
    test  = test.sort_values([ENTITY_COL, DATE_COL]).reset_index(drop=True)
    print(f"    Train: {len(train):,} rows | Test: {len(test):,} rows")
    print(f"    Cities: {train[ENTITY_COL].nunique()} train | {test[ENTITY_COL].nunique()} test")
    return train, test


# ---------------------------------------------------------------------------
# Model factory — defines how each model fits & predicts
# ---------------------------------------------------------------------------

def _make_models() -> list[dict]:
    """
    Return list of model config dicts with fit/predict callables.
    Each dict: {name, model (instance), requires_entity, features}
    """
    return [
        {
            "name":            PooledOLS.name,
            "instance":        PooledOLS(),
            "requires_entity": False,
            "features":        FEATURE_COLS, # Needs city_enc to be competitive
        },
        {
            "name":            LocalOLS.name,
            "instance":        LocalOLS(),
            "requires_entity": True,
            "features":        LAG_COLS,     # city_enc is constant per unit -> collinear
        },
        {
            "name":            FixedEffectsModel.name,
            "instance":        FixedEffectsModel(),
            "requires_entity": True,
            "features":        LAG_COLS,     # city dummies span city_enc -> collinear
        },
        {
            "name":            GlobalRidge.name,
            "instance":        GlobalRidge(),
            "requires_entity": False,
            "features":        FEATURE_COLS,
        },
        {
            "name":            LocalRidge.name,
            "instance":        LocalRidge(),
            "requires_entity": True,
            "features":        LAG_COLS,
        },
        {
            "name":            MixedEffectsModel.name,
            "instance":        MixedEffectsModel(),
            "requires_entity": True,
            "features":        LAG_COLS,     # Let model discover city intercepts via BLUP
        },
    ]


# ---------------------------------------------------------------------------
# Hold-out evaluation
# ---------------------------------------------------------------------------

def holdhout_evaluation(
    train: pd.DataFrame,
    test:  pd.DataFrame,
) -> dict[str, dict]:
    """
    Train all models on full train set, evaluate on hold-out test set.

    Returns
    -------
    {model_name: {"rmse": float, "mae": float, "errors": np.ndarray}}
    """
    print("\n" + "="*60)
    print("  Hold-out Test Evaluation")
    print("="*60)

    y_train    = train[TARGET_COL]
    eid_train  = train[ENTITY_COL]
    y_test     = test[TARGET_COL].values
    eid_test   = test[ENTITY_COL]

    results = {}
    model_configs = _make_models()

    for cfg in model_configs:
        name     = cfg["name"]
        model    = cfg["instance"]
        req_eid  = cfg["requires_entity"]
        feats    = cfg["features"]

        X_train_m = train[feats]
        X_test_m  = test[feats]

        print(f"\n  [{name}]")
        t0 = time.time()

        if req_eid:
            model.fit(X_train_m, y_train, eid_train)
            preds = model.predict(X_test_m, eid_test)
        else:
            model.fit(X_train_m, y_train)
            preds = model.predict(X_test_m)

        elapsed = time.time() - t0
        errors  = y_test - preds
        rmse    = compute_rmse(y_test, preds)
        mae     = compute_mae(y_test, preds)

        print(f"    RMSE = {rmse:.6f}  |  MAE = {mae:.6f}  |  t={elapsed:.1f}s")
        results[name] = {"rmse": rmse, "mae": mae, "errors": errors}

    return results


# ---------------------------------------------------------------------------
# Diebold-Mariano tests vs. baseline
# ---------------------------------------------------------------------------

def run_dm_tests(
    results:  dict[str, dict],
    baseline: str = PooledOLS.name,
) -> dict[str, dict]:
    """
    DM test: each model vs. Pooled OLS (baseline).
    Models with lower MSE loss than baseline have a negative DM stat
    (better_model == 'model_2' = challenger).
    """
    print("\n" + "="*60)
    print(f"  Diebold-Mariano Tests  (baseline: {baseline})")
    print("="*60)

    e_base = results[baseline]["errors"]
    dm_out = {}

    for name, res in results.items():
        if name == baseline:
            continue
        e_chal = res["errors"]
        # e1 = baseline errors, e2 = challenger errors
        dm = diebold_mariano_test(e_base, e_chal, h=1, loss="squared")
        dm_out[name] = dm
        sig = "*" if dm["significant"] else ""
        print(
            f"    {name:35s}  DM={dm['dm_stat']:+.3f}  "
            f"p={dm['p_value']:.4f} {sig}"
        )

    return dm_out


# ---------------------------------------------------------------------------
# Rolling-origin CV
# ---------------------------------------------------------------------------

def rolling_origin_cv(
    train: pd.DataFrame,
    n_splits: int = 5,
) -> dict[str, dict]:
    """
    Rolling-origin cross-validation on the training set.
    Returns aggregated stats per model.
    """
    print("\n" + "="*60)
    print(f"  Rolling-Origin CV  (n_splits={n_splits})")
    print("="*60)

    evaluator   = RollingOriginEvaluator(
        n_splits     = n_splits,
        feature_cols = FEATURE_COLS,
        target_col   = TARGET_COL,
        entity_col   = ENTITY_COL,
        date_col     = DATE_COL,
    )
    cv_results: dict[str, list] = {}
    model_configs = _make_models()

    for cfg in model_configs:
        name    = cfg["name"]
        req_eid = cfg["requires_entity"]
        feats   = cfg["features"]

        evaluator   = RollingOriginEvaluator(
            n_splits     = n_splits,
            feature_cols = feats, # Model-specific features
            target_col   = TARGET_COL,
            entity_col   = ENTITY_COL,
            date_col     = DATE_COL,
        )

        def fit_fn(X, y, eid, _req=req_eid, _cls=type(cfg["instance"])):
            m = _cls()
            if _req:
                m.fit(X, y, eid)
            else:
                m.fit(X, y)
            return m

        def predict_fn(m, X, eid, _req=req_eid):
            if _req:
                return m.predict(X, eid)
            return m.predict(X)

        folds = evaluator.evaluate(
            train,
            fit_fn     = fit_fn,
            predict_fn = predict_fn,
            model_name = name,
            verbose    = True,
        )
        agg  = evaluator.aggregate(folds)
        cv_results[name] = agg

        print(
            f"    {name:35s}  "
            f"RMSE={agg['rmse_mean']:.6f}±{agg['rmse_std']:.6f}  "
            f"MAE={agg['mae_mean']:.6f}±{agg['mae_std']:.6f}"
        )

    return cv_results


# ---------------------------------------------------------------------------
# Save report
# ---------------------------------------------------------------------------

def save_report(
    holdout_results: dict[str, dict],
    dm_results:      dict[str, dict],
    cv_results:      dict[str, dict],
) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "holdout": {
            k: {"rmse": v["rmse"], "mae": v["mae"]}
            for k, v in holdout_results.items()
        },
        "dm_tests":        dm_results,
        "rolling_origin_cv": cv_results,
    }
    out_path = REPORTS_DIR / "panel_results.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n[Pipeline] Report saved → {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_comparison_pipeline() -> dict:
    """
    Full model comparison pipeline.

    Returns
    -------
    dict with holdout_results, dm_results, cv_results, summary_df
    """
    print("=" * 60)
    print("  Panel Forecasting Comparison Pipeline")
    print("  Zillow Metro ZHVI  |  log_return target")
    print("=" * 60)

    train, test = load_data()

    # 1. Hold-out test evaluation
    holdout_results = holdhout_evaluation(train, test)

    # 2. Diebold-Mariano tests vs. Pooled OLS
    dm_results = run_dm_tests(holdout_results, baseline=PooledOLS.name)

    # 3. Summary table
    summary_df = summarize_results(holdout_results, dm_results)
    print("\n" + "=" * 60)
    print("  Hold-out Test Results Summary")
    print("=" * 60)
    print(summary_df.to_string())

    # 4. Rolling-origin CV
    cv_results = rolling_origin_cv(train, n_splits=5)

    # 5. Save report
    save_report(holdout_results, dm_results, cv_results)

    print("\n✅  Pipeline complete.\n")
    return {
        "holdout_results": holdout_results,
        "dm_results":      dm_results,
        "cv_results":      cv_results,
        "summary_df":      summary_df,
    }


if __name__ == "__main__":
    run_comparison_pipeline()

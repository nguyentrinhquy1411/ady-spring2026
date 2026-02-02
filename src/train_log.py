#!/usr/bin/env python3
"""
Training script with log-transformed target and advanced feature engineering.
Goal: Achieve R² > 70%
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from load_data import load_raw_data
from preprocess import split_data_time_based, preprocess_data
from models import MeanBaseline, OLSBaseline, RidgeBaseline, LassoBaseline
from evaluate import calculate_metrics, print_metrics
import pandas as pd
import numpy as np

def train_and_evaluate(model, X_train, y_train, X_test, y_test, model_name):
    """Train a model and evaluate on test set."""
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    metrics = calculate_metrics(y_test, y_pred, model_name)
    print_metrics(metrics)
    return metrics

def main():
    print("="*60)
    print("  Chicago Real Estate - Log-Transformed Target")
    print("  Goal: Achieve R² > 70%")
    print("="*60)
    
    # Load and prepare data
    print("\n[1/5] Loading data...")
    df = load_raw_data()
    
    # Split data
    print("\n[2/5] Splitting data (time-based)...")
    train_df, test_df = split_data_time_based(df, 'soldOn', train_ratio=0.7)
    
    # Log transform the target variable
    print("\n[3/5] Applying log transformation to target...")
    train_df['log_price'] = np.log1p(train_df['lastSoldPrice'])
    test_df['log_price'] = np.log1p(test_df['lastSoldPrice'])
    
    # Preprocess with polynomial features
    print("\n[4/5] Preprocessing with polynomial features...")
    train_df, test_df, scaler = preprocess_data(train_df, test_df, target_col='log_price', use_poly_features=True)
    
    # Prepare features and target
    meta_cols = ['soldOn', 'type', 'text', 'lastSoldPrice']  # Keep original price in meta
    target_col = 'log_price'
    feature_cols = [c for c in train_df.columns if c != target_col and c not in meta_cols]
    
    X_train = train_df[feature_cols]
    y_train_log = train_df[target_col]
    X_test = test_df[feature_cols]
    y_test_log = test_df[target_col]
    
    # Keep original prices for final evaluation
    y_train_orig = train_df['lastSoldPrice']
    y_test_orig = test_df['lastSoldPrice']
    
    print(f"\nDataset summary:")
    print(f"  Training samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")
    print(f"  Features: {len(feature_cols)}")
    
    # Train and evaluate models
    print("\n[5/5] Training models on log-transformed target...")
    print("\n" + "="*60)
    
    results = []
    
    # 1. Mean Baseline
    print("\n1. Mean Baseline (sanity check)")
    model = MeanBaseline()
    model.fit(X_train, y_train_log)
    y_pred_log = model.predict(X_test)
    y_pred = np.expm1(y_pred_log)  # Transform back to original scale
    metrics = calculate_metrics(y_test_orig, y_pred, "Mean Baseline")
    print_metrics(metrics)
    results.append(metrics)
    
    # 2. OLS Linear Regression
    print("\n2. Ordinary Least Squares")
    model = OLSBaseline()
    model.fit(X_train, y_train_log)
    y_pred_log = model.predict(X_test)
    y_pred = np.expm1(y_pred_log)
    metrics = calculate_metrics(y_test_orig, y_pred, "OLS Linear Regression")
    print_metrics(metrics)
    results.append(metrics)
    
    # 3. Ridge Regression
    print("\n3. Ridge Regression (optimized)")
    alphas = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0]
    model = RidgeBaseline(alphas=alphas)
    model.fit(X_train, y_train_log)
    y_pred_log = model.predict(X_test)
    y_pred = np.expm1(y_pred_log)
    metrics = calculate_metrics(y_test_orig, y_pred, "Ridge Regression")
    print_metrics(metrics)
    results.append(metrics)
    print(f"  Best alpha: {model.alpha_}")
    
    # 4. Lasso Regression
    print("\n4. Lasso Regression (optimized)")
    alphas = [0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
    model = LassoBaseline(alphas=alphas)
    model.fit(X_train, y_train_log)
    y_pred_log = model.predict(X_test)
    y_pred = np.expm1(y_pred_log)
    metrics = calculate_metrics(y_test_orig, y_pred, "Lasso Regression")
    print_metrics(metrics)
    results.append(metrics)
    print(f"  Best alpha: {model.alpha_}")
    
    # Summary
    print("\n" + "="*60)
    print("  FINAL RESULTS SUMMARY")
    print("="*60)
    
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('R2', ascending=False)
    
    print("\nRanked by R² Score:")
    print(results_df.to_string(index=False))
    
    best_model = results_df.iloc[0]
    print(f"\n{'='*60}")
    print(f"  BEST MODEL: {best_model['Model']}")
    print(f"  R² Score: {best_model['R2']:.4f} ({best_model['R2']*100:.2f}%)")
    
    if best_model['R2'] > 0.70:
        print(f"  ✓ SUCCESS: R² > 70% requirement MET!")
    else:
        print(f"  ✗ WARNING: R² < 70% requirement NOT met")
        print(f"  Need to improve by: {(0.70 - best_model['R2'])*100:.2f}%")
    
    print(f"{'='*60}\n")
    
    return results_df

if __name__ == "__main__":
    results = main()

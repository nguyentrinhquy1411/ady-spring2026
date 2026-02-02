#!/usr/bin/env python3
"""
Optimized training script with improved hyperparameters and feature engineering.
Goal: Achieve R² > 70%
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from load_data import load_raw_data
from preprocess import split_data_time_based, preprocess_data
from evaluate import calculate_metrics, print_metrics
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV
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
    print("  Chicago Real Estate - Optimized Training")
    print("  Goal: Achieve R² > 70%")
    print("="*60)
    
    # Load and prepare data
    print("\n[1/4] Loading data...")
    df = load_raw_data()
    
    # Split data
    print("\n[2/4] Splitting data (time-based)...")
    train_df, test_df = split_data_time_based(df, 'soldOn', train_ratio=0.7)
    
    # Preprocess
    print("\n[3/4] Preprocessing...")
    train_df, test_df, scaler = preprocess_data(train_df, test_df, target_col='lastSoldPrice')
    
    # Prepare features and target
    meta_cols = ['soldOn', 'type', 'text']
    target_col = 'lastSoldPrice'
    feature_cols = [c for c in train_df.columns if c != target_col and c not in meta_cols]
    
    X_train = train_df[feature_cols]
    y_train = train_df[target_col]
    X_test = test_df[feature_cols]
    y_test = test_df[target_col]
    
    print(f"\nDataset summary:")
    print(f"  Training samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")
    print(f"  Features: {len(feature_cols)}")
    
    # Train and evaluate optimized models
    print("\n[4/4] Training optimized models...")
    print("\n" + "="*60)
    
    results = []
    
    # 1. Optimized Random Forest with Grid Search
    print("\n1. Random Forest with GridSearchCV")
    print("  Searching for best hyperparameters...")
    
    param_grid = {
        'n_estimators': [200, 300],
        'max_depth': [20, 30, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2],
        'max_features': ['sqrt', 'log2']
    }
    
    rf = RandomForestRegressor(random_state=42, n_jobs=-1)
    grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='r2', n_jobs=-1, verbose=1)
    grid_search.fit(X_train, y_train)
    
    print(f"  Best params: {grid_search.best_params_}")
    print(f"  Best CV R²: {grid_search.best_score_:.4f}")
    
    y_pred = grid_search.predict(X_test)
    metrics = calculate_metrics(y_test, y_pred, "Random Forest (Optimized)")
    print_metrics(metrics)
    results.append(metrics)
    
    # 2. Optimized Gradient Boosting
    print("\n2. Gradient Boosting with GridSearchCV")
    print("  Searching for best hyperparameters...")
    
    param_grid_gb = {
        'n_estimators': [200, 300],
        'max_depth': [5, 7, 10],
        'learning_rate': [0.05, 0.1, 0.15],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    }
    
    gb = GradientBoostingRegressor(random_state=42)
    grid_search_gb = GridSearchCV(gb, param_grid_gb, cv=3, scoring='r2', n_jobs=-1, verbose=1)
    grid_search_gb.fit(X_train, y_train)
    
    print(f"  Best params: {grid_search_gb.best_params_}")
    print(f"  Best CV R²: {grid_search_gb.best_score_:.4f}")
    
    y_pred_gb = grid_search_gb.predict(X_test)
    metrics_gb = calculate_metrics(y_test, y_pred_gb, "Gradient Boosting (Optimized)")
    print_metrics(metrics_gb)
    results.append(metrics_gb)
    
    # Summary
    print("\n" + "="*60)
    print("  FINAL RESULTS")
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
    
    # Feature importance from best model
    if best_model['Model'] == "Random Forest (Optimized)":
        best_estimator = grid_search.best_estimator_
    else:
        best_estimator = grid_search_gb.best_estimator_
    
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': best_estimator.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    print(feature_importance.head(10).to_string(index=False))
    
    return results_df

if __name__ == "__main__":
    results = main()

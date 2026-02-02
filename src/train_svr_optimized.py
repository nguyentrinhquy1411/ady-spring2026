#!/usr/bin/env python3
"""
Test SVR with raw features (no polynomial) vs polynomial features.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from load_data import load_raw_data
from preprocess import split_data_time_based, preprocess_data
from models import SVRWrapper
from evaluate import calculate_metrics, print_metrics
import pandas as pd

print("="*60)
print("  SVR Performance Comparison")
print("  Testing with and without polynomial features")
print("="*60)

# Load and prepare data
df = load_raw_data()
train_df, test_df = split_data_time_based(df, 'soldOn', train_ratio=0.7)

# Test 1: SVR with polynomial features (current approach)
print("\n[Test 1] SVR with POLYNOMIAL features (31 features)")
train_poly, test_poly, _ = preprocess_data(train_df.copy(), test_df.copy(), 
                                           target_col='lastSoldPrice', 
                                           use_poly_features=True)

meta_cols = ['soldOn', 'type', 'text']
target_col = 'lastSoldPrice'
feature_cols_poly = [c for c in train_poly.columns if c != target_col and c not in meta_cols]

X_train_poly = train_poly[feature_cols_poly]
y_train = train_poly[target_col]
X_test_poly = test_poly[feature_cols_poly]
y_test = test_poly[target_col]

print(f"Features: {len(feature_cols_poly)}")

param_grid = {
    'C': [1, 10, 100],
    'epsilon': [0.01, 0.1, 1],
    'gamma': ['scale', 0.01, 0.1]
}
model_poly = SVRWrapper(kernel='rbf', param_grid=param_grid, cv=3)
model_poly.fit(X_train_poly, y_train)
y_pred_poly = model_poly.predict(X_test_poly)
metrics_poly = calculate_metrics(y_test, y_pred_poly, "SVR (RBF) with Polynomial")
print_metrics(metrics_poly)
print(f"Best params: {model_poly.best_params_}")

# Test 2: SVR with raw features only (no polynomial)
print("\n[Test 2] SVR with RAW features only (no polynomial)")
train_raw, test_raw, _ = preprocess_data(train_df.copy(), test_df.copy(), 
                                        target_col='lastSoldPrice', 
                                        use_poly_features=False)

feature_cols_raw = [c for c in train_raw.columns if c != target_col and c not in meta_cols]

X_train_raw = train_raw[feature_cols_raw]
X_test_raw = test_raw[feature_cols_raw]

print(f"Features: {len(feature_cols_raw)}")

model_raw = SVRWrapper(kernel='rbf', param_grid=param_grid, cv=3)
model_raw.fit(X_train_raw, y_train)
y_pred_raw = model_raw.predict(X_test_raw)
metrics_raw = calculate_metrics(y_test, y_pred_raw, "SVR (RBF) Raw Features")
print_metrics(metrics_raw)
print(f"Best params: {model_raw.best_params_}")

# Comparison
print("\n" + "="*60)
print("  COMPARISON")
print("="*60)
comparison = pd.DataFrame([metrics_poly, metrics_raw])
print(comparison.to_string(index=False))

improvement = metrics_raw['R2'] - metrics_poly['R2']
print(f"\nR² Improvement with raw features: {improvement:+.4f} ({improvement*100:+.2f}%)")

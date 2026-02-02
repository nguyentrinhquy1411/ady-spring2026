#!/usr/bin/env python3
"""
Test SVR with linear kernel vs RBF kernel.
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
print("  SVR Kernel Comparison")
print("  Testing Linear vs RBF kernel")
print("="*60)

# Load and prepare data
df = load_raw_data()
train_df, test_df = split_data_time_based(df, 'soldOn', train_ratio=0.7)

# Use polynomial features (since they work well for OLS)
train_df, test_df, _ = preprocess_data(train_df, test_df, 
                                       target_col='lastSoldPrice', 
                                       use_poly_features=True)

meta_cols = ['soldOn', 'type', 'text']
target_col = 'lastSoldPrice'
feature_cols = [c for c in train_df.columns if c != target_col and c not in meta_cols]

X_train = train_df[feature_cols]
y_train = train_df[target_col]
X_test = test_df[feature_cols]
y_test = test_df[target_col]

print(f"\nDataset: {len(X_train)} train, {len(X_test)} test, {len(feature_cols)} features")

# Test 1: SVR with Linear kernel
print("\n[Test 1] SVR with LINEAR kernel")
param_grid_linear = {
    'C': [0.1, 1, 10, 100],
    'epsilon': [0.01, 0.1, 1]
}
model_linear = SVRWrapper(kernel='linear', param_grid=param_grid_linear, cv=3)
model_linear.fit(X_train, y_train)
y_pred_linear = model_linear.predict(X_test)
metrics_linear = calculate_metrics(y_test, y_pred_linear, "SVR (Linear)")
print_metrics(metrics_linear)
print(f"Best params: {model_linear.best_params_}")

# Test 2: SVR with RBF kernel
print("\n[Test 2] SVR with RBF kernel")
param_grid_rbf = {
    'C': [1, 10, 100],
    'epsilon': [0.01, 0.1, 1],
    'gamma': ['scale', 0.01, 0.1]
}
model_rbf = SVRWrapper(kernel='rbf', param_grid=param_grid_rbf, cv=3)
model_rbf.fit(X_train, y_train)
y_pred_rbf = model_rbf.predict(X_test)
metrics_rbf = calculate_metrics(y_test, y_pred_rbf, "SVR (RBF)")
print_metrics(metrics_rbf)
print(f"Best params: {model_rbf.best_params_}")

# Comparison
print("\n" + "="*60)
print("  COMPARISON")
print("="*60)
comparison = pd.DataFrame([metrics_linear, metrics_rbf])
print(comparison.to_string(index=False))

if metrics_linear['R2'] > metrics_rbf['R2']:
    print(f"\n✓ Linear kernel is better by {(metrics_linear['R2'] - metrics_rbf['R2'])*100:.2f}%")
else:
    print(f"\n✓ RBF kernel is better by {(metrics_rbf['R2'] - metrics_linear['R2'])*100:.2f}%")

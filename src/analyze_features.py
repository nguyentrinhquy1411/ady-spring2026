#!/usr/bin/env python3
"""
Analyze feature importance to guide feature selection.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from load_data import load_raw_data
from preprocess import split_data_time_based, preprocess_data
from models import OLSBaseline
import pandas as pd
import numpy as np

# Load and prepare data
df = load_raw_data()
train_df, test_df = split_data_time_based(df, 'soldOn', train_ratio=0.7)
train_df, test_df, scaler = preprocess_data(train_df, test_df, target_col='lastSoldPrice', use_poly_features=True)

# Get features
meta_cols = ['soldOn', 'type', 'text']
target_col = 'lastSoldPrice'
feature_cols = [c for c in train_df.columns if c != target_col and c not in meta_cols]

X_train = train_df[feature_cols]
y_train = train_df[target_col]

# Train OLS to get coefficients
model = OLSBaseline()
model.fit(X_train, y_train)

# Get feature importance (absolute coefficients)
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'coefficient': model.coef_,
    'abs_coefficient': np.abs(model.coef_)
}).sort_values('abs_coefficient', ascending=False)

print("="*70)
print("FEATURE IMPORTANCE ANALYSIS (OLS Coefficients)")
print("="*70)
print("\nTop 20 Most Important Features:")
print(feature_importance.head(20).to_string(index=False))

print("\n\nBottom 10 Least Important Features:")
print(feature_importance.tail(10).to_string(index=False))

# Correlation with target
correlations = pd.DataFrame({
    'feature': feature_cols,
    'correlation': [train_df[feat].corr(y_train) for feat in feature_cols]
})
correlations['abs_correlation'] = correlations['correlation'].abs()
correlations = correlations.sort_values('abs_correlation', ascending=False)

print("\n\n" + "="*70)
print("FEATURE CORRELATION WITH TARGET")
print("="*70)
print("\nTop 20 Most Correlated Features:")
print(correlations.head(20).to_string(index=False))

print("\n\nFeatures with near-zero correlation (candidates for removal):")
print(correlations[correlations['abs_correlation'] < 0.05].to_string(index=False))

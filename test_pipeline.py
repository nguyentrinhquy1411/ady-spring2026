#!/usr/bin/env python3
"""Test the data loading and preprocessing pipeline."""

from src.load_data import load_raw_data
from src.preprocess import split_data_time_based, preprocess_data

print('Testing data loading pipeline...\n')

# Load data
df = load_raw_data()
print(f'\n✓ Loaded {len(df)} records')
print(f'  Columns: {list(df.columns)[:10]}...')

# Split data
train_df, test_df = split_data_time_based(df, 'soldOn', train_ratio=0.7)

# Preprocess
train_df, test_df, scaler = preprocess_data(train_df, test_df, target_col='lastSoldPrice')

# Get features and target
meta_cols = ['soldOn', 'type', 'text']
target_col = 'lastSoldPrice'
feature_cols = [c for c in train_df.columns if c != target_col and c not in meta_cols]

X_train = train_df[feature_cols]
y_train = train_df[target_col]
X_test = test_df[feature_cols]
y_test = test_df[target_col]

print(f'\n✓ Data pipeline complete!')
print(f'  X_train shape: {X_train.shape}')
print(f'  X_test shape: {X_test.shape}')
print(f'  y_train range: ${y_train.min():,.0f} - ${y_train.max():,.0f}')
print(f'  y_test range: ${y_test.min():,.0f} - ${y_test.max():,.0f}')
print(f'\n  Feature columns ({len(feature_cols)}):')
for i, col in enumerate(feature_cols, 1):
    print(f'    {i}. {col}')

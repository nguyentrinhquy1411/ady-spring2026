import pandas as pd
from sklearn.preprocessing import StandardScaler
from typing import Tuple

def split_data_time_based(df: pd.DataFrame, time_col: str = 'period_id', train_ratio: float = 0.7) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split data based on time column (Protocol B).
    Sort by time_col, then take first train_ratio as train, rest as test.
    """
    # Ensure sorted by time
    df_sorted = df.sort_values(by=time_col).reset_index(drop=True)
    
    # Calculate split index
    n_train = int(len(df_sorted) * train_ratio)
    
    train_df = df_sorted.iloc[:n_train].copy()
    test_df = df_sorted.iloc[n_train:].copy()
    
    return train_df, test_df

def preprocess_data(train_df: pd.DataFrame, test_df: pd.DataFrame, target_col: str = 'hpi_metro_nsa', meta_cols: list = None) -> Tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """
    Apply StandardScaler to features (excluding target and meta columns).
    Fit on train, transform train and test.
    """
    if meta_cols is None:
        meta_cols = ['year', 'quarter', 'metro_name', 'period_id']

    # Identify feature columns (all non-target, non-meta numericals)
    feature_cols = [c for c in train_df.columns if c != target_col and c not in meta_cols]
    
    # Simple imputation for NaNs before scaling (Mean fill) - Robustness step
    # Important because lags often introduce NaNs at the start
    for col in feature_cols:
        if train_df[col].dtype in ['float64', 'int64']:
             mean_val = train_df[col].mean()
             train_df[col] = train_df[col].fillna(mean_val)
             test_df[col] = test_df[col].fillna(mean_val)

    scaler = StandardScaler()
    
    # Fit on train features
    train_df[feature_cols] = scaler.fit_transform(train_df[feature_cols])
    
    # Transform test features
    test_df[feature_cols] = scaler.transform(test_df[feature_cols])
    
    return train_df, test_df, scaler

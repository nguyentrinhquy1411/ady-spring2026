import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Tuple

def split_data_time_based(df: pd.DataFrame, time_col: str = 'soldOn', train_ratio: float = 0.7) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split data based on time column (chronological split).
    Sort by time_col, then take first train_ratio as train, rest as test.
    
    Args:
        df: DataFrame with time column
        time_col: Name of datetime column to split on (default: 'soldOn')
        train_ratio: Ratio of data to use for training (default: 0.7)
    
    Returns:
        train_df, test_df: Split DataFrames
    """
    # Ensure sorted by time
    df_sorted = df.sort_values(by=time_col).reset_index(drop=True)
    
    # Calculate split index
    n_train = int(len(df_sorted) * train_ratio)
    
    train_df = df_sorted.iloc[:n_train].copy()
    test_df = df_sorted.iloc[n_train:].copy()
    
    print(f"Time-based split:")
    print(f"  Train: {len(train_df)} samples ({train_df[time_col].min()} to {train_df[time_col].max()})")
    print(f"  Test:  {len(test_df)} samples ({test_df[time_col].min()} to {test_df[time_col].max()})")
    
    return train_df, test_df

def preprocess_data(train_df: pd.DataFrame, test_df: pd.DataFrame, target_col: str = 'lastSoldPrice', meta_cols: list = None, use_poly_features: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """
    Apply feature engineering and StandardScaler to features.
    Fit on train, transform train and test.
    
    Args:
        train_df: Training DataFrame
        test_df: Test DataFrame
        target_col: Name of target column (default: 'lastSoldPrice')
        meta_cols: List of metadata columns to exclude from scaling
        use_poly_features: Whether to add polynomial and interaction features
    
    Returns:
        train_df, test_df, scaler: Preprocessed DataFrames and fitted scaler
    """
    if meta_cols is None:
        meta_cols = ['soldOn', 'type', 'text']

    # Additional feature engineering
    for df in [train_df, test_df]:
        # Bathroom-related features
        if 'baths_full' in df.columns and 'baths_half' in df.columns:
            df['total_baths'] = df['baths_full'].fillna(0) + df['baths_half'].fillna(0) * 0.5
        
        # Price per sqft (only for analysis, not as a feature to avoid leakage)
        # Sqft per bedroom ratio
        if 'sqft' in df.columns and 'beds' in df.columns:
            df['sqft_per_bed'] = df['sqft'] / df['beds'].replace(0, np.nan)
        
        # Lot size features
        if 'lot_sqft' in df.columns and 'sqft' in df.columns:
            df['lot_to_building_ratio'] = df['lot_sqft'] / df['sqft'].replace(0, np.nan)

    # Identify feature columns (all non-target, non-meta numericals)
    feature_cols = [c for c in train_df.columns 
                   if c != target_col 
                   and c not in meta_cols 
                   and train_df[c].dtype in ['float64', 'int64', 'bool']]
    
    # Imputation for NaNs before scaling (Median fill for robustness to outliers)
    for col in feature_cols:
        median_val = train_df[col].median()
        train_df[col] = train_df[col].fillna(median_val)
        test_df[col] = test_df[col].fillna(median_val)
    
    # Add polynomial and interaction features for linear models
    if use_poly_features:
        print("  Adding polynomial and interaction features...")
        
        # Select key numerical features for polynomial expansion
        key_features = ['sqft', 'beds', 'baths', 'property_age', 'lot_sqft', 'garage']
        available_key_features = [f for f in key_features if f in feature_cols]
        
        for df in [train_df, test_df]:
            # Polynomial features (squared terms for key features)
            for feat in available_key_features:
                df[f'{feat}_squared'] = df[feat] ** 2
            
            # Important interaction terms
            if 'sqft' in df.columns and 'beds' in df.columns:
                df['sqft_x_beds'] = df['sqft'] * df['beds']
            
            if 'sqft' in df.columns and 'property_age' in df.columns:
                df['sqft_x_age'] = df['sqft'] * df['property_age']
            
            if 'beds' in df.columns and 'baths' in df.columns:
                df['beds_x_baths'] = df['beds'] * df['baths']
            
            if 'lot_sqft' in df.columns and 'sqft' in df.columns:
                df['lot_x_building'] = df['lot_sqft'] * df['sqft']
        
        # Update feature columns list
        feature_cols = [c for c in train_df.columns 
                       if c != target_col 
                       and c not in meta_cols 
                       and train_df[c].dtype in ['float64', 'int64', 'bool']]

    scaler = StandardScaler()
    
    # Fit on train features
    train_df[feature_cols] = scaler.fit_transform(train_df[feature_cols])
    
    # Transform test features
    test_df[feature_cols] = scaler.transform(test_df[feature_cols])
    
    print(f"\nPreprocessing complete:")
    print(f"  Features: {len(feature_cols)}")
    print(f"  Feature names (first 10): {feature_cols[:10]}...")
    
    return train_df, test_df, scaler

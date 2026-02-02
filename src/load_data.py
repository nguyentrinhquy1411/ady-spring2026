import pandas as pd
import numpy as np
import os
from datetime import datetime

def load_raw_data(filepath: str = 'data/raw/real_estate_data_chicago.csv') -> pd.DataFrame:
    """
    Load Chicago real estate data and prepare features/target.
    
    Target: lastSoldPrice (actual sold price)
    Features: year_built, beds, baths, sqft, lot_sqft, garage, stories, property type
    Time column: soldOn (date of sale)
    """
    # Support running from different directories
    if not os.path.exists(filepath):
        if os.path.exists(f"../{filepath}"):
            filepath = f"../{filepath}"
    
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found at {filepath}")

    # Filter to only properties with sale data (soldOn and lastSoldPrice)
    df = df[df['soldOn'].notna() & df['lastSoldPrice'].notna()].copy()
    
    # Parse soldOn as datetime
    df['soldOn'] = pd.to_datetime(df['soldOn'])
    
    # Extract time features
    df['sale_year'] = df['soldOn'].dt.year
    df['sale_month'] = df['soldOn'].dt.month
    df['sale_quarter'] = df['soldOn'].dt.quarter
    
    # Feature engineering: property age at time of sale
    df['property_age'] = df['sale_year'] - df['year_built']
    # Handle cases where year_built is missing or invalid
    df.loc[df['property_age'] < 0, 'property_age'] = np.nan
    df.loc[df['property_age'] > 150, 'property_age'] = np.nan  # More reasonable threshold
    
    # Feature engineering: price per sqft (will be calculated after we have the data)
    # We'll add this as a derived feature but not use it as input to avoid leakage
    
    # One-hot encode property type
    type_dummies = pd.get_dummies(df['type'], prefix='type', drop_first=True)
    df = pd.concat([df, type_dummies], axis=1)
    
    # Define feature columns
    base_feature_cols = [
        'year_built', 'beds', 'baths', 'baths_full', 'baths_half',
        'garage', 'lot_sqft', 'sqft', 'stories', 'property_age',
        'sale_year', 'sale_month', 'sale_quarter'
    ]
    
    # Add property type dummy columns
    type_cols = [col for col in df.columns if col.startswith('type_')]
    feature_cols = base_feature_cols + type_cols
    
    # Target column
    target_col = 'lastSoldPrice'
    
    # Metadata columns
    meta_cols = ['soldOn', 'type', 'text']
    
    # Select only available columns
    available_features = [c for c in feature_cols if c in df.columns]
    cols_to_keep = meta_cols + available_features + [target_col]
    available_cols = [c for c in cols_to_keep if c in df.columns]
    
    # Sort by soldOn for time-based splitting
    df = df.sort_values('soldOn').reset_index(drop=True)
    
    return df[available_cols]

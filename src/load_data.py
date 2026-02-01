import pandas as pd
import os

def load_raw_data(filepath: str = 'data/raw/hpi_master_research_features.csv') -> pd.DataFrame:
    """
    Load data from HPI CSV and prepare features/target.
    
    Target: hpi_metro_nsa (using Non-Seasonally Adjusted as default target)
    Features (X): hpi_lag_1..8, qoq_growth, yoy_growth, etc.
    Meta: year, quarter, metro_name
    """
    if not os.path.join(os.getcwd(), filepath) and not os.path.exists(filepath):
         # Try absolute path check or relative
         pass

    # Support running from different directories
    if not os.path.exists(filepath):
         if os.path.exists(f"../{filepath}"):
             filepath = f"../{filepath}"
    
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found at {filepath}")

    # Basic cleaning
    # Create a sortable time index
    df['period_id'] = df['year'] + df['quarter'] / 4.0
    
    # Select candidate features
    # Based on file preview: hpi_lag_*, growth metrics
    feature_cols = [
        'hpi_lag_1', 'hpi_lag_2', 'hpi_lag_4', 
        'qoq_growth', 'yoy_growth', 'volatility_4q',
        'metro_to_state_ratio'
    ]
    target_col = 'hpi_metro_nsa'
    meta_cols = ['year', 'quarter', 'metro_name', 'period_id']
    
    # Allow passing through but ensure we have what we need
    # Filter only rows where target is not null
    df = df.dropna(subset=[target_col])
    
    # We might want to fill NaNs in features or drop them. 
    # For simplicity in this 'load' step, we pass them through, 
    # but let's at least select relevant columns to avoid noise.
    
    cols_to_keep = meta_cols + feature_cols + [target_col]
    
    # Check if columns exist
    available_cols = [c for c in cols_to_keep if c in df.columns]
    
    return df[available_cols]

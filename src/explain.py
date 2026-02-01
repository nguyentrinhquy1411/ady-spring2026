import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.inspection import permutation_importance
from typing import Dict, Any

def get_linear_coefficients(model: Any, feature_names: list) -> pd.DataFrame:
    """
    Extract coefficients from linear model.
    """
    if hasattr(model, 'coef_'):
        coefs = model.coef_
        # Handle if coef_ is 1D or 2D
        if coefs.ndim > 1:
            coefs = coefs.ravel()
            
        df_coef = pd.DataFrame({
            'Feature': feature_names,
            'Coefficient': coefs,
            'AbsCoefficient': np.abs(coefs)
        }).sort_values(by='AbsCoefficient', ascending=False)
        return df_coef
    else:
        raise ValueError("Model has no 'coef_' attribute.")

def what_if_analysis(model: Any, input_row: pd.DataFrame, changes: Dict[str, float]) -> Dict[str, Any]:
    """
    Predict original, apply changes to input features, predict new.
    Returns delta.
    
    changes: dict of {feature: delta_value_scaled} or absolute value? 
    Assuming input_row is already scaled, changes should be in scaled units roughly, 
    or we should handle scaling. For simplicity here, we assume input_row is ready for model.
    """
    # Original prediction
    pred_orig = model.predict(input_row)[0]
    
    # Modified input
    input_mod = input_row.copy()
    for feat, delta in changes.items():
        if feat in input_mod.columns:
            input_mod[feat] += delta
            
    pred_new = model.predict(input_mod)[0]
    
    return {
        "original_prediction": pred_orig,
        "new_prediction": pred_new,
        "delta": pred_new - pred_orig,
        "changes": changes
    }

def calculate_permutation_importance(model: Any, X_val: pd.DataFrame, y_val: pd.Series, n_repeats=10) -> pd.DataFrame:
    """
    Calculate permutation importance for black-box models (SVR).
    """
    result = permutation_importance(model, X_val, y_val, n_repeats=n_repeats, random_state=42, n_jobs=-1)
    
    df_imp = pd.DataFrame({
        'Feature': X_val.columns,
        'Importance': result.importances_mean,
        'Std': result.importances_std
    }).sort_values(by='Importance', ascending=False)
    
    return df_imp

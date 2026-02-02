from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import pandas as pd

def calculate_metrics(y_true, y_pred, model_name="Model"):
    """
    Calculate MAE, RMSE, R2, and MAPE.
    Returns a dictionary of metrics.
    """
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    
    # MAPE (Mean Absolute Percentage Error)
    # Avoid division by zero
    mask = y_true != 0
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100 if mask.sum() > 0 else np.nan
    
    return {
        "Model": model_name,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
        "MAPE": mape
    }

def print_metrics(metrics):
    """Print metrics with clear formatting and R² highlighting."""
    print(f"\n{'='*50}")
    print(f"  {metrics['Model']}")
    print(f"{'='*50}")
    print(f"  MAE:   ${metrics['MAE']:,.2f}")
    print(f"  RMSE:  ${metrics['RMSE']:,.2f}")
    print(f"  MAPE:  {metrics['MAPE']:.2f}%")
    print(f"  {'─'*46}")
    
    # Highlight R² score
    r2_status = "✓ PASS" if metrics['R2'] > 0.70 else "✗ FAIL"
    print(f"  R² Score: {metrics['R2']:.4f} ({metrics['R2']*100:.2f}%) {r2_status}")
    print(f"{'='*50}\n")


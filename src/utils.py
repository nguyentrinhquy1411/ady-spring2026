import pandas as pd
import numpy as np
from typing import Dict, List, Union

class ExtrapolationGuard:
    """
    Checks if input data falls outside the min-max range of the training data.
    """
    def __init__(self):
        self.bounds = {}

    def fit(self, X_train: pd.DataFrame):
        """
        Learn min/max for each feature in X_train.
        """
        for col in X_train.columns:
            self.bounds[col] = {
                'min': X_train[col].min(),
                'max': X_train[col].max()
            }
        return self

    def check(self, X_input: Union[pd.DataFrame, Dict]) -> List[str]:
        """
        Check if input is within bounds. Returns list of warning messages.
        """
        warnings = []
        
        # Convert dict to DataFrame if needed
        if isinstance(X_input, dict):
            X_input = pd.DataFrame([X_input])
            
        for col, limits in self.bounds.items():
            if col not in X_input.columns:
                continue
                
            col_min = limits['min']
            col_max = limits['max']
            
            # Check for values below min
            if (X_input[col] < col_min).any():
                warnings.append(f"Feature '{col}' value is below training range [{col_min:.4f}, {col_max:.4f}]")
                
            # Check for values above max
            if (X_input[col] > col_max).any():
                warnings.append(f"Feature '{col}' value is above training range [{col_min:.4f}, {col_max:.4f}]")
                
        return warnings

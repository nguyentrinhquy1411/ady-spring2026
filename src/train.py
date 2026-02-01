import pandas as pd
import numpy as np
from typing import Dict, Any
from evaluate import calculate_metrics, print_metrics

def train_and_evaluate(model: Any, X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series, model_name: str, verbose: bool = True) -> Dict[str, Any]:
    """
    Train a model and evaluate on test set.
    Returns metrics dictionary.
    """
    if verbose:
        print(f"Training {model_name}...")
        
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    metrics = calculate_metrics(y_test, y_pred, model_name)
    
    if verbose:
        print_metrics(metrics)
        
    return metrics

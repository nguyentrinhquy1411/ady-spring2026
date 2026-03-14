import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
from pathlib import Path

def evaluate_model(name, y_true, y_pred, price_true=None, price_pred=None):
    log_mae = mean_absolute_error(y_true, y_pred)
    log_rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    log_r2 = r2_score(y_true, y_pred)
    
    print(f"[{name}] log_return - MAE: {log_mae:.6f} | RMSE: {log_rmse:.6f} | R2: {log_r2:.6f}")
    
    if price_true is not None and price_pred is not None:
        price_mae = mean_absolute_error(price_true, price_pred)
        price_rmse = np.sqrt(mean_squared_error(price_true, price_pred))
        price_r2 = r2_score(price_true, price_pred)
        print(f"[{name}] Price Space - MAE: ${price_mae:,.2f} | RMSE: ${price_rmse:,.2f} | R2: {price_r2:.6f}")
    print("-" * 60)

def main():
    # Resolve paths reliably
    current_path = Path(__file__).resolve()
    base_dir = current_path.parent.parent if current_path.parent.name == 'src' else Path.cwd()
    data_dir = base_dir / 'data' / 'processed'
    assets_dir = base_dir / 'assets'
    assets_dir.mkdir(parents=True, exist_ok=True)

    train_path = data_dir / 'train.csv'
    test_path = data_dir / 'test.csv'

    print(f"Loading data from {data_dir}...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    # Ensure chronological order
    train_df['date'] = pd.to_datetime(train_df['date'])
    test_df['date'] = pd.to_datetime(test_df['date'])
    train_df = train_df.sort_values(['RegionID', 'date']).reset_index(drop=True)
    test_df = test_df.sort_values(['RegionID', 'date']).reset_index(drop=True)

    features = ['lag_1', 'lag_2', 'lag_3', 'lag_6', 'lag_12', 'city_enc']
    target = 'log_return'

    # ==========================
    # 1. Leakage Audit
    # ==========================
    print("--- Leakage Audit ---")
    correlations = train_df[features + [target]].corr()[target].drop(target)
    for feat, corr in correlations.items():
        print(f"Correlation between {feat} and {target}: {corr:.4f}")
        if abs(corr) > 0.9:
            print(f"WARNING: High correlation detected for {feat} (> 0.9)!")
    print("-" * 60)

    # Train/Val split for LightGBM
    unique_dates = train_df['date'].sort_values().unique()
    split_idx = int(len(unique_dates) * 0.85)
    split_date = unique_dates[split_idx]

    train_sub = train_df[train_df['date'] < split_date]
    val_sub = train_df[train_df['date'] >= split_date]

    X_train = train_df[features]
    y_train = train_df[target]
    
    X_train_sub = train_sub[features]
    y_train_sub = train_sub[target]
    X_val = val_sub[features]
    y_val = val_sub[target]

    X_test = test_df[features]
    y_test = test_df[target]

    # Pre-calculate previous prices for inverse transforms
    # Price_{t-1} = Price_t / exp(actual_log_return_t)
    test_df['price_prev'] = test_df['price'] / np.exp(test_df['log_return'])
    price_true = test_df['price']

    # Scaler for Regression and LightGBM models
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ==========================
    # 2. Smart Baseline (Zero Growth)
    # ==========================
    # Assumes no change -> predicted log_return = 0
    zero_preds_test = np.zeros(len(test_df))
    zero_price_pred = test_df['price_prev'] * np.exp(zero_preds_test)
    evaluate_model("Smart Baseline (Zero Growth)", y_test, zero_preds_test, price_true, zero_price_pred)

    # ==========================
    # 3. Ridge Regression
    # ==========================
    print("Training Ridge Regression...")
    ridge = Ridge(random_state=42)
    param_grid = {'alpha': [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]}
    tscv = TimeSeriesSplit(n_splits=5)
    
    grid_search = GridSearchCV(
        estimator=ridge, 
        param_grid=param_grid, 
        cv=tscv, 
        scoring='neg_mean_absolute_error', 
        n_jobs=-1
    )
    grid_search.fit(X_train_scaled, y_train)
    best_ridge = grid_search.best_estimator_
    print(f"Best Ridge Alpha: {best_ridge.alpha}")

    ridge_preds_test = best_ridge.predict(X_test_scaled)
    ridge_price_pred = test_df['price_prev'] * np.exp(ridge_preds_test)
    evaluate_model("Ridge Regression", y_test, ridge_preds_test, price_true, ridge_price_pred)

    # ==========================
    # 4. LightGBM
    # ==========================
    print("Training LightGBM...")
    # Rescale sub-training and validation sets
    lgb_scaler = StandardScaler()
    X_train_sub_scaled = lgb_scaler.fit_transform(X_train_sub)
    X_val_scaled = lgb_scaler.transform(X_val)
    X_test_scaled_lgb = lgb_scaler.transform(X_test)
    
    lgb_model = lgb.LGBMRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        random_state=42
    )
    callbacks = [lgb.early_stopping(stopping_rounds=50, verbose=False)]
    
    lgb_model.fit(
        X_train_sub_scaled, y_train_sub,
        eval_set=[(X_val_scaled, y_val)],
        eval_metric='l2',
        callbacks=callbacks
    )

    lgb_preds_test = lgb_model.predict(X_test_scaled_lgb)
    lgb_price_pred = test_df['price_prev'] * np.exp(lgb_preds_test)
    evaluate_model("LightGBM", y_test, lgb_preds_test, price_true, lgb_price_pred)

if __name__ == "__main__":
    main()

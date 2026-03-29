import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import os
# ── Paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # ADY2026/
DATA_DIR     = PROJECT_ROOT / "data" / "processed"
VIZ_DIR      = PROJECT_ROOT / "visualizations"

def plot_presentation_visuals(results_dict, test_df, price_true):
    VIZ_DIR.mkdir(exist_ok=True)
    
    models = list(results_dict.keys())
    
    # 1. Plot True vs Predicted Log-Return
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    sample_idx = np.random.choice(len(test_df), min(10000, len(test_df)), replace=False)
    
    for i, model in enumerate(models):
        y_pred = results_dict[model]['log_pred']
        axes[i].scatter(test_df['log_return'].iloc[sample_idx], y_pred[sample_idx], alpha=0.2, s=8, color='royalblue')
        
        min_val = min(test_df['log_return'].min(), y_pred.min())
        max_val = max(test_df['log_return'].max(), y_pred.max())
        axes[i].plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
        
        axes[i].set_title(f"{model}\nR2: {results_dict[model]['log_r2']:.4f}")
        axes[i].set_xlabel("True Log-Return")
        if i == 0: axes[i].set_ylabel("Predicted Log-Return")
        axes[i].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(VIZ_DIR / 'presentation_log_return_scatter.png', dpi=300)
    plt.close()
    
    # 2. Plot True vs Predicted Price
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    
    for i, model in enumerate(models):
        p_pred = results_dict[model]['price_pred']
        axes[i].scatter(price_true.iloc[sample_idx], p_pred.iloc[sample_idx], alpha=0.2, s=8, color='seagreen')
        
        min_val = min(price_true.min(), p_pred.min())
        max_val = max(price_true.max(), p_pred.max())
        axes[i].plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
        
        # Formatting X and Y to thousands/millions
        axes[i].ticklabel_format(style='plain', axis='both')
        axes[i].set_title(f"{model}\nPrice R2: {results_dict[model]['price_r2']:.4f}")
        axes[i].set_xlabel("True Price ($)")
        if i == 0: axes[i].set_ylabel("Predicted Price ($)")
        axes[i].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(VIZ_DIR / 'presentation_price_scatter.png', dpi=300)
    plt.close()

    # 3. Bar Chart comparison of MAE in Price Space
    plt.figure(figsize=(10, 6))
    maes = [results_dict[model]['price_mae'] for model in models]
    g = sns.barplot(x=models, y=maes, hue=models, palette='viridis', legend=False)
    plt.title("Mean Absolute Error (MAE) by Model in Price Space")
    plt.ylabel("Mean Absolute Error ($)")
    
    for i, v in enumerate(maes):
        g.text(i, v + max(maes)*0.01, f"${v:,.0f}", ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / 'presentation_price_mae_barchart.png', dpi=300)
    plt.close()
    print(f"Presentation plots saved in '{VIZ_DIR}' folder.")

def get_metrics(y_true, y_pred):
    return {
        'mae': mean_absolute_error(y_true, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'r2': r2_score(y_true, y_pred)
    }

def main():
    train_path = DATA_DIR / 'train.csv'
    test_path  = DATA_DIR / 'test.csv'

    print(f"Loading data from {DATA_DIR}...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    # Ensure chronological order
    train_df['date'] = pd.to_datetime(train_df['date'])
    test_df['date'] = pd.to_datetime(test_df['date'])
    train_df = train_df.sort_values(['RegionID', 'date']).reset_index(drop=True)
    test_df = test_df.sort_values(['RegionID', 'date']).reset_index(drop=True)

    features = ['lag_1', 'lag_2', 'lag_3', 'lag_6', 'lag_12', 'city_enc']
    target = 'log_return'

    # Pre-calculate previous prices for inverse transforms
    test_df['price_prev'] = test_df['price'] / np.exp(test_df['log_return'])
    price_true = test_df['price']

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

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    results_dict = {}

    # 1. Smart Baseline
    print("Running Baseline...")
    zero_preds_test = np.zeros(len(test_df))
    zero_price_pred = test_df['price_prev'] * np.exp(zero_preds_test)
    log_metrics = get_metrics(y_test, zero_preds_test)
    price_metrics = get_metrics(price_true, zero_price_pred)
    results_dict['Baseline'] = {
        'log_pred': zero_preds_test, 'price_pred': zero_price_pred,
        'log_r2': log_metrics['r2'], 'price_r2': price_metrics['r2'], 'price_mae': price_metrics['mae']
    }

    # 2. OLS
    print("Running OLS...")
    ols = LinearRegression()
    ols.fit(X_train_scaled, y_train)
    ols_preds = ols.predict(X_test_scaled)
    ols_price = test_df['price_prev'] * np.exp(ols_preds)
    log_metrics = get_metrics(y_test, ols_preds)
    price_metrics = get_metrics(price_true, ols_price)
    results_dict['OLS'] = {
        'log_pred': ols_preds, 'price_pred': ols_price,
        'log_r2': log_metrics['r2'], 'price_r2': price_metrics['r2'], 'price_mae': price_metrics['mae']
    }

    # 3. Ridge (with CV)
    print("Running Ridge CV...")
    ridge = Ridge(random_state=42)
    param_grid = {'alpha': [0.01, 0.1, 1.0, 10.0, 100.0]}
    tscv = TimeSeriesSplit(n_splits=5)
    grid_search = GridSearchCV(ridge, param_grid, cv=tscv, scoring='neg_mean_absolute_error', n_jobs=-1)
    grid_search.fit(X_train_scaled, y_train)
    best_ridge = grid_search.best_estimator_
    
    ridge_preds = best_ridge.predict(X_test_scaled)
    ridge_price = test_df['price_prev'] * np.exp(ridge_preds)
    log_metrics = get_metrics(y_test, ridge_preds)
    price_metrics = get_metrics(price_true, ridge_price)
    results_dict['Ridge'] = {
        'log_pred': ridge_preds, 'price_pred': ridge_price,
        'log_r2': log_metrics['r2'], 'price_r2': price_metrics['r2'], 'price_mae': price_metrics['mae']
    }

    # 4. LightGBM
    print("Running LightGBM...")
    lgb_scaler = StandardScaler()
    X_train_sub_scaled = lgb_scaler.fit_transform(X_train_sub)
    X_val_scaled = lgb_scaler.transform(X_val)
    X_test_scaled_lgb = lgb_scaler.transform(X_test)
    
    lgb_model = lgb.LGBMRegressor(n_estimators=1000, learning_rate=0.05, random_state=42)
    callbacks = [lgb.early_stopping(stopping_rounds=50, verbose=False)]
    lgb_model.fit(
        X_train_sub_scaled, y_train_sub,
        eval_set=[(X_val_scaled, y_val)],
        eval_metric='l2',
        callbacks=callbacks
    )
    lgb_preds = lgb_model.predict(X_test_scaled_lgb)
    lgb_price = test_df['price_prev'] * np.exp(lgb_preds)
    log_metrics = get_metrics(y_test, lgb_preds)
    price_metrics = get_metrics(price_true, lgb_price)
    results_dict['LightGBM'] = {
        'log_pred': lgb_preds, 'price_pred': lgb_price,
        'log_r2': log_metrics['r2'], 'price_r2': price_metrics['r2'], 'price_mae': price_metrics['mae']
    }

    # Output Metrics Table
    print("\n" + "="*50)
    print("Metrics in Price Space ($)")
    print("="*50)
    print("| Model | MAE ($) | RMSE ($) | R² Score |")
    print("| :--- | :--- | :--- | :--- |")
    
    metrics_list = []
    for model in ['Baseline', 'OLS', 'Ridge', 'LightGBM']:
        mae = results_dict[model]['price_mae']
        rmse = np.sqrt(mean_squared_error(price_true, results_dict[model]['price_pred']))
        r2 = results_dict[model]['price_r2']
        print(f"| **{model}** | ${mae:,.0f} | ${rmse:,.0f} | {r2:.6f} |")
        metrics_list.append({'Model': model, 'MAE': mae, 'RMSE': rmse, 'R2': r2})
        
    VIZ_DIR.mkdir(exist_ok=True)
    pd.DataFrame(metrics_list).to_csv(VIZ_DIR / 'model_metrics_v2.csv', index=False)
    print("="*50 + "\n")

    # Output visual comparisons
    print("Generating presentation plots...")
    plot_presentation_visuals(results_dict, test_df, price_true)

if __name__ == "__main__":
    main()

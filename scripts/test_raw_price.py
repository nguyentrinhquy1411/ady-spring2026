import os
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
from pathlib import Path

# Paths
base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / 'data' / 'processed'
assets_dir = base_dir / 'assets'
assets_dir.mkdir(parents=True, exist_ok=True)

# Load data
train_df = pd.read_csv(data_dir / 'train.csv')
test_df = pd.read_csv(data_dir / 'test.csv')

train_df['date'] = pd.to_datetime(train_df['date'])
test_df['date'] = pd.to_datetime(test_df['date'])

# Feature Engineering: Raw Price Lags
def add_price_lags(df):
    df = df.copy()
    for lag in [1, 2, 3, 6, 12]:
        df[f'price_lag_{lag}'] = df.groupby('RegionID')['price'].shift(lag)
    return df

train_price = add_price_lags(train_df).dropna().reset_index(drop=True)
test_price = add_price_lags(test_df).ffill().reset_index(drop=True)

# Features/Target
features = [f'price_lag_{l}' for l in [1, 2, 3, 6, 12]] + ['city_enc']
target = 'price'

# 80/20 Time-based Split
unique_dates = train_price['date'].sort_values().unique()
split_date = unique_dates[int(len(unique_dates) * 0.80)]
train_subset = train_price[train_price['date'] < split_date]
val_subset = train_price[train_price['date'] >= split_date]

X_train_sub = train_subset[features]
y_train_sub = train_subset[target]
X_val = val_subset[features]
y_val = val_subset[target]
X_test = test_price[features]
y_test = test_price[target]

# Scale
scaler = StandardScaler()
X_train_sub_scaled = scaler.fit_transform(X_train_sub)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

# Train
model = lgb.LGBMRegressor(n_estimators=1000, learning_rate=0.05, num_leaves=31, random_state=42)
model.fit(
    X_train_sub_scaled, y_train_sub,
    eval_set=[(X_val_scaled, y_val)],
    eval_metric='rmse',
    callbacks=[lgb.early_stopping(50)]
)

# Predict
y_pred = model.predict(X_test_scaled)

# Metrics
print(f"\n[Raw Price Model - 80/20 Split]")
print(f"MAE: ${mean_absolute_error(y_test, y_pred):.2f}")
print(f"RMSE: ${np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")
print(f"R2: {r2_score(y_test, y_pred):.6f}")

# Visualization: Focus on one major city (New York) to show real scale instead of average
# New York RegionID = 394913
ny_mask = test_price['RegionID'] == 394913
results_df = pd.DataFrame({
    'date': test_price[ny_mask]['date'],
    'actual': y_test[ny_mask],
    'predicted': y_pred[ny_mask]
}).sort_values('date')

plt.figure(figsize=(12, 6))
plt.plot(results_df['date'], results_df['actual'], label='Actual Price (New York, NY)', color='#2ecc71', linewidth=2, marker='o', markersize=4)
plt.plot(results_df['date'], results_df['predicted'], label='Predicted Price (New York, NY)', color='#e74c3c', linestyle='--', linewidth=2)
plt.title('House Price Trends: Actual vs Predicted (New York, NY) - Raw Price Model')
plt.ylabel('Price ($)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(assets_dir / 'raw_price_predictions_date.png', dpi=300)
print(f"Plot saved to assets/raw_price_predictions_date.png")

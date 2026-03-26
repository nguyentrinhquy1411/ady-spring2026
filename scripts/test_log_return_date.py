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

# Log-return Features
features = ['lag_1', 'lag_2', 'lag_3', 'lag_6', 'lag_12', 'city_enc']
target = 'log_return'

# Scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(train_df[features])
X_test_scaled = scaler.transform(test_df[features])

# Train
model = lgb.LGBMRegressor(n_estimators=1000, learning_rate=0.05, num_leaves=31, random_state=42)
model.fit(X_train_scaled, train_df[target])

# Predict log returns
y_pred_log = model.predict(X_test_scaled)

# Transform back to price space
test_df['pred_log_return'] = y_pred_log

# Ensure we have price_lag_1
test_df = test_df.sort_values(['RegionID', 'date'])
test_df['price_lag_1'] = test_df.groupby('RegionID')['price'].shift(1)
first_obs_mask = test_df['price_lag_1'].isna()
test_df.loc[first_obs_mask, 'price_lag_1'] = test_df.loc[first_obs_mask, 'price'] / np.exp(test_df.loc[first_obs_mask, 'log_return'])

test_df['pred_price'] = test_df['price_lag_1'] * np.exp(test_df['pred_log_return'])

# Metrics in Price space
print(f"\n[Log Return Model - Price Space]")
print(f"MAE: ${mean_absolute_error(test_df['price'], test_df['pred_price']):.2f}")
print(f"R2: {r2_score(test_df['price'], test_df['pred_price']):.6f}")

# Visualization: Focus on one major city (New York) to show real scale instead of average
# New York RegionID = 394913
ny_mask = test_df['RegionID'] == 394913
results_df = test_df[ny_mask][['date', 'price', 'pred_price']].sort_values('date')

plt.figure(figsize=(12, 6))
plt.plot(results_df['date'], results_df['price'], label='Actual Price (New York, NY)', color='#2ecc71', linewidth=2, marker='o', markersize=4)
plt.plot(results_df['date'], results_df['pred_price'], label='Predicted Price (New York, NY)', color='#3498db', linestyle='--', linewidth=2)
plt.title('House Price Trends: Actual vs Predicted (New York, NY) - Log Return Model')
plt.ylabel('Price ($)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(assets_dir / 'price_predictions_date.png', dpi=300)
print(f"Plot saved to assets/price_predictions_date.png")

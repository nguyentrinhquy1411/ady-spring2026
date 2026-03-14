# Modeling Results & Insights

## 📈 Performance Summary

All models were evaluated using the `src/train_v2.py` standardized pipeline, comparing against the **Smart Baseline (Zero Growth)**.

| Model | log_return MAE | Price MAE | Price R² |
| :--- | :--- | :--- | :--- |
| **Smart Baseline** | 0.006913 | $1,795.06 | 0.999668 |
| **Ridge Regression** | **0.002009** | **$495.26** | **0.999976** |
| **LightGBM** | 0.002166 | $543.87 | 0.999967 |

### Key Findings
- **Dominance of Linear Trends**: The Ridge Regression model currently outperforms LightGBM. This suggests that the relationship between lagged returns and the current month is primarily linear and stable across metros.
- **Persistence Warning**: We detected an autocorrelation of **0.912** between `lag_1` and the target `log_return`. The market has extremely high momentum, making it highly predictable but sensitive to sudden trend shifts.

## 🎨 Visual Assets
Generated artifacts can be found in the `assets/` directory:
- `feature_importance.png`: Shows that $t-1$ and $t-2$ lags are the most significant predictors.
- `price_predictions_vs_actual.png`: Visual verification of model tracking across 3 random metros.
- `baseline_metrics.txt` / `lightgbm_metrics.txt`: Raw log outputs of the final evaluation runs.

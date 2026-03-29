# AI Usage & Audit: Housing Price Predictor (ADY-2026)

## 1. Overview of AI Integration
Throughout the development of the Housing Price Predictor project, AI tools (specifically Antigravity, a large language model powered by Google DeepMind) were utilized as a collaborative coding partner. The AI assisted in architectural design, code generation, and documentation refinement.

## 2. Specific Use Cases
The following areas benefited from AI collaboration:

- **Architectural Design**: The AI proposed the transition from raw price levels to stationary `log-returns`, explaining the statistical advantages (stationarity, additive properties) for time-series modeling.
- **Leakage Prevention**: AI was used to audit the `preprocess.py` script to ensure that `StandardScaler` and `CityEncoding` were fitted exclusively on the training set, avoiding look-ahead bias.
- **Model Refinement**: Suggestions for hyperparameter tuning (GridSearchCV) and cross-validation strategies (TimeSeriesSplit) were provided by the AI to better handle sequential data.
- **Evaluation Framework**: The AI helped design the "Dual-Space" evaluation logic, enabling the reporting of metrics in both logarithmic units and real-world USD figures.

## 3. Review and Validation Process
All AI-generated outputs were subject to a rigorous review process by the primary researcher:

1. **Manual Audit**: Every line of code generated or modified by the AI was manually inspected for logic errors and adherence to project requirements.
2. **Statistical Verification**: Model results (MAE, R2) produced via AI-proposed pipelines were cross-verified against established baselines (Zero-Growth assumption) to ensure performance claims were rooted in data.
3. **Correctness Testing**: The codebase was executed iteratively to confirm that the AI-proposed transformations (inverse-log-price transforms) were mathematically sound and yielded realistic housing values.
4. **Data Leakage Check**: Correlation heatmaps and feature-shuffling tests were performed to validate that the AI-designed features did not contain hidden target information from the test period.

## 4. Conclusion
The integration of AI tools served to accelerate development and improve the statistical rigor of the project. By combining AI assistance with human-in-the-loop validation, the project achieved a production-ready forecasting pipeline with high reliability.

---
*Date: 2026-03-19*  
*Project ID: ADY-2026*

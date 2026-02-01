Các bước triển khai rõ ràng

1. Load data từ UCI (xlsx) và xác nhận schema X1..X6, Y.

2. Split Protocol B (time-based): sort theo X1; train 70% đầu, test 30% cuối (hoặc cutoff theo mốc năm).

3. Preprocess: StandardScaler (fit trên train), apply val/test.

4. EDA: scatter X3–Y, thử log(X3), outlier check, corr/VIF.

5. Train baselines: mean, OLS.

6. Train Ridge/Lasso: tune alpha bằng CV; lưu hệ số (để explain/chatbot).

7. Train SVR: linear và RBF; tune (C, epsilon, gamma).

8. Đánh giá: MAE/RMSE/R² + error slicing theo distance bins + residual plots.

9. Explainability:

o tuyến tính: hệ số (đã scaling) + what-if delta

o SVR: permutation importance hoặc local surrogate quanh input

10. Extrapolation guard: kiểm tra input ngoài [min,max] train (theo từng feature) → warnin


Codebase structure:
house-price-project/
│
├── data/
│   ├── raw/
│   │   └── house.xlsx
│   └── processed/
│       ├── train.csv
│       └── test.csv
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_baseline.ipynb
│   ├── 03_linear_models.ipynb
│   ├── 04_svr.ipynb
│   ├── 05_evaluation.ipynb
│   └── 06_dl_or_chatbot.ipynb   (optional)
│
├── src/
│   ├── load_data.py
│   ├── preprocess.py
│   ├── models.py
│   ├── train.py
│   ├── evaluate.py
│   ├── explain.py
│   └── utils.py
│
├── reports/
│   ├── figures/
│   ├── tables/
│   └── final_report.docx / pdf
│
├── app/   (nếu làm chatbot)
│   ├── api.py
│   ├── chatbot.py
│   └── ui.py
│
├── requirements.txt
└── README.md
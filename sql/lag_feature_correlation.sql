SELECT
        ROUND(CORR(log_return, lag_1),  4) AS corr_lag1,
        ROUND(CORR(log_return, lag_2),  4) AS corr_lag2,
        ROUND(CORR(log_return, lag_3),  4) AS corr_lag3,
        ROUND(CORR(log_return, lag_6),  4) AS corr_lag6,
        ROUND(CORR(log_return, lag_12), 4) AS corr_lag12
    FROM processed_data
    WHERE log_return != 0;

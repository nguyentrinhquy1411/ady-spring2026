SELECT
        YEAR(date)                      AS year,
        ROUND(AVG(log_return), 6)       AS avg_log_return,
        ROUND(MIN(log_return), 6)       AS min_log_return,
        ROUND(MAX(log_return), 6)       AS max_log_return,
        ROUND(STDDEV(log_return), 6)    AS std_log_return
    FROM processed_data
    WHERE log_return != 0
    GROUP BY YEAR(date)
ORDER BY year;

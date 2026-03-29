SELECT
        RegionName,
        StateName,
        ROUND(AVG(price), 2)          AS avg_price,
        ROUND(MEDIAN(price), 2)       AS median_price,
        ROUND(MIN(price), 2)          AS min_price,
        ROUND(MAX(price), 2)          AS max_price,
        ROUND(AVG(log_return), 6)     AS avg_return,
        ROUND(STDDEV(log_return), 6)  AS volatility
    FROM processed_data
    GROUP BY RegionName, StateName
    ORDER BY avg_price DESC;

SELECT
        StateName,
        ROUND(AVG(log_return), 6)      AS avg_log_return,
        ROUND(AVG(log_return) * 12, 4) AS annualized_return,
        COUNT(DISTINCT RegionName)     AS num_regions
    FROM processed_data
    WHERE log_return != 0
    GROUP BY StateName
    ORDER BY avg_log_return DESC
    LIMIT 10;

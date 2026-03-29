SELECT
        CASE
            WHEN price > 500000 THEN 'High (>500K)'
            WHEN price > 200000 THEN 'Mid (200K-500K)'
            ELSE 'Low (<200K)'
        END AS tier,
        COUNT(*)                        AS observations,
        COUNT(DISTINCT RegionName)      AS num_regions,
        ROUND(AVG(price), 2)            AS avg_price,
        ROUND(MEDIAN(price), 2)         AS median_price,
        ROUND(AVG(log_return), 6)       AS avg_return,
        ROUND(STDDEV(log_return), 6)    AS volatility
    FROM processed_data
    GROUP BY tier
    ORDER BY avg_price DESC;

SELECT
        RegionName,
        StateName,
        ROUND(AVG(price), 2)    AS avg_price,
        ROUND(MEDIAN(price), 2) AS median_price,
        ROUND(MAX(price), 2)    AS max_price
    FROM processed_data
    GROUP BY RegionName, StateName
    ORDER BY avg_price DESC
    LIMIT 10;

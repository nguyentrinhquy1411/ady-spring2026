SELECT
        RegionName,
        StateName,
        ROUND(AVG(price), 2)    AS avg_price,
        ROUND(MEDIAN(price), 2) AS median_price,
        ROUND(MAX(price), 2)    AS max_price
    FROM processed_data
    GROUP BY RegionName, StateName
    ORDER BY ABS(AVG(price) - (SELECT AVG(price) FROM processed_data)) ASC
    LIMIT 10;

SELECT
        COUNT(*)                   AS total_rows,
        COUNT(DISTINCT RegionID)   AS total_regions,
        COUNT(DISTINCT StateName)  AS total_states,
        MIN(date)                  AS start_date,
        MAX(date)                  AS end_date,
        ROUND(AVG(price), 2)       AS avg_price,
        ROUND(MIN(price), 2)       AS min_price,
        ROUND(MAX(price), 2)       AS max_price
    FROM processed_data;

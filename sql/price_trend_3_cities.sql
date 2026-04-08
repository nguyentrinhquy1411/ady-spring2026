SELECT
        RegionName,
        YEAR(date)               AS year,
        ROUND(AVG(price), 2)     AS avg_price
    FROM processed_data
    WHERE RegionName IN ('San Jose, CA', 'Greensboro, NC', 'Clarksdale, MS')
    GROUP BY RegionName, YEAR(date)
    ORDER BY RegionName, year;

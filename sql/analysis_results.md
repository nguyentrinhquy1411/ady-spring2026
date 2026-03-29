# SQL Analysis Results

**Dataset**: `data\processed\processed_data_price.csv`
**SQL Engine**: SQLite3 (in-memory)

---

## Data Understanding

### Tổng quan dataset

```sql
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
```

|   total_rows |   total_regions |   total_states | start_date   | end_date   |   avg_price |   min_price |   max_price |
|-------------:|----------------:|---------------:|:-------------|:-----------|------------:|------------:|------------:|
|       269094 |             894 |             50 | 2001-01-31   | 2026-01-31 |      176868 |     46118.2 | 1.59656e+06 |

## Phân tích giá theo khu vực

### Top 10 khu vực giá nhà cao nhất (trung bình)

```sql
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
```

| RegionName         | StateName   |   avg_price |   median_price |        max_price |
|:-------------------|:------------|------------:|---------------:|-----------------:|
| San Jose, CA       | CA          |      840140 |         673769 |      1.59656e+06 |
| Vineyard Haven, MA | MA          |      779653 |         643329 |      1.47993e+06 |
| Jackson, WY        | WY          |      704378 |         549361 |      1.38421e+06 |
| San Francisco, CA  | CA          |      697098 |         617307 |      1.20913e+06 |
| Santa Cruz, CA     | CA          |      671037 |         621104 |      1.16001e+06 |
| Edwards, CO        | CO          |      631539 |         543285 |      1.28235e+06 |
| Napa, CA           | CA          |      591696 |         579884 | 919688           |
| Key West, FL       | FL          |      591144 |         492257 |      1.00179e+06 |
| Santa Maria, CA    | CA          |      578010 |         552752 | 970808           |
| Kahului, HI        | HI          |      573756 |         525921 |      1.06922e+06 |

### Top 10 khu vực giá nhà ở mức trung bình (trung bình)

```sql
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
```

| RegionName      | StateName   |   avg_price |   median_price |   max_price |
|:----------------|:------------|------------:|---------------:|------------:|
| Reading, PA     | PA          |      176796 |         165969 |      298628 |
| Glens Falls, NY | NY          |      177052 |         166658 |      292041 |
| Huntsville, TX  | TX          |      176444 |         143388 |      281090 |
| Willmar, MN     | MN          |      176402 |         165342 |      266815 |
| Red Bluff, CA   | CA          |      177486 |         135332 |      327692 |
| San Antonio, TX | TX          |      177489 |         148597 |      300694 |
| Yankton, SD     | SD          |      176164 |         152391 |      267055 |
| Racine, WI      | WI          |      177667 |         162184 |      293331 |
| Farmington, NM  | NM          |      177678 |         159656 |      260435 |
| Lewisburg, PA   | PA          |      177810 |         155360 |      278275 |

### Bang có giá nhà tăng trưởng mạnh nhất (avg log_return)

```sql
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
```

| StateName   |   avg_log_return |   annualized_return |   num_regions |
|:------------|-----------------:|--------------------:|--------------:|
| HI          |         0.005082 |              0.061  |             4 |
| MT          |         0.00428  |              0.0514 |             7 |
| NH          |         0.004213 |              0.0506 |             5 |
| ID          |         0.00419  |              0.0503 |            13 |
| ME          |         0.004108 |              0.0493 |             4 |
| UT          |         0.004034 |              0.0484 |             9 |
| RI          |         0.004031 |              0.0484 |             1 |
| OR          |         0.003943 |              0.0473 |            20 |
| CO          |         0.003929 |              0.0472 |            17 |
| NJ          |         0.003824 |              0.0459 |             4 |

## Phân tích log_return (target variable)

### Phân phối log_return theo năm

```sql
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
```

|   year |   avg_log_return |   min_log_return |   max_log_return |   std_log_return |
|-------:|-----------------:|-----------------:|-----------------:|-----------------:|
|   2001 |         0.004831 |        -0.019858 |         0.035569 |         0.003485 |
|   2002 |         0.004205 |        -0.020464 |         0.022549 |         0.003608 |
|   2003 |         0.00492  |        -0.015448 |         0.027334 |         0.004495 |
|   2004 |         0.006792 |        -0.025736 |         0.040273 |         0.005888 |
|   2005 |         0.007496 |        -0.039163 |         0.047999 |         0.00766  |
|   2006 |         0.004193 |        -0.085717 |         0.041039 |         0.005919 |
|   2007 |        -4.2e-05  |        -0.037183 |         0.028096 |         0.005651 |
|   2008 |        -0.004599 |        -0.063084 |         0.036929 |         0.008082 |
|   2009 |        -0.004658 |        -0.053835 |         0.032305 |         0.005734 |
|   2010 |        -0.002114 |        -0.050672 |         0.03623  |         0.00479  |
|   2011 |        -0.002826 |        -0.034433 |         0.023458 |         0.00469  |
|   2012 |         0.002218 |        -0.022815 |         0.045695 |         0.005583 |
|   2013 |         0.00361  |        -0.04305  |         0.053527 |         0.006199 |
|   2014 |         0.002657 |        -0.051625 |         0.070357 |         0.005218 |
|   2015 |         0.004271 |        -0.032667 |         0.028759 |         0.004527 |
|   2016 |         0.002838 |        -0.044914 |         0.026085 |         0.004836 |
|   2017 |         0.003683 |        -0.033368 |         0.02488  |         0.004422 |
|   2018 |         0.00408  |        -0.026915 |         0.043564 |         0.004507 |
|   2019 |         0.004665 |        -0.035308 |         0.032941 |         0.004348 |
|   2020 |         0.007859 |        -0.028048 |         0.066714 |         0.006393 |
|   2021 |         0.010714 |        -0.0311   |         0.050868 |         0.007401 |
|   2022 |         0.006244 |        -0.049732 |         0.043111 |         0.009794 |
|   2023 |         0.002079 |        -0.047792 |         0.026105 |         0.006275 |
|   2024 |         0.002842 |        -0.037116 |         0.031621 |         0.004698 |
|   2025 |         0.000987 |        -0.054642 |         0.031117 |         0.005187 |
|   2026 |         0.004044 |        -0.020221 |         0.023961 |         0.004052 |

### Tương quan lag features với log_return

```sql
SELECT
        ROUND(CORR(log_return, lag_1),  4) AS corr_lag1,
        ROUND(CORR(log_return, lag_2),  4) AS corr_lag2,
        ROUND(CORR(log_return, lag_3),  4) AS corr_lag3,
        ROUND(CORR(log_return, lag_6),  4) AS corr_lag6,
        ROUND(CORR(log_return, lag_12), 4) AS corr_lag12
    FROM processed_data
    WHERE log_return != 0;
```

|   corr_lag1 |   corr_lag2 |   corr_lag3 |   corr_lag6 |   corr_lag12 |
|------------:|------------:|------------:|------------:|-------------:|
|      0.0777 |      0.0669 |      0.0577 |       0.038 |       0.0084 |


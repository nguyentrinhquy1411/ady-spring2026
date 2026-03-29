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

### Xu hướng giá nhà theo năm tại 3 thị trường đại diện (cao / trung / thấp)

```sql
SELECT
        RegionName,
        YEAR(date)               AS year,
        ROUND(AVG(price), 2)     AS avg_price
    FROM processed_data
    WHERE RegionName IN ('San Jose, CA', 'Greensboro, NC', 'Clarksdale, MS')
    GROUP BY RegionName, YEAR(date)
    ORDER BY RegionName, year;
```

| RegionName     |   year |        avg_price |
|:---------------|-------:|-----------------:|
| Clarksdale, MS |   2001 |  52413.3         |
| Clarksdale, MS |   2002 |  52413.3         |
| Clarksdale, MS |   2003 |  52413.3         |
| Clarksdale, MS |   2004 |  52413.3         |
| Clarksdale, MS |   2005 |  52413.3         |
| Clarksdale, MS |   2006 |  52413.3         |
| Clarksdale, MS |   2007 |  52413.3         |
| Clarksdale, MS |   2008 |  52413.3         |
| Clarksdale, MS |   2009 |  52413.3         |
| Clarksdale, MS |   2010 |  52413.3         |
| Clarksdale, MS |   2011 |  52413.3         |
| Clarksdale, MS |   2012 |  52413.3         |
| Clarksdale, MS |   2013 |  52413.3         |
| Clarksdale, MS |   2014 |  52413.3         |
| Clarksdale, MS |   2015 |  52413.3         |
| Clarksdale, MS |   2016 |  51275           |
| Clarksdale, MS |   2017 |  49473.1         |
| Clarksdale, MS |   2018 |  50703.5         |
| Clarksdale, MS |   2019 |  54628.6         |
| Clarksdale, MS |   2020 |  60373.3         |
| Clarksdale, MS |   2021 |  76232.1         |
| Clarksdale, MS |   2022 |  73142.5         |
| Clarksdale, MS |   2023 |  60723.2         |
| Clarksdale, MS |   2024 |  52881.4         |
| Clarksdale, MS |   2025 |  50474.5         |
| Clarksdale, MS |   2026 |  47381.4         |
| Greensboro, NC |   2001 | 114130           |
| Greensboro, NC |   2002 | 116679           |
| Greensboro, NC |   2003 | 118801           |
| Greensboro, NC |   2004 | 121551           |
| Greensboro, NC |   2005 | 125437           |
| Greensboro, NC |   2006 | 130305           |
| Greensboro, NC |   2007 | 133711           |
| Greensboro, NC |   2008 | 133798           |
| Greensboro, NC |   2009 | 129387           |
| Greensboro, NC |   2010 | 124382           |
| Greensboro, NC |   2011 | 119160           |
| Greensboro, NC |   2012 | 117748           |
| Greensboro, NC |   2013 | 120521           |
| Greensboro, NC |   2014 | 124439           |
| Greensboro, NC |   2015 | 127848           |
| Greensboro, NC |   2016 | 133391           |
| Greensboro, NC |   2017 | 140550           |
| Greensboro, NC |   2018 | 149906           |
| Greensboro, NC |   2019 | 161280           |
| Greensboro, NC |   2020 | 174621           |
| Greensboro, NC |   2021 | 201133           |
| Greensboro, NC |   2022 | 228758           |
| Greensboro, NC |   2023 | 240394           |
| Greensboro, NC |   2024 | 251369           |
| Greensboro, NC |   2025 | 254130           |
| Greensboro, NC |   2026 | 255818           |
| San Jose, CA   |   2001 | 474328           |
| San Jose, CA   |   2002 | 469914           |
| San Jose, CA   |   2003 | 482058           |
| San Jose, CA   |   2004 | 527764           |
| San Jose, CA   |   2005 | 626131           |
| San Jose, CA   |   2006 | 669806           |
| San Jose, CA   |   2007 | 670314           |
| San Jose, CA   |   2008 | 594597           |
| San Jose, CA   |   2009 | 498822           |
| San Jose, CA   |   2010 | 505166           |
| San Jose, CA   |   2011 | 476419           |
| San Jose, CA   |   2012 | 505768           |
| San Jose, CA   |   2013 | 622712           |
| San Jose, CA   |   2014 | 707211           |
| San Jose, CA   |   2015 | 808925           |
| San Jose, CA   |   2016 | 867382           |
| San Jose, CA   |   2017 | 895127           |
| San Jose, CA   |   2018 |      1.10307e+06 |
| San Jose, CA   |   2019 |      1.1058e+06  |
| San Jose, CA   |   2020 |      1.12179e+06 |
| San Jose, CA   |   2021 |      1.27631e+06 |
| San Jose, CA   |   2022 |      1.45933e+06 |
| San Jose, CA   |   2023 |      1.39494e+06 |
| San Jose, CA   |   2024 |      1.52575e+06 |
| San Jose, CA   |   2025 |      1.55337e+06 |
| San Jose, CA   |   2026 |      1.56857e+06 |

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

## Phân khúc thị trường & Điểm cực trị

### Phân khúc thị trường theo Tier giá (High/Mid/Low)

```sql
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
```

| tier            |   observations |   num_regions |   avg_price |   median_price |   avg_return |   volatility |
|:----------------|---------------:|--------------:|------------:|---------------:|-------------:|-------------:|
| High (>500K)    |           6269 |            77 |      681636 |         607342 |     0.003914 |     0.008821 |
| Mid (200K-500K) |          63404 |           616 |      283180 |         259179 |     0.003925 |     0.007383 |
| Low (<200K)     |         199421 |           843 |      127199 |         124110 |     0.002143 |     0.005795 |

### Thống kê các thị trường theo mức giá (Từ cao xuống thấp)

```sql
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
```

| RegionName                 | StateName   |   avg_price |   median_price |   min_price |        max_price |   avg_return |   volatility |
|:---------------------------|:------------|------------:|---------------:|------------:|-----------------:|-------------:|-------------:|
| San Jose, CA               | CA          |    840140   |       673769   |    451048   |      1.59656e+06 |     0.00421  |     0.011762 |
| Vineyard Haven, MA         | MA          |    779653   |       643329   |    372503   |      1.47993e+06 |     0.004622 |     0.006812 |
| Jackson, WY                | WY          |    704378   |       549361   |    427697   |      1.38421e+06 |     0.002994 |     0.008082 |
| San Francisco, CA          | CA          |    697098   |       617307   |    341692   |      1.20913e+06 |     0.003903 |     0.009174 |
| Santa Cruz, CA             | CA          |    671037   |       621104   |    350064   |      1.16001e+06 |     0.003855 |     0.009703 |
| Edwards, CO                | CO          |    631539   |       543285   |    326950   |      1.28235e+06 |     0.004548 |     0.009288 |
| Napa, CA                   | CA          |    591696   |       579884   |    296838   | 919688           |     0.00362  |     0.009794 |
| Key West, FL               | FL          |    591144   |       492257   |    492257   |      1.00179e+06 |     0.002126 |     0.006704 |
| Santa Maria, CA            | CA          |    578010   |       552752   |    298502   | 970808           |     0.003955 |     0.010711 |
| Kahului, HI                | HI          |    573756   |       525921   |    208510   |      1.06922e+06 |     0.005215 |     0.008815 |
| Oxnard, CA                 | CA          |    560757   |       544173   |    288783   | 873010           |     0.003668 |     0.009508 |
| Heber, UT                  | UT          |    555254   |       392716   |    329974   |      1.12599e+06 |     0.003466 |     0.007775 |
| Los Angeles, CA            | CA          |    553636   |       515868   |    242362   | 954517           |     0.004535 |     0.010256 |
| Urban Honolulu, HI         | HI          |    550688   |       515470   |    230196   | 875574           |     0.004298 |     0.007334 |
| Breckenridge, CO           | CO          |    545435   |       426584   |    289272   |      1.11044e+06 |     0.004003 |     0.007157 |
| Santa Rosa, CA             | CA          |    543076   |       543676   |    313353   | 797620           |     0.003038 |     0.009451 |
| Salinas, CA                | CA          |    530906   |       509730   |    297689   | 843861           |     0.003346 |     0.012341 |
| Kapaa, HI                  | HI          |    522343   |       436446   |    165545   |      1.01719e+06 |     0.005983 |     0.008203 |
| San Diego, CA              | CA          |    520932   |       488950   |    242963   | 925901           |     0.004399 |     0.009847 |
| San Luis Obispo, CA        | CA          |    519087   |       480724   |    234123   | 879827           |     0.004454 |     0.008797 |
| Steamboat Springs, CO      | CO          |    507735   |       393202   |    242351   |      1.09987e+06 |     0.005049 |     0.007224 |
| Hailey, ID                 | ID          |    487137   |       402130   |    300295   |      1.01442e+06 |     0.003074 |     0.008825 |
| Glenwood Springs, CO       | CO          |    453965   |       361716   |    211964   | 958259           |     0.005041 |     0.005484 |
| New York, NY               | NY          |    451869   |       433795   |    241105   | 703126           |     0.003587 |     0.005333 |
| Bridgeport, CT             | CT          |    437175   |       408630   |    284416   | 652493           |     0.002794 |     0.006304 |
| Ocean City, NJ             | NJ          |    430633   |       395486   |    181976   | 765863           |     0.004808 |     0.007909 |
| Barnstable Town, MA        | MA          |    429291   |       391019   |    217653   | 729722           |     0.004049 |     0.007384 |
| Boulder, CO                | CO          |    429022   |       330311   |    255965   | 765731           |     0.003383 |     0.005992 |
| Boston, MA                 | MA          |    425512   |       378696   |    245508   | 709008           |     0.003568 |     0.005535 |
| Seattle, WA                | WA          |    417464   |       364581   |    230732   | 751725           |     0.003844 |     0.008591 |
| Gardnerville Ranchos, NV   | NV          |    412903   |       382275   |    233244   | 712792           |     0.003564 |     0.010841 |
| Truckee, CA                | CA          |    404260   |       386324   |    203890   | 659777           |     0.003562 |     0.009526 |
| Ukiah, CA                  | CA          |    398236   |       384852   |    245557   | 606631           |     0.002256 |     0.008974 |
| Washington, DC             | VA          |    387730   |       379773   |    192446   | 568923           |     0.003618 |     0.007244 |
| Durango, CO                | CO          |    386651   |       314005   |    288533   | 657614           |     0.002456 |     0.004958 |
| Hood River, OR             | OR          |    386508   |       337864   |    185502   | 677053           |     0.004267 |     0.006675 |
| Vallejo, CA                | CA          |    383159   |       380576   |    188505   | 613795           |     0.003273 |     0.013428 |
| Oak Harbor, WA             | WA          |    371487   |       307339   |    249010   | 632695           |     0.002324 |     0.006761 |
| Sacramento, CA             | CA          |    367347   |       352503   |    187195   | 607281           |     0.003718 |     0.01091  |
| Hilo, HI                   | HI          |    365433   |       308843   |    308843   | 570976           |     0.001943 |     0.00507  |
| Bozeman, MT                | MT          |    364330   |       260666   |    230390   | 692984           |     0.003255 |     0.006682 |
| Kill Devil Hills, NC       | NC          |    358175   |       327915   |    221666   | 589068           |     0.00325  |     0.006807 |
| Bend, OR                   | OR          |    356496   |       314868   |    157274   | 700761           |     0.004755 |     0.011336 |
| Naples, FL                 | FL          |    356490   |       344152   |    192930   | 621623           |     0.003513 |     0.011753 |
| Eureka, CA                 | CA          |    347022   |       348205   |    170544   | 495138           |     0.00298  |     0.008407 |
| Easton, MD                 | MD          |    342833   |       328014   |    201651   | 482543           |     0.002898 |     0.007501 |
| Los Alamos, NM             | NM          |    341224   |       312693   |    241852   | 574992           |     0.001986 |     0.005506 |
| Santa Fe, NM               | NM          |    339639   |       304071   |    216939   | 545337           |     0.003037 |     0.006399 |
| Denver, CO                 | CO          |    336408   |       248515   |    209762   | 601502           |     0.003294 |     0.005891 |
| Kalispell, MT              | MT          |    333998   |       273118   |    207896   | 652734           |     0.002734 |     0.008915 |
| Stockton, CA               | CA          |    333852   |       318903   |    157943   | 565527           |     0.003536 |     0.015034 |
| Bremerton, WA              | WA          |    330031   |       293172   |    161366   | 576231           |     0.004177 |     0.007312 |
| Riverside, CA              | CA          |    329967   |       308135   |    149414   | 588946           |     0.004508 |     0.012659 |
| Portland, OR               | OR          |    328865   |       294078   |    175544   | 558806           |     0.003712 |     0.007219 |
| Fort Collins, CO           | CO          |    328728   |       250754   |    205036   | 557441           |     0.003246 |     0.005052 |
| Bellingham, WA             | WA          |    326983   |       282641   |    142967   | 597566           |     0.00476  |     0.00728  |
| Sandpoint, ID              | ID          |    324362   |       249459   |    195637   | 660124           |     0.003056 |     0.008661 |
| Taos, NM                   | NM          |    323462   |       283282   |    264276   | 505427           |     0.00154  |     0.006186 |
| Reno, NV                   | NV          |    323227   |       305698   |    158514   | 572440           |     0.003715 |     0.012075 |
| Flagstaff, AZ              | AZ          |    323209   |       288588   |    150943   | 611594           |     0.004657 |     0.009722 |
| Corvallis, OR              | OR          |    322248   |       281388   |    181728   | 542291           |     0.003677 |     0.005756 |
| Juneau, AK                 | AK          |    320278   |       303996   |    246888   | 451381           |     0.002005 |     0.00389  |
| Hilton Head Island, SC     | SC          |    310342   |       284012   |    199995   | 515401           |     0.003182 |     0.007593 |
| Sonora, CA                 | CA          |    307777   |       281271   |    280154   | 422101           |     0.001012 |     0.004411 |
| Fredericksburg, TX         | TX          |    306197   |       237251   |    220372   | 542614           |     0.002584 |     0.006378 |
| Mount Vernon, WA           | WA          |    305190   |       260249   |    156840   | 567280           |     0.004291 |     0.007045 |
| California, MD             | MD          |    303020   |       293771   |    169381   | 419788           |     0.00303  |     0.007385 |
| Salt Lake City, UT         | UT          |    297812   |       242829   |    180513   | 562617           |     0.003731 |     0.007618 |
| Astoria, OR                | OR          |    294306   |       262107   |    178683   | 510924           |     0.003391 |     0.007119 |
| Coeur d'Alene, ID          | ID          |    294174   |       219386   |    160606   | 579081           |     0.003215 |     0.008317 |
| Charlottesville, VA        | VA          |    294072   |       277085   |    174119   | 455056           |     0.003216 |     0.005728 |
| Olympia, WA                | WA          |    291559   |       255145   |    150137   | 518309           |     0.004124 |     0.007069 |
| Missoula, MT               | MT          |    291524   |       230678   |    197471   | 552397           |     0.003408 |     0.006902 |
| Providence, RI             | RI          |    291130   |       272457   |    150131   | 501113           |     0.004031 |     0.007025 |
| Ellensburg, WA             | WA          |    290529   |       244477   |    198067   | 494523           |     0.002226 |     0.006029 |
| Provo, UT                  | UT          |    289370   |       235556   |    179686   | 551390           |     0.003608 |     0.007988 |
| Greeley, CO                | CO          |    287917   |       216267   |    168741   | 520091           |     0.003295 |     0.006213 |
| Portland, ME               | ME          |    286953   |       252251   |    146025   | 515571           |     0.004228 |     0.006313 |
| Wenatchee, WA              | WA          |    286179   |       244674   |    148635   | 503458           |     0.004053 |     0.006863 |
| Port Angeles, WA           | WA          |    285483   |       257916   |    190432   | 479149           |     0.002058 |     0.006322 |
| Brookings, OR              | OR          |    285376   |       265879   |    144636   | 466261           |     0.003746 |     0.00749  |
| Modesto, CA                | CA          |    284018   |       271890   |    133922   | 463053           |     0.00362  |     0.014956 |
| St. George, UT             | UT          |    283127   |       209487   |    164548   | 550153           |     0.003022 |     0.007752 |
| Burlington, VT             | VT          |    282675   |       253881   |    145640   | 459699           |     0.003837 |     0.004558 |
| Moscow, ID                 | ID          |    282176   |       250605   |    210542   | 454910           |     0.001981 |     0.005633 |
| Medford, OR                | OR          |    281940   |       268864   |    159415   | 438360           |     0.00328  |     0.008639 |
| Manchester, NH             | NH          |    281618   |       253695   |    157960   | 502848           |     0.003893 |     0.00655  |
| Worcester, MA              | MA          |    279429   |       259995   |    174649   | 460840           |     0.003267 |     0.006639 |
| Salisbury, MD              | DE          |    278214   |       261315   |    145144   | 420808           |     0.003542 |     0.00702  |
| Trenton, NJ                | NJ          |    277767   |       261393   |    159834   | 435501           |     0.003337 |     0.006575 |
| Boone, NC                  | NC          |    275109   |       242601   |    156553   | 497609           |     0.003834 |     0.006503 |
| Crestview, FL              | FL          |    274318   |       247969   |    148826   | 461989           |     0.003521 |     0.009385 |
| Colorado Springs, CO       | CO          |    274293   |       222066   |    170461   | 478705           |     0.003232 |     0.005272 |
| Baltimore, MD              | MD          |    274267   |       269403   |    146555   | 390541           |     0.003268 |     0.006193 |
| Anchorage, AK              | AK          |    274226   |       266747   |    140653   | 403045           |     0.003558 |     0.004895 |
| Austin, TX                 | TX          |    274126   |       211715   |    177935   | 554273           |     0.002851 |     0.008239 |
| Carson City, NV            | NV          |    272602   |       254329   |    142278   | 478787           |     0.003965 |     0.011226 |
| Chico, CA                  | CA          |    269210   |       257789   |    134538   | 420367           |     0.003538 |     0.008828 |
| Morehead City, NC          | NC          |    268994   |       248282   |    145870   | 459853           |     0.003837 |     0.00691  |
| Sheridan, WY               | WY          |    264017   |       228029   |    215061   | 428272           |     0.002272 |     0.004188 |
| Miami, FL                  | FL          |    262770   |       242896   |    121313   | 492148           |     0.004498 |     0.010841 |
| North Port, FL             | FL          |    261885   |       243378   |    140610   | 476545           |     0.003493 |     0.011418 |
| Ogden, UT                  | UT          |    261700   |       203148   |    163260   | 505465           |     0.00376  |     0.006732 |
| Eugene, OR                 | OR          |    260539   |       228509   |    148398   | 444466           |     0.003637 |     0.006929 |
| Spearfish, SD              | SD          |    260104   |       216150   |    202210   | 439805           |     0.002562 |     0.004653 |
| Phoenix, AZ                | AZ          |    259934   |       233091   |    133163   | 492351           |     0.003608 |     0.012734 |
| Elko, NV                   | NV          |    259856   |       255276   |    201755   | 355689           |     0.001102 |     0.004311 |
| Brevard, NC                | NC          |    258218   |       218388   |    188267   | 468168           |     0.002511 |     0.006389 |
| Raleigh, NC                | NC          |    258178   |       217136   |    176127   | 446578           |     0.002962 |     0.005581 |
| Las Vegas, NV              | NV          |    257031   |       237801   |    120735   | 439903           |     0.003255 |     0.013921 |
| Newport, OR                | OR          |    255322   |       223958   |    128418   | 464711           |     0.00425  |     0.007422 |
| Ann Arbor, MI              | MI          |    254550   |       234670   |    169800   | 398084           |     0.002456 |     0.005585 |
| Shelton, WA                | WA          |    253872   |       219660   |    167145   | 444708           |     0.002302 |     0.00687  |
| Wilmington, NC             | NC          |    253619   |       226899   |    173150   | 437483           |     0.003041 |     0.006388 |
| Torrington, CT             | CT          |    253372   |       232632   |    156786   | 404823           |     0.003166 |     0.006721 |
| Salem, OR                  | OR          |    253348   |       215824   |    146903   | 442391           |     0.003683 |     0.006671 |
| Crescent City, CA          | CA          |    252691   |       270591   |    166447   | 359538           |     0.000884 |     0.008065 |
| Gillette, WY               | WY          |    252463   |       243992   |    228513   | 337345           |     0.000915 |     0.003617 |
| Logan, UT                  | UT          |    252109   |       203500   |    173783   | 460719           |     0.00298  |     0.007003 |
| Concord, NH                | NH          |    251540   |       222010   |    133801   | 468928           |     0.004197 |     0.006695 |
| Merced, CA                 | CA          |    251367   |       236305   |    113090   | 421265           |     0.003497 |     0.016983 |
| Laconia, NH                | NH          |    250908   |       213740   |    119548   | 489854           |     0.004708 |     0.006896 |
| Montrose, CO               | CO          |    250684   |       200729   |    131766   | 479999           |     0.004319 |     0.005274 |
| Ketchikan, AK              | AK          |    250007   |       220450   |    191940   | 380280           |     0.002272 |     0.003671 |
| Madison, WI                | WI          |    248892   |       216321   |    151811   | 428692           |     0.003463 |     0.004034 |
| Norwich, CT                | CT          |    248765   |       232136   |    156344   | 400106           |     0.003135 |     0.006518 |
| The Villages, FL           | FL          |    248638   |       236748   |    133899   | 415563           |     0.003546 |     0.007231 |
| Helena, MT                 | MT          |    248431   |       194723   |    182155   | 455118           |     0.002821 |     0.005463 |
| Boise City, ID             | ID          |    248259   |       195131   |    130927   | 519880           |     0.00398  |     0.010175 |
| Minneapolis, MN            | MN          |    248043   |       232504   |    158952   | 373919           |     0.002878 |     0.006143 |
| Pinehurst, NC              | NC          |    245881   |       219993   |    191605   | 403928           |     0.002019 |     0.005791 |
| Hudson, NY                 | NY          |    244516   |       218620   |    111355   | 452332           |     0.004688 |     0.006733 |
| New Haven, CT              | CT          |    243999   |       225879   |    152609   | 385594           |     0.003095 |     0.006699 |
| Nashville, TN              | TN          |    243950   |       189604   |    145076   | 451603           |     0.003726 |     0.005542 |
| Charleston, SC             | SC          |    243604   |       218530   |    141062   | 429010           |     0.003691 |     0.006287 |
| Kennewick, WA              | WA          |    242578   |       189733   |    138712   | 432178           |     0.003783 |     0.005063 |
| Redding, CA                | CA          |    241338   |       227239   |    111745   | 378670           |     0.00391  |     0.00899  |
| Grand Junction, CO         | CO          |    241266   |       215103   |    139276   | 418326           |     0.003668 |     0.006426 |
| Yuba City, CA              | CA          |    240967   |       211324   |    134844   | 439696           |     0.00348  |     0.009865 |
| Fresno, CA                 | CA          |    240771   |       226275   |    112817   | 400897           |     0.00422  |     0.01138  |
| Kingston, NY               | NY          |    239427   |       218560   |    125673   | 422290           |     0.004053 |     0.007808 |
| Cullowhee, NC              | NC          |    238770   |       208276   |    180449   | 396424           |     0.002125 |     0.006204 |
| Hartford, CT               | CT          |    237141   |       223116   |    153934   | 376562           |     0.002996 |     0.005364 |
| Grants Pass, OR            | OR          |    237087   |       214874   |    116083   | 398579           |     0.003961 |     0.007932 |
| Durham, NC                 | NC          |    236919   |       199159   |    163803   | 407612           |     0.002994 |     0.005336 |
| Billings, MT               | MT          |    236493   |       202256   |    182965   | 392350           |     0.002489 |     0.004082 |
| Whitewater, WI             | WI          |    236245   |       217225   |    170046   | 391750           |     0.002783 |     0.005685 |
| Bennington, VT             | VT          |    236137   |       220666   |    125731   | 377535           |     0.003488 |     0.005957 |
| Cheyenne, WY               | WY          |    235913   |       209945   |    140806   | 377330           |     0.003209 |     0.004227 |
| Winchester, VA             | VA          |    235318   |       220415   |    125784   | 376227           |     0.003671 |     0.007563 |
| Barre, VT                  | VT          |    235291   |       216636   |    118324   | 384526           |     0.003875 |     0.004935 |
| Asheville, NC              | NC          |    235211   |       201326   |    121655   | 428939           |     0.004078 |     0.005311 |
| Williston, ND              | ND          |    234533   |       250245   |    169479   | 333089           |     0.002245 |     0.006941 |
| Virginia Beach, VA         | VA          |    233817   |       227524   |    121860   | 360158           |     0.003616 |     0.005735 |
| Longview, WA               | WA          |    233543   |       184711   |    153390   | 408904           |     0.00264  |     0.005755 |
| Fernley, NV                | NV          |    233216   |       215932   |    101214   | 420116           |     0.002087 |     0.010608 |
| Philadelphia, PA           | PA          |    232598   |       219826   |    126328   | 374293           |     0.003622 |     0.005285 |
| Brenham, TX                | TX          |    231004   |       186899   |    180741   | 370130           |     0.002192 |     0.004358 |
| Laramie, WY                | WY          |    231003   |       203693   |    185178   | 366627           |     0.002031 |     0.003697 |
| Cape Coral, FL             | FL          |    230536   |       218711   |    128954   | 407990           |     0.003045 |     0.01306  |
| Fairbanks, AK              | AK          |    229659   |       219881   |    176675   | 295938           |     0.001649 |     0.004042 |
| Richmond, VA               | VA          |    228600   |       211436   |    130608   | 380856           |     0.003568 |     0.005063 |
| Walla Walla, WA            | WA          |    228308   |       196004   |    125645   | 400911           |     0.003872 |     0.006192 |
| Oxford, MS                 | MS          |    228020   |       194269   |    181868   | 395483           |     0.002362 |     0.004301 |
| Prineville, OR             | OR          |    227245   |       170286   |     91778.9 | 475003           |     0.005375 |     0.008135 |
| Albany, OR                 | OR          |    227094   |       187847   |    144126   | 401510           |     0.002524 |     0.006167 |
| Kerrville, TX              | TX          |    226484   |       183800   |    165597   | 385077           |     0.002562 |     0.004913 |
| The Dalles, OR             | OR          |    226283   |       187920   |    150087   | 388126           |     0.00241  |     0.006113 |
| Dover, DE                  | DE          |    226210   |       203578   |    173368   | 361866           |     0.001911 |     0.004811 |
| Georgetown, SC             | SC          |    225883   |       184498   |    177576   | 384526           |     0.002414 |     0.004744 |
| Selinsgrove, PA            | PA          |    225405   |       240578   |    170031   | 271788           |    -0.000187 |     0.009388 |
| Orlando, FL                | FL          |    225309   |       204197   |    124587   | 401145           |     0.003693 |     0.010871 |
| Chicago, IL                | IL          |    224546   |       217406   |    161659   | 333939           |     0.002427 |     0.005969 |
| Centralia, WA              | WA          |    223734   |       179619   |    143495   | 420012           |     0.002822 |     0.006628 |
| Rexburg, ID                | ID          |    223460   |       175459   |    148620   | 429563           |     0.002904 |     0.007265 |
| Madera, CA                 | CA          |    223443   |       201408   |    108020   | 416369           |     0.004483 |     0.010141 |
| Spirit Lake, IA            | IA          |    222896   |       194350   |    167124   | 366663           |     0.002516 |     0.004836 |
| Pittsfield, MA             | MA          |    222726   |       203589   |    133020   | 370902           |     0.003425 |     0.006094 |
| Daphne, AL                 | AL          |    221458   |       202629   |    137370   | 366977           |     0.003244 |     0.006424 |
| Spokane, WA                | WA          |    221311   |       182740   |    117988   | 418103           |     0.004109 |     0.007447 |
| Springfield, MA            | MA          |    221260   |       205640   |    128261   | 356390           |     0.003408 |     0.005235 |
| Milwaukee, WI              | WI          |    221043   |       204956   |    147097   | 363139           |     0.003018 |     0.005168 |
| Watertown, SD              | SD          |    219791   |       193228   |    193228   | 324964           |     0.001727 |     0.004    |
| Sevierville, TN            | TN          |    219135   |       175988   |    121717   | 447541           |     0.003925 |     0.007798 |
| Sebastian, FL              | FL          |    218200   |       197617   |    120194   | 386675           |     0.003639 |     0.010682 |
| Espa-¦ola, NM              | NM          |    218119   |       191637   |    184820   | 323819           |     0.001736 |     0.006335 |
| Harrisonburg, VA           | VA          |    218013   |       188776   |    180073   | 339040           |     0.001945 |     0.003368 |
| Atlanta, GA                | GA          |    217711   |       187449   |    126474   | 387738           |     0.002885 |     0.007358 |
| Lancaster, PA              | PA          |    217577   |       198052   |    137779   | 371862           |     0.003299 |     0.0046   |
| Atlantic City, NJ          | NJ          |    217311   |       197315   |    114817   | 368981           |     0.003898 |     0.008005 |
| Albany, NY                 | NY          |    217232   |       206039   |    119804   | 349818           |     0.003567 |     0.004433 |
| Cedar City, UT             | UT          |    216439   |       169983   |    138425   | 397700           |     0.002823 |     0.007058 |
| Lewiston, ID               | ID          |    216043   |       182584   |    157517   | 359691           |     0.002253 |     0.00525  |
| New Orleans, LA            | LA          |    215812   |       213897   |    144879   | 289635           |     0.001874 |     0.004693 |
| Bismarck, ND               | ND          |    215445   |       210468   |    156736   | 338733           |     0.002542 |     0.004095 |
| State College, PA          | PA          |    215203   |       193688   |    160901   | 335504           |     0.002441 |     0.004024 |
| Gainesville, GA            | GA          |    215043   |       186681   |    128218   | 389868           |     0.003178 |     0.007451 |
| Fargo, ND                  | ND          |    214808   |       185362   |    168252   | 313130           |     0.001742 |     0.003643 |
| Allentown, PA              | PA          |    213609   |       200410   |    124601   | 348915           |     0.003443 |     0.005622 |
| Port St. Lucie, FL         | FL          |    213017   |       192887   |    106130   | 401110           |     0.004207 |     0.01203  |
| Tucson, AZ                 | AZ          |    212884   |       192174   |    126214   | 351398           |     0.003287 |     0.009063 |
| Panama City, FL            | FL          |    212667   |       192029   |    116491   | 363824           |     0.003548 |     0.009383 |
| Charlotte, NC              | NC          |    212618   |       172584   |    145720   | 383134           |     0.003139 |     0.005658 |
| Payson, AZ                 | AZ          |    212177   |       193178   |     92909   | 388227           |     0.004665 |     0.00957  |
| Coos Bay, OR               | OR          |    211818   |       184150   |    141710   | 347853           |     0.002021 |     0.005886 |
| Riverton, WY               | WY          |    211567   |       194631   |    182151   | 312556           |     0.001501 |     0.004946 |
| Myrtle Beach, SC           | SC          |    211528   |       190734   |    141080   | 345180           |     0.002839 |     0.007706 |
| Idaho Falls, ID            | ID          |    211322   |       171892   |    113587   | 420334           |     0.0042   |     0.007993 |
| Dickinson, ND              | ND          |    211162   |       232560   |    158740   | 306400           |     0.002185 |     0.004859 |
| Midland, TX                | TX          |    211022   |       198437   |    154704   | 320345           |     0.002302 |     0.004592 |
| Traverse City, MI          | MI          |    210855   |       168921   |    128193   | 396318           |     0.003766 |     0.006673 |
| Jacksonville, FL           | FL          |    210548   |       189338   |    120773   | 363514           |     0.003495 |     0.008229 |
| Carlsbad, NM               | NM          |    210544   |       204880   |    180616   | 253634           |     0.000372 |     0.00563  |
| Moses Lake, WA             | WA          |    209414   |       180437   |    152760   | 352997           |     0.002229 |     0.005887 |
| Vernal, UT                 | UT          |    209030   |       186817   |    163871   | 340768           |     0.001997 |     0.006774 |
| Dallas, TX                 | TX          |    208899   |       156278   |    129255   | 384604           |     0.003371 |     0.005774 |
| Hanford, CA                | CA          |    208416   |       193295   |    106495   | 356303           |     0.004012 |     0.009572 |
| Rapid City, SD             | SD          |    208053   |       173888   |    160422   | 360342           |     0.002643 |     0.004484 |
| Fallon, NV                 | NV          |    207769   |       168907   |    116442   | 379393           |     0.002688 |     0.00757  |
| Alexandria, MN             | MN          |    207687   |       190007   |    154735   | 326983           |     0.002071 |     0.004978 |
| Bakersfield, CA            | CA          |    207343   |       194861   |     97878.8 | 359845           |     0.004308 |     0.01238  |
| Show Low, AZ               | AZ          |    206570   |       180536   |    101011   | 391652           |     0.004473 |     0.008533 |
| Jefferson, GA              | GA          |    206259   |       163127   |    119055   | 399160           |     0.00406  |     0.006405 |
| Tampa, FL                  | FL          |    205549   |       181725   |    107710   | 381942           |     0.003955 |     0.01023  |
| Winnemucca, NV             | NV          |    205497   |       174192   |    174192   | 336912           |     0.002192 |     0.004492 |
| Clearlake, CA              | CA          |    205168   |       168448   |    118645   | 350307           |     0.00192  |     0.007868 |
| Minot, ND                  | ND          |    205066   |       196605   |    171723   | 258379           |     0.001357 |     0.005416 |
| Visalia, CA                | CA          |    204901   |       189842   |    103929   | 352414           |     0.004036 |     0.010765 |
| Auburn, AL                 | AL          |    204593   |       183421   |    138582   | 335395           |     0.002958 |     0.0041   |
| Faribault, MN              | MN          |    204424   |       185738   |    129470   | 335130           |     0.003168 |     0.00607  |
| Watertown, WI              | WI          |    203345   |       174185   |    154932   | 348919           |     0.002446 |     0.003966 |
| Lake Havasu City, AZ       | AZ          |    202812   |       180939   |    101117   | 362186           |     0.004054 |     0.010598 |
| Palm Bay, FL               | FL          |    202162   |       183656   |    109397   | 357536           |     0.003738 |     0.011178 |
| Casper, WY                 | WY          |    201317   |       188208   |    167657   | 301852           |     0.001899 |     0.003552 |
| Pullman, WA                | WA          |    200982   |       175430   |    137835   | 317914           |     0.001935 |     0.005936 |
| Savannah, GA               | GA          |    200707   |       181410   |    126606   | 352780           |     0.003345 |     0.00525  |
| Rock Springs, WY           | WY          |    200371   |       193044   |    171219   | 285972           |     0.001639 |     0.003058 |
| Hobbs, NM                  | NM          |    200306   |       187537   |    183442   | 256098           |     0.000132 |     0.006072 |
| Brainerd, MN               | MN          |    200150   |       167348   |    143218   | 339222           |     0.002347 |     0.00529  |
| Albuquerque, NM            | NM          |    200010   |       179396   |    136446   | 339931           |     0.003033 |     0.005384 |
| Gettysburg, PA             | PA          |    198783   |       189643   |    104911   | 322343           |     0.003751 |     0.005327 |
| Athens, GA                 | GA          |    198002   |       170249   |    137049   | 356443           |     0.003188 |     0.005609 |
| Lake Charles, LA           | LA          |    197946   |       195551   |    183024   | 217716           |    -9.4e-05  |     0.003092 |
| Ca-¦on City, CO            | CO          |    197728   |       158500   |    158500   | 332913           |     0.002446 |     0.00492  |
| Deltona, FL                | FL          |    197698   |       178211   |    105882   | 351003           |     0.003727 |     0.010456 |
| Hagerstown, MD             | MD          |    197268   |       181122   |    130103   | 313332           |     0.002943 |     0.006793 |
| Keene, NH                  | NH          |    196937   |       172302   |    104794   | 370151           |     0.004216 |     0.006411 |
| Baraboo, WI                | WI          |    196286   |       165494   |    150686   | 321583           |     0.002207 |     0.004136 |
| Blackfoot, ID              | ID          |    196003   |       145710   |    145710   | 378786           |     0.003119 |     0.006636 |
| Rochester, MN              | MN          |    195398   |       163721   |    134029   | 323702           |     0.00296  |     0.004739 |
| Brunswick, GA              | GA          |    195350   |       171708   |    141013   | 322490           |     0.002712 |     0.006222 |
| Las Cruces, NM             | NM          |    195331   |       177597   |    151350   | 284502           |     0.002067 |     0.007081 |
| Red Wing, MN               | MN          |    195190   |       176157   |    122081   | 313663           |     0.003147 |     0.004798 |
| Staunton, VA               | VA          |    194878   |       163035   |    153218   | 316550           |     0.002256 |     0.003798 |
| Sioux Falls, SD            | SD          |    194455   |       163491   |    146477   | 329005           |     0.002687 |     0.003759 |
| College Station, TX        | TX          |    194111   |       158650   |    150748   | 300626           |     0.002286 |     0.00354  |
| Iowa City, IA              | IA          |    194011   |       170839   |    163740   | 287473           |     0.001812 |     0.002496 |
| El Centro, CA              | CA          |    193810   |       181980   |     93397.2 | 368707           |     0.004562 |     0.009413 |
| St. Cloud, MN              | MN          |    193584   |       191238   |    126963   | 301924           |     0.001409 |     0.007008 |
| Punta Gorda, FL            | FL          |    193425   |       171105   |     92253.9 | 384652           |     0.003871 |     0.011732 |
| Roseburg, OR               | OR          |    191869   |       171552   |    101040   | 334492           |     0.003995 |     0.0067   |
| La Crosse, WI              | WI          |    191591   |       169797   |    140211   | 314620           |     0.002685 |     0.003948 |
| Twin Falls, ID             | ID          |    191326   |       151938   |    121082   | 372302           |     0.003505 |     0.007248 |
| Ithaca, NY                 | NY          |    190919   |       177468   |     89273.9 | 335088           |     0.004403 |     0.005942 |
| Houston, TX                | TX          |    190721   |       155491   |    124554   | 312318           |     0.002932 |     0.004739 |
| Fayetteville, AR           | AR          |    190565   |       164443   |    125645   | 358484           |     0.003502 |     0.006315 |
| Yakima, WA                 | WA          |    189941   |       154242   |    114971   | 342087           |     0.003596 |     0.005605 |
| Rutland, VT                | VT          |    189707   |       178039   |    101235   | 300426           |     0.003627 |     0.005643 |
| Sierra Vista, AZ           | AZ          |    189678   |       196741   |    145971   | 256044           |     0.000831 |     0.005574 |
| Hammond, LA                | LA          |    189371   |       188659   |    153324   | 241970           |     0.000465 |     0.006582 |
| Evanston, WY               | WY          |    189245   |       169369   |    153911   | 317038           |     0.002351 |     0.004341 |
| Appleton, WI               | WI          |    189231   |       164011   |    145169   | 333083           |     0.00238  |     0.004241 |
| Mankato, MN                | MN          |    188577   |       172020   |    150091   | 294872           |     0.002074 |     0.004197 |
| Jamestown, ND              | ND          |    188574   |       187120   |    176628   | 219065           |     0.000524 |     0.003931 |
| Aberdeen, WA               | WA          |    188400   |       159980   |    125207   | 332936           |     0.002218 |     0.007129 |
| East Stroudsburg, PA       | PA          |    187813   |       171981   |    138469   | 301763           |     0.001858 |     0.007432 |
| Pocatello, ID              | ID          |    187510   |       153940   |    129046   | 339880           |     0.002624 |     0.007236 |
| Lebanon, PA                | PA          |    187054   |       170395   |    152737   | 303268           |     0.002279 |     0.004093 |
| La Grande, OR              | OR          |    186943   |       161482   |    141158   | 319600           |     0.002268 |     0.004743 |
| Chambersburg, PA           | PA          |    186537   |       176043   |    119245   | 279147           |     0.002826 |     0.005979 |
| Brookings, SD              | SD          |    186286   |       160011   |    154595   | 301354           |     0.002218 |     0.003269 |
| Lawrence, KS               | KS          |    186255   |       159850   |    135872   | 320265           |     0.002849 |     0.003927 |
| Gainesville, FL            | FL          |    186042   |       171190   |    107246   | 302979           |     0.003362 |     0.00743  |
| Great Falls, MT            | MT          |    185220   |       158019   |    146174   | 330536           |     0.002581 |     0.004822 |
| Harrisburg, PA             | PA          |    185019   |       173120   |    120034   | 297744           |     0.003037 |     0.003702 |
| Columbia, MO               | MO          |    184927   |       157928   |    148251   | 307966           |     0.002429 |     0.003975 |
| Pahrump, NV                | NV          |    184150   |       142953   |     95416.8 | 352902           |     0.003002 |     0.008509 |
| Elizabeth City, NC         | NC          |    184032   |       189874   |    144635   | 258371           |     0.000992 |     0.005349 |
| Sulphur Springs, TX        | TX          |    183943   |       157544   |    157544   | 282586           |     0.001561 |     0.005059 |
| Stephenville, TX           | TX          |    183687   |       142987   |    135760   | 332734           |     0.002848 |     0.004853 |
| York, PA                   | PA          |    182943   |       172816   |    117898   | 296601           |     0.003069 |     0.005306 |
| Tallahassee, FL            | FL          |    182879   |       170326   |    113130   | 277602           |     0.002937 |     0.006501 |
| Chattanooga, TN            | TN          |    182874   |       157321   |    120343   | 315522           |     0.003199 |     0.004534 |
| Holland, MI                | MI          |    182238   |       154384   |    122018   | 332242           |     0.003157 |     0.005748 |
| Baton Rouge, LA            | LA          |    181854   |       180634   |    133855   | 241421           |     0.001945 |     0.004512 |
| Lexington, KY              | KY          |    181782   |       155906   |    127487   | 312718           |     0.002997 |     0.003657 |
| Pierre, SD                 | SD          |    181589   |       161330   |    147972   | 282077           |     0.002083 |     0.003601 |
| Columbus, OH               | OH          |    181560   |       152241   |    128410   | 317223           |     0.003011 |     0.004685 |
| Hermiston, OR              | OR          |    181532   |       156515   |    131733   | 301712           |     0.00218  |     0.005151 |
| Knoxville, TN              | TN          |    180869   |       150542   |    107208   | 352076           |     0.003966 |     0.005117 |
| Grand Rapids, MI           | MI          |    180661   |       146586   |    118174   | 338550           |     0.003319 |     0.005287 |
| Starkville, MS             | MS          |    180589   |       168200   |    162608   | 241582           |     0.001203 |     0.004454 |
| Eau Claire, WI             | WI          |    180276   |       149820   |    135140   | 306255           |     0.002375 |     0.004218 |
| Sheboygan, WI              | WI          |    180021   |       177218   |    121880   | 305815           |     0.001813 |     0.006166 |
| Pensacola, FL              | FL          |    179574   |       157440   |    111286   | 308153           |     0.003299 |     0.007555 |
| Grand Forks, ND            | MN          |    179524   |       156665   |    152981   | 259677           |     0.001758 |     0.003066 |
| Fergus Falls, MN           | MN          |    178875   |       145039   |    138652   | 310140           |     0.002667 |     0.004238 |
| Mountain Home, ID          | ID          |    178618   |       142551   |    111903   | 347241           |     0.002958 |     0.008171 |
| Houma, LA                  | LA          |    178611   |       175345   |    165398   | 209797           |     0.00017  |     0.005005 |
| Des Moines, IA             | IA          |    178554   |       153121   |    119637   | 284525           |     0.002886 |     0.003292 |
| Roanoke, VA                | VA          |    178318   |       159377   |    146792   | 286523           |     0.001949 |     0.004604 |
| Fort Morgan, CO            | CO          |    178086   |       126775   |    120636   | 327025           |     0.003257 |     0.004845 |
| Kansas City, MO            | MO          |    178080   |       148630   |    116054   | 311990           |     0.003303 |     0.004439 |
| Lewisburg, PA              | PA          |    177810   |       155360   |    152722   | 278275           |     0.001988 |     0.003519 |
| Farmington, NM             | NM          |    177678   |       159656   |    150606   | 260435           |     0.001663 |     0.004214 |
| Racine, WI                 | WI          |    177667   |       162184   |    126752   | 293331           |     0.001969 |     0.005381 |
| San Antonio, TX            | TX          |    177489   |       148597   |    109574   | 300694           |     0.002999 |     0.004811 |
| Red Bluff, CA              | CA          |    177486   |       135332   |    114090   | 327692           |     0.003315 |     0.0058   |
| Glens Falls, NY            | NY          |    177052   |       166658   |     88782.4 | 292041           |     0.003984 |     0.005274 |
| Reading, PA                | PA          |    176796   |       165969   |    106129   | 298628           |     0.003453 |     0.005265 |
| Huntsville, TX             | TX          |    176444   |       143388   |    139302   | 281090           |     0.002041 |     0.004404 |
| Willmar, MN                | MN          |    176402   |       165342   |    137147   | 266815           |     0.00159  |     0.004437 |
| Yankton, SD                | SD          |    176164   |       152391   |    140720   | 267055           |     0.002062 |     0.004126 |
| Cincinnati, OH             | OH          |    175869   |       154546   |    130767   | 295717           |     0.002721 |     0.00442  |
| Blacksburg, VA             | VA          |    175572   |       164124   |    101137   | 275368           |     0.003351 |     0.004976 |
| Bemidji, MN                | MN          |    175254   |       180929   |    129043   | 253036           |     0.001114 |     0.007822 |
| Greenville, SC             | SC          |    175000   |       145816   |    120716   | 303241           |     0.00306  |     0.004136 |
| Gainesville, TX            | TX          |    174984   |       129461   |    122418   | 315694           |     0.002914 |     0.00525  |
| Lincoln, NE                | NE          |    174872   |       149241   |    122057   | 289265           |     0.002879 |     0.003742 |
| Omaha, NE                  | NE          |    174827   |       148573   |    120092   | 295170           |     0.003    |     0.004296 |
| Green Bay, WI              | WI          |    174487   |       147148   |    118188   | 326489           |     0.003376 |     0.004962 |
| Pecos, TX                  | TX          |    174127   |       158523   |    152998   | 282195           |     3e-05    |     0.009587 |
| Safford, AZ                | AZ          |    174124   |       163384   |    104329   | 295566           |     0.003479 |     0.008693 |
| Clarksville, TN            | TN          |    173485   |       153258   |    114746   | 292509           |     0.003086 |     0.004407 |
| Othello, WA                | WA          |    173398   |       145696   |    128405   | 304080           |     0.002438 |     0.005288 |
| Las Vegas, NM              | NM          |    173337   |       160425   |    148913   | 238609           |     0.001319 |     0.00585  |
| Beaver Dam, WI             | WI          |    173303   |       148822   |    131149   | 305028           |     0.002384 |     0.004514 |
| Jacksonville, NC           | NC          |    173039   |       163937   |    129335   | 284170           |     0.002615 |     0.004962 |
| Craig, CO                  | CO          |    172998   |       157063   |    104968   | 296161           |     0.003468 |     0.004374 |
| Angola, IN                 | IN          |    172748   |       141768   |    131703   | 299757           |     0.002488 |     0.004771 |
| Ontario, OR                | OR          |    172533   |       135756   |     86295.2 | 363935           |     0.004763 |     0.008039 |
| Lynchburg, VA              | VA          |    172277   |       156676   |    114325   | 276646           |     0.002952 |     0.004827 |
| Oshkosh, WI                | WI          |    171842   |       155137   |    125819   | 286744           |     0.002041 |     0.005303 |
| Kearney, NE                | NE          |    171547   |       151537   |    128671   | 287197           |     0.00262  |     0.00391  |
| Yuma, AZ                   | AZ          |    171109   |       151828   |    114385   | 279448           |     0.002865 |     0.010615 |
| Natchitoches, LA           | LA          |    170564   |       169185   |    159213   | 192916           |    -7.2e-05  |     0.005037 |
| Burlington, NC             | NC          |    170404   |       143078   |    143010   | 287701           |     0.002321 |     0.004715 |
| St. Louis, MO              | MO          |    170055   |       158294   |    118072   | 261627           |     0.002659 |     0.004302 |
| Lakeland, FL               | FL          |    170004   |       149910   |     93924.7 | 317880           |     0.003807 |     0.010399 |
| Bloomington, IL            | IL          |    169834   |       163551   |    136171   | 245524           |     0.001959 |     0.003797 |
| Menomonie, WI              | WI          |    169285   |       136498   |    124180   | 295091           |     0.002561 |     0.004737 |
| Seneca, SC                 | SC          |    169236   |       147820   |    135821   | 279292           |     0.002114 |     0.00536  |
| Warrensburg, MO            | MO          |    169212   |       143390   |    134621   | 269019           |     0.00209  |     0.004092 |
| Susanville, CA             | CA          |    168743   |       181425   |    112430   | 229661           |     0.000615 |     0.007381 |
| Athens, TX                 | TX          |    168692   |       136443   |    132080   | 278255           |     0.00216  |     0.005561 |
| Owatonna, MN               | MN          |    168611   |       142390   |    125371   | 283746           |     0.002291 |     0.004439 |
| DeRidder, LA               | LA          |    168345   |       162247   |    147013   | 225161           |     0.00072  |     0.007746 |
| Burley, ID                 | ID          |    168337   |       130942   |    112406   | 323389           |     0.003004 |     0.006347 |
| Columbus, IN               | IN          |    168270   |       160902   |    125992   | 265333           |     0.001326 |     0.007312 |
| Stevens Point, WI          | WI          |    168243   |       137963   |    130741   | 302740           |     0.00275  |     0.003899 |
| Bloomsburg, PA             | PA          |    167976   |       160902   |    107000   | 233641           |     0.002617 |     0.003882 |
| Dubuque, IA                | IA          |    167819   |       147770   |    143794   | 263734           |     0.001975 |     0.003106 |
| Hays, KS                   | KS          |    167571   |       158083   |    153616   | 232160           |     0.001277 |     0.003356 |
| Ames, IA                   | IA          |    167317   |       141800   |    135833   | 253188           |     0.001995 |     0.00311  |
| Manhattan, KS              | KS          |    167256   |       151448   |    139541   | 258618           |     0.002049 |     0.002921 |
| Bloomington, IN            | IN          |    167229   |       138843   |    117973   | 288262           |     0.002968 |     0.003919 |
| Lafayette, LA              | LA          |    166747   |       166721   |    126963   | 204607           |     0.001407 |     0.004497 |
| St. Marys, GA              | GA          |    166670   |       151370   |     93019.6 | 300506           |     0.003923 |     0.00672  |
| Vineland, NJ               | NJ          |    166399   |       150294   |    100096   | 265989           |     0.003255 |     0.00815  |
| Victoria, TX               | TX          |    166353   |       156367   |    148131   | 215181           |     0.000988 |     0.003123 |
| Huntsville, AL             | AL          |    165866   |       164463   |     79113.8 | 307986           |     0.004096 |     0.009855 |
| Lewiston, ME               | ME          |    165849   |       142698   |     88828.9 | 315474           |     0.004253 |     0.006284 |
| Monroe, MI                 | MI          |    165675   |       161690   |    112213   | 254089           |     0.001757 |     0.008455 |
| Gallup, NM                 | NM          |    165474   |       151927   |    147377   | 218219           |     0.00117  |     0.004189 |
| Albemarle, NC              | NC          |    165039   |       133996   |    133709   | 295411           |     0.002626 |     0.005586 |
| Cambridge, MD              | MD          |    164769   |       152230   |     79841.9 | 268326           |     0.004051 |     0.008249 |
| Hutchinson, MN             | MN          |    164650   |       141972   |    110517   | 283299           |     0.002522 |     0.005626 |
| Birmingham, AL             | AL          |    164416   |       149027   |    114966   | 251892           |     0.002621 |     0.004567 |
| Crossville, TN             | TN          |    164326   |       141187   |    104877   | 302851           |     0.003495 |     0.007975 |
| Cleveland, TN              | TN          |    163848   |       138236   |    101698   | 298457           |     0.003604 |     0.005043 |
| Ludington, MI              | MI          |    163644   |       153974   |    116694   | 249386           |     0.002237 |     0.007764 |
| Louisville, KY             | KY          |    163555   |       140252   |    113944   | 269643           |     0.002884 |     0.003592 |
| Killeen, TX                | TX          |    163063   |       140745   |    131366   | 263866           |     0.001875 |     0.005129 |
| Winona, MN                 | MN          |    163004   |       141146   |    133866   | 268486           |     0.002312 |     0.00328  |
| Pueblo, CO                 | CO          |    162961   |       128220   |    108372   | 298054           |     0.003173 |     0.005595 |
| Mineral Wells, TX          | TX          |    162624   |       130084   |    120683   | 283083           |     0.00254  |     0.00563  |
| Augusta, ME                | ME          |    162222   |       140268   |     86974.4 | 303417           |     0.004159 |     0.006153 |
| Klamath Falls, OR          | OR          |    162180   |       145924   |     80037.8 | 302600           |     0.004432 |     0.007338 |
| Tyler, TX                  | TX          |    162001   |       131536   |    124846   | 266989           |     0.002292 |     0.00461  |
| Ocala, FL                  | FL          |    161824   |       141656   |     97082.2 | 286042           |     0.00289  |     0.010048 |
| Winston, NC                | NC          |    161780   |       141765   |    119799   | 272058           |     0.002741 |     0.004593 |
| Warsaw, IN                 | IN          |    161604   |       137701   |    112894   | 271351           |     0.002941 |     0.005802 |
| Vermillion, SD             | SD          |    161548   |       138115   |    137721   | 274019           |     0.002276 |     0.004096 |
| Shelbyville, TN            | TN          |    161539   |       120160   |     97367.7 | 322505           |     0.003994 |     0.006401 |
| Indianapolis, IN           | IN          |    160882   |       130292   |    116810   | 283408           |     0.002945 |     0.00459  |
| Niles, MI                  | MI          |    160712   |       144367   |    114334   | 259531           |     0.002745 |     0.00548  |
| Marion, NC                 | NC          |    160381   |       135164   |    135164   | 255682           |     0.00199  |     0.005241 |
| Cornelia, GA               | GA          |    160344   |       128444   |    102648   | 312536           |     0.002954 |     0.006921 |
| Fond du Lac, WI            | WI          |    160035   |       138921   |    128164   | 273017           |     0.002245 |     0.004148 |
| Hinesville, GA             | GA          |    159386   |       144318   |    124114   | 253288           |     0.002393 |     0.006501 |
| Mitchell, SD               | SD          |    158981   |       137440   |    137440   | 246214           |     0.001937 |     0.003724 |
| Sherman, TX                | TX          |    158803   |       116209   |    108286   | 298191           |     0.003193 |     0.005668 |
| El Campo, TX               | TX          |    158589   |       130267   |    121633   | 239175           |     0.001833 |     0.004695 |
| Ruston, LA                 | LA          |    158546   |       147600   |    101632   | 215119           |     0.00249  |     0.003493 |
| Statesboro, GA             | GA          |    157793   |       139546   |    113767   | 279172           |     0.002304 |     0.005235 |
| Kalamazoo, MI              | MI          |    157777   |       137854   |    114741   | 262073           |     0.002506 |     0.00491  |
| Andrews, TX                | TX          |    157759   |       138508   |    117212   | 248241           |     0.002478 |     0.004426 |
| Homosassa Springs, FL      | FL          |    157720   |       137327   |     92430.6 | 281771           |     0.00355  |     0.009684 |
| Jefferson City, MO         | MO          |    156633   |       135122   |    124692   | 258546           |     0.002156 |     0.004196 |
| Nogales, AZ                | AZ          |    156194   |       141232   |     77123.6 | 273797           |     0.004218 |     0.009795 |
| Tullahoma, TN              | TN          |    155898   |       123654   |     93872.8 | 305678           |     0.003946 |     0.005021 |
| Corpus Christi, TX         | TX          |    155847   |       138888   |    117007   | 225981           |     0.00205  |     0.004018 |
| Lewisburg, TN              | TN          |    155235   |       109523   |     88151.7 | 318304           |     0.004287 |     0.006079 |
| Cookeville, TN             | TN          |    155227   |       128288   |     97570.8 | 283252           |     0.003561 |     0.005051 |
| San Angelo, TX             | TX          |    154553   |       129614   |    129614   | 242259           |     0.002078 |     0.004119 |
| Morgantown, WV             | WV          |    154217   |       149079   |    103574   | 214576           |     0.002449 |     0.005474 |
| Fayetteville, NC           | NC          |    154160   |       141860   |    112528   | 251176           |     0.002638 |     0.004479 |
| Morristown, TN             | TN          |    154111   |       129419   |     97868.4 | 288786           |     0.003618 |     0.005805 |
| Columbia, SC               | SC          |    153958   |       138907   |    111633   | 247877           |     0.00266  |     0.004329 |
| Eagle Pass, TX             | TX          |    153555   |       140114   |    129139   | 224549           |     0.001786 |     0.004894 |
| Cedar Rapids, IA           | IA          |    153240   |       139711   |    112419   | 230288           |     0.002397 |     0.002876 |
| New Bern, NC               | NC          |    153239   |       140544   |    101692   | 254839           |     0.003072 |     0.00522  |
| Sanford, NC                | NC          |    153081   |       127717   |    102967   | 286550           |     0.003424 |     0.005794 |
| Little Rock, AR            | AR          |    152913   |       144147   |    105605   | 222292           |     0.002486 |     0.003222 |
| Cleveland, MS              | MS          |    152608   |       155369   |    118697   | 171197           |    -0.000894 |     0.007977 |
| Lafayette, IN              | IN          |    152488   |       125154   |    108509   | 271800           |     0.003107 |     0.00448  |
| Bangor, ME                 | ME          |    152246   |       136430   |     85583.2 | 265209           |     0.003791 |     0.005549 |
| Greensboro, NC             | NC          |    152083   |       131239   |    112337   | 255818           |     0.002748 |     0.004484 |
| Cullman, AL                | AL          |    151238   |       133939   |     98131   | 245411           |     0.003061 |     0.004611 |
| Bowling Green, KY          | KY          |    151137   |       127519   |    100545   | 260905           |     0.003165 |     0.004107 |
| Spartanburg, SC            | SC          |    150876   |       122505   |    110480   | 272076           |     0.002991 |     0.004978 |
| Detroit, MI                | MI          |    150477   |       144456   |     77805.6 | 254400           |     0.002279 |     0.008854 |
| Springfield, MO            | MO          |    150406   |       125889   |    108907   | 259517           |     0.002403 |     0.005062 |
| Champaign, IL              | IL          |    150321   |       143661   |    105166   | 224206           |     0.002513 |     0.003986 |
| Johnson City, TN           | TN          |    150277   |       127389   |     92165.1 | 271382           |     0.003585 |     0.004414 |
| Greenville, NC             | NC          |    150237   |       139236   |    121521   | 238948           |     0.001794 |     0.00471  |
| Deming, NM                 | NM          |    150018   |       156680   |    111321   | 166178           |    -0.000196 |     0.007412 |
| Branson, MO                | MO          |    149906   |       126500   |    110064   | 249834           |     0.002129 |     0.006026 |
| Laredo, TX                 | TX          |    149902   |       128904   |    121424   | 213504           |     0.001692 |     0.003401 |
| Silver City, NM            | NM          |    149828   |       134656   |    131564   | 215069           |     0.00098  |     0.005959 |
| Cape Girardeau, MO         | MO          |    149700   |       137010   |    122290   | 220700           |     0.001584 |     0.004683 |
| Aberdeen, SD               | SD          |    149252   |       138645   |    123894   | 227871           |     0.001993 |     0.003442 |
| Wausau, WI                 | WI          |    149131   |       130324   |    119165   | 252710           |     0.0022   |     0.004442 |
| Elizabethtown, KY          | KY          |    149029   |       133316   |    104885   | 249487           |     0.002815 |     0.005696 |
| Fort Leonard Wood, MO      | MO          |    148835   |       143216   |    122144   | 218328           |     0.001401 |     0.004689 |
| Williamsport, PA           | PA          |    148810   |       138158   |     99814.9 | 221396           |     0.002668 |     0.004001 |
| Odessa, TX                 | TX          |    148805   |       128262   |    101262   | 246494           |     0.002954 |     0.005385 |
| Marshall, MN               | MN          |    148738   |       138147   |    130999   | 210383           |     0.001546 |     0.004022 |
| Celina, OH                 | OH          |    148717   |       134307   |    116139   | 258793           |     0.00259  |     0.004676 |
| Sumter, SC                 | SC          |    148550   |       143062   |    121111   | 204954           |     0.001128 |     0.004286 |
| Lake City, FL              | FL          |    148465   |       127534   |     84794.9 | 265175           |     0.003755 |     0.008455 |
| Shreveport, LA             | LA          |    148304   |       148342   |    125360   | 175125           |     0.001035 |     0.004321 |
| Oklahoma City, OK          | OK          |    148212   |       130478   |     94777.1 | 239204           |     0.003089 |     0.003375 |
| Warner Robins, GA          | GA          |    148157   |       132360   |    111362   | 245190           |     0.00264  |     0.004049 |
| Hattiesburg, MS            | MS          |    148041   |       132078   |    129939   | 207962           |     0.001508 |     0.003657 |
| Memphis, TN                | TN          |    147995   |       127964   |    106791   | 240380           |     0.002386 |     0.005255 |
| Tuscaloosa, AL             | AL          |    147827   |       137062   |    104766   | 215430           |     0.002375 |     0.003526 |
| Rochester, NY              | NY          |    147823   |       127739   |    100834   | 261753           |     0.003183 |     0.0046   |
| Price, UT                  | UT          |    147791   |       123226   |    123226   | 268047           |     0.002582 |     0.005313 |
| Richmond, KY               | KY          |    147357   |       127879   |     96690.9 | 254392           |     0.003233 |     0.004086 |
| Alice, TX                  | TX          |    147071   |       147770   |    117566   | 159101           |    -0.000999 |     0.006286 |
| Tulsa, OK                  | OK          |    147067   |       127481   |    104710   | 243345           |     0.002817 |     0.00383  |
| Duluth, MN                 | MN          |    147057   |       131163   |    112498   | 244891           |     0.002584 |     0.004423 |
| Raymondville, TX           | TX          |    146242   |       126702   |    123966   | 234215           |     0.000969 |     0.008099 |
| Clovis, NM                 | NM          |    146055   |       143755   |    132177   | 166312           |     0.000224 |     0.004475 |
| Uvalde, TX                 | TX          |    145978   |       125427   |    119801   | 197200           |     0.001349 |     0.004754 |
| Nacogdoches, TX            | TX          |    145801   |       129252   |    124700   | 208214           |     0.001569 |     0.003937 |
| Augusta, GA                | GA          |    145766   |       131772   |     96961.7 | 239314           |     0.00302  |     0.004259 |
| Del Rio, TX                | TX          |    145615   |       131114   |    118489   | 214047           |     0.001478 |     0.004566 |
| Rochelle, IL               | IL          |    145573   |       144344   |    106535   | 216644           |     0.001349 |     0.006939 |
| Buffalo, NY                | NY          |    145329   |       122338   |     86196.9 | 268849           |     0.003776 |     0.004213 |
| Findlay, OH                | OH          |    144860   |       131938   |    113132   | 226431           |     0.002212 |     0.004713 |
| Cleveland, OH              | OH          |    144819   |       133496   |    109840   | 236080           |     0.00227  |     0.004649 |
| Montgomery, AL             | AL          |    144570   |       135689   |    117181   | 204707           |     0.001838 |     0.003903 |
| Janesville, WI             | WI          |    144562   |       112947   |    108228   | 277504           |     0.003064 |     0.004007 |
| Newberry, SC               | SC          |    144424   |       128759   |    116343   | 213200           |     0.001522 |     0.005506 |
| Stillwater, OK             | OK          |    144269   |       128605   |     97291.1 | 231293           |     0.002894 |     0.003902 |
| Garden City, KS            | KS          |    143802   |       123302   |    115841   | 226087           |     0.002191 |     0.00331  |
| Waco, TX                   | TX          |    143695   |       111023   |    104457   | 252165           |     0.002645 |     0.005331 |
| Mountain Home, AR          | AR          |    143695   |       135137   |     92501.3 | 222909           |     0.002947 |     0.00481  |
| Bardstown, KY              | KY          |    143416   |       120518   |     95807.7 | 257915           |     0.003308 |     0.004443 |
| Shawano, WI                | WI          |    143225   |       126202   |    112489   | 260298           |     0.002405 |     0.00526  |
| Hickory, NC                | NC          |    142625   |       119585   |     96904.9 | 258539           |     0.003285 |     0.005137 |
| McPherson, KS              | KS          |    142613   |       123642   |    122551   | 214820           |     0.001835 |     0.003046 |
| Port Lavaca, TX            | TX          |    142517   |       121377   |    116164   | 202816           |     0.001569 |     0.004272 |
| Greensburg, IN             | IN          |    142363   |       118328   |    114515   | 246093           |     0.002542 |     0.004203 |
| Valdosta, GA               | GA          |    142314   |       132058   |    117821   | 214027           |     0.001865 |     0.006071 |
| Jacksonville, TX           | TX          |    142170   |       118453   |    111775   | 236969           |     0.002066 |     0.005465 |
| Okeechobee, FL             | FL          |    142044   |       118611   |     80462.7 | 282020           |     0.004176 |     0.009087 |
| Effingham, IL              | IL          |    142003   |       128697   |    116588   | 206099           |     0.001564 |     0.004177 |
| Bay City, TX               | TX          |    141889   |       122300   |    117336   | 198363           |     0.00164  |     0.003978 |
| Grand Island, NE           | NE          |    141793   |       121552   |     99803.6 | 247377           |     0.003016 |     0.003406 |
| Rolla, MO                  | MO          |    141758   |       125972   |    125177   | 219785           |     0.001849 |     0.004033 |
| Sterling, CO               | CO          |    141711   |       112359   |     95867.6 | 246783           |     0.003164 |     0.004436 |
| Gulfport, MS               | MS          |    141583   |       121688   |    109323   | 215114           |     0.001875 |     0.004354 |
| Michigan City, IN          | IN          |    141543   |       118590   |    114301   | 242861           |     0.002381 |     0.00423  |
| Opelousas, LA              | LA          |    141371   |       137410   |    126808   | 168035           |     4e-06    |     0.007136 |
| Tifton, GA                 | GA          |    141225   |       131668   |    111494   | 199927           |     0.001886 |     0.004273 |
| Frankfort, KY              | KY          |    141156   |       125594   |     97950.9 | 245454           |     0.003053 |     0.004416 |
| Columbus, NE               | NE          |    140966   |       125443   |     75602.7 | 267606           |     0.004211 |     0.004093 |
| El Paso, TX                | TX          |    140959   |       132417   |     93253.9 | 225660           |     0.002842 |     0.005055 |
| Hot Springs, AR            | AR          |    140651   |       126947   |     89594.6 | 238654           |     0.003245 |     0.006147 |
| Pittsburgh, PA             | PA          |    140623   |       125755   |     88149.1 | 217855           |     0.003022 |     0.003716 |
| Lubbock, TX                | TX          |    140604   |       130842   |     87245.7 | 211380           |     0.00289  |     0.005386 |
| Kankakee, IL               | IL          |    140603   |       131300   |    114597   | 212257           |     0.001596 |     0.005915 |
| Huron, SD                  | SD          |    140567   |       129016   |    128654   | 188617           |     0.001165 |     0.00464  |
| Milledgeville, GA          | GA          |    140510   |       127077   |    100521   | 224811           |     0.001895 |     0.005713 |
| Columbus, GA               | GA          |    140299   |       136989   |    111846   | 200074           |     0.001274 |     0.006898 |
| Elkhart, IN                | IN          |    140085   |       116585   |    101505   | 251055           |     0.002853 |     0.005128 |
| Plymouth, IN               | IN          |    139786   |       118612   |     97468.4 | 245068           |     0.003082 |     0.004074 |
| Amarillo, TX               | TX          |    139645   |       121343   |    115983   | 210733           |     0.001834 |     0.003599 |
| Troy, AL                   | AL          |    139434   |       133549   |    128085   | 168658           |     0.000565 |     0.003672 |
| Alamogordo, NM             | NM          |    139334   |       121612   |    120327   | 231280           |     0.00204  |     0.004648 |
| Worthington, MN            | MN          |    139305   |       116053   |    115956   | 227822           |     0.002241 |     0.004564 |
| Sandusky, OH               | OH          |    139272   |       127502   |    107200   | 223737           |     0.002472 |     0.004957 |
| Jasper, IN                 | IN          |    139186   |       117163   |    111694   | 233097           |     0.00236  |     0.003607 |
| Albertville, AL            | AL          |    139122   |       117398   |    101752   | 233375           |     0.002434 |     0.005521 |
| Fort Polk South, LA        | LA          |    139045   |       136218   |    122739   | 168287           |     0.000806 |     0.007132 |
| Midland, MI                | MI          |    138994   |       125747   |    106382   | 228938           |     0.002497 |     0.005761 |
| Palestine, TX              | TX          |    138896   |       122153   |    112418   | 217677           |     0.001725 |     0.005128 |
| Lansing, MI                | MI          |    138338   |       124245   |     96453.7 | 234119           |     0.002865 |     0.005281 |
| Akron, OH                  | OH          |    138101   |       125055   |    106998   | 225386           |     0.002425 |     0.004238 |
| New Ulm, MN                | MN          |    137623   |       119159   |    113676   | 232223           |     0.002373 |     0.003708 |
| Manitowoc, WI              | WI          |    137572   |       121726   |    102239   | 247796           |     0.002953 |     0.005212 |
| Calhoun, GA                | GA          |    137446   |       106369   |     88321.4 | 269934           |     0.003094 |     0.005824 |
| Wapakoneta, OH             | OH          |    137065   |       118278   |    109607   | 226555           |     0.002159 |     0.003933 |
| Sayre, PA                  | PA          |    136995   |       131250   |    110591   | 193412           |     0.001496 |     0.005725 |
| Urbana, OH                 | OH          |    136652   |       117953   |    100587   | 238697           |     0.002891 |     0.004762 |
| Beeville, TX               | TX          |    136601   |       117140   |    111861   | 196793           |     0.001077 |     0.005489 |
| Lock Haven, PA             | PA          |    136543   |       128334   |    114145   | 189404           |     0.001283 |     0.004346 |
| Jackson, MS                | MS          |    136463   |       124726   |    106065   | 205126           |     0.002191 |     0.004337 |
| Scranton, PA               | PA          |    136270   |       126665   |     88273.9 | 220488           |     0.003066 |     0.005043 |
| Norfolk, NE                | NE          |    136167   |       114485   |     86143.8 | 242557           |     0.003439 |     0.003862 |
| Bellefontaine, OH          | OH          |    135994   |       113460   |     98094.6 | 239539           |     0.002966 |     0.004717 |
| Kingsport, TN              | TN          |    135802   |       119682   |     93195   | 235380           |     0.003097 |     0.004633 |
| Arcadia, FL                | FL          |    135721   |       116642   |     66953.3 | 261237           |     0.004321 |     0.010353 |
| Athens, TN                 | TN          |    135479   |       106171   |    101608   | 248624           |     0.002966 |     0.004881 |
| Auburn, IN                 | IN          |    135349   |       111376   |    104344   | 240583           |     0.002559 |     0.004177 |
| Mount Pleasant, TX         | TX          |    135293   |       108528   |     99162.4 | 229164           |     0.002421 |     0.005511 |
| Longview, TX               | TX          |    135220   |       123522   |     83117.5 | 211064           |     0.003086 |     0.004543 |
| Butte, MT                  | MT          |    134835   |       101643   |     98196.8 | 271262           |     0.003376 |     0.005948 |
| Dayton, TN                 | TN          |    134630   |       108347   |     75590.5 | 248057           |     0.003968 |     0.005436 |
| Washington Court House, OH | OH          |    134602   |       115665   |     97965.9 | 227560           |     0.002817 |     0.004996 |
| Fort Wayne, IN             | IN          |    134560   |       109498   |    100670   | 245239           |     0.002958 |     0.004208 |
| North Platte, NE           | NE          |    134134   |       118157   |    108087   | 208545           |     0.001959 |     0.003772 |
| Portales, NM               | NM          |    134115   |       134280   |    119495   | 146357           |     0.000179 |     0.005613 |
| Coldwater, MI              | MI          |    134046   |       126272   |    104506   | 193709           |     0.001906 |     0.005834 |
| Lebanon, MO                | MO          |    133775   |       115524   |    104085   | 222078           |     0.002171 |     0.004666 |
| Platteville, WI            | WI          |    133668   |       114951   |    106109   | 216419           |     0.002102 |     0.003994 |
| Mount Vernon, OH           | OH          |    133376   |        91862.9 |     86668.1 | 271282           |     0.003598 |     0.005638 |
| Syracuse, NY               | NY          |    133296   |       118727   |     79468.4 | 245046           |     0.003757 |     0.004318 |
| Mount Airy, NC             | NC          |    132861   |       114905   |    106791   | 224356           |     0.002193 |     0.006872 |
| Adrian, MI                 | MI          |    132263   |       115794   |     87230.6 | 226966           |     0.002847 |     0.006284 |
| Springfield, IL            | IL          |    132186   |       126127   |    117112   | 188362           |     0.001547 |     0.003163 |
| Decatur, IN                | IN          |    132083   |       111604   |    105573   | 234027           |     0.00246  |     0.00406  |
| Watertown, NY              | NY          |    132013   |       138690   |     55224.7 | 211946           |     0.004497 |     0.006183 |
| Plattsburgh, NY            | NY          |    131960   |       120842   |     84289.8 | 212670           |     0.003098 |     0.00475  |
| Washington, NC             | NC          |    131765   |       120189   |     86362.4 | 226147           |     0.003215 |     0.006528 |
| Dalton, GA                 | GA          |    131700   |       111705   |     84823.8 | 241763           |     0.003507 |     0.005412 |
| Beaumont, TX               | TX          |    131497   |       120998   |    101658   | 181054           |     0.001817 |     0.003688 |
| Quincy, IL                 | IL          |    131293   |       119412   |    109625   | 176940           |     0.001306 |     0.004202 |
| Brownsville, TX            | TX          |    131124   |       123294   |     97026.3 | 199650           |     0.002253 |     0.005933 |
| Davenport, IA              | IL          |    131038   |       122661   |    109462   | 182860           |     0.001705 |     0.003099 |
| Roswell, NM                | NM          |    130812   |       122268   |    112139   | 176771           |     0.000934 |     0.005181 |
| Seymour, IN                | IN          |    130719   |       109316   |    102213   | 219621           |     0.002374 |     0.003818 |
| Berlin, NH                 | NH          |    130705   |       112726   |     72360.3 | 245875           |     0.004052 |     0.007018 |
| Maryville, MO              | MO          |    130145   |       118718   |    102741   | 213415           |     0.002429 |     0.005238 |
| Abilene, TX                | TX          |    130129   |       108559   |    102204   | 199711           |     0.002044 |     0.003645 |
| Sault Ste. Marie, MI       | MI          |    130099   |       122432   |    101552   | 180095           |     0.001278 |     0.007126 |
| Thomasville, GA            | GA          |    129853   |       116404   |     93194.5 | 208884           |     0.002705 |     0.005047 |
| Wilmington, OH             | OH          |    129625   |       102282   |     89822.2 | 241213           |     0.003092 |     0.005351 |
| Marquette, MI              | MI          |    129415   |       119363   |     84830.6 | 231815           |     0.003354 |     0.005023 |
| Mount Pleasant, MI         | MI          |    129250   |       106086   |     97775.6 | 216273           |     0.002637 |     0.005222 |
| Washington, IN             | IN          |    129224   |       108923   |    104469   | 223034           |     0.002519 |     0.004073 |
| Clewiston, FL              | FL          |    129026   |       104696   |     57258.9 | 283065           |     0.005205 |     0.009803 |
| Russellville, AR           | AR          |    129005   |       118383   |     87275.4 | 190780           |     0.002614 |     0.003358 |
| Waterloo, IA               | IA          |    128871   |       120321   |    109353   | 191869           |     0.001868 |     0.003218 |
| Florence, AL               | AL          |    128805   |       115163   |    100798   | 205759           |     0.002234 |     0.004366 |
| Evansville, IN             | IN          |    128766   |       111782   |     97652.1 | 214194           |     0.002625 |     0.003598 |
| Decatur, AL                | AL          |    128717   |       120729   |     84164.8 | 222754           |     0.002988 |     0.006677 |
| Ashland, OH                | OH          |    128704   |       107156   |     98676   | 229733           |     0.002534 |     0.004542 |
| Big Rapids, MI             | MI          |    128665   |       110659   |     89708.5 | 212990           |     0.002175 |     0.005605 |
| McMinnville, TN            | TN          |    128614   |        99740.2 |     84536.2 | 244946           |     0.003546 |     0.00601  |
| Kendallville, IN           | IN          |    128386   |        99687.6 |     96202   | 237210           |     0.002995 |     0.00456  |
| Wilson, NC                 | NC          |    128203   |       111223   |     98678.4 | 216977           |     0.00222  |     0.005693 |
| Sebring, FL                | FL          |    128127   |       111297   |     78388.7 | 238340           |     0.003405 |     0.010895 |
| Harrison, AR               | AR          |    127971   |       110946   |     83875.2 | 224604           |     0.003198 |     0.004844 |
| Jonesboro, AR              | AR          |    127898   |       115029   |     90549.2 | 195556           |     0.002584 |     0.00323  |
| Searcy, AR                 | AR          |    127825   |       118147   |     94550.6 | 199193           |     0.002498 |     0.004072 |
| Morgan City, LA            | LA          |    127746   |       128275   |    113318   | 133258           |    -0.000341 |     0.006814 |
| Corsicana, TX              | TX          |    127682   |       102056   |     93706   | 223656           |     0.002567 |     0.005223 |
| Oneonta, NY                | NY          |    127572   |       123722   |     56040.3 | 201784           |     0.004219 |     0.006276 |
| Wichita, KS                | KS          |    127470   |       111735   |     91733.5 | 212890           |     0.002672 |     0.004861 |
| Wisconsin Rapids, WI       | WI          |    127233   |       112643   |    105709   | 214213           |     0.002135 |     0.004259 |
| Greeneville, TN            | TN          |    127143   |       104995   |     78235.7 | 240931           |     0.003756 |     0.006375 |
| Batavia, NY                | NY          |    126987   |       116856   |     80901.9 | 210442           |     0.003201 |     0.005693 |
| South Bend, IN             | IN          |    126947   |       109703   |     92415.6 | 221296           |     0.002331 |     0.005086 |
| Mobile, AL                 | AL          |    126885   |       117655   |     93260.6 | 190821           |     0.002319 |     0.005736 |
| Shelby, NC                 | NC          |    126819   |       109878   |     91330   | 217605           |     0.002635 |     0.006469 |
| Newport, TN                | TN          |    126764   |       107781   |     71521   | 233979           |     0.00396  |     0.006006 |
| Sidney, OH                 | OH          |    126604   |       109000   |     86996.3 | 231112           |     0.003265 |     0.004291 |
| Dothan, AL                 | AL          |    126585   |       121433   |     87577.7 | 187002           |     0.002512 |     0.004689 |
| Auburn, NY                 | NY          |    126551   |       118191   |     64716.4 | 216154           |     0.004035 |     0.005341 |
| Lufkin, TX                 | TX          |    126503   |       110244   |     87740.9 | 196680           |     0.002644 |     0.004113 |
| Gaffney, SC                | SC          |    126265   |       105003   |     86863.1 | 197205           |     0.00183  |     0.006707 |
| Fremont, NE                | NE          |    126077   |        96471.1 |     92575.8 | 232841           |     0.002959 |     0.004611 |
| Sturgis, MI                | MI          |    125802   |       111834   |     94345.8 | 204437           |     0.002392 |     0.00562  |
| St. Joseph, MO             | MO          |    125768   |       113727   |    103123   | 201656           |     0.002228 |     0.003887 |
| Columbus, MS               | MS          |    125764   |       111643   |    102811   | 175746           |     0.001472 |     0.00604  |
| Texarkana, TX              | TX          |    125731   |       113020   |     86933.5 | 186222           |     0.002315 |     0.004395 |
| Alexandria, LA             | LA          |    125667   |       123708   |     82277.5 | 169039           |     0.002217 |     0.006284 |
| Wahpeton, ND               | ND          |    125579   |       111931   |     84436.8 | 216237           |     0.00312  |     0.004634 |
| Levelland, TX              | TX          |    125482   |       112765   |    107767   | 166636           |     0.001267 |     0.003772 |
| Erie, PA                   | PA          |    125257   |       115270   |     86696.8 | 208540           |     0.002917 |     0.00365  |
| Laurel, MS                 | MS          |    125236   |       116839   |    108912   | 158484           |     0.000713 |     0.005218 |
| Paris, TX                  | TX          |    125158   |       104581   |     99737.2 | 198378           |     0.002053 |     0.005634 |
| Rome, GA                   | GA          |    124990   |       104825   |     82752.7 | 225726           |     0.003162 |     0.006014 |
| Fort Smith, AR             | AR          |    124965   |       114762   |     88874.1 | 194680           |     0.002626 |     0.003672 |
| Seneca Falls, NY           | NY          |    124707   |       114743   |     78422.2 | 208426           |     0.003273 |     0.005473 |
| Brownwood, TX              | TX          |    124302   |       109878   |    105076   | 179959           |     0.001534 |     0.004509 |
| Houghton, MI               | MI          |    124005   |       116125   |     97551.7 | 177529           |     0.002012 |     0.006681 |
| Greenville, OH             | OH          |    123965   |       111817   |     96411.6 | 203218           |     0.002498 |     0.006395 |
| Durant, OK                 | OK          |    123954   |       103358   |     73249.6 | 220537           |     0.00368  |     0.005288 |
| Florence, SC               | SC          |    123954   |       113754   |    103697   | 184233           |     0.001815 |     0.004251 |
| Muskegon, MI               | MI          |    123721   |       101518   |     75025.9 | 237339           |     0.003247 |     0.006792 |
| Jackson, TN                | TN          |    123597   |       108690   |     96572.8 | 197861           |     0.002385 |     0.005416 |
| Marshall, MO               | MO          |    123498   |       112496   |    101579   | 174115           |     0.00179  |     0.008389 |
| Jesup, GA                  | GA          |    123265   |       110201   |     87696.6 | 201463           |     0.002788 |     0.00525  |
| Corinth, MS                | MS          |    123065   |       111714   |    103450   | 169960           |     0.001394 |     0.005387 |
| Sioux City, IA             | IA          |    122956   |       103280   |     80134.9 | 211295           |     0.003236 |     0.003363 |
| Jackson, MI                | MI          |    122771   |       108981   |     71421.1 | 212207           |     0.002607 |     0.008643 |
| Scottsbluff, NE            | NE          |    121859   |       107289   |    101430   | 188478           |     0.001872 |     0.003721 |
| Crawfordsville, IN         | IN          |    121858   |        99530.3 |     95131.9 | 210784           |     0.002493 |     0.004367 |
| Gloversville, NY           | NY          |    121622   |       110140   |     63801.5 | 204960           |     0.003906 |     0.005373 |
| Lawrenceburg, TN           | TN          |    121622   |        94840.4 |     78847.3 | 236159           |     0.003663 |     0.005723 |
| Muscatine, IA              | IA          |    121535   |       108016   |     98983.3 | 188446           |     0.002061 |     0.003819 |
| New Philadelphia, OH       | OH          |    121465   |       114782   |     84110.4 | 201255           |     0.002135 |     0.011501 |
| Picayune, MS               | MS          |    121397   |       100754   |     91176.8 | 195330           |     0.002531 |     0.006127 |
| Tupelo, MS                 | MS          |    121277   |       109249   |    101420   | 178652           |     0.001863 |     0.004455 |
| Owensboro, KY              | KY          |    121178   |       103019   |     91286   | 204024           |     0.002661 |     0.004315 |
| Dixon, IL                  | IL          |    121018   |       130553   |     64292.2 | 172602           |     0.000922 |     0.010661 |
| Enterprise, AL             | AL          |    120911   |       112198   |    107251   | 172520           |     0.001505 |     0.003633 |
| Mount Vernon, IL           | IL          |    120866   |       112838   |     99717.7 | 184681           |     0.000533 |     0.010929 |
| Goldsboro, NC              | NC          |    120786   |       108307   |     90642.1 | 186963           |     0.002242 |     0.005377 |
| Sikeston, MO               | MO          |    120638   |       110880   |    110880   | 152201           |     0.001014 |     0.004193 |
| Brookhaven, MS             | MS          |    120566   |       100803   |     95399.2 | 175037           |     0.001523 |     0.006139 |
| Big Spring, TX             | TX          |    120542   |       108503   |     93223.4 | 173004           |     0.001334 |     0.007392 |
| North Vernon, IN           | IN          |    120225   |       103578   |     90628.9 | 212360           |     0.002829 |     0.004613 |
| Ottawa, KS                 | KS          |    120220   |        90697.3 |     80883.7 | 246956           |     0.003708 |     0.00494  |
| Huntingdon, PA             | PA          |    120192   |       104897   |     97935.7 | 183963           |     0.002058 |     0.00565  |
| Hastings, NE               | NE          |    120183   |       102012   |     85858.5 | 202955           |     0.002858 |     0.003567 |
| Somerset, PA               | PA          |    120108   |       113440   |    103607   | 165695           |     0.001259 |     0.004659 |
| Canton, OH                 | OH          |    120086   |       105841   |     91756.3 | 203433           |     0.002606 |     0.004508 |
| Tahlequah, OK              | OK          |    119868   |       106610   |     80298.9 | 200902           |     0.003065 |     0.005219 |
| Lexington, NE              | NE          |    119864   |       100934   |     89803   | 205284           |     0.002739 |     0.003836 |
| Amsterdam, NY              | NY          |    119853   |       109455   |     66943.3 | 200414           |     0.003623 |     0.005797 |
| Topeka, KS                 | KS          |    119798   |       105356   |     80821.2 | 205374           |     0.003104 |     0.003717 |
| Altoona, PA                | PA          |    119706   |       116275   |     81526.2 | 166225           |     0.002394 |     0.00613  |
| Anniston, AL               | AL          |    119666   |       108086   |    101034   | 165193           |     0.00146  |     0.011323 |
| Poplar Bluff, MO           | MO          |    119419   |       119457   |     91693.7 | 158464           |     0.001831 |     0.004733 |
| Zapata, TX                 | TX          |    119416   |       112494   |    101545   | 162444           |     0.00047  |     0.006777 |
| Elk City, OK               | OK          |    119204   |       118234   |     96361.3 | 147991           |     0.00144  |     0.005276 |
| Bainbridge, GA             | GA          |    119148   |       112104   |     95421   | 177486           |     0.001561 |     0.006844 |
| North Wilkesboro, NC       | NC          |    118817   |       101919   |     74894   | 213383           |     0.003517 |     0.008274 |
| Hannibal, MO               | MO          |    118801   |       101002   |     94298.4 | 201924           |     0.002354 |     0.00508  |
| Dodge City, KS             | KS          |    118483   |       102353   |    100535   | 202320           |     0.00223  |     0.005007 |
| Palatka, FL                | FL          |    118477   |        97147.3 |     78633   | 213851           |     0.003204 |     0.0101   |
| Forest City, NC            | NC          |    118452   |        98066.2 |     72907   | 215139           |     0.003504 |     0.00598  |
| Hillsdale, MI              | MI          |    118426   |       100434   |     82567.5 | 199576           |     0.002281 |     0.005555 |
| Monroe, LA                 | LA          |    118362   |       112589   |     78130.1 | 162199           |     0.002334 |     0.004742 |
| Macon, GA                  | GA          |    118317   |       105888   |     90237   | 190547           |     0.002443 |     0.005572 |
| Chillicothe, OH            | OH          |    118068   |       104865   |     92490.1 | 191953           |     0.002441 |     0.004496 |
| Spencer, IA                | IA          |    117984   |       104344   |     95347.9 | 185847           |     0.002127 |     0.003996 |
| Rocky Mount, NC            | NC          |    117577   |       103378   |     88088.2 | 199077           |     0.002626 |     0.00597  |
| Paris, TN                  | TN          |    117445   |       101546   |     84561   | 204853           |     0.002961 |     0.005491 |
| Utica, NY                  | NY          |    117426   |       105097   |     67694.2 | 213496           |     0.003836 |     0.004657 |
| Paragould, AR              | AR          |    117292   |       104509   |     77453.5 | 184720           |     0.002883 |     0.004827 |
| Wauchula, FL               | FL          |    117165   |       101461   |     64389.7 | 226542           |     0.004196 |     0.00895  |
| Athens, OH                 | OH          |    117151   |       103336   |     94450.9 | 174901           |     0.001748 |     0.004599 |
| Danville, KY               | KY          |    117123   |       100827   |     79723.8 | 204557           |     0.003122 |     0.004522 |
| Marshalltown, IA           | IA          |    116660   |       102190   |     93733.1 | 182321           |     0.001923 |     0.005188 |
| Marietta, OH               | OH          |    116595   |       105088   |     87881   | 175408           |     0.002316 |     0.003928 |
| Cortland, NY               | NY          |    116505   |       109046   |     65916   | 189992           |     0.003543 |     0.004658 |
| Madison, IN                | IN          |    116382   |        89782.4 |     84294.6 | 225436           |     0.003257 |     0.005197 |
| Toledo, OH                 | OH          |    116358   |       105313   |     87281.3 | 190400           |     0.002598 |     0.004884 |
| Kirksville, MO             | MO          |    115700   |       104794   |     95020.8 | 176328           |     0.002054 |     0.003853 |
| Dumas, TX                  | TX          |    115632   |       114362   |     84673.2 | 182976           |     0.00256  |     0.006911 |
| Joplin, MO                 | MO          |    115546   |        91402   |     74679.7 | 216293           |     0.003134 |     0.005554 |
| Toccoa, GA                 | GA          |    115541   |        92474.9 |     73866.2 | 233525           |     0.003804 |     0.007    |
| Dyersburg, TN              | TN          |    115529   |       106075   |     93663   | 169102           |     0.001682 |     0.005522 |
| Douglas, GA                | GA          |    115476   |       106412   |     89574.3 | 172839           |     0.001961 |     0.006244 |
| Rio Grande City, TX        | TX          |    115472   |       103726   |     95237.8 | 160466           |     0.000671 |     0.007929 |
| Magnolia, AR               | AR          |    115073   |       108890   |     87248.6 | 154403           |     0.001241 |     0.006324 |
| Scottsboro, AL             | AL          |    114657   |        96813.4 |     82454.9 | 182160           |     0.00204  |     0.005737 |
| Carbondale, IL             | IL          |    114624   |       119034   |     92509.8 | 141543           |     0.000505 |     0.006325 |
| Sunbury, PA                | PA          |    114575   |       102283   |     98332.2 | 165815           |     0.001633 |     0.005163 |
| Elkins, WV                 | WV          |    114399   |       105651   |    105237   | 155836           |     0.001277 |     0.004943 |
| Fremont, OH                | OH          |    114362   |       106981   |     91983.4 | 178788           |     0.002065 |     0.004455 |
| Frankfort, IN              | IN          |    114202   |        95518.7 |     82077.5 | 213251           |     0.003191 |     0.004799 |
| Huntington, IN             | IN          |    113845   |        93825.3 |     87688.6 | 198287           |     0.002486 |     0.004176 |
| Dublin, GA                 | GA          |    113605   |       105421   |     88816.6 | 167089           |     0.001988 |     0.005107 |
| Mount Sterling, KY         | KY          |    113511   |        96414.8 |     78689.7 | 187833           |     0.002854 |     0.006123 |
| Zanesville, OH             | OH          |    112987   |        95843.6 |     76591.1 | 199272           |     0.003198 |     0.004977 |
| Talladega, AL              | AL          |    112800   |       101492   |     78285.6 | 178588           |     0.00265  |     0.005334 |
| Natchez, MS                | LA          |    112784   |       106061   |     99341.9 | 160858           |     0.000456 |     0.008056 |
| West Plains, MO            | MO          |    112593   |        94062.5 |     84254.6 | 209810           |     0.002878 |     0.006476 |
| Mason City, IA             | IA          |    112541   |        95666.8 |     86989.5 | 188649           |     0.002498 |     0.004365 |
| Ada, OK                    | OK          |    112524   |       105775   |     71036.9 | 179869           |     0.003101 |     0.006529 |
| Binghamton, NY             | NY          |    112372   |       104891   |     68732.6 | 184968           |     0.003313 |     0.00466  |
| Peoria, IL                 | IL          |    112352   |       108823   |     93258.9 | 161415           |     0.001823 |     0.003697 |
| Lawton, OK                 | OK          |    112302   |       110669   |     93542.2 | 149161           |     0.001566 |     0.005283 |
| Guymon, OK                 | OK          |    112185   |       101066   |    101066   | 160160           |     0.00153  |     0.00484  |
| Kingsville, TX             | TX          |    112038   |       100937   |     96208.2 | 148783           |     0.00125  |     0.004667 |
| Batesville, AR             | AR          |    112030   |       104644   |     77769.4 | 156104           |     0.00225  |     0.004283 |
| LaGrange, GA               | GA          |    112016   |        97714.1 |     76396.4 | 196832           |     0.003145 |     0.006325 |
| Wichita Falls, TX          | TX          |    111925   |       102466   |     90805.7 | 169009           |     0.001621 |     0.004871 |
| Emporia, KS                | KS          |    111616   |        95060.1 |     90869.8 | 181087           |     0.002141 |     0.004533 |
| Campbellsville, KY         | KY          |    111285   |        92161.4 |     86836.8 | 197324           |     0.002455 |     0.004909 |
| Clinton, IA                | IA          |    111281   |        97759.8 |     92325.9 | 166669           |     0.001925 |     0.004153 |
| Rockford, IL               | IL          |    111143   |       101579   |     77933.4 | 206080           |     0.003247 |     0.006086 |
| Iron Mountain, MI          | MI          |    110883   |        97746.4 |     81300.9 | 171591           |     0.00187  |     0.007343 |
| Albany, GA                 | GA          |    110805   |       103184   |     89473.5 | 163906           |     0.001882 |     0.005232 |
| Vicksburg, MS              | MS          |    110785   |        95631   |     89145.1 | 146417           |     0.001152 |     0.006074 |
| Liberal, KS                | KS          |    110761   |       104635   |    100334   | 141893           |     0.001012 |     0.004079 |
| Snyder, TX                 | TX          |    110645   |       102671   |     98339.9 | 139823           |     0.001007 |     0.004467 |
| Bedford, IN                | IN          |    110323   |        88542.6 |     83946.4 | 200346           |     0.002807 |     0.005    |
| Huntington, WV             | OH          |    110234   |       103502   |     80517.7 | 156316           |     0.002224 |     0.004306 |
| Cadillac, MI               | MI          |    110092   |        82912.8 |     64753.9 | 215575           |     0.003174 |     0.008819 |
| Escanaba, MI               | MI          |    109827   |        98847.4 |     92095.2 | 189804           |     0.002403 |     0.005563 |
| Johnstown, PA              | PA          |    109819   |       105542   |     97962   | 143957           |     0.000489 |     0.008123 |
| Storm Lake, IA             | IA          |    109763   |        94449.8 |     71759.9 | 180882           |     0.003091 |     0.003711 |
| Moultrie, GA               | GA          |    109594   |       101495   |     81872.1 | 159089           |     0.002238 |     0.005934 |
| Alma, MI                   | MI          |    109542   |        97037.2 |     85041.1 | 172491           |     0.002184 |     0.005812 |
| Parkersburg, WV            | WV          |    109513   |        99750   |     79320.5 | 163795           |     0.002439 |     0.00442  |
| Austin, MN                 | MN          |    109226   |        95916.2 |     72738.2 | 193324           |     0.003274 |     0.00571  |
| Salina, KS                 | KS          |    109056   |        96986.5 |     90874.1 | 170511           |     0.002091 |     0.003699 |
| Fairfield, IA              | IA          |    109010   |        98970.7 |     84513   | 175284           |     0.002424 |     0.004755 |
| Norwalk, OH                | OH          |    108862   |        93627.4 |     78971.1 | 184020           |     0.002791 |     0.006167 |
| Henderson, NC              | NC          |    108810   |        93833   |     75408.7 | 183139           |     0.002847 |     0.00709  |
| Orangeburg, SC             | SC          |    108800   |        99467.5 |     88339.5 | 158541           |     0.001798 |     0.00585  |
| Corning, NY                | NY          |    108739   |       100640   |     79948.6 | 160826           |     0.002338 |     0.006555 |
| Glasgow, KY                | KY          |    108630   |        88648.9 |     65938.1 | 206603           |     0.003709 |     0.004955 |
| Fairmont, WV               | WV          |    108377   |       100292   |     79747.4 | 159670           |     0.002274 |     0.005928 |
| Malone, NY                 | NY          |    108022   |       100677   |     63785.9 | 163617           |     0.003166 |     0.00626  |
| Arkadelphia, AR            | AR          |    107785   |       102046   |     81284.2 | 154442           |     0.002153 |     0.004953 |
| Indiana, PA                | PA          |    107639   |        97315.4 |     90900.1 | 155666           |     0.001686 |     0.00426  |
| Defiance, OH               | OH          |    107584   |        95624.6 |     83833.2 | 175008           |     0.002466 |     0.004106 |
| Lima, OH                   | OH          |    107183   |        99645   |     81219.2 | 178539           |     0.002624 |     0.006097 |
| Weatherford, OK            | OK          |    107027   |        97947.7 |     74215.8 | 170436           |     0.002786 |     0.004998 |
| Alpena, MI                 | MI          |    107007   |       101041   |     70627.9 | 181440           |     0.003154 |     0.009227 |
| Marinette, WI              | WI          |    106905   |        96704.4 |     72471.8 | 190638           |     0.003222 |     0.006404 |
| Beatrice, NE               | NE          |    106837   |        89100   |     81638.6 | 189485           |     0.002797 |     0.004285 |
| Bartlesville, OK           | OK          |    106801   |        97137.2 |     69314.9 | 176969           |     0.003133 |     0.004509 |
| Oskaloosa, IA              | IA          |    106474   |        88793.3 |     80528.6 | 186537           |     0.002692 |     0.004901 |
| McAllen, TX                | TX          |    106323   |        86535.5 |     78644   | 189590           |     0.00287  |     0.005034 |
| Lewistown, PA              | PA          |    106174   |        89019.7 |     87771.1 | 183490           |     0.002403 |     0.00516  |
| DuBois, PA                 | PA          |    106083   |        99036.1 |     66422.9 | 150524           |     0.002303 |     0.007025 |
| Cumberland, MD             | MD          |    105970   |        99635   |     71795.4 | 158500           |     0.002636 |     0.006366 |
| Malvern, AR                | AR          |    105387   |        96020.7 |     63275   | 160686           |     0.002963 |     0.005175 |
| Charleston, WV             | WV          |    105200   |       101673   |     83809.7 | 145891           |     0.001794 |     0.004108 |
| Murray, KY                 | KY          |    105097   |        82269.9 |     57507.6 | 220879           |     0.003437 |     0.011332 |
| Cedartown, GA              | GA          |    104489   |        80513.2 |     61638.9 | 217361           |     0.004009 |     0.007467 |
| Meridian, MS               | MS          |    104425   |       100162   |     96074.2 | 126464           |     0.000439 |     0.005349 |
| Sweetwater, TX             | TX          |    104306   |        94742.1 |     88549.8 | 134765           |     0.00056  |     0.005865 |
| Mexico, MO                 | MO          |    104125   |        92992.9 |     85979.3 | 177781           |     0.002338 |     0.004685 |
| Wabash, IN                 | IN          |    104050   |        86921.4 |     81926.8 | 179799           |     0.002415 |     0.004201 |
| Danville, VA               | VA          |    103992   |        94814.7 |     72318.7 | 159881           |     0.002598 |     0.006125 |
| Farmington, MO             | MO          |    103918   |        79243.8 |     76726.2 | 182209           |     0.002796 |     0.005119 |
| Grants, NM                 | NM          |    103672   |        95613.7 |     83259.7 | 147790           |     0.001398 |     0.005822 |
| Ozark, AL                  | AL          |    103666   |        97787.4 |     76655   | 154597           |     0.002299 |     0.004556 |
| Atchison, KS               | KS          |    103438   |        94590.4 |     73051   | 175043           |     0.002045 |     0.007178 |
| Albert Lea, MN             | MN          |    103392   |        82275.7 |     78496.9 | 185329           |     0.002844 |     0.00481  |
| Bay City, MI               | MI          |    103357   |        95892.4 |     77169.8 | 171861           |     0.002228 |     0.005432 |
| Paducah, KY                | KY          |    103339   |        92401.9 |     74012.5 | 168957           |     0.002679 |     0.006186 |
| Tiffin, OH                 | OH          |    103320   |        91655.8 |     78023.8 | 166389           |     0.002536 |     0.005035 |
| Sterling, IL               | IL          |    103012   |       102571   |     85604.8 | 136677           |     0.000954 |     0.005312 |
| Charleston, IL             | IL          |    102943   |       100249   |     90449.4 | 140409           |     0.001119 |     0.004283 |
| Martin, TN                 | TN          |    102900   |        90629.4 |     78363.2 | 179486           |     0.002776 |     0.005216 |
| Lincoln, IL                | IL          |    102862   |        95213.2 |     95213.2 | 134765           |     0.001154 |     0.004703 |
| Middlesborough, KY         | KY          |    102839   |        99747.2 |     89764.1 | 121810           |    -0.00035  |     0.008589 |
| Battle Creek, MI           | MI          |    102729   |        92655.4 |     70625.9 | 178104           |     0.002629 |     0.007766 |
| Greenville, MS             | MS          |    102726   |       109062   |     48179.1 | 109745           |    -0.002714 |     0.010613 |
| Springfield, OH            | OH          |    102528   |        86789.4 |     73613.5 | 190705           |     0.003137 |     0.005782 |
| Clarksburg, WV             | WV          |    102504   |        94260.2 |     65792.7 | 149132           |     0.002699 |     0.004698 |
| Waycross, GA               | GA          |    102390   |        90488.1 |     71573.9 | 170710           |     0.002877 |     0.005807 |
| Greenwood, SC              | SC          |    102338   |        89552.3 |     59305.4 | 172483           |     0.003439 |     0.005385 |
| Gadsden, AL                | AL          |    102258   |        91087.3 |     65613.7 | 173387           |     0.003228 |     0.005075 |
| Mansfield, OH              | OH          |    102210   |        90764.6 |     70286.4 | 185505           |     0.002736 |     0.00723  |
| Meadville, PA              | PA          |    102187   |        90755.4 |     61151.1 | 161207           |     0.003201 |     0.005995 |
| Burlington, IA             | IA          |    101886   |        91161.5 |     87139.1 | 136076           |     0.001449 |     0.003677 |
| Jacksonville, IL           | IL          |    101862   |       100550   |     87604.4 | 120567           |     0.000603 |     0.005045 |
| Flint, MI                  | MI          |    101364   |        96726.2 |     46118.2 | 183222           |     0.00248  |     0.010321 |
| Shawnee, OK                | OK          |    100763   |        86461.3 |     64052.5 | 184982           |     0.003544 |     0.004972 |
| New Castle, PA             | PA          |    100641   |        90068.5 |     80270.2 | 151580           |     0.001713 |     0.004756 |
| McComb, MS                 | MS          |    100528   |       102069   |     88912.7 | 117888           |    -0.000106 |     0.006296 |
| Vidalia, GA                | GA          |    100502   |        91162.1 |     73279.1 | 161990           |     0.00266  |     0.006294 |
| Ardmore, OK                | OK          |    100318   |        85920.2 |     61460.8 | 173970           |     0.003435 |     0.004549 |
| Summerville, GA            | GA          |    100249   |        87661.7 |     70135.8 | 169825           |     0.002847 |     0.007186 |
| Coshocton, OH              | OH          |     99959.4 |        83317.4 |     76313.6 | 173895           |     0.002511 |     0.004715 |
| Indianola, MS              | MS          |     99923.9 |        98842.9 |     90839.1 | 123560           |    -0.000276 |     0.008177 |
| Richmond, IN               | IN          |     99645.5 |        90735.7 |     80578   | 162545           |     0.001937 |     0.004357 |
| Moberly, MO                | MO          |     99527   |        84527.6 |     82239.6 | 172252           |     0.002456 |     0.004478 |
| Bogalusa, LA               | LA          |     99452.7 |        90881.2 |     79003.6 | 146059           |     0.001448 |     0.006994 |
| Union City, TN             | TN          |     99451.3 |        90203.1 |     81091   | 155900           |     0.002054 |     0.005552 |
| Pontiac, IL                | IL          |     99431.2 |        94560.7 |     72356.9 | 157790           |     0.002604 |     0.005439 |
| Kokomo, IN                 | IN          |     99420.3 |        80809   |     73412.3 | 184108           |     0.002736 |     0.00468  |
| New Castle, IN             | IN          |     99406.8 |        81789.2 |     73154   | 180102           |     0.002623 |     0.00498  |
| Americus, GA               | GA          |     99008.3 |        99233.9 |     76878.5 | 135358           |     0.001108 |     0.007312 |
| Point Pleasant, WV         | OH          |     98958.4 |        89002.1 |     71085.4 | 155650           |     0.002626 |     0.005094 |
| Borger, TX                 | TX          |     98791.6 |        96581.6 |     85777.6 | 117644           |     0.000559 |     0.005586 |
| El Dorado, AR              | AR          |     98588.1 |        94510   |     78799.4 | 133505           |     0.001395 |     0.005128 |
| Hereford, TX               | TX          |     98384.5 |        75660.5 |     72892.6 | 174282           |     0.002774 |     0.006184 |
| Cambridge, OH              | OH          |     98196.9 |        89391.4 |     74186.7 | 153075           |     0.002187 |     0.006392 |
| Van Wert, OH               | OH          |     97928.2 |        82628.5 |     73185.7 | 177111           |     0.002954 |     0.004604 |
| Terre Haute, IN            | IN          |     97860.8 |        85737.7 |     82136.5 | 157580           |     0.002006 |     0.003895 |
| Big Stone Gap, VA          | VA          |     97806.7 |        98332.5 |     80654.9 | 128694           |     0.000749 |     0.006129 |
| Bennettsville, SC          | SC          |     97535.1 |        86865.7 |     84721.1 | 140636           |     0.000223 |     0.010382 |
| Martinsville, VA           | VA          |     97437.8 |        91305   |     79723.6 | 134139           |     0.001611 |     0.008045 |
| Woodward, OK               | OK          |     97206.4 |        99393.5 |     65861.6 | 125216           |     0.002138 |     0.005376 |
| Maysville, KY              | KY          |     96898.8 |        81800.8 |     79473.6 | 173069           |     0.00234  |     0.006232 |
| Youngstown, OH             | OH          |     96815.4 |        88582.8 |     74586   | 162557           |     0.002403 |     0.004908 |
| Ashtabula, OH              | OH          |     96778   |        85532.1 |     67930.5 | 170186           |     0.003066 |     0.004963 |
| Grenada, MS                | MS          |     96762.5 |        88990.7 |     88313.3 | 130978           |     0.001156 |     0.006432 |
| Plainview, TX              | TX          |     96477.9 |        90146.2 |     85145.8 | 128947           |     0.000744 |     0.004945 |
| Elmira, NY                 | NY          |     96242.3 |        92991.4 |     57458.9 | 147703           |     0.003141 |     0.004476 |
| Muskogee, OK               | OK          |     96122.1 |        86909.2 |     71356   | 155308           |     0.002496 |     0.005595 |
| Enid, OK                   | OK          |     95583.5 |        88826.8 |     72476.4 | 136521           |     0.00212  |     0.005541 |
| Marion, OH                 | OH          |     95454.8 |        79379.9 |     72897.9 | 169850           |     0.002527 |     0.006475 |
| Salem, OH                  | OH          |     95357.9 |        83481.6 |     70208.3 | 150331           |     0.002541 |     0.004244 |
| Jackson, OH                | OH          |     95261.3 |        83563.5 |     71343.2 | 147972           |     0.002224 |     0.00563  |
| Olean, NY                  | NY          |     94617.6 |        85536   |     58430.7 | 154235           |     0.003247 |     0.006234 |
| Warren, PA                 | PA          |     94501.5 |        89175.3 |     76680.4 | 129827           |     0.001223 |     0.006271 |
| Madisonville, KY           | KY          |     93930.9 |        85550.7 |     66638.5 | 155178           |     0.002577 |     0.00564  |
| London, KY                 | KY          |     93632.9 |        83275.4 |     60453.6 | 156724           |     0.003021 |     0.006039 |
| Pottsville, PA             | PA          |     93594.1 |        88780.9 |     73621.7 | 153426           |     0.001817 |     0.006623 |
| McAlester, OK              | OK          |     93373.4 |        86482.5 |     66531.8 | 140148           |     0.0025   |     0.005393 |
| Sedalia, MO                | MO          |     92615   |        74836.8 |     57512.6 | 183526           |     0.003873 |     0.007374 |
| Bluefield, WV              | VA          |     92546.6 |        86941.5 |     65824.9 | 142438           |     0.002433 |     0.005314 |
| Cordele, GA                | GA          |     91804.9 |        84815.2 |     71581.1 | 135571           |     0.00194  |     0.006034 |
| Somerset, KY               | KY          |     91597.6 |        70703.2 |     47822.3 | 180741           |     0.004208 |     0.007084 |
| Jamestown, NY              | NY          |     90761.2 |        79495.1 |     57198.4 | 164092           |     0.00353  |     0.005216 |
| Saginaw, MI                | MI          |     89895.6 |        82187.3 |     64602.4 | 159603           |     0.002425 |     0.00755  |
| Muncie, IN                 | IN          |     89688.9 |        76081   |     70909.9 | 158185           |     0.002432 |     0.004544 |
| Logansport, IN             | IN          |     89673.1 |        72304.3 |     70486.2 | 164183           |     0.002725 |     0.005087 |
| Wheeling, WV               | OH          |     89459.2 |        83836.7 |     53617.1 | 132107           |     0.003021 |     0.004465 |
| Centralia, IL              | IL          |     89281.4 |        85709.5 |     77697.8 | 113960           |     0.000946 |     0.005317 |
| Marion, IN                 | IN          |     89263.6 |        79254.1 |     71031   | 145649           |     0.002031 |     0.006691 |
| Beckley, WV                | WV          |     89067.6 |        81323.2 |     60293.4 | 149745           |     0.002841 |     0.007346 |
| Vincennes, IN              | IN          |     88860.9 |        76376.1 |     74393.1 | 147613           |     0.002277 |     0.004538 |
| Bucyrus, OH                | OH          |     88781.2 |        75908.8 |     72019.4 | 149472           |     0.002251 |     0.005287 |
| Pittsburg, KS              | KS          |     88485.3 |        81335.1 |     77217.7 | 134500           |     0.001576 |     0.004396 |
| Taylorville, IL            | IL          |     88316.6 |        84218.1 |     79300.3 | 126365           |     0.001348 |     0.00486  |
| Lamesa, TX                 | TX          |     88028.2 |        78965.9 |     76359.9 | 122464           |     0.001032 |     0.007343 |
| Duncan, OK                 | OK          |     87696.7 |        82860.3 |     60189.7 | 138659           |     0.002683 |     0.005845 |
| Hutchinson, KS             | KS          |     87045.2 |        72102.1 |     69832.3 | 144699           |     0.002328 |     0.00437  |
| Thomaston, GA              | GA          |     86616.1 |        69413.2 |     57581.3 | 179887           |     0.003762 |     0.00784  |
| Lumberton, NC              | NC          |     86122.3 |        75840.6 |     73064.3 | 135674           |     0.001756 |     0.005592 |
| Fort Madison, IA           | IA          |     86081.2 |        81000.4 |     69685.3 | 117835           |     0.001684 |     0.004871 |
| Camden, AR                 | AR          |     85201.1 |        81330.7 |     65958.6 | 115441           |     0.001435 |     0.006587 |
| Portsmouth, OH             | OH          |     84732.8 |        77376   |     73540.4 | 132158           |     0.001947 |     0.006069 |
| Greenwood, MS              | MS          |     84628.3 |        72049.9 |     63806.1 | 131699           |     0.00113  |     0.008745 |
| Laurinburg, NC             | NC          |     84411.9 |        76411.4 |     62269.7 | 139571           |     0.002615 |     0.006481 |
| Vernon, TX                 | TX          |     84346.2 |        81627.5 |     73624.5 | 111348           |     0.000266 |     0.006656 |
| Mayfield, KY               | KY          |     84102.8 |        67590.6 |     61111.5 | 161137           |     0.003181 |     0.005583 |
| Ogdensburg, NY             | NY          |     83961.4 |        79414.9 |     47072.5 | 133576           |     0.003448 |     0.006202 |
| Freeport, IL               | IL          |     83693.7 |        82752.5 |     55873.5 | 148434           |     0.001941 |     0.007771 |
| Oil City, PA               | PA          |     83120.2 |        77258.1 |     50354.9 | 126868           |     0.002998 |     0.00561  |
| Macomb, IL                 | IL          |     82917.4 |        83290.3 |     67077.7 |  94869.3         |     0.001118 |     0.005564 |
| Kinston, NC                | NC          |     82873.5 |        72360.4 |     65138.5 | 143589           |     0.002277 |     0.006204 |
| Kennett, MO                | MO          |     82606.6 |        80473.1 |     74432   |  98128.9         |     0.000239 |     0.00633  |
| Decatur, IL                | IL          |     82287.6 |        78625.4 |     67335.8 | 116128           |     0.001824 |     0.005124 |
| Bradford, PA               | PA          |     82259.9 |        77739.6 |     71331.1 | 102200           |     0.000934 |     0.005331 |
| Great Bend, KS             | KS          |     82256.5 |        79363.2 |     74010.9 | 114903           |     0.001229 |     0.005256 |
| Rockingham, NC             | NC          |     82255.2 |        74397.1 |     62148.2 | 128397           |     0.002332 |     0.006853 |
| Pampa, TX                  | TX          |     81993.4 |        78049.7 |     74100.9 | 101770           |     0.000768 |     0.005862 |
| Peru, IN                   | IN          |     81895.7 |        65433.9 |     60882.3 | 152658           |     0.002814 |     0.005294 |
| Miami, OK                  | OK          |     81563   |        75820.6 |     48937.4 | 141310           |     0.003302 |     0.006893 |
| Galesburg, IL              | IL          |     81383.4 |        76949.5 |     70427   | 110039           |     0.001188 |     0.005734 |
| Fitzgerald, GA             | GA          |     80915   |        73197.1 |     62368.1 | 126420           |     0.002199 |     0.007538 |
| Ottumwa, IA                | IA          |     80640.5 |        71821.3 |     65973.2 | 124265           |     0.001988 |     0.006712 |
| Selma, AL                  | AL          |     79663.4 |        82750.4 |     56931.5 |  94892.6         |     0.001318 |     0.008802 |
| Altus, OK                  | OK          |     79659.8 |        76142.1 |     58755.5 | 117844           |     0.002112 |     0.006255 |
| Connersville, IN           | IN          |     77512.4 |        62756.7 |     59682.2 | 153223           |     0.003126 |     0.006042 |
| Coffeyville, KS            | KS          |     77470.7 |        82115.8 |     59552.7 |  91899.4         |     0.000373 |     0.006026 |
| Parsons, KS                | KS          |     75230.2 |        75163.4 |     57626.7 |  93446           |     0.000537 |     0.00726  |
| Weirton, WV                | OH          |     75102.4 |        62062.9 |     56496.8 | 124473           |     0.002382 |     0.005325 |
| Blytheville, AR            | AR          |     72201.2 |        63469   |     48298.6 | 122879           |     0.002612 |     0.013155 |
| Ponca City, OK             | OK          |     71665.8 |        64551.7 |     51990.2 | 107688           |     0.00244  |     0.005588 |
| Roanoke Rapids, NC         | NC          |     71425.9 |        66013   |     55326   | 102722           |     0.00199  |     0.00678  |
| Pine Bluff, AR             | AR          |     70721.4 |        66060.1 |     48959   |  99818.2         |     0.002181 |     0.005182 |
| Forrest City, AR           | AR          |     68818.9 |        67865.2 |     53707.6 |  83113.8         |     0.00105  |     0.005973 |
| Danville, IL               | IL          |     66328.1 |        63574.6 |     46787.6 |  93680.8         |     0.002289 |     0.007014 |
| Helena, AR                 | AR          |     56523.7 |        55813   |     47225.5 |  67099.7         |    -0.000555 |     0.007884 |
| Clarksdale, MS             | MS          |     54620.1 |        52413.3 |     46486.9 |  83943.4         |    -0.000335 |     0.011639 |


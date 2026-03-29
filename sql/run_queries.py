"""
SQL Analysis — U.S. Housing Price Data
=======================================
Engine  : SQLite3 (in-memory)
Dataset : data/processed/processed_data_price.csv

SQLite3 does not natively support MEDIAN, STDDEV, CORR, or YEAR().
This script registers them as custom aggregate / scalar functions
so the user-facing SQL queries remain unchanged.

Run from project root:
    uv run python sql/run_queries.py
"""

import sqlite3
import math
import numpy as np
import pandas as pd
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_DIR      = PROJECT_ROOT / "sql"
CSV_PATH     = PROJECT_ROOT / "data" / "processed" / "processed_data_price.csv"


# ══════════════════════════════════════════════════════════════════════════════
# Custom SQLite3 aggregate functions (missing from SQLite3 standard library)
# ══════════════════════════════════════════════════════════════════════════════

class _Median:
    """Population median aggregate."""
    def __init__(self):        
        self._v = []

    def step(self, x):
        if x is not None:
            self._v.append(x)

    def finalize(self):
        if not self._v:
            return None
        s = sorted(self._v)
        n = len(s)
        return (s[n // 2 - 1] + s[n // 2]) / 2 if n % 2 == 0 else s[n // 2]


class _Stddev:
    """Sample standard deviation aggregate (ddof=1)."""
    def __init__(self):        
        self._v = []

    def step(self, x):
        if x is not None:
            self._v.append(x)

    def finalize(self):
        n = len(self._v)
        if n < 2:
            return None
        m = sum(self._v) / n
        return math.sqrt(sum((xi - m) ** 2 for xi in self._v) / (n - 1))


class _Corr:
    """Pearson correlation aggregate for two columns."""
    def __init__(self):        
        self._x = []; self._y = []

    def step(self, x, y):
        if x is not None and y is not None:
            self._x.append(x); self._y.append(y)

    def finalize(self):
        if len(self._x) < 2:
            return None
        return float(np.corrcoef(self._x, self._y)[0, 1])


# ══════════════════════════════════════════════════════════════════════════════
# SQL Queries (grouped by section, matching the analysis report structure)
# ══════════════════════════════════════════════════════════════════════════════

SECTIONS = {

    # ── #3 Data Understanding ─────────────────────────────────────────────────
    "Data Understanding": {
        "dataset_overview": (
            "Tổng quan dataset",
            """
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
    """,
            ),
        },

    # ── #4 SQL Analysis — Price by Region ────────────────────────────────────
    "Phân tích giá theo khu vực": {
        "top10_highest_price_regions": (
            "Top 10 khu vực giá nhà cao nhất (trung bình)",
            """
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
    """,
            ),
        "top10_median_price_regions": (
            "Top 10 khu vực giá nhà ở mức trung bình (trung bình)",
            """
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
    """,
            ),
        "top10_highest_growth_states": (
            "Bang có giá nhà tăng trưởng mạnh nhất (avg log_return)",
            """
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
""",
        ),
    },

    # ── #4 SQL Analysis — log_return distribution ─────────────────────────────
    "Phân tích log_return (target variable)": {
        "log_return_by_year": (
            "Phân phối log_return theo năm",
            """
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
""",
        ),
        "lag_feature_correlation": (
            "Tương quan lag features với log_return",
            """
    SELECT
        ROUND(CORR(log_return, lag_1),  4) AS corr_lag1,
        ROUND(CORR(log_return, lag_2),  4) AS corr_lag2,
        ROUND(CORR(log_return, lag_3),  4) AS corr_lag3,
        ROUND(CORR(log_return, lag_6),  4) AS corr_lag6,
        ROUND(CORR(log_return, lag_12), 4) AS corr_lag12
    FROM processed_data
    WHERE log_return != 0;
    """,
        ),
    },
    
    # ── #4 SQL Analysis — Segmentation & Extremes ─────────────────────────────
    "Phân khúc thị trường & Điểm cực trị": {
        "market_segmentation": (
            "Phân khúc thị trường theo Tier giá (High/Mid/Low)",
            """
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
    """,
        ),
        "highest_lowest_regions": (
            "Thống kê các thị trường theo mức giá (Từ cao xuống thấp)",
            """
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
    """,
        ),
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# Setup: load CSV → SQLite3 in-memory table with computed log_return
# ══════════════════════════════════════════════════════════════════════════════

def build_connection(csv_path: Path) -> sqlite3.Connection:
    """Load CSV into SQLite3 in-memory DB and register custom functions."""
    print(f"Loading data from: {csv_path}")
    df = pd.read_csv(csv_path)

    # Compute log_return = ln(price / lag_price_1), guard against <= 0
    df["log_return"] = np.where(
        (df["price"] > 0) & (df["lag_price_1"] > 0),
        np.log(df["price"] / df["lag_price_1"]),
        0.0,
    )

    # Rename lag columns to match SQL query aliases
    df = df.rename(columns={
        "lag_price_1":  "lag_1",
        "lag_price_2":  "lag_2",
        "lag_price_3":  "lag_3",
        "lag_price_6":  "lag_6",
        "lag_price_12": "lag_12",
    })

    con = sqlite3.connect(":memory:")
    df.to_sql("processed_data", con, index=False, if_exists="replace")
    print(f"  Table 'processed_data': {len(df):,} rows loaded into SQLite3.")

    # Register custom aggregate functions
    con.create_aggregate("MEDIAN", 1, _Median)
    con.create_aggregate("STDDEV", 1, _Stddev)
    con.create_aggregate("CORR",   2, _Corr)

    # Register scalar function: YEAR(date_str) → integer year
    con.create_function("YEAR", 1, lambda d: int(d[:4]) if d else None)

    return con


# ══════════════════════════════════════════════════════════════════════════════
# Runner: execute all queries and write results to Markdown + .sql files
# ══════════════════════════════════════════════════════════════════════════════

def run_all(con: sqlite3.Connection) -> None:
    SQL_DIR.mkdir(exist_ok=True)
    output_file = SQL_DIR / "analysis_results.md"

    with open(output_file, "w", encoding="utf-8") as md:
        md.write("# SQL Analysis Results\n\n")
        md.write(f"**Dataset**: `{CSV_PATH.relative_to(PROJECT_ROOT)}`\n")
        md.write("**SQL Engine**: SQLite3 (in-memory)\n\n")
        md.write("---\n\n")

        for section, queries in SECTIONS.items():
            md.write(f"## {section}\n\n")

            for filename_key, (title, query) in queries.items():
                print(f"  Running: {title}")
                try:
                    df_result = pd.read_sql_query(query, con)

                    md.write(f"### {title}\n\n")
                    md.write("```sql\n" + query.strip() + "\n```\n\n")
                    md.write(df_result.to_markdown(index=False) + "\n\n")

                    # Save individual .sql file with ASCII-safe name
                    sql_file = SQL_DIR / f"{filename_key}.sql"
                    sql_file.write_text(query.strip() + "\n", encoding="utf-8")

                except Exception as e:
                    print(f"    ERROR: {e}")
                    md.write(f"### {title}\n\n")
                    md.write(f"**Error:**\n```\n{e}\n```\n\n")

    print(f"\n✅ Done. Results saved to: {output_file}")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found at {CSV_PATH}")
        raise SystemExit(1)

    con = build_connection(CSV_PATH)
    run_all(con)
    con.close()

import sqlite3
import pandas as pd

def run_advanced_analytics():
    # Connect to SQLite
    try:
        conn = sqlite3.connect('global_budget_db.db')
    
    except Exception as e:
        print("message: ", e)

    cursor = conn.cursor()

    # 1. ANALYSIS: year over year budget growth and 5 year rolling average for each country
    print("Step 1: Year-over-Year Budget Growth and 5-Year Rolling Average...")

    moving_avg_query = """
    SELECT
        c.country_name,
        b.year,
        b.Total_Budget_Billions_USD,
        AVG(b.Total_Budget_Billions_USD) OVER (
            PARTITION BY c.country_name
            ORDER BY b.year
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS rolling_5yr_avg
    FROM budgets b
    JOIN countries c ON b.country_id = c.country_id
    """

    df_moving = pd.read_sql(moving_avg_query, conn)
    print("Year-over-Year Budget Growth and 5-Year Rolling Average:")
    print("----1. 5 year rolling budget trend ----")
    print(df_moving.head())

    # 2. ANALYSIS: historical sector dominance matrix (isolating the #1 funded sector per year)
    print("Step 2: Historical Sector Dominance Matrix...")

    dominance_query = """
    WITH RankedSectors AS (
        SELECT
            c.country_name,
            b.year,
            sa.sector_name,
            sa.allocated_percentage,
            DENSE_RANK() OVER (
                PARTITION BY c.country_name, b.year
                ORDER BY sa.allocated_percentage DESC
            ) AS rnk
        FROM sector_allocations sa
        JOIN budgets b ON sa.budget_id = b.budget_id
        JOIN countries c ON b.country_id = c.country_id
    )
    SELECT
        country_name,
        year,
        sector_name,
        allocated_percentage
    FROM RankedSectors
    WHERE rnk = 1
    """

    df_dom = pd.read_sql(dominance_query, conn)
    print("Historical Sector Dominance Matrix:")
    print("----2. Dominant sector per year ----")
    print(df_dom.head())


if __name__ == "__main__":
    run_advanced_analytics()

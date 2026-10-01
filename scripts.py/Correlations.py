from sqlalchemy import create_engine, text
import pandas as pd


def compute_sector_correlation(country_name):

    engine = create_engine(
        "sqlite:///global_budget_db.db"
    )

    query = text("""
        SELECT
            b.year,
            sa.sector_name,
            sa.allocated_percentage
        FROM sector_allocations sa
        JOIN budgets b
            ON sa.budget_id = b.budget_id
        JOIN countries c
            ON b.country_id = c.country_id
        WHERE c.country_name = :country_name
        ORDER BY b.year;
    """)

    df = pd.read_sql(
        query,
        engine,
        params={"country_name": country_name}
    )

    if df.empty:
        print(f"No data found for '{country_name}'.")
        return None

    wide_df = df.pivot_table(
        index="year",
        columns="sector_name",
        values="allocated_percentage",
        aggfunc="mean"
    )

    correlation_matrix = wide_df.corr()

    print(
        f"\n----- Cross-sector Correlation Matrix for {country_name} -----"
    )
    print(correlation_matrix.round(2))

    return correlation_matrix


if __name__ == "__main__":
    compute_sector_correlation("USA")
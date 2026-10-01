from sqlalchemy import create_engine, text
import pandas as pd


def analyze_budget_volatility(country_name):

    # SQLite SQLAlchemy engine
    engine = create_engine(
        "sqlite:///global_budget_db.db"
    )

    query = text("""
        SELECT
            b.year,
            b.Total_Budget_Billions_USD
        FROM budgets b
        JOIN countries c
            ON b.country_id = c.country_id
        WHERE c.country_name = :country_name
        ORDER BY b.year ASC
    """)

    df = pd.read_sql(
        query,
        engine,
        params={"country_name": country_name}
    )

    if df.empty:
        print(f"No data found for '{country_name}'.")
        return None

    # 10-year rolling mean
    df["rolling_mean"] = (
        df["Total_Budget_Billions_USD"]
        .rolling(window=10)
        .mean()
    )

    # 10-year rolling standard deviation
    df["rolling_std"] = (
        df["Total_Budget_Billions_USD"]
        .rolling(window=10)
        .std()
    )

    # Volatility Index (Coefficient of Variation)
    df["volatility_index"] = (
        df["rolling_std"] / df["rolling_mean"]
    ) * 100

    print(f"\n--- Era Volatility Index for {country_name} ---")
    print(df.dropna().head(10))

    return df


if __name__ == "__main__":
    analyze_budget_volatility("USA")
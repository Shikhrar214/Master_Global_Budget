import sqlite3
import pandas as pd
import numpy as np


def generate_statistical_forecast(
    country_name,
    target_year=2035,
    degree=2
):
    # Connect to SQLite
    conn = sqlite3.connect("global_budget_db.db")

    query = """
    SELECT
        b.year,
        b.Total_Budget_Billions_USD
    FROM budgets b
    JOIN countries c
        ON b.country_id = c.country_id
    WHERE c.country_name = ?
    ORDER BY b.year ASC;
    """

    df = pd.read_sql(
        query,
        conn,
        params=(country_name,)
    )

    conn.close()

    if df.empty:
        print(f"No data found for '{country_name}'.")
        return None, None

    # Historical data
    x_hist = df["year"].values
    y_hist = df["Total_Budget_Billions_USD"].values

    # Polynomial regression
    coefficients = np.polyfit(
        x_hist,
        y_hist,
        deg=degree
    )

    polynomial_model = np.poly1d(coefficients)

    # Historical trend
    df["trend_fit"] = polynomial_model(x_hist)

    # Future years
    future_years = np.array(
        list(range(x_hist.max() + 1, target_year + 1))
    )

    future_predictions = polynomial_model(future_years)

    df_forecast = pd.DataFrame({
        "year": future_years,
        "forecasted_budget": future_predictions
    })

    print(
        f"\n--- Analytical Projection for {country_name} "
        f"({x_hist.max() + 1}-{target_year}) ---"
    )

    print(df_forecast.head(10))

    return df, df_forecast


if __name__ == "__main__":

    hist_fit, future_proj = generate_statistical_forecast(
        "India",
        target_year=2035,
        degree=2
    )
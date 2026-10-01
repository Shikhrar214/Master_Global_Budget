import pandas as pd
from sqlalchemy import create_engine, text


def detect_budget_anomalies(country_name):

    # SQLite connection
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
        ORDER BY b.year ASC;
    """)

    df = pd.read_sql(
        query,
        engine,
        params={"country_name": country_name}
    )

    engine.dispose()

    if df.empty:
        print(f"No budget data found for country: {country_name}")
        return None

    # Calculate mean and standard deviation
    mean_val = df["Total_Budget_Billions_USD"].mean()
    std_val = df["Total_Budget_Billions_USD"].std()

    # Avoid division by zero
    if std_val == 0:
        print("Standard deviation is 0. Cannot calculate z-scores.")
        return None

    # Calculate Z-score
    df["z_score"] = (
        df["Total_Budget_Billions_USD"] - mean_val
    ) / std_val

    # Detect anomalies
    anomalies = df[
        df["z_score"].abs() > 1.96
    ]

    print(
        f"\n--- Budget Anomalies for {country_name} ---"
    )

    if anomalies.empty:
        print("No extreme anomalies detected.")
    else:
        print(
            anomalies[
                [
                    "year",
                    "Total_Budget_Billions_USD",
                    "z_score"
                ]
            ]
        )

        print(
            f"\nTotal anomalies detected: {len(anomalies)}"
        )

    return anomalies


if __name__ == "__main__":

    country_name = input(
        "Enter the country name to analyze budget anomalies: "
    )

    detect_budget_anomalies(country_name)
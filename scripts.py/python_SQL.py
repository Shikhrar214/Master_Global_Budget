import pandas as pd
import sqlite3


def run_robust_etl(csv_path):

    # Read CSV
    df = pd.read_csv(csv_path)

    # Replace missing values with 0
    df = df.fillna(0)

    conn = None

    try:
        # Connect to SQLite
        conn = sqlite3.connect("global_budget_db.db")
        cursor = conn.cursor()

        print("Step 1: Seeding Countries...")

        # Insert unique countries
        unique_countries = df["Country"].unique()

        for country in unique_countries:
            cursor.execute(
                """
                INSERT OR IGNORE INTO countries (country_name)
                VALUES (?)
                """,
                (country.strip(),)
            )

        conn.commit()

        # Create lookup dictionary
        cursor.execute(
            "SELECT country_name, country_id FROM countries"
        )

        country_lookup = dict(cursor.fetchall())

        # Sector names
        sectors = [
            "Defense",
            "Education",
            "Health",
            "Interest_Payments",
            "Infrastructure",
            "Agriculture",
            "State_Transfers",
            "Social_Welfare",
            "Administration_and_Others"
        ]

        success_count = 0

        print(f"Processing {len(df)} rows...")

        for idx, row in df.iterrows():

            try:

                country_name = row["Country"].strip()

                country_id = country_lookup.get(country_name)

                if country_id is None:
                    print(f"Country not found: {country_name}")
                    continue

                year = int(row["Year"])

                total_budget = float(
                    row["Total_Budget_Billions_USD"]
                )

                # Insert budget
                cursor.execute(
                    """
                    INSERT INTO budgets
                    (
                        country_id,
                        year,
                        Total_Budget_Billions_USD
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        country_id,
                        year,
                        total_budget
                    )
                )

                budget_id = cursor.lastrowid

                # Insert sector allocations
                for sector in sectors:

                    pct_col = f"{sector}_Percentage"
                    amt_col = f"{sector}_Amount_Billions_USD"

                    percentage = float(row[pct_col])
                    amount = float(row[amt_col])

                    cursor.execute(
                        """
                        INSERT INTO sector_allocations
                        (
                            budget_id,
                            sector_name,
                            allocated_percentage,
                            allocated_amount_billions_usd
                        )
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            budget_id,
                            sector,
                            percentage,
                            amount
                        )
                    )

                success_count += 1

            except Exception as row_err:
                print(f"Error processing row {idx}: {row_err}")

        conn.commit()

        print("\nETL completed successfully.")
        print(f"Rows inserted: {success_count}")

    except sqlite3.Error as db_err:
        print("Database Error:", db_err)

    finally:

        if conn is not None:
            conn.close()
            print("SQLite connection closed.")


if __name__ == "__main__":
    run_robust_etl("Master_Global_Budgets_Historical.csv")
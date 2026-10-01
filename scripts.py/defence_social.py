import pandas as pd
from sqlalchemy import create_engine, text


def analyze_guns_vs_butter(selected_year=2025):

    engine = create_engine(
        "sqlite:///global_budget_db.db"
    )

    query = text("""
    SELECT
        c.country_name,

        MAX(CASE
            WHEN sa.sector_name = 'Defense'
            THEN sa.allocated_percentage
        END) AS defense_pct,

        MAX(CASE
            WHEN sa.sector_name = 'Social_Welfare'
            THEN sa.allocated_percentage
        END) AS social_welfare_pct,

        MAX(CASE
            WHEN sa.sector_name = 'Education'
            THEN sa.allocated_percentage
        END) AS education_pct,

        ROUND(
            (
                MAX(CASE
                    WHEN sa.sector_name = 'Social_Welfare'
                    THEN sa.allocated_percentage
                END)
                +
                MAX(CASE
                    WHEN sa.sector_name = 'Education'
                    THEN sa.allocated_percentage
                END)
            )
            /
            NULLIF(
                MAX(CASE
                    WHEN sa.sector_name = 'Defense'
                    THEN sa.allocated_percentage
                END),
                0
            ),
            2
        ) AS civilian_to_defense_ratio

    FROM sector_allocations sa

    JOIN budgets b
        ON sa.budget_id = b.budget_id

    JOIN countries c
        ON b.country_id = c.country_id

    WHERE b.year = :selected_year

    GROUP BY c.country_name

    ORDER BY civilian_to_defense_ratio DESC;
    """)

    df = pd.read_sql(
        query,
        engine,
        params={"selected_year": selected_year}
    )

    print(
        f"\n--- Guns vs. Butter Ratio Rankings ({selected_year}) ---"
    )

    print(df.head(10))

    return df


if __name__ == "__main__":
    analyze_guns_vs_butter(2025)
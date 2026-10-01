import sqlite3

conn = sqlite3.connect("global_budget_db.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS countries (
    country_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_name TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS budgets (
    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    Total_Budget_Billions_USD REAL NOT NULL,
    
    FOREIGN KEY (country_id)
        REFERENCES countries(country_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sector_allocations (
    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_id INTEGER NOT NULL,
    sector_name TEXT NOT NULL,
    allocated_percentage REAL,
    allocated_amount_billions_usd REAL,

    FOREIGN KEY (budget_id)
        REFERENCES budgets(budget_id)
)
""")

conn.commit()
conn.close()

print("Tables created successfully!")
"""
load.py
Loads processed CSVs into a local SQLite database for SQL-based analysis.
"""

import sqlite3
from pathlib import Path

import pandas as pd

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "analytics.db"


def load_table(conn, csv_name, table_name):
    df = pd.read_csv(PROCESSED_DIR / csv_name)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"Loaded {table_name} ({len(df)} rows)")


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        load_table(conn, "repos.csv", "repos")
        load_table(conn, "events.csv", "events")
        load_table(conn, "languages.csv", "languages")
        conn.commit()
        print(f"Database ready at {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

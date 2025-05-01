# scripts/extract_valid_users.py

import duckdb
import joblib
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.config import DB_PATH, FILTERED_RATINGS_TABLE

def extract_valid_users():
    """Extrait les userId valides depuis la table filtrée et les sauvegarde."""
    if not os.path.exists("db/data"):
        os.makedirs("db/data")

    conn = duckdb.connect(DB_PATH)

    query = f"""
    SELECT DISTINCT userId
    FROM {FILTERED_RATINGS_TABLE}
    """

    df_users = conn.execute(query).fetchdf()
    valid_users = df_users["userId"].tolist()

    joblib.dump(valid_users, "db/data/valid_users.pkl")
    print(f"✅ {len(valid_users)} utilisateurs valides extraits et sauvegardés dans db/data/valid_users.pkl")

if __name__ == "__main__":
    extract_valid_users()

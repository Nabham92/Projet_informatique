# scripts/extract_data.py

import pandas as pd
from connect_db import connect_db
import config

def load_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Charge les tables 'ratings' et 'films' depuis DuckDB."""
    con = connect_db()
    df_ratings = con.execute(f"SELECT * FROM {config.FILTERED_RATINGS_TABLE}").fetchdf()
    df_films = con.execute(f"SELECT * FROM {config.FILMS_TABLE}").fetchdf()
    con.close()
    return df_ratings, df_films

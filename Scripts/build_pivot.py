# scripts/build_pivot.py

import pandas as pd
from extract_data import load_tables
import joblib

def build_pivot_table() -> pd.DataFrame:
    """Construit et sauvegarde la pivot table userId x movieId."""
    df_ratings, _ = load_tables()
    pivot = df_ratings.pivot(index='userId', columns='movieId', values='rating')
    joblib.dump(pivot, 'models/pivot_table.pkl')
    return pivot

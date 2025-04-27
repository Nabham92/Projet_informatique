import sys
import os
import joblib
import pandas as pd
import duckdb

# Monter jusqu'à la racine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Scripts')))

from config import MIN_USER_RATINGS, MIN_FILM_RATINGS, DB_PATH
from Scripts.build_pivot import build_pivot_table

# Charger modèle et pivot
MODEL_PATH = os.getenv("MODEL_PATH", "models/svd_model.pkl")
PIVOT_PATH = os.getenv("PIVOT_PATH", "models/pivot_table.pkl")
svd_model = joblib.load(MODEL_PATH)
pivot = joblib.load(PIVOT_PATH)

# Ne PAS ouvrir duckdb.connect ici !
duckdb_conn = None

def get_duckdb_conn():
    """Crée une seule connexion DuckDB quand nécessaire."""
    global duckdb_conn
    if duckdb_conn is None:
        duckdb_conn = duckdb.connect(DB_PATH)
    return duckdb_conn

def get_movie_titles(film_ids):
    if not film_ids:
        return {}

    conn = get_duckdb_conn()
    ids = ",".join(map(str, film_ids))
    query = f"""
        SELECT id, title
        FROM films
        WHERE id IN ({ids})
    """
    results = conn.execute(query).fetchall()
    return {row[0]: row[1] for row in results}

def get_recommendations(user_id: int, k: int = 10):
    pivot_filled = pivot.fillna(0)

    if user_id not in pivot_filled.index:
        raise ValueError(f"L'utilisateur {user_id} n'existe pas dans les données.")

    user_vector = pivot_filled.loc[user_id].values.reshape(1, -1)
    user_reduced = svd_model.transform(user_vector)
    reconstructed_ratings = user_reduced.dot(svd_model.components_).flatten()

    predictions = pd.DataFrame({
        "film_id": pivot.columns,
        "rating_predicted": reconstructed_ratings
    }).sort_values("rating_predicted", ascending=False).head(k)

    film_ids = predictions["film_id"].tolist()
    titles_dict = get_movie_titles(film_ids)

    enriched_predictions = []
    for _, row in predictions.iterrows():
        enriched_predictions.append({
            "film_id": int(row["film_id"]),
            "title": titles_dict.get(int(row["film_id"]), "Titre inconnu"),
            "rating_predicted": row["rating_predicted"]
        })

    return enriched_predictions

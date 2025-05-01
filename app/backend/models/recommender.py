import pandas as pd
import numpy as np
import duckdb
import sys
import os

# Ajouter le répertoire racine du projet au chemin Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from app.common import config
from app.backend.models.model_loader import load_model_and_pivot
from functools import lru_cache
from typing import List, Dict, Any

# Chargement unique
svd_model, pivot = load_model_and_pivot()
_duckdb_conn = None

def get_duckdb_conn():
    global _duckdb_conn
    if _duckdb_conn is None:
        _duckdb_conn = duckdb.connect(config.DB_PATH)
    return _duckdb_conn

@lru_cache(maxsize=1000)
def get_movie_titles(film_ids_tuple: tuple) -> dict:
    """Récupérer les titres des films à partir de leurs IDs"""
    film_ids = list(film_ids_tuple)
    if not film_ids:
        return {}
    try:
        conn = get_duckdb_conn()
        ids = ",".join(map(str, film_ids))
        query = f"SELECT id, title FROM films WHERE id IN ({ids})"
        results = conn.execute(query).fetchall()
        return {row[0]: row[1] for row in results}
    except Exception as e:
        print(f"Erreur lors de la récupération des titres: {e}")
        return {film_id: f"Film {film_id}" for film_id in film_ids}

async def get_recommendations(user_id: int, k: int = 10):
    """
    Générer des recommandations personnalisées pour un utilisateur
    
    Args:
        user_id: ID de l'utilisateur
        k: Nombre de recommandations à générer
        
    Returns:
        Tuple contenant la liste des recommandations et le type de recommandation
    """
    # S'assurer que l'utilisateur existe dans la matrice pivot
    pivot_filled = pivot.fillna(0)
    if user_id not in pivot_filled.index:
        raise ValueError(f"L'utilisateur {user_id} n'existe pas dans les données filtrées.")

    # Générer les recommandations avec le modèle SVD
    user_vector = pivot_filled.loc[user_id].values.reshape(1, -1)
    user_reduced = svd_model.transform(user_vector)
    reconstructed = user_reduced.dot(svd_model.components_).flatten()
    reconstructed = np.clip(reconstructed, 0, 5)

    # Sélectionner les films avec les meilleures notes prédites
    preds = pd.DataFrame({
        "film_id": pivot.columns,
        "rating_predicted": reconstructed
    }).nlargest(k, "rating_predicted")
    
    # Récupérer les titres des films
    film_ids = tuple(int(row["film_id"]) for _, row in preds.iterrows())
    titles = get_movie_titles(film_ids)
    
    # Construire la liste des recommandations
    recommendations = [
        {
            "film_id": int(row["film_id"]),
            "title": titles.get(int(row["film_id"]), f"Film {int(row['film_id'])}"),
            "rating_predicted": float(row["rating_predicted"])
        }
        for _, row in preds.iterrows()
    ]
    
    return recommendations, "personalized"

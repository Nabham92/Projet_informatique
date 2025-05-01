# Mise à jour du fichier app/backend/api/endpoints.py
from fastapi import APIRouter, HTTPException
from functools import lru_cache
try:
    from app.backend.models.recommender import get_recommendations
    from app.common.db import get_movie_details
    from app.common.config import VALID_USERS_PATH, CSV_PATH
    import joblib
    import pandas as pd
    import numpy as np
    import_success = True
except ImportError as e:
    print(f"Warning: Failed to import recommendation modules: {e}")
    import_success = False

router = APIRouter()

# Cache pour les données fréquemment utilisées
@lru_cache(maxsize=1)
def load_ratings_data():
    try:
        return pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"Error loading ratings data: {e}")
        return pd.DataFrame()

@lru_cache(maxsize=1)
def load_valid_users():
    try:
        return joblib.load(VALID_USERS_PATH)
    except Exception as e:
        print(f"Error loading valid users: {e}")
        return []

# Endpoint pour les recommandations
@router.post("/recommendations/{user_id}")
async def recommend_movies(user_id: int, k: int = 10):
    if not import_success:
        # Données fictives pour test si les imports ont échoué
        return {
            "user_id": user_id, 
            "recommendations": [
                {"film_id": 1, "title": "Test Movie 1", "rating_predicted": 4.5},
                {"film_id": 2, "title": "Test Movie 2", "rating_predicted": 4.3}
            ],
            "recommendation_type": "test"
        }
        
    valid_users = load_valid_users()
    if user_id not in valid_users:
        raise HTTPException(
            status_code=400, 
            detail=f"L'utilisateur {user_id} n'est pas dans la liste des utilisateurs avec suffisamment de données. Veuillez choisir un utilisateur parmi la liste fournie."
        )
    
    try:
        # Appel à la fonction de recommandation
        recommendations, recommendation_type = await get_recommendations(user_id, k)
        
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "recommendation_type": recommendation_type
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/movie/{movie_id}")
async def get_movie(movie_id: int):
    if not import_success:
        return {"id": movie_id, "title": "Test Movie", "overview": "Test overview"}
        
    movie = get_movie_details(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Film non trouvé")
    return movie

# Endpoint de santé pour vérifier si le backend est prêt
@router.get("/health")
async def health_check():
    try:
        # Vérifie que les données sont chargées
        ratings = load_ratings_data()
        valid_users = load_valid_users()
        return {
            "status": "ok", 
            "imports_ok": import_success,
            "data_loaded": not ratings.empty and len(valid_users) > 0,
            "valid_users_count": len(valid_users)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
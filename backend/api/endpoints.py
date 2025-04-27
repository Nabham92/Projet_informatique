from fastapi import APIRouter, HTTPException
from backend.models.recommender import get_recommendations
from backend.db import get_movie_details

router = APIRouter()

@router.post("/recommendations/{user_id}")
def recommend_movies(user_id: int, k: int = 10):
    try:
        recommendations = get_recommendations(user_id, k)
        return {"user_id": user_id, "recommendations": recommendations}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/movie/{movie_id}")
def get_movie(movie_id: int):
    movie = get_movie_details(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Film non trouvé")
    return movie

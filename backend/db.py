import duckdb
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DB_PATH

def get_movie_details(movie_id: int):
    conn = duckdb.connect(DB_PATH)
    query = f"""
    SELECT id, title, genres, description, release_date, vote_average, vote_count
    FROM films
    WHERE id = {movie_id}
    """
    result = conn.execute(query).fetchone()
    if result:
        keys = ["id", "title", "genres", "description", "release_date", "vote_average", "vote_count"]
        return dict(zip(keys, result))
    else:
        return None

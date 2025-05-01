import os
from pathlib import Path

# === CONFIGURATION DES RÉPERTOIRES ===
BASE_DIR = Path(__file__).resolve().parents[1]  # remonte à /app/
ROOT_DIR = BASE_DIR.parent                     # racine du projet
DATA_DIR = ROOT_DIR / "data"
MODEL_DIR = BASE_DIR / "backend" / "models"

# === FICHIERS DE DONNÉES ===
CSV_PATH = DATA_DIR / "ratings.csv"
LINKS_CSV_PATH = DATA_DIR / "links.csv"
DB_PATH = DATA_DIR / "movie_ratings.duckdb"

# === FICHIERS DE MODÈLES ===
MODEL_PATH = MODEL_DIR / "svd_model.pkl"
PIVOT_PATH = MODEL_DIR / "pivot_table.pkl"

# === TABLES ===
RATINGS_TABLE = "ratings"
FILTERED_RATINGS_TABLE = "filtered_ratings"
FILMS_TABLE = "films"

# === FILTRES POUR LE MODÈLE ===
MIN_USER_RATINGS = 200
MIN_FILM_RATINGS = 2000

# === API TMDB ===
API_KEY = os.getenv("API_KEY", "d307f7aa11cf0b88e95564888ae450ef")
BASE_URL = "https://api.themoviedb.org/3"
LANG = "fr-FR"
N_PAGES = 5

TMDB_MOVIE_URL_TEMPLATE = (
    "https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=fr-FR"
)
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

# === BACKEND ===
# Déterminer dynamiquement l'URL du backend en fonction de l'environnement
# Si la variable d'environnement DOCKER_ENV est définie, nous sommes dans Docker
# Sinon, nous supposons une exécution locale
if os.getenv("DOCKER_ENV") == "true":
    # Dans Docker, utilisez le nom du service comme hôte
    BACKEND_URL = "http://backend:8000"
else:
    # En local, utilisez localhost
    BACKEND_URL = "http://localhost:8000"


print(f"Backend URL configurée: {BACKEND_URL}")

VALID_USERS_PATH = DATA_DIR / "valid_users.pkl"

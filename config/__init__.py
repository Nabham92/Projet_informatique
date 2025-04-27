# config.py

# API TMDB
API_KEY_TMDB = "d307f7aa11cf0b88e95564888ae450ef"
BASE_URL_TMDB = "https://api.themoviedb.org/3"
LANGUAGE_TMDB = "fr-FR"
N_PAGES_TMDB = 5

# Base de données
DB_PATH = "movies.duckdb"

# Chemins fichiers
CSV_PATH = r"db\data\ratings.csv"
LINKS_CSV_PATH = r"db\data\links.csv"

# Noms des tables DuckDB
RATINGS_TABLE = "ratings"
FILMS_TABLE = "films"
FILTERED_RATINGS_TABLE = "filtered_ratings"

# Seuils de filtrage pour filtrage collaboratif
MIN_USER_RATINGS = 1000
MIN_FILM_RATINGS = 300

# URL du Backend API
BACKEND_URL = "http://127.0.0.1:8000"

# Format TMDB pour récupérer un film
TMDB_MOVIE_URL_TEMPLATE = f"{BASE_URL_TMDB}/movie/{{}}?api_key={API_KEY_TMDB}&language={LANGUAGE_TMDB}"

# Base pour les affiches TMDB
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

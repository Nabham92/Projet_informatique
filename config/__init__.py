# API TMDB
API_KEY = r"d307f7aa11cf0b88e95564888ae450ef"
BASE_URL = "https://api.themoviedb.org/3"
LANG = "fr-FR"
N_PAGES = 5

# Base de données
DB_PATH = "movies.duckdb"

# Chemins fichiers
CSV_PATH = r"db\data\ratings.csv"

# Noms des tables DuckDB
RATINGS_TABLE = "ratings"
FILMS_TABLE = "films"
FILTERED_RATINGS_TABLE = "filtered_ratings"

# Seuils de filtrage pour le modèle
MIN_USER_RATINGS = 10
MIN_FILM_RATINGS = 50

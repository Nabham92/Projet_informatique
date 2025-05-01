# app/scripts/load_data.py

import pandas as pd
import duckdb
import requests
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common import config
from common.db import get_db_connection as connect_db

# === Load ratings.csv dans DuckDB ===

def create_table_from_csv(con, table_name, csv_path):
    query = f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_csv('{csv_path}', AUTO_DETECT=TRUE)
            """
    con.execute(query)
    print(f"Table '{table_name}' créée à partir de {csv_path}")

def show_tables(con):
    tables = con.execute("SHOW TABLES").fetchdf()
    print("Tables dans la base :")
    print(tables)

# === Collecte films depuis TMDB API ===

def get_popular_movies(n_pages=config.N_PAGES, language=config.LANG):
    all_films = []
    for page in range(1, n_pages + 1):
        url = f"{config.BASE_URL}/movie/popular?api_key={config.API_KEY}&language={language}&page={page}"
        res = requests.get(url)
        if res.status_code == 200:
            all_films.extend(res.json().get("results", []))
    return pd.DataFrame(all_films)

def clean_films_dataframe(df):
    cols = ["id", "title", "genre_ids", "overview", "release_date", "vote_average", "vote_count"]
    df = df[cols].copy()    
    df.columns = ["id", "title", "genres", "description", "release_date", "vote_average", "vote_count"]
    return df

def get_genre_mapping(api_key=config.API_KEY, language=config.LANG):
    """Récupérer la liste des genres avec leur ID depuis TMDB API"""
    url = f"{config.BASE_URL}/genre/movie/list?api_key={api_key}&language={language}"
    response = requests.get(url)
    if response.status_code == 200:
        genres = response.json().get("genres", [])
        return {genre["id"]: genre["name"] for genre in genres}
    return {}

def create_film_genres_table(con, df_films, genre_mapping):
    """Créer une table film_genres avec les relations film-genre"""
    film_genres = []
    
    for _, row in df_films.iterrows():
        film_id = row["id"]
        # Les genres peuvent être des listes JSON ou des chaînes représentant des listes
        if isinstance(row["genres"], str):
            try:
                genre_ids = json.loads(row["genres"])
            except:
                genre_ids = []
        else:
            genre_ids = row["genres"]
            
        # Si c'est une liste, extraire chaque genre
        if isinstance(genre_ids, list):
            for genre_id in genre_ids:
                genre_name = genre_mapping.get(genre_id, "Unknown")
                film_genres.append({"film_id": film_id, "genre_id": genre_id, "genre": genre_name})
    
    # Créer un DataFrame à partir des relations film-genre
    df_film_genres = pd.DataFrame(film_genres)
    
    # Sauvegarder dans DuckDB
    if not df_film_genres.empty:
        con.execute("CREATE OR REPLACE TABLE film_genres AS SELECT * FROM df_film_genres")
        print(f"Table 'film_genres' créée avec {len(df_film_genres)} associations film-genre")
    else:
        print("Aucune donnée de genre à sauvegarder")

def save_to_duckdb(df, table_name="films"):
    con = connect_db()
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
    print(f"Table '{table_name}' enregistrée dans {config.DB_PATH}")
    
    # Si nous sauvegardons la table films, créons aussi la table des genres
    if table_name == "films":
        genre_mapping = get_genre_mapping()
        create_film_genres_table(con, df, genre_mapping)
    
    con.close()

# === Main principal ===

def main():
    # 1. Charger ratings.csv
    con = connect_db()
    create_table_from_csv(con, table_name="ratings", csv_path=config.CSV_PATH)
    show_tables(con)
    con.close()

    # 2. Récupérer les films populaires via TMDB
    df_raw = get_popular_movies()
    df_clean = clean_films_dataframe(df_raw)
    save_to_duckdb(df_clean, table_name="films")

if __name__ == "__main__":
    main()

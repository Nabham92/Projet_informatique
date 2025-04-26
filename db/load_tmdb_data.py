import pandas as pd 
import requests 
import json 
import duckdb
import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config

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

def save_to_duckdb(df, table_name="films"):
    con = duckdb.connect(config.DB_PATH)
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
    print(f"Table '{table_name}' enregistrée dans {config.DB_PATH}")
    con.close()

def main():
    df_raw = get_popular_movies()
    df_clean = clean_films_dataframe(df_raw)
    save_to_duckdb(df_clean)

if __name__ == "__main__":
    main()
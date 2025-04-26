import pandas as pd
import duckdb
import logging
from typing import Optional
import sys
import os
# Permet d'importer config peut importe notre dossier
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config

# Setup du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def connect_db(db_path: str) -> duckdb.DuckDBPyConnection:
    """Se connecte à la base de données DuckDB."""
    try:
        con = duckdb.connect(db_path)
        logging.info(f"Connecté à la base de données : {db_path}")
        return con
    except Exception as e:
        logging.error(f"Erreur de connexion à la base de données : {e}")
        raise

def create_filtered_ratings_table(con: duckdb.DuckDBPyConnection) -> None:
    """
    Crée une table 'filtered_ratings' contenant :
    - uniquement les utilisateurs ayant noté au moins MIN_USER_RATINGS films
    - uniquement les films ayant reçu au moins MIN_FILM_RATINGS évaluations dans ratings.csv
    """
    try:
        con.execute(f"""
        CREATE OR REPLACE TABLE {config.FILTERED_RATINGS_TABLE} AS
        WITH active_users AS (
            SELECT userId
            FROM {config.RATINGS_TABLE}
            GROUP BY userId
            HAVING COUNT(*) >= {config.MIN_USER_RATINGS}
        ),
        popular_movies AS (
            SELECT movieId
            FROM {config.RATINGS_TABLE}
            GROUP BY movieId
            HAVING COUNT(*) >= {config.MIN_FILM_RATINGS}
        )
        SELECT r.userId, r.movieId, r.rating
        FROM {config.RATINGS_TABLE} r
        JOIN active_users au ON r.userId = au.userId
        JOIN popular_movies pm ON r.movieId = pm.movieId
        """)
        logging.info(f"Table '{config.FILTERED_RATINGS_TABLE}' créée avec succès.")
    except Exception as e:
        logging.error(f"Erreur lors de la création de la table '{config.FILTERED_RATINGS_TABLE}': {e}")
        raise

def summarize_filtered_data(con: duckdb.DuckDBPyConnection) -> None:
    """Affiche des statistiques basiques sur la table filtrée."""
    try:
        stats = con.execute(f"""
        SELECT 
            COUNT(DISTINCT userId) AS nb_users,
            COUNT(DISTINCT movieId) AS nb_films,
            COUNT(*) AS nb_ratings
        FROM {config.FILTERED_RATINGS_TABLE}
        """).fetchdf()

        logging.info(f"Résumé des données filtrées :\n{stats}")
    except Exception as e:
        logging.error(f"Erreur lors du résumé des données : {e}")
        raise

def main() -> None:
    """Fonction principale."""
    try:
        con = connect_db(config.DB_PATH)
        create_filtered_ratings_table(con)
        summarize_filtered_data(con)
        con.close()
        logging.info("Traitement terminé avec succès.")
    except Exception as e:
        logging.error(f"Erreur dans l'exécution du script : {e}")

if __name__ == "__main__":
    main()

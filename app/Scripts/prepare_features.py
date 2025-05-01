# app/scripts/prepare_features.py

import os
import sys
import logging
import pandas as pd
import joblib
import duckdb
import json

# Ajouter le répertoire racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common import config

# Logger configuration
logging.basicConfig(level=logging.INFO, format="%((asctime)s)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_connection():
    """
    Ouvre une nouvelle connexion DuckDB en lecture-écriture.
    """
    return duckdb.connect(database=str(config.DB_PATH), read_only=False)


def create_filtered_ratings_table():
    """
    Crée une table filtrée ne contenant que les utilisateurs actifs et les films populaires.
    """
    con = get_connection()
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
        """ )
        logger.info(f"✅ Table '{config.FILTERED_RATINGS_TABLE}' créée.")
    except Exception as e:
        logger.error(f"❌ Erreur création table filtrée : {e}")
        raise
    finally:
        con.close()


def summarize_filtered_data():
    """
    Affiche un résumé statistique de la table filtrée.
    """
    con = get_connection()
    try:
        stats = con.execute(f"""
        SELECT
            COUNT(DISTINCT userId) AS nb_users,
            COUNT(DISTINCT movieId) AS nb_films,
            COUNT(*) AS nb_ratings
        FROM {config.FILTERED_RATINGS_TABLE}
        """).fetchdf()
        logger.info(f"📊 Résumé des données filtrées :\n{stats}")
    except Exception as e:
        logger.error(f"❌ Erreur résumé des données : {e}")
        raise
    finally:
        con.close()


def build_pivot_table():
    """
    Construit et sauvegarde la table pivot (userId x movieId).
    """
    con = get_connection()
    try:
        df_ratings = con.execute(f"SELECT * FROM {config.FILTERED_RATINGS_TABLE}").fetchdf()
    finally:
        con.close()

    pivot = df_ratings.pivot(index='userId', columns='movieId', values='rating')

    pivot_path = os.path.join(config.MODEL_DIR, 'pivot_table.pkl')
    joblib.dump(pivot, pivot_path)
    logger.info(f"✅ Pivot table sauvegardée dans {pivot_path}")
    return pivot


def save_valid_users_list():
    """
    Génère la liste des utilisateurs valides et leur mapping, puis sauvegarde.
    """
    con = get_connection()
    try:
        result = con.execute(f"SELECT DISTINCT userId FROM {config.FILTERED_RATINGS_TABLE} ORDER BY userId").fetchnumpy()
    finally:
        con.close()

    valid_users_list = result['userId'].tolist()

    # Mappings original -> nouveau et inverse
    reindexed_map = {orig: idx for idx, orig in enumerate(valid_users_list, start=1)}
    inv_map = {idx: orig for orig, idx in reindexed_map.items()}

    # Sauvegarde
    joblib.dump(valid_users_list, config.VALID_USERS_PATH)
    base_dir = os.path.dirname(config.VALID_USERS_PATH)
    joblib.dump(reindexed_map, os.path.join(base_dir, 'user_id_mapping.pkl'))
    joblib.dump(inv_map, os.path.join(base_dir, 'inv_user_id_mapping.pkl'))

    # Sauvegarde du nombre
    count_path = os.path.join(base_dir, 'valid_users_count.json')
    with open(count_path, 'w') as f:
        json.dump({'count': len(valid_users_list)}, f)

    logger.info(f"✅ {len(valid_users_list)} utilisateurs valides sauvegardés dans {config.VALID_USERS_PATH}")


def main():
    try:
        create_filtered_ratings_table()
        summarize_filtered_data()
        build_pivot_table()
        save_valid_users_list()
        logger.info("✅ Prétraitement terminé avec succès.")
    except Exception as e:
        logger.critical(f"❌ Erreur globale dans prepare_features.py : {e}")


if __name__ == '__main__':
    main()

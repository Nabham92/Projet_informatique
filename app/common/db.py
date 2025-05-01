# Mise à jour de app/common/db.py
import os
import time
import logging
import duckdb
from functools import lru_cache
from app.common.config import DB_PATH

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db")

# Connexion singleton pour DuckDB
_conn = None

def get_db_connection():
    """
    Crée une connexion singleton à la base DuckDB
    avec gestion des erreurs et retry améliorés
    """
    global _conn
    
    if _conn is not None:
        return _conn
    
    max_retries = 5
    retry_interval = 2  # secondes
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Tentative de connexion à DuckDB ({attempt+1}/{max_retries})")
            
            # Vérifier l'existence du fichier
            if not os.path.exists(DB_PATH):
                logger.warning(f"Le fichier DB n'existe pas: {DB_PATH}")
                _conn = duckdb.connect(str(DB_PATH), read_only=False)
                logger.info("Nouveau fichier DB créé")
                return _conn
            
            # Vérifier les permissions
            if not os.access(DB_PATH, os.R_OK | os.W_OK):
                logger.warning(f"Problème de permissions sur {DB_PATH}, tentative de correction")
                try:
                    # Tenter de corriger les permissions
                    os.chmod(DB_PATH, 0o666)
                    logger.info(f"Permissions corrigées pour {DB_PATH}")
                except Exception as e:
                    logger.error(f"Impossible de corriger les permissions: {e}")
            
            # Tenter la connexion
            _conn = duckdb.connect(str(DB_PATH), read_only=False)
            logger.info("Connexion à DuckDB établie avec succès")
            return _conn
            
        except Exception as e:
            logger.error(f"Erreur de connexion à DuckDB (tentative {attempt+1}): {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"Nouvelle tentative dans {retry_interval} secondes...")
                time.sleep(retry_interval)
                retry_interval *= 1.5  # Augmenter progressivement l'intervalle
    
    logger.critical("Impossible de se connecter à DuckDB après plusieurs tentatives")
    raise Exception("Échec de connexion à la base de données après plusieurs tentatives")

@lru_cache(maxsize=1000)
def get_movie_details(movie_id):
    """
    Récupère les détails d'un film à partir de son ID
    avec cache pour améliorer les performances
    """
    try:
        conn = get_db_connection()
        start_time = time.time()
        
        # Requête optimisée
        query = f"""
            SELECT 
                id, 
                title,
                overview,
                release_date,
                vote_average,
                vote_count,
                popularity
            FROM films
            WHERE id = {movie_id}
            LIMIT 1
        """
        
        result = conn.execute(query).fetchone()
        
        logger.debug(f"Requête film {movie_id} exécutée en {time.time() - start_time:.4f}s")
        
        if result:
            # Convertir le résultat en dictionnaire
            columns = ["id", "title", "overview", "release_date", "vote_average", "vote_count", "popularity"]
            movie = {columns[i]: result[i] for i in range(len(columns))}
            return movie
        return None
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du film {movie_id}: {e}")
        return None
import duckdb
from pathlib import Path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

def connect_db() -> duckdb.DuckDBPyConnection:
    """Se connecte à la base DuckDB en vérifiant l'existence du fichier."""
    db_path = Path(config.DB_PATH)
    if not db_path.exists():
        raise FileNotFoundError(f"Base de données non trouvée à {db_path.resolve()}")
    return duckdb.connect(str(db_path))

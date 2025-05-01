import joblib
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from app.common.config import MODEL_PATH, PIVOT_PATH

def load_model_and_pivot():
    """Charge le modèle SVD et la table pivot depuis des fichiers .pkl."""
    try:
        svd_model = joblib.load(MODEL_PATH)
        pivot = joblib.load(PIVOT_PATH)
        print("Modèle SVD et pivot chargés avec succès.")
        return svd_model, pivot
    except Exception as e:
        raise RuntimeError(f"Erreur lors du chargement du modèle ou du pivot: {e}")

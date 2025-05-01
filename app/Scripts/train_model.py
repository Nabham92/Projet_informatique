# app/scripts/train_model.py

import os
import joblib
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from scipy import sparse

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Scripts.prepare_features import build_pivot_table

def train_svd(n_components: int = 50) -> None:
    """Entraîne un modèle SVD et sauvegarde modèle, pivot, et users valides."""
    
    pivot = build_pivot_table()
    pivot_filled = pivot.fillna(0)

    svd = TruncatedSVD(n_components=n_components, random_state=42)
    svd.fit(pivot_filled)

    model_dir = os.path.join("app", "backend", "models")
    os.makedirs(model_dir, exist_ok=True)

    joblib.dump(svd, os.path.join(model_dir, "svd_model.pkl"))
    
    pivot_sparse = sparse.csr_matrix(pivot_filled.values.astype("float32"))
    joblib.dump(pivot_sparse, os.path.join(model_dir, "pivot.pkl"), compress=3)

    users_path = os.path.join("data", "valid_users.pkl")
    os.makedirs("data", exist_ok=True)
    joblib.dump(pivot.index.to_list(), users_path, compress=3)

    print(f"✅ Modèle SVD sauvé ({n_components} composants).")
    print(f"📁 Pivot : {model_dir}/pivot.pkl\n📁 Utilisateurs valides : {users_path}")

if __name__ == "__main__":
    train_svd()

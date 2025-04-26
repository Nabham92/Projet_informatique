# scripts/train_svd.py

import joblib
from sklearn.decomposition import TruncatedSVD
from build_pivot import build_pivot_table
import os

def train_svd(n_components: int = 50) -> None:
    """Entraîne un modèle SVD et sauvegarde modèle + pivot."""
    if not os.path.exists('models'):
        os.makedirs('models')
        
    pivot = build_pivot_table()
    pivot_filled = pivot.fillna(0)

    svd = TruncatedSVD(n_components=n_components, random_state=42)
    matrix_reduced = svd.fit_transform(pivot_filled)

    joblib.dump(svd, 'models/svd_model.pkl')
    print(f"Modèle SVD sauvé avec {n_components} dimensions.")

if __name__ == "__main__":
    train_svd()

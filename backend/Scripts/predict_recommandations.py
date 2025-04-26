# scripts/predict_recommendations.py

import joblib
import pandas as pd

def recommend_top_n(user_id: int, n: int = 5) -> pd.Series:
    """Charge le modèle SVD et la pivot table pour recommander N films."""
    svd = joblib.load('models/svd_model.pkl')
    pivot = joblib.load('models/pivot_table.pkl')

    pivot_filled = pivot.fillna(0)
    matrix_reduced = svd.transform(pivot_filled)

    approximation = svd.inverse_transform(matrix_reduced)
    predicted_ratings = pd.DataFrame(approximation, index=pivot.index, columns=pivot.columns)

    try:
        user_pred = predicted_ratings.loc[user_id]
    except KeyError:
        raise ValueError(f"Utilisateur {user_id} introuvable dans la base.")

    already_rated = pivot.loc[user_id][pivot.loc[user_id].notna()].index
    recommendations = user_pred.drop(index=already_rated).sort_values(ascending=False)
    
    return recommendations.head(n)

if __name__ == "__main__":
    user_id = 1
    print(recommend_top_n(user_id))

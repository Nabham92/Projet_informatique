import streamlit as st
st.set_page_config(page_title="🎬 Recommandations de Films", layout="wide")
import pandas as pd
import joblib
import requests
import os 
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import BACKEND_URL, TMDB_MOVIE_URL_TEMPLATE, TMDB_IMAGE_URL, LINKS_CSV_PATH

import streamlit as st
import pandas as pd
import joblib
import requests
import os
import sys

# --------------------
# FONCTIONS UTILES
# --------------------
@st.cache_data
def load_links():
    links = pd.read_csv(LINKS_CSV_PATH)
    links = links.dropna(subset=["tmdbId"])
    links["tmdbId"] = links["tmdbId"].astype(int)
    return dict(zip(links["movieId"], links["tmdbId"]))

@st.cache_data
def load_valid_users():
    return joblib.load("db/data/valid_users.pkl")

def get_recommendations(user_id, k=5):
    url = f"{BACKEND_URL}/recommendations/{user_id}?k={k}"
    response = requests.post(url)
    if response.status_code == 200:
        return response.json().get("recommendations", [])
    else:
        raise ValueError(response.json().get("detail", "Erreur lors de la récupération des recommandations"))

def get_movie_details(tmdb_id):
    url = TMDB_MOVIE_URL_TEMPLATE.format(tmdb_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def rescale_rating(rating_predicted):
    """Passe une note sur 5 vers une note sur 10, avec clip à 10."""
    scaled = rating_predicted * 2
    clipped = min(scaled, 10.0)
    return round(clipped, 1)

# --------------------
# CHARGEMENT DES DONNÉES
# --------------------
links_mapping = load_links()
valid_users = load_valid_users()

# --------------------
# INTERFACE STREAMLIT
# --------------------
st.title("🎬 Système de Recommandation de Films")

user_id = st.selectbox("Choisissez votre ID utilisateur :", valid_users)
k = st.slider("Nombre de recommandations :", min_value=1, max_value=20, value=5)

if st.button("Obtenir mes recommandations"):
    with st.spinner("Chargement des recommandations... 🍿"):
        try:
            recommendations = get_recommendations(user_id, k)
        except Exception as e:
            st.error(f"Erreur : {e}")
            st.stop()

        if recommendations:
            st.success(f"Top {k} recommandations pour l'utilisateur {user_id}")
            cols = st.columns(3)  # 3 cartes par ligne

            for idx, rec in enumerate(recommendations):
                movie_id = rec["film_id"]
                predicted_rating = rec["rating_predicted"]

                # Conversion movieId --> tmdbId
                tmdb_id = links_mapping.get(movie_id)

                if tmdb_id:
                    movie = get_movie_details(tmdb_id)

                    if movie:
                        title = movie.get("title", "Titre non disponible")
                        overview = movie.get("overview", "Pas de synopsis.")
                        poster_path = movie.get("poster_path", None)
                        tmdb_rating = movie.get("vote_average", None)

                        rescaled_rating = rescale_rating(predicted_rating)

                        with cols[idx % 3]:  # 3 colonnes, modulo pour alterner
                            with st.container():
                                if poster_path:
                                    st.image(f"{TMDB_IMAGE_URL}{poster_path}", width=200)
                                else:
                                    st.text("(Pas d'image disponible)")

                                st.markdown(f"### {title}")
                                st.markdown(f"⭐ **Note prédite** : {rescaled_rating}/10")
                                
                                if tmdb_rating:
                                    st.markdown(f"🎯 **Note TMDB** : {tmdb_rating}/10")

                                st.caption(overview[:150] + "...")  # Petit extrait de synopsis
                    else:
                        st.warning(f"Détails introuvables pour TMDB ID {tmdb_id}")
                else:
                    st.warning(f"Aucun TMDB ID pour movieId {movie_id}")
        else:
            st.warning("Aucune recommandation trouvée pour cet utilisateur.")

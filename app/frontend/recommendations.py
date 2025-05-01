import streamlit as st
import pandas as pd
import joblib
import requests
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.config import VALID_USERS_PATH, TMDB_MOVIE_URL_TEMPLATE, TMDB_IMAGE_URL, LINKS_CSV_PATH, API_KEY
if os.environ.get('DOCKER_ENV') == 'true':
    BACKEND_URL = "http://backend:8000"
else:
    BACKEND_URL = "http://localhost:8000"
# --------------------
# FONCTIONS POUR LES RECOMMANDATIONS
# --------------------
@st.cache_data
def load_links():
    links = pd.read_csv(LINKS_CSV_PATH, encoding="ISO-8859-1")
    links = links.dropna(subset=["tmdbId"])
    links["tmdbId"] = links["tmdbId"].astype(int)
    return dict(zip(links["movieId"], links["tmdbId"]))
    
@st.cache_data
def load_valid_users():
    return joblib.load(VALID_USERS_PATH)

@st.cache_data
def load_ratings_data():
    ratings = pd.read_csv(os.path.join(os.path.dirname(VALID_USERS_PATH), 'ratings.csv'))
    return ratings

def get_user_ratings_count(user_id):
    """Obtenir le nombre d'évaluations données par un utilisateur"""
    ratings = load_ratings_data()
    return len(ratings[ratings['userId'] == user_id])

def get_recommendations(user_id, k=5):
    try:
        url = f"{BACKEND_URL}/recommendations/{user_id}"
        
        with st.sidebar.expander("🔧 Informations de débogage", expanded=False):
            st.write(f"Tentative de connexion à: {url} (POST)")
        
        response = requests.post(url, params={"k": k}, timeout=60)
        
        with st.sidebar.expander("🔧 Informations de débogage", expanded=False):
            st.write(f"Statut de la réponse: {response.status_code}")
            st.write(f"Temps de réponse: {response.elapsed.total_seconds():.2f} secondes")
        
        if response.status_code == 200:
            data = response.json()
            return data.get("recommendations", []), data.get("recommendation_type", "personalized")
        else:
            with st.sidebar.expander("🔧 Erreur", expanded=True):
                st.error(f"Erreur {response.status_code}: {response.text}")
            error_message = response.json().get("detail", "Erreur lors de la récupération des recommandations")
            raise ValueError(error_message)
    except Exception as e:
        with st.sidebar.expander("🔧 Erreur", expanded=True):
            st.error(f"Erreur inattendue: {e}")
        raise ValueError(f"Une erreur s'est produite: {str(e)}")

def get_movie_details(tmdb_id):
    url = TMDB_MOVIE_URL_TEMPLATE.format(movie_id=tmdb_id, api_key=API_KEY)
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

def display_movie_card(movie, predicted_rating, col):
    """Affiche une carte de film dans la colonne spécifiée"""
    with col:
        with st.container():
            # Image du film
            poster_path = movie.get("poster_path", None)
            if poster_path:
                st.image(f"{TMDB_IMAGE_URL}{poster_path}", width=200)
            else:
                st.image("https://via.placeholder.com/200x300?text=Pas+d'image", width=200)

            # Titre et notes
            st.markdown(f"### {movie.get('title', 'Titre non disponible')}")
            st.markdown(f"⭐ **Note prédite** : {rescale_rating(predicted_rating)}/10")
            
            tmdb_rating = movie.get("vote_average", None)
            if tmdb_rating:
                st.markdown(f"🎯 **Note TMDB** : {tmdb_rating}/10")
            
            # Genres
            genres = movie.get("genres", [])
            if genres:
                genre_names = [g["name"] for g in genres]
                st.markdown(f"🎭 **Genres** : {', '.join(genre_names)}")
            
            # Date de sortie
            release_date = movie.get("release_date", "")
            if release_date:
                year = release_date.split("-")[0]
                st.markdown(f"📅 **Année** : {year}")
            
            # Synopsis avec bouton "lire la suite"
            overview = movie.get("overview", "Pas de synopsis disponible.")
            if overview:
                # Créer un ID unique pour ce film
                movie_id = movie.get("id", "unknown")
                read_more_id = f"read_more_{movie_id}"
                
                # Ajouter le synopsis
                st.markdown("📝 **Synopsis** :")
                
                if len(overview) > 100:
                    # Créer un état pour suivre si le texte est développé
                    if read_more_id not in st.session_state:
                        st.session_state[read_more_id] = False
                    
                    # Afficher l'extrait ou le texte complet selon l'état
                    if not st.session_state[read_more_id]:
                        st.markdown(f"{overview[:100]}...")
                        if st.button("Lire la suite", key=f"btn_{read_more_id}"):
                            st.session_state[read_more_id] = True
                            st.experimental_rerun()
                    else:
                        st.markdown(overview)
                        if st.button("Réduire", key=f"btn_{read_more_id}"):
                            st.session_state[read_more_id] = False
                            st.experimental_rerun()
                else:
                    st.markdown(overview)

def show_recommendations():
    """Afficher la page des recommandations"""
    st.markdown("### Découvrez des films adaptés à vos goûts")
    
    # Charger les données nécessaires
    links_mapping = load_links()
    valid_users = load_valid_users()
    
    # Information sur le nombre total d'utilisateurs valides
    st.info(f"Notre système propose des recommandations pour {len(valid_users)} utilisateurs qui ont suffisamment d'évaluations.")
    
    # Créer deux colonnes pour la sélection de l'utilisateur et la recherche
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Sélection de l'utilisateur avec un menu déroulant
        user_id = st.selectbox("Choisissez un utilisateur :", valid_users, key="select_user")
    
    with col2:
        # Barre de recherche pour les utilisateurs
        search_id = st.number_input("Ou recherchez un ID utilisateur spécifique :", min_value=1, step=1, key="search_user")
        if st.button("Rechercher", key="search_button"):
            if search_id in valid_users:
                # Si l'utilisateur est valide, le sélectionner dans le dropdown
                st.session_state.select_user = search_id
                user_id = search_id
            else:
                # Si l'utilisateur n'est pas valide, afficher un message
                ratings_count = get_user_ratings_count(search_id)
                if ratings_count > 0:
                    st.warning(f"⚠️ L'utilisateur {search_id} a donné {ratings_count} avis, ce qui est insuffisant pour générer des recommandations personnalisées (minimum requis: {200}).")
                else:
                    st.error(f"❌ L'utilisateur {search_id} n'a donné aucun avis. Aucune recommandation ne peut être générée.")
    
    # Sélection du nombre de recommandations
    k = st.slider("Nombre de recommandations :", min_value=1, max_value=20, value=5)
    
    # Bouton pour lancer la recherche
    if st.button("Obtenir les recommandations"):
        with st.spinner("Chargement des recommandations... 🍿"):
            try:
                # Vérifier que l'utilisateur est dans la liste des utilisateurs valides
                if user_id not in valid_users:
                    st.error(f"❌ L'utilisateur {user_id} n'a pas donné suffisamment d'avis pour générer des recommandations personnalisées.")
                else:
                    recommendations, rec_type = get_recommendations(user_id, k)
                    
                    # Afficher le message de recommandations personnalisées
                    st.success(f"✅ Top {k} recommandations personnalisées pour l'utilisateur {user_id}")
                    st.markdown("Ces recommandations sont basées sur l'historique personnel de l'utilisateur et ses préférences.")
                    
                    if recommendations:
                        # Créer des colonnes pour l'affichage en grille
                        cols = st.columns(3)  # 3 cartes par ligne
                        
                        for idx, rec in enumerate(recommendations):
                            movie_id = rec["film_id"]
                            predicted_rating = rec["rating_predicted"]
                            
                            # Conversion movieId --> tmdbId
                            tmdb_id = links_mapping.get(movie_id)
                            
                            if tmdb_id:
                                movie = get_movie_details(tmdb_id)
                                
                                if movie:
                                    display_movie_card(movie, predicted_rating, cols[idx % 3])
                                else:
                                    with cols[idx % 3]:
                                        st.warning(f"Détails introuvables pour TMDB ID {tmdb_id}")
                            else:
                                with cols[idx % 3]:
                                    st.warning(f"Aucun TMDB ID pour movieId {movie_id}")
                    else:
                        st.error("Aucune recommandation trouvée pour cet utilisateur.")
            except Exception as e:
                st.error(f"Erreur : {e}")
                with st.expander("Détails de l'erreur"):
                    st.exception(e)
    
    # Informations sur le système de recommandation en bas de page
    with st.expander("ℹ️ À propos du système de recommandation"):
        st.markdown("""
        ### Comment fonctionnent les recommandations ?
        
        Ce système utilise une approche avancée pour recommander des films basée sur la factorisation matricielle (SVD) :
        
        1. **Filtrage des données** : Nous sélectionnons les utilisateurs avec suffisamment d'évaluations et les films populaires.
        
        2. **Modèle SVD** : Notre système identifie les facteurs latents qui influencent les préférences des utilisateurs.
        
        3. **Prédictions personnalisées** : Pour chaque utilisateur, nous prédisons les films qu'il est susceptible d'apprécier.
        
        Les notes prédites sont calculées sur une échelle de 0 à 10, et sont basées sur l'analyse des préférences de l'utilisateur.
        """)
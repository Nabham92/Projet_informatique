import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.common.db import get_db_connection as connect_db

# --------------------
# FONCTIONS POUR LES VISUALISATIONS
# --------------------
@st.cache_data
def load_movies_data():
    """Charger les données des films depuis la base DuckDB"""
    from app.common.db import get_db_connection as connect_db

    films_df = pd.DataFrame()
    genres_df = pd.DataFrame()
    ratings_counts = pd.DataFrame()
    ratings_distribution = pd.DataFrame()
    user_ratings_counts = pd.DataFrame()
    
    try:
        # On récupère simplement la connexion (pas de with)
        conn = connect_db()
        
        # Récupérer les films avec année extraite de la date de sortie
        films_df = conn.execute("""
            SELECT id, title, genres,
                   CAST(SUBSTRING(release_date, 1, 4) AS INTEGER) as year,
                   vote_average, vote_count
            FROM films
            WHERE release_date IS NOT NULL
              AND vote_average IS NOT NULL
              AND genres IS NOT NULL
        """).fetchdf()
        
        # Extraire le premier genre
        genres_df = conn.execute("""
            SELECT f.id,
                   json_extract(json_extract(f.genres, '$[0]'), '$.name') as genre_name
            FROM films f
            WHERE f.genres IS NOT NULL
              AND json_extract(f.genres, '$[0]') IS NOT NULL
        """).fetchdf()
        
        # Et les comptages…
        ratings_counts = conn.execute("""
            SELECT movieId, COUNT(*) as num_ratings, AVG(rating) as avg_rating
            FROM ratings
            GROUP BY movieId
        """).fetchdf()
        
        ratings_distribution = conn.execute("""
            SELECT rating, COUNT(*) as count
            FROM ratings
            GROUP BY rating
            ORDER BY rating
        """).fetchdf()
        
        user_ratings_counts = conn.execute("""
            SELECT userId, COUNT(*) as num_ratings
            FROM ratings
            GROUP BY userId
        """).fetchdf()
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
    return films_df, genres_df, ratings_counts, ratings_distribution, user_ratings_counts

def get_top_genres(genres_df, n=10):
    """Obtenir les n genres les plus fréquents"""
    return genres_df['genre_name'].value_counts().head(n)

def get_avg_rating_by_genre(films_df, genres_df, ratings_counts):
    """Préparer les données pour visualiser les notes moyennes par genre"""
    # Fusionner les données de films avec les comptages d'évaluations
    merged = films_df.merge(ratings_counts, left_on='id', right_on='movieId', how='inner')
    
    # Fusionner avec les genres
    genre_ratings = merged.merge(genres_df, on='id', how='inner')
    
    # Grouper par genre et calculer les statistiques
    genre_stats = genre_ratings.groupby('genre_name').agg({
        'avg_rating': 'mean',
        'num_ratings': 'sum',
        'id': 'nunique'  # Nombre unique de films
    }).reset_index()
    
    # Renommer les colonnes
    genre_stats.columns = ['genre', 'avg_rating', 'total_ratings', 'num_movies']
    
    # Arrondir les notes moyennes pour une meilleure lisibilité
    genre_stats['avg_rating'] = genre_stats['avg_rating'].round(2)
    
    # Trier par note moyenne décroissante
    return genre_stats.sort_values('avg_rating', ascending=False)

def get_ratings_by_year(films_df, ratings_counts):
    """Préparer les données pour visualiser les notes moyennes par année"""
    # Fusionner les données de films avec les comptages d'évaluations
    merged = films_df.merge(ratings_counts, left_on='id', right_on='movieId', how='inner')
    # Grouper par année et calculer les statistiques
    yearly_stats = merged.groupby('year').agg({
        'avg_rating': 'mean',
        'num_ratings': 'sum',
        'id': 'count'
    }).reset_index()
    yearly_stats.columns = ['year', 'avg_rating', 'total_ratings', 'num_movies']
    # Filtrer pour éliminer les valeurs aberrantes (années trop anciennes ou futures)
    return yearly_stats[(yearly_stats['year'] >= 1900) & (yearly_stats['year'] <= 2023)]

def create_genre_distribution_chart(genres_data):
    """Créer un graphique de distribution des genres"""
    # Création d'un graphique à barres horizontal plus clair
    fig = px.bar(
        genres_data.reset_index(), 
        y='genre_name', 
        x='count',
        orientation='h',
        title="Distribution des genres de films",
        labels={'count': 'Nombre de films', 'genre_name': 'Genre'},
        color='count',
        color_continuous_scale='Viridis',
        text='count'  # Afficher le nombre de films pour chaque genre
    )
    
    # Amélioration de la mise en page
    fig.update_layout(
        height=600,  # Plus d'espace pour les genres
        width=700, 
        yaxis={'categoryorder':'total ascending'},  # Trier par nombre de films
        xaxis_title="Nombre de films",
        yaxis_title="Genre",
        font=dict(size=12)
    )
    
    # Afficher les nombres de films directement sur les barres
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    
    return fig

def create_ratings_distribution_chart(ratings_distribution):
    """Créer un graphique de distribution des notes"""
    fig = px.bar(
        ratings_distribution,
        x='rating',
        y='count',
        title="Distribution des notes attribuées",
        labels={'count': 'Nombre d\'évaluations', 'rating': 'Note'},
        color='count',
        color_continuous_scale='Reds'
    )
    fig.update_layout(height=400, width=700, xaxis_tickvals=ratings_distribution['rating'].unique())
    return fig

def create_genre_ratings_chart(genre_ratings_data):
    """Créer un graphique des notes moyennes par genre"""
    print(genre_ratings_data)
    # Créer un graphique à barres avec les notes moyennes par genre
    fig = px.bar(
        genre_ratings_data,
        y='genre',
        x='avg_rating',
        orientation='h',  # Barres horizontales
        title="Notes moyennes par genre de film",
        labels={'avg_rating': 'Note moyenne', 'genre': 'Genre'},
        color='avg_rating',
        color_continuous_scale='RdYlGn',  # Rouge à vert pour montrer les bonnes/mauvaises notes
        text='avg_rating',  # Afficher la note moyenne sur chaque barre
        hover_data=['num_movies', 'total_ratings']  # Données additionnelles au survol
    )
    
    # Amélioration de la mise en page
    fig.update_layout(
        height=600,
        width=700,
        yaxis={'categoryorder':'total ascending'},  # Trier par note moyenne
        xaxis_title="Note moyenne (/5)",
        yaxis_title="Genre",
        xaxis=dict(range=[0, 5]),  # Fixer l'échelle de 0 à 5
        font=dict(size=12)
    )
    
    # Afficher les notes directement sur les barres
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    
    return fig

def create_top_categories_chart(genre_ratings_data):
    """Créer deux graphiques séparés montrant les 5 principales catégories de films:
    1. Un barplot pour le nombre de films par genre
    2. Un barplot pour la note moyenne par genre
    """
    # Sélectionner les 5 genres avec le plus grand nombre de films
    top_5_genres = genre_ratings_data.sort_values('num_movies', ascending=False).head(5)
    
    # Créer deux figures séparées
    # Figure 1: Barplot pour le nombre de films par genre
    fig_count = px.bar(
        top_5_genres,
        x='genre',
        y='num_movies',
        title="Top 5 des catégories de films - Nombre de films par genre",
        labels={'num_movies': 'Nombre de films', 'genre': 'Genre'},
        color='genre',
        text='num_movies'
    )
    
    fig_count.update_layout(
        height=400,
        width=600,
        xaxis_title="Genre",
        yaxis_title="Nombre de films",
        showlegend=False
    )
    
    # Afficher les valeurs directement sur les barres
    fig_count.update_traces(texttemplate='%{text:,}', textposition='outside')
    
    # Figure 2: Barplot pour la note moyenne par genre
    fig_rating = px.bar(
        top_5_genres,
        x='genre',
        y='avg_rating',
        title="Top 5 des catégories de films - Note moyenne par genre",
        labels={'avg_rating': 'Note moyenne', 'genre': 'Genre'},
        color='genre',
        text='avg_rating'
    )
    
    fig_rating.update_layout(
        height=400,
        width=600,
        xaxis_title="Genre",
        yaxis_title="Note moyenne",
        yaxis=dict(range=[0, 5]),  # Échelle fixe pour les notes de 0 à 5
        showlegend=False
    )
    
    # Afficher les valeurs directement sur les barres
    fig_rating.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    
    return fig_count, fig_rating

def create_user_ratings_distribution_chart(user_ratings_counts):
    """Créer un graphique de distribution du nombre d'évaluations par utilisateur"""
    # Créer des catégories (buckets) pour le nombre d'évaluations
    bins = [0, 5, 10, 20, 50, 100, 200, 500, 1000, float('inf')]
    labels = ['1-5', '6-10', '11-20', '21-50', '51-100', '101-200', '201-500', '501-1000', '1000+']
    
    # Assigner chaque utilisateur à une catégorie
    user_ratings_counts['rating_bucket'] = pd.cut(
        user_ratings_counts['num_ratings'], 
        bins=bins, 
        labels=labels, 
        right=False
    )
    
    # Compter le nombre d'utilisateurs par catégorie
    bucket_counts = user_ratings_counts['rating_bucket'].value_counts().sort_index().reset_index()
    bucket_counts.columns = ['rating_bucket', 'num_users']
    
    # Créer le graphique
    fig = px.bar(
        bucket_counts,
        x='rating_bucket',
        y='num_users',
        title="Distribution du nombre d'évaluations par utilisateur",
        labels={'num_users': "Nombre d'utilisateurs", 'rating_bucket': "Nombre d'évaluations"},
        color='num_users',
        color_continuous_scale='Viridis',
        text='num_users'
    )
    
    # Amélioration de la mise en page
    fig.update_layout(
        height=500,
        width=700,
        xaxis_title="Nombre d'évaluations par utilisateur",
        yaxis_title="Nombre d'utilisateurs",
        font=dict(size=12)
    )
    
    # Afficher les nombres d'utilisateurs directement sur les barres
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    
    return fig

def show_visualizations():
    """Afficher la page des visualisations"""
    st.markdown("### 📊 Analyse de la Base de Films")
    st.markdown("""
    Explorez les statistiques et tendances de notre base de données de films. Ces visualisations 
    vous permettent de mieux comprendre la composition de notre catalogue et les habitudes d'évaluation des utilisateurs.
    """)
    
    with st.spinner("Chargement des données... 📈"):
        # Charger les données des films
        films_df, genres_df, ratings_counts, ratings_distribution, user_ratings_counts = load_movies_data()
        
        if not films_df.empty:
            # Statistiques globales
            st.subheader("📋 Statistiques générales")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Nombre de films", f"{len(films_df):,}")
            
            with col2:
                st.metric("Note moyenne globale", f"{films_df['vote_average'].mean():.1f} / 10")
            
            with col3:
                # Corriger le nom de la colonne pour correspondre à celui défini dans la requête SQL
                total_ratings = ratings_counts['num_ratings'].sum()
                st.metric("Nombre total d'évaluations", f"{total_ratings:,}")
            
            # Afficher la distribution des notes
            st.subheader("🌟 Distribution des notes")
            ratings_fig = create_ratings_distribution_chart(ratings_distribution)
            st.plotly_chart(ratings_fig, use_container_width=True)
            st.markdown("""
            Cette visualisation montre comment les utilisateurs notent les films.
            On remarque que certaines notes sont plus fréquemment attribuées que d'autres.
            """)
            
            # Distribution des évaluations par utilisateur
            st.subheader("👤 Distribution des évaluations par utilisateur")
            user_ratings_fig = create_user_ratings_distribution_chart(user_ratings_counts)
            st.plotly_chart(user_ratings_fig, use_container_width=True)
            st.markdown("""
            Cette visualisation montre comment les utilisateurs évaluent les films, en regroupant les utilisateurs par nombre d'évaluations.
            """)
            
            # Top films
            st.subheader("🏆 Top 10 des films les mieux notés")
            # Filtrer pour n'avoir que les films avec un nombre significatif de votes
            popular_films = films_df[films_df['vote_count'] > 100].sort_values(by='vote_average', ascending=False).head(10)
            
            # Afficher la table des top films
            st.dataframe(
                popular_films[['title', 'vote_average', 'vote_count', 'year']].rename(
                    columns={'title': 'Titre', 'vote_average': 'Note', 'vote_count': 'Nombre de votes', 'year': 'Année'}
                ),
                use_container_width=True
            )
            
        else:
            st.error("Impossible de charger les données pour les visualisations. Veuillez vérifier la connexion à la base de données.")
# Système de Recommandation de Films

Ce projet propose une solution complète de **recommandation personnalisée de films** basée sur des données réelles (TMDB + Kaggle) et un modèle de filtrage collaboratif SVD. L'architecture est distribuée via Docker Compose pour un déploiement rapide.

---

## Fonctionnalités principales

- Recommandations personnalisées (filtrage collaboratif SVD)
- API REST (FastAPI)
- Dashboard interactif (Streamlit)
- Base de données locale (DuckDB)
- Déploiement conteneurisé avec Docker

---

## Lancer l'application avec Docker

### 1. Assurez-vous d’avoir **Docker** et **Docker Compose** installés.

### 2. Clonez ce dépôt :

```bash
git clone https://github.com/Nabham92/Projet_informatique
cd Projet_informatique
```

### 3. Lancez l'application :

```bash
docker-compose up
```

Docker va automatiquement :

- Télécharger les images publiées sur Docker Hub
- Créer le réseau
- Démarrer le backend et le frontend

---

##  Accéder aux interfaces

-  **Backend (API)** : [http://localhost:8000/docs](http://localhost:8000/docs)
-  **Frontend (dashboard Streamlit)** : [http://localhost:8501](http://localhost:8501)

ℹ️ Le système vérifie la santé du backend au démarrage. L'interface peut mettre quelques secondes à s'afficher la première fois.

---

##  Images Docker disponibles sur Docker Hub

Pas besoin de build localement. Les images sont déjà publiées :

- **Backend** : `nabham92/projet-final-backend:latest`
- **Frontend** : `nabham92/projet-final-frontend:latest`

---

##  À propos du moteur de recommandation

Le modèle utilise une factorisation matricielle (SVD) entraînée sur une table filtrée `userId × movieId`.

 Par défaut, le système ne recommande des films qu’aux utilisateurs et pour des films ayant suffisamment de notes.  
Ces seuils sont configurables dans `common/config.py` :

```python
MIN_USER_RATINGS = 200  # Min notes par utilisateur
MIN_FILM_RATINGS = 100  # Min notes par film
```

Vous pouvez baisser ces valeurs pour élargir les recommandations.

---

## 🧪 Fonctionnalités en détail

### Backend (FastAPI)

- `GET /movie/{id}` → Détails d’un film
- `POST /recommendations/{user_id}?k=10` → Top k recommandations
- `GET /health` → Statut du backend

### Frontend (Streamlit)

- Saisie d’un `user_id` pour obtenir ses recommandations
- Graphiques :
    - Distribution des notes
    - Répartition par genre
    - Évolution annuelle
    - Activité utilisateurs
    - Top films par popularité/note

---

## 📁 Structure simplifiée du projet

```bash
.
├── app/
│   ├── backend/       # Backend FastAPI
│   ├── frontend/      # Dashboard Streamlit
│   ├── common/        # Config, base de données
│   └── scripts/       # Prétraitement, chargement
├── data/              # Fichiers CSV, DB, modèles
├── docker-compose.yml
├── dockerfile.backend
├── dockerfile.frontend
└── README.md
```
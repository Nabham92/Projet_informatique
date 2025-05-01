# 🎬 Système de Recommandation de Films

Ce projet propose une solution complète de **recommandation de films personnalisée** basée sur des données réelles et un modèle de **filtrage collaboratif (SVD)**. Il couvre la collecte de données, la modélisation, une API REST et une interface utilisateur interactive.

---

## 🧩 Architecture du projet

L'application est divisée en **3 services Dockerisés** :

- 🗄️ **Base de données DuckDB**  
  Contient les films et les évaluations utilisateurs (données TMDB + Kaggle).
- ⚙️ **Backend (FastAPI)**  
  Fournit une API REST pour générer les recommandations et exposer les films.
- 🎛️ **Frontend (Streamlit)**  
  Interface utilisateur pour visualiser les recommandations et explorer les statistiques.

---

## 🚀 Lancer l'application

1. **Cloner le projet**
   ```bash
   git clone https://github.com/Nabham92/Projet_informatique
   cd <nom-du-dossier>
   ```

2. **Lancer avec Docker**
   ```bash
   docker-compose up
   ```

3. **Accéder aux interfaces**
   - 🔁 API backend : [http://localhost:8000/docs](http://localhost:8000/docs)
   - 📊 Dashboard : [http://localhost:8501](http://localhost:8501)

> 🕒 L'application peut mettre quelques secondes à démarrer (healthcheck + téléchargement des images).

---

## 🧠 Fonctionnement du moteur de recommandation

Le système repose sur un modèle SVD (factorisation matricielle) entraîné sur une table user–film–note filtrée.

⚠️ Par défaut, seules les notes provenant d’utilisateurs et de films suffisamment actifs sont utilisées pour entraîner le modèle, afin d’assurer la qualité des recommandations.

Ces paramètres sont modifiables dans le fichier `common/config.py` :

```python
MIN_USER_RATINGS = 200   # Nombre minimal de notes par utilisateur
MIN_FILM_RATINGS = 100   # Nombre minimal de notes par film
```

---

## 🧪 Fonctionnalités

### Backend (API REST)

- `GET /movie/{id}` : détails d’un film
- `POST /recommendations/{user_id}?k=10` : top k recommandations personnalisées
- `GET /health` : vérification du statut

### Frontend (Streamlit)

- Sélection d’un utilisateur pour obtenir des recommandations
- Graphiques interactifs :
  - Distribution des notes
  - Répartition par genre
  - Top films par note ou popularité
  - Activité des utilisateurs
  - Tendance annuelle

---

## 🐳 Images Docker utilisées

Les images sont déjà publiées sur Docker Hub :

- `nabham92/projet-final-backend:latest`
- `nabham92/projet-final-frontend:latest`

Elles sont automatiquement téléchargées lors de l'exécution de `docker-compose up`.

---

## 📁 Arborescence simplifiée

```bash
.
├── app/
│   ├── backend/       # Code FastAPI
│   ├── frontend/      # Interface Streamlit
│   ├── common/        # Config, utils, DB
│   └── scripts/       # Prétraitement et chargement
├── data/              # Fichiers CSV / DB
├── docker-compose.yml
├── dockerfile.backend
├── dockerfile.frontend
└── README.md
```
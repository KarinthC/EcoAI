# EcoAI – Modélisation et analyse d’impact carbone de pipelines data science

EcoAI est une application web qui permet de **modéliser graphiquement** des pipelines de data science (enchaînement de traitements, entraînement de modèles, inférence, appels LLM…) et d’**estimer leur empreinte carbone**. L’outil est conçu pour fonctionner en mode “bac à sable” : on dessine un flux, on le paramètre, puis on lance une analyse qui retourne l’impact CO₂ global, des indicateurs par nœud et des suggestions de réduction.

L’application est développée avec **Vue 3** (frontend), **Flask** (backend) et **PostgreSQL** (base de données). L’ensemble est conteneurisé avec Docker et s’exécute aussi bien en développement qu’en production derrière un reverse proxy Nginx.

## Fonctionnalités principales

- **Éditeur de pipeline visuel** : glisser-déposer de nœuds (Données, Entraînement, Inférence, LLM Call, LLM Expert, etc.) sur un canevas, connexion par arêtes dirigées.
- **Paramétrage détaillé** : chaque type de nœud expose ses propres paramètres (taille des données, nombre d’epochs, modèle, fournisseur, tokens…) via un panneau latéral.
- **Analyse carbone** : appel au backend qui utilise la librairie `ecologits` pour les nœuds LLM et des formules paramétrables pour les autres nœuds.
- **Restitution visuelle** : badges de criticité (vert/orange/rouge) sur les nœuds, bandeau inférieur avec l’empreinte totale et suggestions, panneau de détail par nœud.
- **Gestion multi-pipelines** : système d’onglets, sauvegarde/chargement des pipelines (base PostgreSQL), suppression.
- **Sessions utilisateur légères** : identification par cookie de session Flask, possibilité de choisir un pseudonyme.
- **Déploiement simple** : configuration Docker Compose pour le développement (hot reload) et pour la production (Nginx + Gunicorn).

## Architecture
```bash
Navigateur ──► Nginx (reverse proxy + fichiers statiques)
│
├── /api/* ──► Flask (Gunicorn)
│ └── PostgreSQL
└── /* (SPA) ──► fichiers Vue.js
```
- **Frontend** : Vue 3 (Composition API), Pinia, VueFlow, Vite.
- **Backend** : Flask (API REST), SQLAlchemy, Flask-Migrate, ecologits.
- **Base de données** : PostgreSQL 15.
- **Conteneurisation** : Docker & Docker Compose.

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) et Docker Compose (v2+)
- Node.js 18+ (pour le développement frontend hors conteneur)

## Installation et lancement

### 1. Cloner le projet
```bash

git clone <url-du-repo>
cd ecoai
```

### 2. Configurer les variables d’environnement

Copier le fichier .env.example en .env et renseigner les valeurs :
```bash

cp .env.example .env

```
Exemple de contenu (à adapter) :
```bash
POSTGRES_USER=carbone_user
POSTGRES_PASSWORD=un_mot_de_passe_solide
POSTGRES_DB=carbone_db
DATABASE_URL=postgresql://carbone_user:un_mot_de_passe_solide@db:5432/carbone_db
SECRET_KEY=une_cle_secrete
JWT_SECRET_KEY=une_cle_jwt
```
### 3. Démarrer en mode développement

Le mode développement utilise deux fichiers Compose (docker-compose.yml + docker-compose.dev.yml) et monte les sources en direct pour le hot reload.
```bash

# Lancer les services backend (Flask + PostgreSQL)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d db api

# Appliquer les migrations (création des tables)
docker compose exec api flask db upgrade

# Dans un autre terminal, lancer le frontend avec Vite
cd frontend
npm install
npm run dev
```

L’application est accessible sur http://localhost:5173 (le proxy Vite redirige les appels API vers Flask sur le port 5000).

### 4. Démarrer en mode production

```bash

# Construire les images et lancer tous les services
docker compose up -d --build

# Appliquer les migrations
docker compose exec api flask db upgrade
```

L’application est disponible sur http://localhost (Nginx écoute sur le port 80).

## Utilisation

    1. Ouvrir l’application, la modale de bienvenue propose de saisir un pseudonyme (facultatif).

    2. Créer un pipeline via l’onglet “+” ou en utiliser un existant.

    3. Glisser-déposer des nœuds depuis la palette latérale, les connecter.

    4. Configurer chaque nœud en cliquant dessus (panneau de droite).

    5. Sauvegarder le pipeline (💾).

    6. Lancer l’analyse carbone (🔍) – le mode analyse fige l’édition, affiche les impacts et des conseils.

    6. Revenir à l’édition avec le même bouton.

## Tests

Des tests unitaires sont disponibles pour les modules de calcul carbone (backend).
```bash

# Dans le conteneur api, ou en local avec les dépendances
cd backend
pip install -r requirements.txt
pytest tests/
```

Pour l’instant, un test vérifie les combinaisons valides de provider/modèle pour les nœuds LLM Call (tests/test_llm_call.py). Ajoutez vos propres tests au fur et à mesure.
Structure du projet
```text

.
├── backend/
│   ├── app/
│   │   ├── api/                # Blueprints Flask (endpoints)
│   │   ├── models/             # Modèles SQLAlchemy
│   │   ├── services/           # Logique métier
│   │   │   └── carbon/         # Calculs d'impact par type de nœud
│   │   ├── config.py           # Configuration Flask
│   │   ├── extensions.py       # Extensions (SQLAlchemy, Migrate)
│   │   └── __init__.py         # Factory create_app()
│   ├── migrations/             # Scripts Alembic
│   ├── tests/                  # Tests unitaires
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/         # Composants Vue
│   │   │   └── pipeline/       # Composants de l’éditeur
│   │   ├── composables/        # Composables (drag & drop)
│   │   ├── config/             # Configuration statique (champs nœuds)
│   │   ├── stores/             # Pinia stores
│   │   ├── views/              # Vues (pages)
│   │   └── router/             # Vue Router
│   ├── Dockerfile
│   └── vite.config.js
├── docker-compose.yml          # Configuration production
├── docker-compose.dev.yml      # Surcharge développement
└── README.md
```

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
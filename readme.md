# EcoAI – Modélisation et analyse d’impact carbone de pipelines data science

EcoAI est une application web qui permet de **modéliser graphiquement** des pipelines de data science (enchaînement de traitements, entraînement de modèles, inférence, appels LLM…) et d’**estimer leur empreinte carbone**. L’outil est conçu pour fonctionner en mode “bac à sable” : on dessine un flux, on le paramètre, puis on lance une analyse qui retourne l’impact CO₂ global, des indicateurs par nœud et des suggestions de réduction.

L’application est développée avec **Vue 3** (frontend), **Flask** (backend) et **PostgreSQL** (base de données). L’ensemble est conteneurisé avec Docker et s’exécute aussi bien en développement qu’en production derrière un reverse proxy Nginx.

## Fonctionnalités principales

- **Éditeur de pipeline visuel** : glisser-déposer de nœuds (Données, Données persistantes, Données SSD temporaires, Entraînement, Inférence, LLM Call, LLM Expert, etc.) sur un canevas, connexion par arêtes dirigées.
- **Paramétrage détaillé** : chaque type de nœud expose ses propres paramètres (taille des données, nombre d’epochs, modèle, fournisseur, tokens…) via un panneau latéral.
- **Analyse carbone** : appel au backend qui utilise la librairie `ecologits` pour les nœuds LLM et des formules paramétrables pour les autres nœuds.
- **Restitution visuelle** : badges de criticité (vert/orange/rouge) sur les nœuds, panneau de détail par nœud.
- **Analyse par onglets** : en mode analyse, une barre d’onglets propose une analyse globale (note single score ACV + synthèse + suggestions), le graphe parcourable, puis un onglet par indicateur (comparatif jauge vs seuil + contribution par nœud). La barre latérale des critères reste affichée en permanence et sert de navigation.
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

git clone https://github.com/KarinthC/EcoAI
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

    6. Lancer l’analyse carbone (🔍) – le mode analyse fige l’édition et ouvre une zone à onglets : « Analyse globale » (note single score + synthèse + suggestions), « Graphe » (canevas parcourable) et un onglet par indicateur (comparatif). La barre latérale des critères reste affichée et permet d’ouvrir directement l’onglet d’un indicateur.

    7. Revenir à l’édition avec le même bouton.



## Tests

Des tests unitaires sont disponibles pour les modules de calcul carbone (backend).

```bash

# Dans le conteneur api, ou en local avec les dépendances
cd backend
pip install -r requirements.txt
pytest tests/
```

Les tests disponibles :

- `tests/test_llm_call.py` : combinaisons valides de provider/modèle pour les nœuds LLM Call.
- `tests/test_acv.py` : moteur ACV (linéarité heures/nb_gpu), parc serveurs/GPUs et nœuds Entrainement/Inférence.
- `tests/test_storage.py` : nœuds de stockage (Données persistantes HDD / Données SSD temporaires), linéarité et ordres de grandeur.
- `tests/test_datasource.py` : nœud « Données » (représentation sans calcul : impact 0, `computed=False`).
- `tests/test_single_score.py` : single score ACV (note générale) — structure, linéarité, cas limites, exclusion de l’eau ecologits.

Ajoutez vos propres tests au fur et à mesure.

### Tests frontend

Les tests frontend utilisent **Vitest** et **@vue/test-utils**.

```bash

cd frontend
npm install
npm test          # exécution unique
npm run test:watch
```

Les tests couvrent le composable `useAnalysisTabs`, l’onglet d’analyse du store, et les composants `GlobalScoreCard` et `IndicatorComparison`.


## Structure détaillée du projet
### Dossier backend

Le backend suit une architecture modulaire avec séparation des responsabilités : les routes (API), la logique métier (services) et les modèles de données (models). Le sous‑dossier services/carbon applique le même principe pour les calculs d’impact.
```text

backend/
├── app/
│   ├── api/                    # Endpoints REST (blueprints Flask)
│   │   ├── analysis.py         # POST /api/analyze (lance l'analyse carbone)
│   │   ├── health.py           # GET  /api/health (contrôle de l'état)
│   │   ├── pipelines.py        # CRUD /api/pipelines (gestion des pipelines)
│   │   ├── session.py          # GET  /api/session (infos de session utilisateur)
│   │   └── username.py         # POST /api/username (choix du pseudonyme)
│   ├── models/                 # Modèles SQLAlchemy (tables BDD)
│   │   ├── pipeline.py         # Table pipelines (id, user_id, nom, JSON du graphe)
│   │   └── user.py             # Table users (id, public_id, username, dates)
│   ├── services/               # Logique métier (appelée par les blueprints)
│   │   ├── carbon/             # Calcul d’impact carbone (2 familles de nœuds)
│   │   │   ├── common.py       # Fonctions partagées (seuils, extraction GWP/énergie)
│   │   │   ├── equivalences.py # Équivalences parlantes (streaming, marche, course, VE)
│   │   │   ├── orchestrator.py # Dispatcheur : label -> compute() du bon module
│   │   │   ├── acv/            # Famille ACV (données documentées, multi-indicateurs PEF)
│   │   │   │   ├── gpu_models.py # Modèles ACV GPUs + parc serveurs + moteur compute_acv()
│   │   │   │   ├── datasource.py # Nœud “Données” (représentation, aucun calcul)
│   │   │   │   ├── storage.py    # Nœuds “Données persistantes” (HDD) & “Données SSD temporaires” (SSD)
│   │   │   │   ├── training.py   # Nœud “Entrainement” (charge 100%)
│   │   │   │   ├── inference.py  # Nœud “Inférence” (charge 33%)
│   │   │   │   ├── operator.py   # Nœud “Opérateur” (charge paramétrable)
│   │   │   │   └── single_score.py # Single score ACV (note générale)
│   │   │   └── ecologits/      # Famille ecologits (estimations, vouée à évoluer)
│   │   │       ├── llm_call.py   # Nœud “LLM Call”
│   │   │       ├── llm_expert.py # Nœud “LLM Expert”
│   │   │       └── video.py      # Nœud “Video Generation”
│   │   ├── pipeline_service.py # CRUD pipelines
│   │   └── user_service.py     # Gestion des utilisateurs (cookie session)
│   ├── config.py               # Configuration Flask (variables d’environnement)
│   ├── extensions.py           # Instanciation SQLAlchemy et Flask-Migrate
│   └── __init__.py             # Factory create_app() – assemble l’application
├── migrations/                 # Scripts Alembic (historique du schéma)
├── tests/                      # Tests unitaires et fonctionnels
└── Dockerfile
```
### Interactions

    Les blueprints (api/) reçoivent les requêtes HTTP et délèguent aux services (services/).

    Les services interagissent avec les modèles (models/) pour lire/écrire en base.

    Le sous‑package carbon/ est isolé et organisé en deux familles de nœuds : `acv/` (calculs ACV documentés, multi‑indicateurs PEF, confiance `high`) et `ecologits/` (estimations, confiance `low`, vouées à évoluer). L’orchestrateur mappe chaque label de nœud vers la fonction `compute()` du module correspondant, puis agrège les impacts et les indicateurs.

    Les extensions (extensions.py) sont importées dans la factory pour lier SQLAlchemy et Flask-Migrate à l’application.

### Dossier frontend

Le frontend est organisé autour de composants Vue réutilisables, d’un store centralisé (Pinia) et d’un routeur. Les fichiers de configuration statique (comme la définition des champs par type de nœud) sont rangés dans un dossier config/.
```text

frontend/
├── src/
│   ├── assets/
│   │   └── main.css            # Styles globaux (VueFlow, bordures de nœuds)
│   ├── components/
│   │   ├── pipeline/           # Composants spécifiques à l’éditeur
│   │   │   ├── analysis/       # Composants du mode analyse (onglets)
│   │   │   │   ├── AnalysisTabs.vue          # Barre d’onglets d’analyse
│   │   │   │   ├── AnalysisGlobalTab.vue     # Onglet analyse globale (note + synthèse)
│   │   │   │   ├── GlobalScoreCard.vue       # Carte single score + barre empilée
│   │   │   │   ├── AnalysisGraphTab.vue      # Onglet graphe parcourable
│   │   │   │   ├── AnalysisIndicatorTab.vue  # Onglet d’un indicateur
│   │   │   │   └── IndicatorComparison.vue   # Jauge vs seuil + barres par nœud
│   │   │   ├── AnalysisNodePanel.vue  # Panneau de détail en mode analyse
│   │   │   ├── CustomNode.vue         # Rendu d’un nœud dans le graphe
│   │   │   ├── DropzoneBackground.vue # Fond du canvas avec grille
│   │   │   ├── ParameterPanel.vue     # Édition des paramètres d’un nœud
│   │   │   ├── PipelineTabs.vue       # Barre d’onglets (multi‑pipelines)
│   │   │   ├── Sidebar.vue            # Palette de nœuds + bouton analyse
│   │   │   └── nodeConfig.js          # Définition des champs par type de nœud
│   │   ├── ConnectionIndicator.vue    # Indicateur de connexion API
│   │   ├── UserIdentification.vue     # Affichage du pseudonyme
│   │   └── UsernameModal.vue          # Modale de saisie du pseudonyme
│   ├── composables/
│   │   ├── useDnD.js          # Logique de drag & drop réutilisable
│   │   └── useAnalysisTabs.js # Dérivation des onglets d’analyse + navigation
│   ├── stores/
│   │   └── usePipelineStore.js # État global (nœuds, arêtes, analyse, onglets)
│   ├── router/
│   │   └── index.js           # Définition des routes (actuellement /)
│   ├── views/
│   │   └── HomeView.vue       # Page principale (éditeur + analyse)
│   ├── App.vue                # Composant racine (layout global)
│   └── main.js                # Initialisation de Vue, Pinia, Router
├── Dockerfile
├── nginx.conf                 # Configuration du reverse proxy
└── vite.config.js             # Configuration Vite (alias, proxy dev)
```

### Interactions

    HomeView.vue orchestre les composants de l’éditeur et la logique d’analyse, en s’appuyant sur le store.

    usePipelineStore.js centralise les données du pipeline actif et expose des actions (ajout de nœuds, sauvegarde, analyse…). Il est consommé par tous les composants pipeline.

    Le composable useDnD.js fournit la mécanique de glisser‑déposer ; il utilise également le store pour ajouter les nœuds.

    Le composable useAnalysisTabs.js dérive la liste des onglets d’analyse (global, graphe, un par indicateur) et gère l’onglet actif, porté par le store.

    Les composants de la palette (Sidebar.vue), du canvas (CustomNode.vue) et des paramètres (ParameterPanel.vue) communiquent via le store, sans dépendances directes entre eux.

    En mode analyse, HomeView.vue affiche la Sidebar (permanente) et la zone à onglets ; les composants du dossier components/pipeline/analysis/ rendent l’onglet actif.

    Les appels HTTP vers le backend (sauvegarde, chargement, analyse) sont encapsulés dans les actions du store, mais pourraient être extraits dans un dossier api/ à l’avenir.


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
Navigateur ──► Nginx (reverse proxy + fichiers statiques)
│
├── /api/* ──► Flask (Gunicorn)
│ └── PostgreSQL
└── /* (SPA) ──► fichiers Vue.js

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

### 2. Configurer les variables d’environnement

Copier le fichier .env.example en .env et renseigner les valeurs :
```bash

cp .env.example .env


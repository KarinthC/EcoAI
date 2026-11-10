# EcoAI – Environmental footprint modeling and analysis for data science pipelines

EcoAI is a web application that lets you **graphically model** data science pipelines (chains of processing steps, model training, inference, LLM calls…) and **estimate their total environmental footprint**. The tool is designed to work in a "sandbox" mode: you draw a flow, configure it, then run an analysis that returns the overall multi-indicator footprint (PEF), per-node indicators and reduction suggestions. CO₂ (climate change) is only one of these indicators, alongside resource use, human health and ecosystem impacts.

The application is built with **Vue 3** (frontend), **Flask** (backend) and **PostgreSQL** (database). Everything is containerized with Docker and runs both in development and in production behind an Nginx reverse proxy.

## Main features

- **Visual pipeline editor**: drag & drop nodes (Data, Persistent data, Temporary SSD data, Training, Inference, LLM Call, LLM Expert, etc.) onto a canvas, connect them with directed edges.
- **Detailed configuration**: each node type exposes its own parameters (data size, number of epochs, model, provider, tokens…) through a side panel.
- **Environmental footprint analysis**: calls the backend, which uses the `ecologits` library for LLM nodes and documented LCA formulas (multi-indicator PEF) for the other nodes. The result is a total footprint across all PEF indicators, not just carbon.
- **PEF single score**: the analysis aggregates the criteria into a single score in milli-points (mPt) following the EF 3.1 method (JRC 2023, Recommendation (EU) 2021/2279), then compares it to reference usages (plane, cement, beef) to contextualize the impact.
- **Visual restitution**: criticality badges (green/orange/red) on nodes, per-node detail panel.
- **Tabbed analysis**: in analysis mode, a tab bar offers a global analysis (PEF single score + summary + suggestions + hotspots heatmap + contributions treemap), the browsable graph, then one tab per indicator (gauge vs. threshold comparison + per-node contribution). Each indicator tab also shows a narrative **"Stakes"** card (why the indicator matters, with an illustration and a reveal effect) and a **"Foundational references"** card (links to the domain's reference papers/reports). The criteria sidebar stays visible at all times and acts as navigation.
- **Internationalization (FR/EN)**: all labels go through `vue-i18n`; a language switcher in the header toggles between French and English (choice persisted in `localStorage`).
- **Multi-pipeline management**: tab system, save/load pipelines (PostgreSQL database), deletion.
- **Lightweight user sessions**: identification via a Flask session cookie, option to choose a nickname.
- **Simple deployment**: Docker Compose configuration for development (hot reload) and production (Nginx + Gunicorn).

## Architecture
```bash
Browser ──► Nginx (reverse proxy + static files)
│
├── /api/* ──► Flask (Gunicorn)
│ └── PostgreSQL
└── /* (SPA) ──► Vue.js files
```
- **Frontend**: Vue 3 (Composition API), Pinia, VueFlow, ECharts, Vite, vue-i18n.
- **Backend**: Flask (REST API), SQLAlchemy, Flask-Migrate, ecologits.
- **Database**: PostgreSQL 15.
- **Containerization**: Docker & Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose (v2+)
- Node.js 18+ (for frontend development outside the container)

## Installation and launch

### 1. Clone the project
```bash

git clone https://github.com/KarinthC/EcoAI
cd ecoai
```

### 2. Configure environment variables

Copy the .env.example file to .env and fill in the values:
```bash

cp .env.example .env

```
Example content (to adapt):
```bash
POSTGRES_USER=carbone_user
POSTGRES_PASSWORD=a_strong_password
POSTGRES_DB=carbone_db
DATABASE_URL=postgresql://carbone_user:a_strong_password@db:5432/carbone_db
SECRET_KEY=a_secret_key
JWT_SECRET_KEY=a_jwt_key
```
### 3. Start in development mode

Development mode uses two Compose files (docker-compose.yml + docker-compose.dev.yml) and mounts the sources live for hot reload.
```bash

# Start the backend services (Flask + PostgreSQL)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d db api

# Apply migrations (table creation)
docker compose exec api flask db upgrade

# In another terminal, start the frontend with Vite
cd frontend
npm install
npm run dev
```

The application is available at http://localhost:5173 (the Vite proxy forwards API calls to Flask on port 5000).

### 4. Start in production mode

```bash

# Build the images and start all services
docker compose up -d --build

# Apply migrations
docker compose exec api flask db upgrade
```

The application is available at http://localhost (Nginx listens on port 80).

## Usage

    1. Open the application; the welcome modal offers to enter a nickname (optional).

    2. Create a pipeline via the "+" tab or use an existing one.

    3. Drag & drop nodes from the side palette and connect them.

    4. Configure each node by clicking on it (right panel).

    5. Save the pipeline (💾).

    6. Run the footprint analysis (🔍) – analysis mode freezes editing and opens a tabbed area: "Global analysis" (PEF single score + summary + suggestions + hotspots heatmap + contributions treemap), "Graph" (browsable canvas) and one tab per indicator (comparison). Each indicator tab includes a "Stakes" card and a "Foundational references" card. The criteria sidebar stays visible and lets you open an indicator's tab directly.

    7. Return to editing with the same button.

## Tests

Unit tests are available for the footprint calculation modules (backend).

```bash

# Inside the api container, or locally with the dependencies
cd backend
pip install -r requirements.txt
pytest tests/
```

Available tests:

- `tests/test_llm_call.py`: valid provider/model combinations for LLM Call nodes.
- `tests/test_acv.py`: LCA engine (hours/nb_gpu linearity), server/GPU fleet and Training/Inference nodes.
- `tests/test_storage.py`: storage nodes (Persistent HDD data / Temporary SSD data), linearity and orders of magnitude.
- `tests/test_datasource.py`: "Data" node (representation without calculation: impact 0, `computed=False`).
- `tests/test_single_score.py`: PEF single score (overall score) — compliance with the EF 3.1 formula, negative contributions, stable ordering.
- `tests/test_reference_usages.py`: reference usages (plane, cement, beef) — structure, formula consistency, orders of magnitude, scaling assumptions.
- `tests/test_orchestrator.py`: orchestrator — node dispatch, indicator aggregation, criteria building, single score and reference usages.

Add your own tests as you go.

### Frontend tests

Frontend tests use **Vitest** and **@vue/test-utils**. By convention, each test is **colocated** with its subject (`Xxx.test.js` next to `Xxx.vue` or `Xxx.js`); Vitest discovers them via the `src/**/*.test.js` pattern defined in `vite.config.js`.

```bash

cd frontend
npm install
npm test          # single run
npm run test:watch
```

The tests cover the store (`usePipelineStore`), the `useAnalysisTabs` composable, and the analysis-mode components: `IndicatorComparison`, `ScoreComparisonChart`, `NodeContributionPie`, `NodeIndicatorHeatmap`, `IndicatorTreemap`, `StakesCard`, as well as the support modules `indicatorColors`, `nodeColors`, `protectionAreas`, `indicatorStakes`, `indicatorReferences` and `useStakesReveal`. ECharts components are tested by mocking `vue-echarts` (Canvas rendering is not supported in jsdom) and inspecting the passed `option`.

## Detailed project structure
### Backend folder

The backend follows a modular architecture with separation of concerns: routes (API), business logic (services) and data models (models). The services/carbon subfolder applies the same principle to impact calculations.
```text

backend/
├── app/
│   ├── api/                    # REST endpoints (Flask blueprints)
│   │   ├── analysis.py         # POST /api/analyze (runs the footprint analysis)
│   │   ├── health.py           # GET  /api/health (health check)
│   │   ├── pipelines.py        # CRUD /api/pipelines (pipeline management)
│   │   ├── session.py          # GET  /api/session (user session info)
│   │   └── username.py         # POST /api/username (nickname choice)
│   ├── models/                 # SQLAlchemy models (DB tables)
│   │   ├── pipeline.py         # pipelines table (id, user_id, name, graph JSON)
│   │   └── user.py             # users table (id, public_id, username, dates)
│   ├── services/               # Business logic (called by blueprints)
│   │   ├── carbon/             # Environmental footprint calculation (2 node families)
│   │   │   ├── common.py       # Shared functions (thresholds, PEF criteria, EF 3.1 NF/WF)
│   │   │   ├── orchestrator.py # Dispatcher: label -> compute() of the right module
│   │   │   ├── acv/            # LCA family (documented data, multi-indicator PEF)
│   │   │   │   ├── gpu_models.py # LCA GPU models + server fleet + compute_acv() engine
│   │   │   │   ├── parametric.py # Parametric model (hours / nb_gpu linearity)
│   │   │   │   ├── datasource.py # "Data" node (representation, no calculation)
│   │   │   │   ├── storage.py    # "Persistent data" (HDD) & "Temporary SSD data" (SSD) nodes
│   │   │   │   ├── training.py   # "Training" node (100% load)
│   │   │   │   ├── inference.py  # "Inference" node (33% load)
│   │   │   │   ├── operator.py   # "Operator" node (configurable load)
│   │   │   │   ├── single_score.py # PEF single score (overall score, EF 3.1 method)
│   │   │   │   └── reference_usages.py # Reference usages (plane, cement, beef)
│   │   │   └── ecologits/      # ecologits family (estimates, meant to evolve)
│   │   │       ├── llm_call.py   # "LLM Call" node
│   │   │       ├── llm_expert.py # "LLM Expert" node
│   │   │       └── video.py      # "Video Generation" node
│   │   ├── pipeline_service.py # Pipeline CRUD
│   │   └── user_service.py     # User management (session cookie)
│   ├── config.py               # Flask configuration (environment variables)
│   ├── extensions.py           # SQLAlchemy and Flask-Migrate instantiation
│   └── __init__.py             # create_app() factory – assembles the application
├── migrations/                 # Alembic scripts (schema history)
├── tests/                      # Unit and functional tests
└── Dockerfile
```
### Interactions

    The blueprints (api/) receive HTTP requests and delegate to the services (services/).

    The services interact with the models (models/) to read/write to the database.

    The carbon/ subpackage is isolated and organized into two node families: `acv/` (documented LCA calculations, multi-indicator PEF, `high` confidence) and `ecologits/` (estimates, `low` confidence, meant to evolve). The orchestrator maps each node label to the `compute()` function of the corresponding module, then aggregates impacts and indicators. It also computes the PEF single score (`acv/single_score.py`, EF 3.1 method) and the reference usages (`acv/reference_usages.py`), and attaches to each node its ratios to the monthly threshold (`threshold_ratios`) and its PEF contributions (`pef_contributions`).

    The extensions (extensions.py) are imported in the factory to bind SQLAlchemy and Flask-Migrate to the application.

### Frontend folder

The frontend is organized around reusable Vue components, a centralized store (Pinia) and a router. Static configuration files (such as the field definitions per node type) live in a config/ folder. All user-facing text goes through `vue-i18n` (`src/i18n/locales/fr.json` and `en.json`); long editorial content (indicator "Stakes" texts, quotes) lives in dedicated modules outside the locale files.
```text

frontend/
├── src/
│   ├── assets/
│   │   ├── main.css            # Global styles (VueFlow, node borders)
│   │   └── stakes/             # Illustration images + reference PDFs (Stakes cards)
│   ├── components/
│   │   ├── pipeline/           # Editor-specific components
│   │   │   ├── analysis/       # Analysis-mode components (tabs)
│   │   │   │   ├── AnalysisTabs.vue          # Analysis tab bar
│   │   │   │   ├── AnalysisGlobalTab.vue     # Global analysis tab (score + summary)
│   │   │   │   ├── AnalysisGraphTab.vue      # Browsable graph tab
│   │   │   │   ├── AnalysisIndicatorTab.vue  # Single indicator tab
│   │   │   │   ├── IndicatorComparison.vue   # Gauge vs. threshold + per-node pie
│   │   │   │   ├── IndicatorStakes.vue       # "Stakes" card (narrative per indicator)
│   │   │   │   ├── StakesCard.vue            # Stakes card rendering (image + reveal effect)
│   │   │   │   ├── IndicatorReference.vue    # "Foundational references" card
│   │   │   │   ├── ScoreComparisonChart.vue  # Single score comparison (reference usages)
│   │   │   │   ├── NodeIndicatorHeatmap.vue  # Hotspots heatmap (nodes × indicators)
│   │   │   │   ├── IndicatorTreemap.vue      # PEF contributions treemap
│   │   │   │   ├── NodeContributionPie.vue   # Per-node contribution pie
│   │   │   │   ├── indicatorColors.js        # Stable color per indicator
│   │   │   │   ├── indicatorStakes.js        # Stakes texts + quotes per indicator
│   │   │   │   ├── indicatorReferences.js    # Foundational references per indicator
│   │   │   │   ├── stakesImages.js           # Illustration image per indicator
│   │   │   │   ├── useStakesReveal.js        # Stakes reveal effect (hover) composable
│   │   │   │   ├── nodeColors.js             # Stable palette per node
│   │   │   │   └── protectionAreas.js        # EF 3.1 protection areas
│   │   │   ├── AnalysisNodePanel.vue  # Detail panel in analysis mode
│   │   │   ├── CustomNode.vue         # Rendering of a node in the graph
│   │   │   ├── DropzoneBackground.vue # Canvas background with grid
│   │   │   ├── ParameterPanel.vue     # Node parameter editing
│   │   │   ├── PipelineTabs.vue       # Tab bar (multi-pipeline)
│   │   │   ├── Sidebar.vue            # Node palette + analysis button
│   │   │   ├── nodeConfig.js          # Field definitions per node type
│   │   │   ├── nodeTypes.js           # Stable node ids + i18n labels
│   │   │   └── criterionI18n.js       # i18n resolution of PEF criteria
│   │   ├── ConnectionIndicator.vue    # API connection indicator
│   │   ├── LanguageSwitcher.vue       # FR/EN language switcher
│   │   ├── UserIdentification.vue     # Nickname display
│   │   └── UsernameModal.vue          # Nickname input modal
│   ├── composables/
│   │   ├── useDnD.js          # Reusable drag & drop logic
│   │   ├── useImpactColor.js  # Impact color (green/orange/red) based on a ratio
│   │   └── useAnalysisTabs.js # Analysis tabs derivation + navigation
│   ├── i18n/
│   │   ├── index.js           # vue-i18n setup (locale detection, persistence)
│   │   └── locales/
│   │       ├── fr.json        # French messages
│   │       └── en.json        # English messages
│   ├── stores/
│   │   └── usePipelineStore.js # Global state (nodes, edges, analysis, tabs)
│   ├── router/
│   │   └── index.js           # Route definitions (currently /)
│   ├── views/
│   │   └── HomeView.vue       # Main page (editor + analysis)
│   ├── App.vue                # Root component (global layout)
│   └── main.js                # Vue, Pinia, Router, i18n initialization
├── Dockerfile
├── nginx.conf                 # Reverse proxy configuration
└── vite.config.js             # Vite configuration (aliases, dev proxy)
```

### Interactions

    HomeView.vue orchestrates the editor components and the analysis logic, relying on the store.

    usePipelineStore.js centralizes the active pipeline's data and exposes actions (adding nodes, saving, analyzing…). It is consumed by all pipeline components.

    The useDnD.js composable provides the drag & drop mechanics; it also uses the store to add nodes.

    The useAnalysisTabs.js composable derives the list of analysis tabs (global, graph, one per indicator) and manages the active tab, held by the store.

    The palette (Sidebar.vue), canvas (CustomNode.vue) and parameter (ParameterPanel.vue) components communicate through the store, with no direct dependencies between them.

    In analysis mode, HomeView.vue displays the Sidebar (permanent) and the tabbed area; the components in components/pipeline/analysis/ render the active tab. Charts (ECharts) are loaded via async import (`defineAsyncComponent`) to isolate ECharts in a separate chunk, outside the initial bundle.

    i18n keys returned by the backend (e.g. `label_i18n`) are resolved on the frontend with a fallback: if the key is missing, a readable label derived from the `id` is shown rather than the raw key.

    HTTP calls to the backend (save, load, analyze) are encapsulated in the store's actions, but could be extracted into an api/ folder in the future.

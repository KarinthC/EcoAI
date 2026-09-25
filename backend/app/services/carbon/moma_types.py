"""Référentiel des types de nœuds MoMa (source de vérité backend).

Ce module centralise les identifiants STABLES des types de nœuds du modèle de
données MoMa, ainsi que les sous-types d'Operator. Il est le pendant backend de
`frontend/src/components/pipeline/momaTypes.js` : les deux doivent rester
synchronisés.

Convention de typage des Operator : MoMa ne type pas les opérateurs (tout est
`Operator`). On ajoute donc une propriété `subtype` (liste fermée) qui pilote le
choix de la formule d'impact. Les extensions propres à l'évaluation écologique
sont préfixées `eco:` (ex. `eco:executionTimeSec`) pour éviter toute collision
avec le schéma MoMa, qui les ignore.
"""

# Types de nœuds MoMa retenus dans l'outil.
NODE_TYPE_DATASET = 'dataset'                  # conteneur (sc:Dataset), impact 0
NODE_TYPE_DATA = 'data'                        # données persistées (stockage)
NODE_TYPE_ML_MODEL = 'ml_model'                # paramètre les formules, impact 0
NODE_TYPE_OPERATOR = 'operator'                # compute (subtype pilote la formule)
NODE_TYPE_RESULT_TYPE = 'result_type'          # valeurs échangées, impact marginal
NODE_TYPE_ANALYTICAL_PATTERN = 'analytical_pattern'  # conteneur, impact 0
NODE_TYPE_TASK = 'task'                        # métadonnée, impact 0
NODE_TYPE_USER = 'user'                        # métadonnée, impact 0

# Liste fermée des sous-types d'Operator.
SUBTYPE_PREPROCESSING = 'preprocessing'
SUBTYPE_TRAINING = 'training'
SUBTYPE_INFERENCE_LOCAL = 'inference_local'
SUBTYPE_INFERENCE_API = 'inference_api'
SUBTYPE_LLM_CALL = 'llm_call'
SUBTYPE_VIDEO_GENERATION = 'video_generation'
SUBTYPE_DATA_TRANSFORMATION = 'data_transformation'

OPERATOR_SUBTYPES = (
    SUBTYPE_PREPROCESSING,
    SUBTYPE_TRAINING,
    SUBTYPE_INFERENCE_LOCAL,
    SUBTYPE_INFERENCE_API,
    SUBTYPE_LLM_CALL,
    SUBTYPE_VIDEO_GENERATION,
    SUBTYPE_DATA_TRANSFORMATION,
)

# Types d'arêtes typées (sémantique du graphe).
EDGE_PERFORM_INFERENCE = 'perform_inference'  # Operator -> ML_Model
EDGE_INPUT = 'input'                          # Operator <- Data/ResultType
EDGE_OUTPUT = 'output'                        # Operator -> Data/ResultType
EDGE_FOLLOWS = 'follows'                      # ordre d'exécution

EDGE_TYPES = (
    EDGE_PERFORM_INFERENCE,
    EDGE_INPUT,
    EDGE_OUTPUT,
    EDGE_FOLLOWS,
)

# Médias de stockage impactants (mappés vers les modules ACV existants).
# Les autres médias (cloud, tape) sont traités comme neutres dans un premier temps.
STORAGE_MEDIUM_SSD = 'ssd'
STORAGE_MEDIUM_HDD = 'hdd'
STORAGE_MEDIUM_CLOUD = 'cloud'
STORAGE_MEDIUM_TAPE = 'tape'

STORAGE_MEDIUMS = (
    STORAGE_MEDIUM_SSD,
    STORAGE_MEDIUM_HDD,
    STORAGE_MEDIUM_CLOUD,
    STORAGE_MEDIUM_TAPE,
)

# Médias effectivement calculés (les autres -> impact 0, computed=False).
IMPACTFUL_STORAGE_MEDIUMS = (STORAGE_MEDIUM_SSD, STORAGE_MEDIUM_HDD)

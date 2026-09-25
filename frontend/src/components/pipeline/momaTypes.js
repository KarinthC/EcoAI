// frontend/src/components/pipeline/momaTypes.js
//
// Référentiel des types de nœuds MoMa (source de vérité frontend).
//
// Pendant frontend de `backend/app/services/carbon/moma_types.py` : les deux
// doivent rester synchronisés. Les identifiants sont STABLES et servent de clé
// partout (graphe sauvegardé, dispatch backend, mapping des champs, CSS).
//
// Convention de typage des Operator : MoMa ne type pas les opérateurs. On ajoute
// une propriété `subtype` (liste fermée) qui pilote la formule d'impact. Les
// extensions propres à l'évaluation écologique sont préfixées `eco:`.

// Catégories MoMa (pilote la couleur et le regroupement dans la palette).
export const MOMA_CATEGORIES = {
  data: { color: 'node-border-datasource' },
  ml: { color: 'node-border-ml' },
  operator: { color: 'node-border-operator' },
  result: { color: 'node-border-result' },
  meta: { color: 'node-border-meta' },
}

// Types de nœuds MoMa retenus dans l'outil.
export const NODE_TYPES = {
  dataset: {
    i18n: 'nodes.dataset',
    category: 'data',
    color: 'node-border-datasource',
  },
  data: {
    i18n: 'nodes.data',
    category: 'data',
    color: 'node-border-datasource',
  },
  ml_model: {
    i18n: 'nodes.ml_model',
    category: 'ml',
    color: 'node-border-ml',
  },
  operator: {
    i18n: 'nodes.operator',
    category: 'operator',
    color: 'node-border-operator',
  },
  result_type: {
    i18n: 'nodes.result_type',
    category: 'result',
    color: 'node-border-result',
  },
  analytical_pattern: {
    i18n: 'nodes.analytical_pattern',
    category: 'meta',
    color: 'node-border-meta',
  },
  task: {
    i18n: 'nodes.task',
    category: 'meta',
    color: 'node-border-meta',
  },
  user: {
    i18n: 'nodes.user',
    category: 'meta',
    color: 'node-border-meta',
  },
}

// Liste fermée des sous-types d'Operator (pilote la formule d'impact).
export const OPERATOR_SUBTYPES = [
  'preprocessing',
  'training',
  'inference_local',
  'inference_api',
  'llm_call',
  'video_generation',
  'data_transformation',
]

// Types d'arêtes typées (sémantique du graphe).
export const EDGE_TYPES = {
  perform_inference: 'perform_inference', // Operator -> ML_Model
  input: 'input',                         // Operator <- Data/ResultType
  output: 'output',                       // Operator -> Data/ResultType
  follows: 'follows',                     // ordre d'exécution
}

// Médias de stockage (les médias non impactants sont neutres dans un premier temps).
export const STORAGE_MEDIUMS = ['ssd', 'hdd', 'cloud', 'tape']

// Ordre d'affichage dans la palette latérale (Sidebar), groupé par catégorie.
export const SIDEBAR_NODE_ORDER = [
  'dataset',
  'data',
  'ml_model',
  'operator',
  'result_type',
  'analytical_pattern',
  'task',
  'user',
]

// Classe CSS de bordure de nœud par id stable.
export const NODE_BORDER_CLASS = Object.fromEntries(
  Object.entries(NODE_TYPES).map(([id, cfg]) => [id, cfg.color])
)

// Résout l'id stable d'un nœud depuis `node.data.nodeType`.
export function resolveNodeType(nodeOrData) {
  const data = nodeOrData?.data ?? nodeOrData ?? {}
  if (data.nodeType && NODE_TYPES[data.nodeType]) return data.nodeType
  return null
}

// Clé i18n du libellé d'un nœud à partir de son id stable.
export function nodeTypeLabelKey(nodeTypeId) {
  return NODE_TYPES[nodeTypeId]?.i18n || null
}

// frontend/src/components/pipeline/nodeTypes.js
//
// Identifiants techniques STABLES des types de nœuds.
//
// IMPORTANT : ces ids servent de clé partout dans la chaîne (graphe sauvegardé
// en base, dispatch backend NODE_COMPUTERS, mapping des champs, classes CSS).
// Ils ne doivent JAMAIS être traduits ni modifiés : le libellé affiché est
// résolu à l'exécution via i18n (clé `i18n`).
//
// Rétro-compatibilité : les anciens graphes contiennent encore le libellé
// FRANÇAIS dans `data.label` (ex. "Entrainement"). La fonction
// `resolveNodeType()` traduit ces anciennes valeurs vers les ids stables.

export const NODE_TYPES = {
  datasource: {
    i18n: 'nodes.datasource',
    color: 'node-border-datasource',
  },
  storage_persistent: {
    i18n: 'nodes.storage_persistent',
    color: 'node-border-datasource',
  },
  storage_temporary: {
    i18n: 'nodes.storage_temporary',
    color: 'node-border-datasource',
  },
  ml_model: {
    i18n: 'nodes.ml_model',
    color: 'node-border-ml',
  },
  operator: {
    i18n: 'nodes.operator',
    color: 'node-border-operator',
  },
  training: {
    i18n: 'nodes.training',
    color: 'node-border-operator',
  },
  inference: {
    i18n: 'nodes.inference',
    color: 'node-border-operator',
  },
  llm_call: {
    i18n: 'nodes.llm_call',
    color: 'node-border-operator',
  },
  llm_expert: {
    i18n: 'nodes.llm_expert',
    color: 'node-border-operator',
  },
  video_generation: {
    i18n: 'nodes.video_generation',
    color: 'node-border-operator',
  },
}

// Ordre d'affichage dans la palette latérale (Sidebar).
export const SIDEBAR_NODE_ORDER = [
  'datasource',
  'storage_persistent',
  'storage_temporary',
  'ml_model',
  'operator',
  'training',
  'inference',
  'llm_call',
  'llm_expert',
  'video_generation',
]

// Classe CSS de bordure de nœud par id stable.
export const NODE_BORDER_CLASS = Object.fromEntries(
  Object.entries(NODE_TYPES).map(([id, cfg]) => [id, cfg.color])
)

// Mapping de rétro-compatibilité : ancien libellé français -> id stable.
// Utilisé pour reconstruire l'id depuis les graphes enregistrés avant i18n.
const LEGACY_LABEL_TO_ID = {
  'Données': 'datasource',
  'Données persistantes': 'storage_persistent',
  'Données SSD temporaires': 'storage_temporary',
  'Modèle ML': 'ml_model',
  'Opérateur': 'operator',
  'Entrainement': 'training',
  'Inférence': 'inference',
  'LLM Call': 'llm_call',
  'LLM Expert': 'llm_expert',
  'Video Generation': 'video_generation',
}

// Résout l'id stable d'un nœud, quelle que soit sa provenance :
//   - `node.data.nodeType` (nouveaux graphes) ;
//   - `node.data.label` contenant déjà un id stable ;
//   - `node.data.label` contenant un ancien libellé français (rétro-compat).
export function resolveNodeType(nodeOrData) {
  const data = nodeOrData?.data ?? nodeOrData ?? {}
  if (data.nodeType && NODE_TYPES[data.nodeType]) return data.nodeType
  const label = data.label
  if (!label) return null
  if (NODE_TYPES[label]) return label
  return LEGACY_LABEL_TO_ID[label] || null
}

// Clé i18n du libellé d'un nœud à partir de son id stable.
export function nodeTypeLabelKey(nodeTypeId) {
  return NODE_TYPES[nodeTypeId]?.i18n || null
}


// frontend/src/components/pipeline/nodeTypes.js
//
// Façade de compatibilité : les identifiants de types de nœuds vivent désormais
// dans `momaTypes.js` (modèle de données MoMa). Ce module ré-exporte l'API
// attendue par les composants existants (CustomNode, Sidebar, useDnD, store).
//
// IMPORTANT : plus aucune rétro-compatibilité avec les anciens graphes (branche
// de démonstration MoMa, jamais fusionnée avec la branche principale).

export {
  NODE_TYPES,
  NODE_BORDER_CLASS,
  SIDEBAR_NODE_ORDER,
  OPERATOR_SUBTYPES,
  EDGE_TYPES,
  STORAGE_MEDIUMS,
  resolveNodeType,
  nodeTypeLabelKey,
} from './momaTypes.js'

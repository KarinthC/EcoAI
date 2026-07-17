// src/utils/momaToVueFlow.js
// MoMatoVueFlow.js
import { nodeFields } from '@/components/pipeline/nodeConfig.js' // ou le bon chemin

export function convertMoMaAPToVueFlow(apJson) {
  const { nodes: momaNodes, edges: momaEdges } = apJson;

  // 1. Classification des nœuds MoMa
  const nodeMap = new Map();
  const operators = [];
  const dataNodes = [];
  const mlModels = [];
  const resultTypes = [];

  for (const n of momaNodes) {
    const labels = n.labels || [];
    if (labels.includes('Analytical_Pattern')) {
      // Ignorer la racine
      continue;
    }
    nodeMap.set(n.id, n);

    if (labels.includes('ML_Model')) {
      mlModels.push(n);
    } else if (
      labels.includes('Data') ||
      labels.includes('sc:Dataset') ||
      labels.includes('cr:FileObject') ||
      labels.includes('CsvSet') || 
      labels.includes('JSONSet') ||
      labels.includes('XMLSet') ||
      labels.includes('TextSet') ||
      labels.includes('PDFSet') ||
      labels.includes('VideoSet') ||
      labels.includes('ImageSet') ||
      labels.includes('Table') ||
      labels.includes('CSV') ||
      labels.includes('JSON') ||
      labels.includes('XML') ||
      labels.includes('Text') ||
      labels.includes('PDF') ||
      labels.includes('Video') ||
      labels.includes('Image')
    ) {
      dataNodes.push(n);
    } else if (
      labels.includes('ResultType') ||
      labels.includes('string') ||
      labels.includes('boolean') ||
      labels.includes('number') ||
      labels.includes('array') ||
      labels.includes('object')
    ) {
      resultTypes.push(n);
    } else if (labels.includes('Operator')) {
      operators.push(n);
    } else {
      // Par défaut, si pas de label reconnu, on le traite comme opérateur
      operators.push(n);
    }
  }

  // 2. Mapping des types d'opérateurs MoMa → type VueFlow
  function getVueFlowType(momaNode) {
    const labels = momaNode.labels || [];
    const props = momaNode.properties || {};

    // Correspondances explicites via labels (on peut étendre cette liste)
    if (labels.includes('Text_To_SQL_Operator')) return 'Opérateur';
    if (labels.includes('SQL_Query_Operator')) return 'Opérateur';
    if (labels.includes('Schema_Analyzer_Operator')) return 'Opérateur';
    if (labels.includes('SQL_With_Context_Operator')) return 'Opérateur';
    // Si on stockait un champ "subtype" dans les propriétés (ex: "training")
    if (props.subtype === 'training') return 'Entrainement';
    if (props.subtype === 'inference') return 'Inférence';
    if (props.subtype === 'preprocessing') return 'Préprocessing';
    if (props.subtype === 'llm_call') return 'LLM Call';
    if (props.subtype === 'llm_expert') return 'LLM Expert';
    if (props.subtype === 'video_generation') return 'Video Generation';

    // Fallback : détection heuristique basée sur les propriétés
    if (props.epochs != null || props.batch_size != null) return 'Entrainement';
    if (props.modele_utilise != null || props.appels != null) return 'Inférence';
    if (props.Volume != null || props.temps != null) return 'Préprocessing';
    if (props.provider != null || props.model != null) return 'LLM Call';

    // Type générique par défaut
    return 'Opérateur';
  }

  // 3. Construction des nœuds VueFlow
  const vueFlowNodes = [];
  const idCounter = { current: 0 };
  const generateId = () => `imported_${idCounter.current++}`;

  // Fonction utilitaire pour créer un nœud VueFlow
  const addNode = (momaId, type, label, extraData = {}) => {
    const id = generateId();
    const position = { x: Math.random() * 400, y: Math.random() * 400 }; // placement aléatoire, à améliorer
    const node = {
      id,
      type: 'custom', // ton type de nœud VueFlow (custom)
      position,
      data: {
        label,          // le texte affiché dans le nœud (ex. "Données", "Modèle ML", nom de l'opérateur)
        params: {},     // initialisation vide des champs spécifiques
        momaId,         // référence arrière pour éventuelle synchro
        ...extraData,
      },
      class: getBorderClass(type), // réutilisation du mapping borderClassMap
    };
    // Définir les champs de paramètres par défaut selon le type
    const config = nodeFields[type];
    if (config) {
      const defaultParams = {};
      config.forEach(field => {
        defaultParams[field.key] = field.placeholder || '';
      });
      node.data.params = defaultParams;
    }
    vueFlowNodes.push(node);
    return id;
  };

  // Conserve la correspondance momaId → vueFlowId
  const momaToVueFlow = new Map();

  // Ajouter les nœuds Données
  dataNodes.forEach(dn => {
    const vId = addNode(dn.id, 'Données', dn.properties.name || 'Données', {
      momaProperties: dn.properties,
    });
    momaToVueFlow.set(dn.id, vId);
  });

  // Ajouter les modèles ML
  mlModels.forEach(m => {
    const vId = addNode(m.id, 'Modèle ML', m.properties.name || 'Modèle ML', {
      momaProperties: m.properties,
    });
    momaToVueFlow.set(m.id, vId);
  });

  // Ajouter les opérateurs
  operators.forEach(op => {
    const vueType = getVueFlowType(op);
    const vId = addNode(op.id, vueType, op.properties.name || vueType, {
      momaProperties: op.properties,
    });
    momaToVueFlow.set(op.id, vId);
  });

  // 4. Construction des arêtes VueFlow à partir des relations MoMa
  // On utilise un graphe dirigé intermédiaire pour relier directement producteurs et consommateurs.
  // Algorithme simplifié : pour chaque arête MoMa, on suit les chaînes input/output en ignorant les ResultTypes.
  
  // Index des ResultType (mais on ne les affiche pas, on les utilise pour résoudre les connexions)
  const resultTypeMap = new Map();
  resultTypes.forEach(rt => resultTypeMap.set(rt.id, rt));

  // Parcourir les arêtes MoMa
  const vueFlowEdges = [];
  const processedConnections = new Set(); // pour éviter les doublons

  for (const edge of momaEdges) {
    const { from, to, labels } = edge;

    // a) consist_of : ignoré (pas de représentation graphique)
    if (labels.includes('consist_of')) continue;

    // b) perform_inference : arête directe opérateur -> ML_Model
    if (labels.includes('perform_inference')) {
      const sourceVId = momaToVueFlow.get(from);
      const targetVId = momaToVueFlow.get(to);
      if (sourceVId && targetVId) {
        vueFlowEdges.push({
          id: `edge_${from}_${to}`,
          source: sourceVId,
          target: targetVId,
          label: 'inférence',
          type: 'smoothstep', // ou personnalisé
        });
      }
      continue;
    }

    // c) input / output : on résout les chemins transitifs en sautant les ResultType
    if (labels.includes('input') || labels.includes('output')) {
      // On cherche à connecter l'opérateur (ou data) final au bout de la chaîne.
      // Stratégie simple : si 'from' ou 'to' est un ResultType, on remonte/descend le long des arêtes.
      let sourceId = from;
      let targetId = to;

      // Si la cible est un ResultType, il faut trouver tous les consommateurs de ce ResultType
      // pour créer des arêtes vers eux.
      if (resultTypeMap.has(sourceId)) {
        // On ignore l'arête où la source est un ResultType (car l'arête partant d'un opérateur vers le ResultType sera traitée comme producteur)
        continue;
      }

      if (resultTypeMap.has(targetId)) {
        // Le nœud cible est un ResultType : il faut trouver toutes les arêtes qui partent de ce ResultType (comme input)
        // et créer des connexions directes source -> consommateur.
        const downstreamEdges = momaEdges.filter(e => e.from === targetId && e.labels.includes('input'));
        downstreamEdges.forEach(de => {
          const finalTarget = de.to;
          const sourceVId = momaToVueFlow.get(sourceId);
          const targetVId = momaToVueFlow.get(finalTarget);
          if (sourceVId && targetVId && !processedConnections.has(`${sourceVId}->${targetVId}`)) {
            processedConnections.add(`${sourceVId}->${targetVId}`);
            vueFlowEdges.push({
              id: `edge_${sourceId}_${finalTarget}`,
              source: sourceVId,
              target: targetVId,
              type: 'smoothstep',
              // On peut ajouter un label si le ResultType a un nom
              label: resultTypeMap.get(targetId)?.properties?.name || '',
            });
          }
        });
      } else {
        // Connexion directe (ex. Data -> Operator, Operator -> Data)
        const sourceVId = momaToVueFlow.get(sourceId);
        const targetVId = momaToVueFlow.get(targetId);
        if (sourceVId && targetVId && !processedConnections.has(`${sourceVId}->${targetVId}`)) {
          processedConnections.add(`${sourceVId}->${targetVId}`);
          vueFlowEdges.push({
            id: `edge_${sourceId}_${targetId}`,
            source: sourceVId,
            target: targetVId,
            type: 'smoothstep',
          });
        }
      }
      continue;
    }

    // d) follows : on peut les représenter comme arêtes (optionnel)
    if (labels.includes('follows')) {
      const sourceVId = momaToVueFlow.get(from);
      const targetVId = momaToVueFlow.get(to);
      if (sourceVId && targetVId && !processedConnections.has(`${sourceVId}->${targetVId}`)) {
        processedConnections.add(`${sourceVId}->${targetVId}`);
        vueFlowEdges.push({
          id: `edge_follows_${from}_${to}`,
          source: sourceVId,
          target: targetVId,
          label: 'follows',
          type: 'smoothstep',
          style: { strokeDasharray: '5,5' }, // pointillé pour distinguer
        });
      }
    }
  }

  return {
    nodes: vueFlowNodes,
    edges: vueFlowEdges,
  };
}

/**
 * Retourne la classe CSS de bordure pour le type de nœud VueFlow.
 */
function getBorderClass(type) {
  const borderClassMap = {
    'Données': 'node-border-datasource',
    'Modèle ML': 'node-border-ml',
    'Entrainement': 'node-border-operator',
    'Inférence': 'node-border-operator',
    'LLM Call': 'node-border-operator',
    'LLM Expert': 'node-border-operator',
    'Video Generation': 'node-border-operator',
    'Opérateur': 'node-border-operator',
    'Préprocessing': 'node-border-operator',
  };
  return borderClassMap[type] || '';
}
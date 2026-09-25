// src/stores/usePipelineStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

import { resolveNodeType, NODE_BORDER_CLASS } from '@/components/pipeline/nodeTypes.js'

// Base des endpoints de la branche MoMa (table dédiée `pipelines_moma`).
const MOMA_API = '/api/moma/pipelines'

// Recalcule la classe CSS de bordure d'un nœud depuis son id stable.
// Fonction pure : renvoie un nouveau tableau, ne mute pas l'entrée.
function normalizeGraphNodes(rawNodes) {
  if (!Array.isArray(rawNodes)) return []
  return rawNodes.map((node) => {
    const nodeType = resolveNodeType(node?.data)
    if (!nodeType) return node
    return {
      ...node,
      data: { ...(node.data || {}), nodeType },
      class: NODE_BORDER_CLASS[nodeType] || node.class || '',
    }
  })
}

export const usePipelineStore = defineStore('pipeline', () => {

    const pipelines = ref({})
    const activeId = ref(null)
        // Pipeline actif
    const activePipeline = computed(() => {
        if (!activeId.value) return null
        return pipelines.value[activeId.value] || null
    })

    // Propriétées liées à l'analyse
    const analysisResult = ref(null)
    const isAnalyzing = computed(() => analysisResult.value !== null)

    // Propriétés exposées (liées au pipeline actif)
    const nodes = computed(() => activePipeline.value?.nodes || [])
    const edges = computed(() => activePipeline.value?.edges || [])
    const selectedNodeId = computed(() => activePipeline.value?.selectedNodeId || null)

    function createPipeline(graphJson = null) {
        const id = `pipe_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        const name = 'pipeline'.concat(String(id).slice(4, -1))

        pipelines.value[id] = {
        name,

        nodes: normalizeGraphNodes(graphJson?.nodes),
        edges: graphJson?.edges || [],
        selectedNodeId: null,
        backendId: null   
        }
        activeId.value = id
        return id
    }

    function switchTo(id) {
        if (pipelines.value[id]) activeId.value = id
    }

    function closePipeline(id) {
        if (pipelines.value[id]) {
        delete pipelines.value[id]
        // Si on ferme l'actif, basculer sur un autre
        if (activeId.value === id) {
            const remaining = Object.keys(pipelines.value)
            activeId.value = remaining.length > 0 ? remaining[0] : null
        }
        }
    }
    

    function addNode(node) {
         if (activePipeline.value) {
            activePipeline.value.nodes.push(node)
        }
    }

    function updateNodeData(nodeId, newData) {
        if (activePipeline.value) {
            const node = activePipeline.value.nodes.find(n => n.id === nodeId)
            if (node) node.data = { ...node.data, ...newData }
        }
    }

    function removeNode(nodeId) {
        if (activePipeline.value) {
            activePipeline.value.nodes = activePipeline.value.nodes.filter(n => n.id !== nodeId)
            activePipeline.value.edges = activePipeline.value.edges.filter(
                e => e.source !== nodeId && e.target !== nodeId
            )
        }
    }

    // Ajoute une arête typée (perform_inference, input, output, follows).
    // Le type porte la sémantique du graphe MoMa ; il est conservé tel quel.
    function addEdge(source, target, type = 'follows') {
        if (activePipeline.value) {
            const id = `edge_${source}_${target}`
            if (!activePipeline.value.edges.some(e => e.source === source && e.target === target)) {
                activePipeline.value.edges.push({ id, source, target, type })
            }
        }
    }

    function selectNode(nodeId) {
        if (activePipeline.value) {
            activePipeline.value.selectedNodeId = nodeId
        }
    }

    function clearSelection() {
        if (activePipeline.value) {
            activePipeline.value.selectedNodeId = null
        }
    }

    const selectedNode = computed(() => {
        if (!activePipeline.value) return null
        return activePipeline.value.nodes.find(
            n => n.id === activePipeline.value.selectedNodeId
        ) || null
    })

    function getPipelineJSON() {
        if (!activePipeline.value) return { nodes: [], edges: [] }
        const cleanNodes = activePipeline.value.nodes.map(node => {
            // Le contrat de transport est l'id STABLE MoMa (`data.nodeType`),
            // complété par `data.params` (dont `subtype` pour les Operator).
            const nodeType = resolveNodeType(node.data)
            return {
                id: node.id,
                type: node.type,
                position: node.position,
                data: {
                    ...node.data,
                    ...(nodeType && { nodeType }),
                },
                class: node.class
            }
        })
        // Arêtes typées : le `type` (perform_inference, input, output, follows)
        // porte la sémantique du graphe MoMa.
        const cleanEdges = activePipeline.value.edges.map(edge => ({
            id: edge.id,
            source: edge.source,
            target: edge.target,
            type: edge.type || 'follows',
            sourceHandle: edge.sourceHandle,
            targetHandle: edge.targetHandle
        }))
        return { nodes: cleanNodes, edges: cleanEdges }
    }

    function exportJSON() {
        if (activePipeline.value) {
            const json = getPipelineJSON()
            console.log('Pipeline JSON (nettoyé) :', JSON.stringify(json, null, 2))
            // Plus tard : axios.post('/api/pipelines', json)
        }
    }


    async function savePipeline(name = 'Sans nom') {
        if (activePipeline.value) {

            const json = getPipelineJSON()
            try {
                const response = await axios.post(MOMA_API, {
                name: name,
                graph_json: json
                })
                console.log('Pipeline sauvegardé, id:', response.data.id)
                return response.data
            } catch (e) {
                console.error('Erreur sauvegarde pipeline', e)
                throw e
            }
        }
    }

    async function saveCurrent() {
    if (!activePipeline.value) return
    const json = getPipelineJSON()
    const payload = { name: activePipeline.value.name, graph_json: json }
    if (activePipeline.value.backendId) {
        await axios.put(`${MOMA_API}/${activePipeline.value.backendId}`, payload)
    } else {
        const res = await axios.post(MOMA_API, payload)
        const newBackendId = res.data.id
        const oldId = activeId.value
        // Créer une nouvelle entrée avec le bon ID backend, puis supprimer l'ancienne
        pipelines.value[newBackendId] = {
        ...pipelines.value[oldId],
        backendId: newBackendId
        }
        delete pipelines.value[oldId]
        activeId.value = newBackendId
    }
    }

    // Chargement des pipelines depuis l'API (au démarrage)
    async function loadPipelines() {
        const res = await axios.get(MOMA_API)
        for (const p of res.data) {
        pipelines.value[p.id] = {
            name: p.name,
            nodes: normalizeGraphNodes(p.graph_json.nodes),
            edges: p.graph_json.edges || [],
            selectedNodeId: null,
            backendId: p.id
        }
        }
        const keys = Object.keys(pipelines.value)
        if (keys.length > 0) {
            if (!activeId.value || !pipelines.value[activeId.value]) {
                activeId.value = keys[0]
        }}
        else {
            createPipeline('Sans nom')
        }
    }

    async function deletePipeline(id) {
        const pipeline = pipelines.value[id]
        if (!pipeline) return
        if (pipeline.backendId) {
            await axios.delete(`${MOMA_API}/${pipeline.backendId}`)
        }
        delete pipelines.value[id]
        if (activeId.value === id) {
            const remaining = Object.keys(pipelines.value)
            activeId.value = remaining.length > 0 ? remaining[0] : null
        }
    }

        // Lancer l'analyse
    async function analyzePipeline() {
    if (!activePipeline.value) return
    const json = getPipelineJSON()
    try {
        const response = await axios.post('/api/analyze', json)
        analysisResult.value = response.data
        // Mettre à jour les nœuds avec leurs données d'impact
        if (activePipeline.value && response.data.nodes) {
        response.data.nodes.forEach(item => {
            const node = activePipeline.value.nodes.find(n => n.id === item.id)
            if (!node) return
            // Nœud non calculé (ex. « Données ») : pas de badge d'impact ni
            // d'indicateurs (on purge ceux d'une éventuelle analyse précédente).
            if (item.computed === false) {
                const { impactLevel, indicators, reason, ...rest } = node.data
                node.data = {
                    ...rest,
                    ...(item.method && { method: item.method }),
                    ...(item.confidence && { confidence: item.confidence }),
                    // Cause du caractère neutre (ex. support non sélectionné).
                    ...(item.reason && { reason: item.reason })
                }
                return
            }
            node.data = {
                ...node.data,
                impactLevel: item.level,
                ...(item.indicators && { indicators: item.indicators }),
                ...(item.method && { method: item.method }),
                ...(item.confidence && { confidence: item.confidence })
            }
        })
        }
    } catch (e) {
        console.error('Erreur analyse', e)
        throw e
    }
    }

    function clearAnalysis() {
    analysisResult.value = null
    if (activePipeline.value) {
        activePipeline.value.nodes.forEach(node => {
        delete node.data.impactLevel
        })
    }}

    function updateViewport(viewport) {
    if (activePipeline.value) {
        activePipeline.value.viewport = { ...viewport }
    }
    }

    function applyViewport(setViewportFn) {
    if (activePipeline.value?.viewport) {
        const v = activePipeline.value.viewport
        // utiliser requestAnimationFrame pour être sûr que le composant est monté
        requestAnimationFrame(() => {
        setViewportFn({ x: v.x, y: v.y, zoom: v.zoom }, { duration: 0 })
        })
    }
    }

    return {
        pipelines,
        activeId,
        activePipeline,
        selectedNodeId,
        selectedNode,
        selectNode,
        clearSelection,
        nodes,
        edges,
        analysisResult,
        isAnalyzing,
        addNode,
        updateNodeData,
        removeNode,
        addEdge,
        getPipelineJSON,
        exportJSON,
        savePipeline,
        createPipeline,
        switchTo,
        closePipeline,
        saveCurrent,
        loadPipelines,
        deletePipeline,
        analyzePipeline,
        clearAnalysis,
        applyViewport,
        updateViewport
    }
})
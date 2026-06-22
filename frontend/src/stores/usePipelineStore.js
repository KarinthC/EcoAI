// src/stores/usePipelineStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const usePipelineStore = defineStore('pipeline', () => {
    const nodes = ref([])
    const edges = ref([])
    const selectedNodeId = ref(null)

        function addNode(node) {
        nodes.value.push(node)
    }

    function updateNodeData(nodeId, newData) {
        const node = nodes.value.find(n => n.id === nodeId)
        if (node) node.data = { ...node.data, ...newData }
    }

    function removeNode(nodeId) {
        nodes.value = nodes.value.filter(n => n.id !== nodeId)
        edges.value = edges.value.filter(e => e.source !== nodeId && e.target !== nodeId)
    }

    function addEdge(source, target) {
        const id = `edge_${source}_${target}`
        if (!edges.value.some(e => e.source === source && e.target === target)) {
        edges.value.push({ id, source, target })
        }
    }

    function selectNode(nodeId) {
        selectedNodeId.value = nodeId
    }

    function clearSelection() {
        selectedNodeId.value = null
    }

    const selectedNode = computed(() => {
        return nodes.value.find(n => n.id === selectedNodeId.value) || null
    })

    function getPipelineJSON() {
    // Nettoyer les nœuds : ne garder que ce qui est utile
    const cleanNodes = nodes.value.map(node => ({
        id: node.id,
        type: node.type,
        position: node.position,
        data: node.data,
        class: node.class
    }))

    // Nettoyer les arêtes : ne garder que la structure de connexion
    const cleanEdges = edges.value.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        sourceHandle: edge.sourceHandle,
        targetHandle: edge.targetHandle
    }))

    return {
        nodes: cleanNodes,
        edges: cleanEdges
    }
    }

    function exportJSON() {
    const json = getPipelineJSON()
    console.log('Pipeline JSON (nettoyé) :', JSON.stringify(json, null, 2))
    // Plus tard : axios.post('/api/pipelines', json)
    }


    async function savePipeline(name = 'Sans nom') {
    const json = getPipelineJSON()
    try {
        const response = await axios.post('/api/pipelines', {
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

    // On peut aussi ajouter une fonction pour charger un pipeline :
    async function loadPipeline(pipelineId) {
    const response = await axios.get(`/api/pipelines/${pipelineId}`)
    const pipeline = response.data
    // Reconstituer le graphe dans le store
    nodes.value = pipeline.graph_json.nodes || []
    edges.value = pipeline.graph_json.edges || []
    pipelineName.value = pipeline.name
    }

    return {
        selectedNodeId,
        selectedNode,
        selectNode,
        clearSelection,
        nodes,
        edges,
        addNode,
        updateNodeData,
        removeNode,
        addEdge,
        getPipelineJSON,
        exportJSON,
        savePipeline,
        loadPipeline
    }
})
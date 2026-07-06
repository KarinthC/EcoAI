// src/stores/usePipelineStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

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

    function createPipeline(name = 'Sans nom', graphJson = null) {
        const id = `pipe_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        pipelines.value[id] = {
        name,
        nodes: graphJson?.nodes || [],
        edges: graphJson?.edges || [],
        selectedNodeId: null,
        backendId: null   // sera renseigné après sauvegarde
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

    function addEdge(source, target) {
        if (activePipeline.value) {
            const id = `edge_${source}_${target}`
            if (!activePipeline.value.edges.some(e => e.source === source && e.target === target)) {
                activePipeline.value.edges.push({ id, source, target })
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
        const cleanNodes = activePipeline.value.nodes.map(node => ({
            id: node.id,
            type: node.type,
            position: node.position,
            data: node.data,
            class: node.class
        }))
        const cleanEdges = activePipeline.value.edges.map(edge => ({
            id: edge.id,
            source: edge.source,
            target: edge.target,
            sourceHandle: edge.sourceHandle,
            targetHandle: edge.targetHandle
        }))
        return { nodes: cleanNodes, edges: cleanEdges }
    }

    async function saveCurrent() {
        if (!activePipeline.value) return
        const json = getPipelineJSON()
        const name = activePipeline.value.name
        const payload = { name, graph_json: json }
        if (activePipeline.value.backendId) {
            await axios.put(`/api/pipelines/${activePipeline.value.backendId}`, payload)
        } else {
            const res = await axios.post('/api/pipelines', payload)
            pipelines.value[activeId.value].backendId = res.data.id
        }
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
    }

    async function saveCurrent() {
    if (!activePipeline.value) return
    const json = getPipelineJSON()
    const payload = { name: activePipeline.value.name, graph_json: json }
    if (activePipeline.value.backendId) {
        await axios.put(`/api/pipelines/${activePipeline.value.backendId}`, payload)
    } else {
        const res = await axios.post('/api/pipelines', payload)
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
        const res = await axios.get('/api/pipelines')
        for (const p of res.data) {
        pipelines.value[p.id] = {
            name: p.name,
            nodes: p.graph_json.nodes || [],
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
            await axios.delete(`/api/pipelines/${pipeline.backendId}`)
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
            if (node) {
            node.data = {
                ...node.data,
                impactLevel: item.level,
                impact_kg: item.impact_kg,
                impactMessage: item.message || '',
                ...(item.energy_kwh !== undefined && { energy_kwh: item.energy_kwh }),
                ...(item.equivalences && { equivalences: item.equivalences })
            }
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
        delete node.data.impact_kg
        delete node.data.impactMessage
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
        clearAnalysis
    }
})
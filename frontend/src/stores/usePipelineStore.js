// src/stores/usePipelineStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePipelineStore = defineStore('pipeline', () => {
  const nodes = ref([])
  const edges = ref([])

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

  function getPipelineJSON() {
    return {
      nodes: nodes.value,
      edges: edges.value,
    }
  }

  function exportJSON() {
    const json = getPipelineJSON()
    console.log('Pipeline JSON:', JSON.stringify(json, null, 2))
    alert('JSON affiché dans la console (F12)')
    // Plus tard : axios.post('/api/pipelines', json)
  }

  return {
    nodes,
    edges,
    addNode,
    updateNodeData,
    removeNode,
    addEdge,
    getPipelineJSON,
    exportJSON,
  }
})
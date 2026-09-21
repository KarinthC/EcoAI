import { useVueFlow } from '@vue-flow/core'
import { ref, watch } from 'vue'
import { usePipelineStore } from '@/stores/usePipelineStore'
import { NODE_BORDER_CLASS } from '@/components/pipeline/nodeTypes.js'


function getId() {
  return `dndnode_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// État partagé (hors de la fonction pour être global au module)
const draggedType = ref(null)
const draggedNodeType = ref(null)
const isDragOver = ref(false)
const isDragging = ref(false)

export default function useDragAndDrop() {
  const { screenToFlowCoordinate, onNodesInitialized, updateNode } = useVueFlow()
  const store = usePipelineStore()

  watch(isDragging, (dragging) => {
    document.body.style.userSelect = dragging ? 'none' : ''
  })

  // `nodeType` est un ID STABLE (cf. nodeTypes.js) : jamais traduit, sert de clé
  // dans le graphe, la config des champs et le dispatch backend.
  function onDragStart(event, type, nodeType) {
    if (event.dataTransfer) {
      event.dataTransfer.setData('application/vueflow', type)
      event.dataTransfer.effectAllowed = 'move'
    }
    draggedType.value = type
    draggedNodeType.value = nodeType || type
    isDragging.value = true
    document.addEventListener('drop', onDragEnd)
  }

  function onDragOver(event) {
    if (store.isAnalyzing) return
    event.preventDefault()
    if (draggedType.value) {
      isDragOver.value = true
      if (event.dataTransfer) {
        event.dataTransfer.dropEffect = 'move'
      }
    }
  }

  function onDragLeave() {
    isDragOver.value = false
  }

  function onDragEnd() {
    isDragging.value = false
    isDragOver.value = false
    draggedType.value = null
    document.removeEventListener('drop', onDragEnd)
  }

  function onDrop(event) {
    if (store.isAnalyzing) return
    const position = screenToFlowCoordinate({
      x: event.clientX,
      y: event.clientY,
    })

    const nodeId = getId()
    const newNode = {
      id: nodeId,
      type: draggedType.value,
      position,


      // On stocke l'ID STABLE du type de nœud. Le libellé affiché est résolu
      // dynamiquement via i18n (cf. CustomNode.vue / Sidebar.vue).
      data: { nodeType: draggedNodeType.value },
      class: NODE_BORDER_CLASS[draggedNodeType.value] || ''
    }

    const { off } = onNodesInitialized(() => {
      updateNode(nodeId, (node) => ({
        position: {
          x: node.position.x - node.dimensions.width / 2,
          y: node.position.y - node.dimensions.height / 2,
        },
      }))
      off()
    })

    store.addNode(newNode)
  }

  return {
    isDragOver,
    isDragging,
    onDragStart,
    onDragLeave,
    onDragOver,
    onDrop,
  }
}
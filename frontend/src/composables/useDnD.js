import { useVueFlow } from '@vue-flow/core'
import { ref, watch } from 'vue'
import { usePipelineStore } from '@/stores/usePipelineStore'


function getId() {
  return `dndnode_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// État partagé (hors de la fonction pour être global au module)
const draggedType = ref(null)
const draggedLabel = ref(null)
const isDragOver = ref(false)
const isDragging = ref(false)

export default function useDragAndDrop() {
  const { screenToFlowCoordinate, onNodesInitialized, updateNode } = useVueFlow()
  const store = usePipelineStore()

  const borderClassMap = {
  'Données': 'node-border-datasource',
  'Modèle ML' : 'node-border-ml',
  'Entrainement': 'node-border-operator',
  'Inférence': 'node-border-operator',
  'LLM Call': 'node-border-operator',        
  'LLM Expert': 'node-border-operator',
  'Video Generation': 'node-border-operator',
  'Opérateur': 'node-border-operator',
  'Préprocessing': 'node-border-operator'

  }


  watch(isDragging, (dragging) => {
    document.body.style.userSelect = dragging ? 'none' : ''
  })

  function onDragStart(event, type, label) {
    if (event.dataTransfer) {
      event.dataTransfer.setData('application/vueflow', type)
      event.dataTransfer.effectAllowed = 'move'
    }
    draggedType.value = type
    draggedLabel.value = label || type
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
    draggedLabel.value = null
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
      data: { label: draggedLabel.value },
      class: borderClassMap[draggedLabel.value] || ''
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
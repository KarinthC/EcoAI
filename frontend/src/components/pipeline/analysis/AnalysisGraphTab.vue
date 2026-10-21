<script setup>
// Onglet « Graphe » : canevas VueFlow parcourable (pan/zoom) en mode analyse,
// avec le panneau de détail du nœud sélectionné. Le drag & drop est désactivé
// (mode lecture seule) : on ne fait que parcourir le graphe analysé.
import { VueFlow, useVueFlow, MarkerType } from '@vue-flow/core'
import { markRaw, onMounted, watch } from 'vue'
import { usePipelineStore } from '@/stores/usePipelineStore'
import CustomNode from '@/components/pipeline/CustomNode.vue'
import DropzoneBackground from '@/components/pipeline/DropzoneBackground.vue'
import AnalysisNodePanel from '@/components/pipeline/AnalysisNodePanel.vue'

const store = usePipelineStore()
const { setViewport } = useVueFlow()

const nodeTypes = {
  custom: markRaw(CustomNode),
}

function onPaneClick() {
  store.clearSelection()
}

function onViewportChange(viewport) {
  store.updateViewport(viewport)
}

// Appliquer le viewport sauvegardé quand l'onglet actif change.
watch(() => store.activeId, () => {
  if (store.activePipeline) {
    store.applyViewport(setViewport)
  }
})

onMounted(() => {
  store.applyViewport(setViewport)
})
</script>

<template>
  <div class="graph-tab">
    <VueFlow
      :key="store.activeId"
      v-model:nodes="store.activePipeline.nodes"
      v-model:edges="store.activePipeline.edges"
      :node-types="nodeTypes"
      :default-edge-options="{
        markerEnd: MarkerType.ArrowClosed,
        style: { strokeWidth: '3px' }
      }"
      @pane-click="onPaneClick"
      @viewport-change="onViewportChange"
    >
      <DropzoneBackground />
    </VueFlow>

    <AnalysisNodePanel
      v-if="store.selectedNode"
      :node="store.selectedNode"
    />
  </div>
</template>

<style scoped>
.graph-tab {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: row;
  overflow: hidden;
  min-height: 0;
}
</style>

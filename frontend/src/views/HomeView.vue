<script setup>
import { VueFlow, useVueFlow, MarkerType } from '@vue-flow/core'
import { usePipelineStore } from '@/stores/usePipelineStore'
import Sidebar from '@/components/pipeline/Sidebar.vue'
import DropzoneBackground from '@/components/pipeline/DropzoneBackground.vue'
import useDragAndDrop from '@/composables/useDnD'
import { markRaw, onMounted, watch } from 'vue'
import CustomNode from '@/components/pipeline/CustomNode.vue'
import ParameterPanel from '@/components/pipeline/ParameterPanel.vue'
import ConnectionIndicator from '@/components/ConnectionIndicator.vue'
import UserIdentification from '@/components/UserIdentification.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import PipelineTabs from '@/components/pipeline/PipelineTabs.vue'
import AnalysisTabs from '@/components/pipeline/analysis/AnalysisTabs.vue'
import AnalysisGlobalTab from '@/components/pipeline/analysis/AnalysisGlobalTab.vue'
import AnalysisGraphTab from '@/components/pipeline/analysis/AnalysisGraphTab.vue'
import AnalysisIndicatorTab from '@/components/pipeline/analysis/AnalysisIndicatorTab.vue'

const store = usePipelineStore()
const { onConnect, addEdges, setViewport } = useVueFlow()
const { onDragOver, onDrop, onDragLeave, isDragOver } = useDragAndDrop()

const nodeTypes = {
  custom: markRaw(CustomNode)
}

function onPaneClick() {
  store.clearSelection()
}

function onViewportChange(viewport) {
  store.updateViewport(viewport)
}

// Appliquer le viewport sauvegardé quand l'onglet actif change
watch(() => store.activeId, () => {
  if (store.activePipeline) {
    store.applyViewport(setViewport)
  }
})

onMounted(async () => {
  await store.loadPipelines()
  if (!store.activePipeline) {
    store.createPipeline('Sans nom')
  }
  store.applyViewport(setViewport)
})

onConnect(addEdges)

</script>

<template>
  <div class="home-layout">
    <header class="app-header">
      <div class="header-left">
        <h1>EcoAI</h1>
        <ConnectionIndicator />
        <UserIdentification />
      </div>
      <div class="header-right">

      <LanguageSwitcher />

      <button class="btn-export" @click="store.saveCurrent('Test depuis UI')">
        📤 {{ $t('header.savePipeline') }}
      </button>
      <button
        v-if="store.activePipeline"
        class="btn-delete"
        :class="{ 'btn-delete-disabled': store.isAnalyzing }"
        :disabled="store.isAnalyzing"
        @click="store.deletePipeline(store.activeId)"
      >
        🗑 {{ $t('header.deletePipeline') }}
      </button>
    </div>
    </header>

    <PipelineTabs />

    <!-- Mode ÉDITION : canevas éditable + panneau de paramètres -->
    <div class="dnd-flow" @drop="onDrop" v-if="store.activePipeline && !store.isAnalyzing">
      <Sidebar />
      <VueFlow
        :key="store.activeId"
        v-model:nodes="store.activePipeline.nodes"
        v-model:edges="store.activePipeline.edges"
        :node-types="nodeTypes"
        :default-edge-options="{
          markerEnd: MarkerType.ArrowClosed,
          style: { strokeWidth: '3px' }
        }"
        @dragover="onDragOver"
        @dragleave="onDragLeave"
        @pane-click="onPaneClick"
        @viewport-change="onViewportChange"
      >
        <DropzoneBackground
          :style="{
            backgroundColor: isDragOver ? '#e7f3ff' : 'transparent',
            transition: 'background-color 0.2s ease',
          }"
        >
          <p v-if="isDragOver">{{ $t('canvas.dropHere') }}</p>
        </DropzoneBackground>
      </VueFlow>

      <ParameterPanel
        v-if="store.selectedNode"
        :node="store.selectedNode"
        @close="store.clearSelection"
      />
    </div>

    <!-- Mode ANALYSE : Sidebar permanente (critères + retour édition) + onglets -->
    <div class="dnd-flow" v-if="store.activePipeline && store.isAnalyzing">
      <Sidebar />
      <div class="analysis-area">
        <AnalysisTabs />
        <AnalysisGlobalTab v-if="store.activeAnalysisTab === 'global'" />
        <AnalysisGraphTab v-else-if="store.activeAnalysisTab === 'graph'" />
        <AnalysisIndicatorTab v-else />
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Largeur fixe commune aux boutons d'action : le libellé change avec la langue
   (FR plus long que EN), on fige donc la largeur pour éviter que le bloc ne se
   décale horizontalement lors du changement de langue. */
.btn-export,
.btn-delete {
  /* Largeur FIGÉE (et non min-) : les deux boutons ont la même taille quelle que
     soit la langue, donc le bloc de droite ne se décale plus quand on passe de
     FR (« Sauvegarder Pipeline ») à EN (« Save Pipeline »). La valeur couvre le
     libellé le plus long (FR) avec une marge de sécurité. */
  flex: 0 0 13rem;
  width: 13rem;
  justify-content: center;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  white-space: nowrap;
  font-size: 0.85rem;
  box-sizing: border-box;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between; 
  gap: 1rem;
  padding: 0.5rem 1rem;
  background: #2d3748;
  color: white;
}
.app-header h1 {
  margin: 0;
  font-size: 1.2rem;
  text-transform: none;
}

.btn-delete {
  padding: 0.4rem 1rem;
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}
.btn-delete:hover {
  background: #c53030;
}

.btn-delete:disabled,
.btn-delete-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-export {
  padding: 0.4rem 1rem;
  background: #48bb78;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-export:hover {
  background: #38a169;
}

.dnd-flow {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Zone principale du mode analyse : barre d'onglets + onglet actif. */
.analysis-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

@media screen and (min-width: 640px) {
  .dnd-flow {
    flex-direction: row;
  }
}
</style>

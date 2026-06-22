<script setup>
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { usePipelineStore } from '@/stores/usePipelineStore'
import Sidebar from '@/components/pipeline/Sidebar.vue'
import DropzoneBackground from '@/components/pipeline/DropzoneBackground.vue'
import useDragAndDrop from '@/composables/useDnD'
import { markRaw, ref } from 'vue'
import CustomNode from '@/components/pipeline/CustomNode.vue'
import ParameterPanel from '@/components/pipeline/ParameterPanel.vue'
import ConnectionIndicator from '@/components/ConnectionIndicator.vue'
import UserIdentification from '@/components/UserIdentification.vue'

const selectedNode = ref(null)


const store = usePipelineStore()
const { onConnect, addEdges } = useVueFlow()
const { onDragOver, onDrop, onDragLeave, isDragOver } = useDragAndDrop()


const nodeTypes = {
  custom: markRaw(CustomNode)
}

function onPaneClick() {
  store.clearSelection()
}


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
      <button class="btn-export" @click="store.exportJSON()">
        📤 Exporter le pipeline
      </button>
    </header>


    <div class="dnd-flow" @drop="onDrop">

      <Sidebar />

      <VueFlow
        v-model:nodes="store.nodes"
        v-model:edges="store.edges"
        :node-types="nodeTypes"
        @dragover="onDragOver"
        @dragleave="onDragLeave"
        @pane-click="onPaneClick"
      >
        <DropzoneBackground
          :style="{
            backgroundColor: isDragOver ? '#e7f3ff' : 'transparent',
            transition: 'background-color 0.2s ease',
          }"
        >
          <p v-if="isDragOver">Déposer ici</p>
        </DropzoneBackground>
      </VueFlow>


  <ParameterPanel
          v-if="store.selectedNode"
          :node="store.selectedNode"
          @close="store.clearSelection"
        />
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
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

@media screen and (min-width: 640px) {
  .dnd-flow {
    flex-direction: row;
  }
}
</style>
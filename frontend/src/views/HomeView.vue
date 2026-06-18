<script setup>
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { usePipelineStore } from '@/stores/usePipelineStore'
import Sidebar from '@/components/pipeline/Sidebar.vue'
import DropzoneBackground from '@/components/pipeline/DropzoneBackground.vue'
import useDragAndDrop from '@/composables/useDnD'

const store = usePipelineStore()
const { onConnect, addEdges } = useVueFlow()
const { onDragOver, onDrop, onDragLeave, isDragOver } = useDragAndDrop()

onConnect(addEdges)
</script>

<template>
  <div class="home-layout">
    <header class="app-header">
      <h1>EcoAI</h1>
      <button class="btn-export" @click="store.exportJSON()">
        📤 Exporter le pipeline
      </button>
    </header>

    <div class="dnd-flow" @drop="onDrop">
      <VueFlow
        :nodes="store.nodes"
        :edges="store.edges"
        @dragover="onDragOver"
        @dragleave="onDragLeave"
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

      <Sidebar />
    </div>
  </div>
</template>

<style scoped>
.home-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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
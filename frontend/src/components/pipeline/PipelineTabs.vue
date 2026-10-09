<script setup>
import { usePipelineStore } from '@/stores/usePipelineStore'
const store = usePipelineStore()
</script>

<template>
  <div class="tabs-bar">
    <div 
      v-for="(pipe, id) in store.pipelines"
      :key="id"
      class="tab"
      :class="{ active: store.activeId === id,
      disabled: store.isAnalyzing && store.activeId !== id
      }"
      @click="!store.isAnalyzing && store.switchTo(id)"
    >
      <span class="tab-name">{{ pipe.name }}</span>
      <span class="tab-close"   v-if="!store.isAnalyzing" @click.stop="store.closePipeline(id)">✕</span>
    </div>
    <button class="tab-add"  v-if="!store.isAnalyzing"  @click="store.createPipeline()">+</button>
  </div>
</template>

<style scoped>
.tabs-bar {
  display: flex;
  gap: 0.25rem;
  background: #edf2f7;
  border-bottom: 1px solid #cbd5e0;
  padding: 0.25rem 0.5rem;
  overflow-x: auto;
  flex-shrink: 0;
}
/* Style aligné sur les onglets d'analyse (AnalysisTabs) : même police, même
   taille, même couleur et même état actif. */
.tab {
  padding: 0.35rem 0.8rem;
  border: 1px solid transparent;
  border-radius: 4px 4px 0 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: #e2e8f0;
  color: #2d3748;
  font-size: 0.9rem;
  font-weight: 600;
  white-space: nowrap;
}
.tab:hover {
  background: #cbd5e0;
}
.tab.active {
  background: white;
  border-color: #cbd5e0;
  border-bottom-color: white;
}
.tab-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.tab-close {
  font-weight: bold;
  opacity: 0.5;
}
.tab-close:hover {
  opacity: 1;
  color: red;
}
.tab-add {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 0.5rem;
}

.tab.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
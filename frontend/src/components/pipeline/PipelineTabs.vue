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
      :class="{ active: store.activeId === id }"
      @click="store.switchTo(id)"
    >
      <span class="tab-name">{{ pipe.name }}</span>
      <span class="tab-close" @click.stop="store.closePipeline(id)">✕</span>
    </div>
    <button class="tab-add" @click="store.createPipeline('Nouveau pipeline')">+</button>
  </div>
</template>

<style scoped>
.tabs-bar {
  display: flex;
  background: #edf2f7;
  border-bottom: 1px solid #cbd5e0;
  padding: 0.25rem 0.5rem;
  overflow-x: auto;
}
.tab {
  padding: 0.3rem 0.8rem;
  border: 1px solid transparent;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  margin-right: 0.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: #e2e8f0;
}
.tab.active {
  background: white;
  border-color: #cbd5e0;
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
</style>
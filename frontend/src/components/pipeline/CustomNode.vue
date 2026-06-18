<script setup>
const nodeTypes = [
  { type: 'input', label: 'Données (CSV)' },
  { type: 'training', label: 'Entraînement'},
  { type: 'inference', label: 'Inférence'}
]

function onDragStart(event, nodeType) {
  event.dataTransfer.setData('nodeType', nodeType)
  event.dataTransfer.effectAllowed = 'move'
}
</script>

<template>
  <div class="palette">
    <h3>Types de nœuds</h3>
    <div
      v-for="nt in nodeTypes"
      :key="nt.type"
      class="palette-item"
      draggable="true"
      @dragstart="onDragStart($event, nt.type)"
    >
      <span class="icon">{{ nt.icon }}</span>
      {{ nt.label }}
    </div>
  </div>
</template>

<style scoped>
.palette {
  width: 200px;
  background: #f7fafc;
  padding: 1rem;
  border-right: 1px solid #e2e8f0;
  height: 100%;
}
.palette-item {
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  background: white;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  cursor: grab;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.icon { font-size: 1.2rem; }
</style>
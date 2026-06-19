<script setup>
import useDragAndDrop from '@/composables/useDnD'

const { onDragStart } = useDragAndDrop()
</script>

<template>
  <aside>
    <div class="description">Glissez-déposez ces nœuds sur le canvas.</div>

    <div class="nodes">
      <div
        class="sidebar-node sidebar-node-datasource"
        :draggable="true"
        @dragstart="onDragStart($event, 'custom', 'Données')"
      >
        Données
      </div>

      <div
        class="sidebar-node sidebar-node-training"
        :draggable="true"
        @dragstart="onDragStart($event, 'custom', 'Entraînement')"
      >
        Entraînement
      </div>

      <div
        class="sidebar-node sidebar-node-inference"
        :draggable="true"
        @dragstart="onDragStart($event, 'custom', 'Inférence')"
      >
        Inférence
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar-node {
  margin-bottom: 10px;
  cursor: grab;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 6px;
  box-shadow: 2px 2px 8px rgba(0,0,0,0.15);
  color: white;
}
.sidebar-node-datasource {
  background: #3182ce;
}
.sidebar-node-training {
  background: #805ad5;
}
.sidebar-node-inference {
  background: #38a169;
}
</style>
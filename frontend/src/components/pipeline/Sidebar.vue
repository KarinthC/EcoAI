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
        @dragstart="onDragStart($event, 'custom', 'Entrainement')"
      >
        Entrainement
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
aside {
  color: #fff;
  font-weight: 700;
  border-right: 1px solid #eee;
  padding: 15px 10px;
  font-size: 12px;
  background: #10b981bf;
  box-shadow: 0 5px 10px #0000004d;
}

aside .description {
  margin-bottom: 10px;
}

aside .nodes {
  /* conteneur des nœuds */
}

aside .nodes > * {
  margin-bottom: 10px;
  cursor: grab;
  font-weight: 500;
  box-shadow: 5px 5px 10px 2px #00000040;
}

.sidebar-node {
  margin-bottom: 10px;
  cursor: grab;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 6px;
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.15);
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

@media screen and (min-width: 640px) {
  aside {
    min-width: 15%;
  }
}

@media screen and (max-width: 639px) {
  aside .nodes {
    display: flex;
    flex-direction: row;
    gap: 5px;
  }
}
</style>
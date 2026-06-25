<script setup>
import useDragAndDrop from '@/composables/useDnD'
import { usePipelineStore } from '@/stores/usePipelineStore'
import { ref } from 'vue'

const store = usePipelineStore()

const analyzing = ref(false)

async function toggleAnalysis() {
  if (store.isAnalyzing) {
    store.clearAnalysis()
  } else {
    analyzing.value = true
    try {
      await store.analyzePipeline()
    } finally {
      analyzing.value = false
    }
  }
}
const { onDragStart } = useDragAndDrop()
</script>

<template>
  <aside>
    <div class="description" v-if="!store.isAnalyzing">Glissez-déposez ces nœuds sur le canvas.</div>

    <div class="nodes" v-if="!store.isAnalyzing">
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
    <div class="sidebar-footer">
    <button class="analyze-btn" @click="toggleAnalysis" :disabled="analyzing">
      <span v-if="analyzing">⏳ Analyse...</span>
      <span v-else>{{ store.isAnalyzing ? '🔙 Retour à l\'édition' : '🔍 Lancer l\'analyse' }}</span>
    </button>
  </div>
  </aside>
</template>

<style scoped>

.analyze-btn {
  width: 100%;
  padding: 0.5rem;
  background: white;
  color: #2d3748;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}
.analyze-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}


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

.sidebar-footer {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid rgba(255,255,255,0.3);
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
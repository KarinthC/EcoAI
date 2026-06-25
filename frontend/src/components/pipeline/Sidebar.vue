<script setup>
import useDragAndDrop from '@/composables/useDnD'
import { usePipelineStore } from '@/stores/usePipelineStore'
import { ref, computed } from 'vue'

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

const asideClass = computed(() => {
  if (!store.isAnalyzing || !store.analysisResult) return ''
  const total = store.analysisResult.total_impact_kg
  if (total < 5) return 'sidebar-green'
  if (total < 20) return 'sidebar-yellow'
  return 'sidebar-red'
})

const { onDragStart } = useDragAndDrop()
</script>

<template>
  <aside :class="asideClass">
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

    <div v-if="store.isAnalyzing" class="analysis-summary">
      <div class="total-score">
        {{ store.analysisResult.total_impact_kg }} <small>kg CO₂</small>
      </div>
      <div class="equivalences">
        <div class="equiv-item">🚗 {{ store.analysisResult.equivalences.km_voiture }} km</div>
        <div class="equiv-item">📺 {{ store.analysisResult.equivalences.heures_streaming }} h</div>
        <div class="equiv-item">🥗 {{ store.analysisResult.equivalences.repas_equivalent }} repas</div>
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

.analysis-summary {
  color: white;
  padding: 1rem 0;
  text-align: center;
}
.total-score {
  font-size: 2rem;
  font-weight: bold;
}
.equivalences {
  margin-top: 1rem;
  font-size: 0.8rem;
}
.equiv-item {
  margin-bottom: 0.5rem;
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

.sidebar-green { background: #38a169 !important; }
.sidebar-yellow { background: #d69e2e !important; }
.sidebar-red { background: #e53e3e !important; }



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
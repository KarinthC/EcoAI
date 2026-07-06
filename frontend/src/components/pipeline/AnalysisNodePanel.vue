<script setup>
import { usePipelineStore } from '@/stores/usePipelineStore'
import { watch } from 'vue'

const props = defineProps({
  node: Object
})

const store = usePipelineStore()

</script>

<template>
  <div v-if="node && node.data" class="panel analysis-panel">
    <div class="panel-header">
      <h3>{{ node.data.label }}</h3>
      <button class="close-btn" @click="store.clearSelection">✕</button>
    </div>
    <div class="panel-body">
      <div class="impact-value" :class="'impact-text-' + node.data.impactLevel">
        {{ node.data.impact_kg }} kg CO₂
      </div>
      <div class="impact-level-badge" :class="'badge-' + node.data.impactLevel">
        {{ node.data.impactLevel === 'low' ? 'Faible' : node.data.impactLevel === 'medium' ? 'Moyen' : 'Élevé' }}
      </div>
      <p v-if="node.data.impactMessage" class="impact-message">{{ node.data.impactMessage }}</p>

      <!-- Affichage des équivalences si le nœud est LLM -->
      <div v-if="node.data.equivalences" class="equivalences-box">
        <h4>Équivalences</h4>
        <ul>
          <li v-if="node.data.equivalences.streaming">{{ node.data.equivalences.streaming }}</li>
          <li v-if="node.data.equivalences.walking">{{ node.data.equivalences.walking }}</li>
          <li v-if="node.data.equivalences.running">{{ node.data.equivalences.running }}</li>
          <li v-if="node.data.equivalences.ev">{{ node.data.equivalences.ev }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analysis-panel {
  width: 280px;
  background: white;
  border-left: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
}
.panel-header h3 { margin: 0; font-size: 1rem; }
.close-btn { background: none; border: none; font-size: 1.2rem; cursor: pointer; }
.panel-body { padding: 1rem; }
.impact-value { font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem; }
.impact-text-low { color: #48bb78; }
.impact-text-medium { color: #d69e2e; }
.impact-text-high { color: #e53e3e; }
.impact-level-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  color: white;
  margin-bottom: 1rem;
}
.badge-low { background: #48bb78; }
.badge-medium { background: #d69e2e; }
.badge-high { background: #e53e3e; }
.impact-message { font-size: 0.9rem; color: #4a5568; }
.equivalences-box {
  margin-top: 1rem;
  padding: 0.5rem;
  background: #f7fafc;
  border-radius: 6px;
  font-size: 0.85rem;
}
.equivalences-box h4 {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
}
.equivalences-box ul {
  list-style: none;
  padding-left: 0.5rem;
}
.equivalences-box li {
  margin-bottom: 0.25rem;
}
</style>
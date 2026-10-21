<script setup>
// Barre d'onglets du mode analyse : « Analyse globale », « Graphe », puis un
// onglet par indicateur. La navigation passe par le store (onglet actif partagé
// avec la Sidebar).
import useAnalysisTabs from '@/composables/useAnalysisTabs'

const { tabs, activeTab, selectTab } = useAnalysisTabs()
</script>

<template>
  <div class="analysis-tabs">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      class="analysis-tab"
      :class="{ active: activeTab === tab.id }"
      @click="selectTab(tab.id)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<style scoped>
.analysis-tabs {
  display: flex;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: #edf2f7;
  border-bottom: 1px solid #cbd5e0;
  overflow-x: auto;
  flex-shrink: 0;
}
.analysis-tab {
  padding: 0.35rem 0.8rem;
  border: 1px solid transparent;
  border-radius: 4px 4px 0 0;
  background: #e2e8f0;
  color: #2d3748;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}
.analysis-tab:hover {
  background: #cbd5e0;
}
.analysis-tab.active {
  background: white;
  border-color: #cbd5e0;
  border-bottom-color: white;
}
</style>

<script setup>
// Onglet « Analyse globale » : note générale (single score) + synthèse
// (critères au-delà du budget) + suggestions de réduction.
// Reprend la logique de l'ancien AnalysisOverlay (supprimé).
import { computed, defineAsyncComponent } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePipelineStore } from '@/stores/usePipelineStore'

// Chargement asynchrone : ECharts (~500 ko) n'est téléchargé qu'à l'ouverture
// de l'onglet « Analyse globale », pas dans le bundle initial.
const ScoreComparisonChart = defineAsyncComponent(
  () => import('@/components/pipeline/analysis/ScoreComparisonChart.vue')
)

// Heatmap « hotspots » (nœuds × indicateurs) : également chargée à la demande
// pour garder ECharts hors du bundle initial.
const NodeIndicatorHeatmap = defineAsyncComponent(
  () => import('@/components/pipeline/analysis/NodeIndicatorHeatmap.vue')
)

// Treemap des contributions PEF (surface ∝ contribution du nœud) : chargé à la
// demande pour garder ECharts hors du bundle initial.
const IndicatorTreemap = defineAsyncComponent(
  () => import('@/components/pipeline/analysis/IndicatorTreemap.vue')
)

const store = usePipelineStore()
const { t } = useI18n()

const globalLevel = computed(() => store.analysisResult?.global_level || 'low')

// Nombre de critères au-delà du budget mensuel (ratio >= 1).
const redCount = computed(() =>
  (store.analysisResult?.criteria || []).filter((c) => (c.ratio || 0) >= 1).length
)

// Suggestions : le backend renvoie des objets { code, params }. On les traduit
// via « overlay.items.<code> ». Repli sur la chaîne si le backend envoie encore
// du texte brut, ou sur le code si la clé est inconnue.
const suggestions = computed(() => {
  const raw = store.analysisResult?.suggestions || []
  return raw.map((s) => {
    if (typeof s === 'string') return s
    const code = s?.code
    if (!code) return String(s)
    const key = `overlay.items.${code}`
    const translated = t(key, s.params || {})
    return translated === key ? code : translated
  })
})
</script>

<template>
  <div class="global-tab">
    <ScoreComparisonChart />

    <div class="summary-card" :class="`level-${globalLevel}`">
      <div class="summary-row">
        <span class="summary-label">{{ $t('analysis.global.beyondBudget') }}</span>
        <span class="summary-value">{{ redCount }}</span>
      </div>
    </div>

    <div class="pef-explainer">
      <span class="pef-explainer-icon" aria-hidden="true">ℹ️</span>
      <p>{{ $t('analysis.global.pefExplainer') }}</p>
    </div>

    <div class="suggestions-card">
      <h4>{{ $t('overlay.reduceImpact') }}</h4>
      <ul v-if="suggestions.length">
        <li v-for="(s, idx) in suggestions" :key="idx">{{ s }}</li>
      </ul>
      <p v-else class="suggestions-empty">{{ $t('overlay.noSuggestion') }}</p>
    </div>

    <!-- Rangée du bas : heatmap (gauche) + treemap (droite), 50 % chacune. -->
    <div class="charts-row">
      <NodeIndicatorHeatmap />
      <IndicatorTreemap />
    </div>
  </div>
</template>

<style scoped>
.global-tab {
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  /* Dans un parent flex column, un enfant scrollable doit pouvoir rétrécir
     (min-height: 0) pour que overflow-y: auto s'active : sinon il prend sa
     hauteur de contenu et le bas est coupé sans possibilité de défiler. */
  flex: 1;
  min-height: 0;
}
/* Les blocs enfants gardent leur hauteur naturelle : sans flex-shrink: 0, ils
   se compriment quand la place manque au lieu de laisser le conteneur défiler. */
.global-tab > * {
  flex-shrink: 0;
}
/* Encart explicatif : distingue le PEF des seuils planétaires par habitant. */
.pef-explainer {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  background: #ebf8ff;
  border-left: 4px solid #4299e1;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}
.pef-explainer-icon {
  font-size: 1rem;
  line-height: 1.5;
}
.pef-explainer p {
  margin: 0;
  color: #2c5282;
  font-size: 0.85rem;
  line-height: 1.5;
}
/* Rangée du bas : deux graphiques côte à côte (50 % / 50 %). */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  align-items: start;
}
/* Sur écran étroit, on empile les deux graphiques. */
@media (max-width: 900px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}
.summary-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
  border-left: 6px solid #a0aec0;
}
.summary-card.level-low { border-left-color: #48bb78; }
.summary-card.level-medium { border-left-color: #ed8936; }
.summary-card.level-high { border-left-color: #e53e3e; }
.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 0.25rem 0;
}
.summary-label {
  color: #4a5568;
  font-size: 0.85rem;
}
.summary-value {
  font-weight: 700;
  color: #2d3748;
  font-variant-numeric: tabular-nums;
}
.suggestions-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}
.suggestions-card h4 {
  margin: 0 0 0.5rem;
}
.suggestions-card ul {
  margin: 0;
  padding-left: 1.2rem;
}
.suggestions-empty {
  color: #718096;
  font-style: italic;
  margin: 0;
}
</style>


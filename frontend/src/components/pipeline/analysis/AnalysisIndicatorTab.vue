<script setup>
// Onglet d'un indicateur : jauge (seuil + PEF) et barres par nœud.
// Le critère est résolu depuis l'onglet actif du store.
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePipelineStore } from '@/stores/usePipelineStore'
import { criterionLabel, criterionDescription } from '@/components/pipeline/criterionI18n.js'
import { resolveNodeType, nodeTypeLabelKey } from '@/components/pipeline/nodeTypes.js'
import IndicatorComparison from '@/components/pipeline/analysis/IndicatorComparison.vue'

// Clé dédiée de l'eau ecologits (litres), non fusionnée avec PEF-WU (m³ eq).
const WATER_ECOLOGITS_KEY = 'PEF-WU_ecologits'

const store = usePipelineStore()
const { t } = useI18n()

// Critère correspondant à l'onglet actif (clé technique).
const criterion = computed(() =>
  (store.analysisResult?.criteria || []).find((c) => c.key === store.activeAnalysisTab) || null
)

const label = computed(() =>
  criterion.value ? criterionLabel(t, criterion.value.key, criterion.value.label) : ''
)

const description = computed(() =>
  criterion.value ? criterionDescription(t, criterion.value.key, criterion.value.description) : ''
)

// Contributions par nœud pour une clé d'indicateur donnée : on lit la valeur
// dans node.data.indicators (posée par le store lors de l'analyse).
function contributionsFor(key) {
  const rows = []
  for (const node of store.nodes) {
    const indicators = node.data?.indicators
    if (!indicators || !(key in indicators)) continue
    const typeKey = nodeTypeLabelKey(resolveNodeType(node.data))
    rows.push({
      id: node.id,
      label: typeKey ? t(typeKey) : (node.data?.label || node.id),
      value: indicators[key],
    })
  }
  return rows
}

// Contributions ACV (unité du critère, ex. m³ eq pour l'eau).
const nodeContributions = computed(() => contributionsFor(store.activeAnalysisTab))

// Contributions ecologits en litres : uniquement pour l'eau (PEF-WU), où la
// contribution ecologits est exposée sous une clé dédiée (unités différentes).
const ecologitsContributions = computed(() => {
  if (store.activeAnalysisTab !== 'PEF-WU') return []
  return contributionsFor(WATER_ECOLOGITS_KEY)
})
</script>

<template>
  <div v-if="criterion" class="indicator-tab">
    <div class="indicator-header">
      <h3>{{ label }}</h3>
      <p v-if="description" class="indicator-desc">{{ description }}</p>
    </div>
    <IndicatorComparison
      :criterion="criterion"
      :node-contributions="nodeContributions"
      :ecologits-contributions="ecologitsContributions"
    />
  </div>
</template>

<style scoped>
.indicator-tab {
  padding: 1rem;
  overflow-y: auto;
}
.indicator-header {
  margin-bottom: 1rem;
}
.indicator-header h3 {
  margin: 0 0 0.25rem;
}
.indicator-desc {
  margin: 0;
  font-size: 0.8rem;
  color: #718096;
}
</style>


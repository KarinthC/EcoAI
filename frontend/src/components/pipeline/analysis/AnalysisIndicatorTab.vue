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
//
// Plusieurs nœuds peuvent partager le même type (ex. deux « Entraînement ») :
// on les distingue alors par un numéro d'occurrence (« Entraînement 1 », « 2 »…).
// Le numéro n'est ajouté QUE si le type apparaît plusieurs fois dans le
// pipeline (un type unique reste sans numéro). Le comptage porte sur l'ENSEMBLE
// des nœuds (pas seulement les contributeurs) pour rester stable d'un
// indicateur à l'autre.
function contributionsFor(key) {
  // Nombre total de nœuds par type, dans l'ordre des nœuds du pipeline.
  const typeTotals = {}
  for (const node of store.nodes) {
    const typeKey = nodeTypeLabelKey(resolveNodeType(node.data))
    const typeId = typeKey || node.data?.label || node.id
    typeTotals[typeId] = (typeTotals[typeId] || 0) + 1
  }

  // Numéro d'occurrence par nœud (uniquement utile si le type est multiple).
  const typeCounters = {}
  const occurrence = {}
  for (const node of store.nodes) {
    const typeKey = nodeTypeLabelKey(resolveNodeType(node.data))
    const typeId = typeKey || node.data?.label || node.id
    typeCounters[typeId] = (typeCounters[typeId] || 0) + 1
    occurrence[node.id] = typeCounters[typeId]
  }

  const rows = []
  for (const node of store.nodes) {
    const indicators = node.data?.indicators
    if (!indicators || !(key in indicators)) continue
    const typeKey = nodeTypeLabelKey(resolveNodeType(node.data))
    const typeId = typeKey || node.data?.label || node.id
    const baseLabel = typeKey ? t(typeKey) : (node.data?.label || node.id)
    const suffix = typeTotals[typeId] > 1 ? ` ${occurrence[node.id]}` : ''
    rows.push({
      id: node.id,
      label: `${baseLabel}${suffix}`,
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

// Vrai si ecologits remonte une contribution (eau en litres) : la valeur
// affichée est alors incomplète (non fusionnée avec l'ACV), comme un critère
// partiel. Sert à griser la jauge PEF et à masquer l'interprétation verte.
const hasEcologits = computed(() => ecologitsContributions.value.length > 0)
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
      :has-ecologits="hasEcologits"
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


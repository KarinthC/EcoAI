<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePipelineStore } from '@/stores/usePipelineStore'
import useImpactColor from '@/composables/useImpactColor'
import { resolveNodeType, nodeTypeLabelKey } from '@/components/pipeline/nodeTypes.js'
import { criterionLabel } from '@/components/pipeline/criterionI18n.js'

const props = defineProps({
  node: Object
})

const store = usePipelineStore()
const { ratioColor } = useImpactColor()

const { t, locale } = useI18n()

// Libellé traduit du nœud (en-tête du panneau).
const nodeLabel = computed(() => {
  const key = nodeTypeLabelKey(resolveNodeType(props.node?.data))
  return key ? t(key) : (props.node?.data?.label || '')
})

// Message affiché pour un nœud neutre (confidence='none'). On distingue la
// cause : support de stockage non sélectionné vs nœud de représentation.
const neutralMessage = computed(() => {
  if (props.node?.data?.reason === 'missing_medium') {
    return t('analysis.missingStorageMedium')
  }
  return t('analysis.confidenceNone')
})

// Libellé du niveau d'impact (couleur appliquée via la classe impact-level-*).
const levelLabel = computed(() => {
  const level = props.node?.data?.impactLevel
  if (level === 'high') return t('analysis.levelHigh')
  if (level === 'medium') return t('analysis.levelMedium')
  if (level === 'low') return t('analysis.levelLow')
  return null
})

// Mapping clé d'indicateur -> unité, construit depuis les critères de l'analyse.
const unitByKey = computed(() => {
  const map = {}
  for (const c of (store.analysisResult?.criteria || [])) {
    map[c.key] = c.unit
  }
  // L'eau ecologits est exposée en litres (clé dédiée, absente de criteria).
  map['PEF-WU_ecologits'] = 'L (ecologits)'
  return map
})

function unitFor(key) {
  return unitByKey.value[key] || ''
}

// Mapping clé d'indicateur -> seuil mensuel par habitant, construit depuis les
// critères de l'analyse (threshold_monthly, déjà exposé au front).
const thresholdByKey = computed(() => {
  const map = {}
  for (const c of (store.analysisResult?.criteria || [])) {
    if (c.threshold_monthly) map[c.key] = c.threshold_monthly
  }
  return map
})

// Couleur d'un indicateur selon la MÊME logique que le panel de gauche :
// ratio valeur/seuil passé dans le dégradé partagé (useImpactColor).
// L'eau ecologits (litres) n'est pas comparable au seuil (m³ eq) -> neutre ;
// critère sans seuil -> couleur neutre également.
function indicatorColor(key, value) {
  if (key === 'PEF-WU_ecologits') return '#4a5568'
  const threshold = thresholdByKey.value[key]
  if (!threshold || value === null || value === undefined) return '#4a5568'
  return ratioColor(Math.abs(value) / threshold)
}

// Indicateurs du nœud, remis dans le MÊME ORDRE que le panel de gauche
// (ordre de store.analysisResult.criteria), avec nom, valeur, unité.
// On n'affiche que les indicateurs réellement portés par le nœud.
const orderedIndicators = computed(() => {
  const indicators = props.node?.data?.indicators
  if (!indicators) return []

  const rows = []
  const handled = new Set()

  for (const c of (store.analysisResult?.criteria || [])) {
    const key = c.key
    if (!(key in indicators)) continue
    handled.add(key)
    rows.push({
      // Libellé du critère traduit (clé technique stable + repli backend FR).
      name: criterionLabel(t, key, c.label),
      value: indicators[key],
      unit: c.unit,
      color: indicatorColor(key, indicators[key]),
      // Ligne « eau » ecologits affichée juste après PEF-WU.
      extraEcologits: key === 'PEF-WU' && ('PEF-WU_ecologits' in indicators)
        ? indicators['PEF-WU_ecologits']
        : null,
    })
    if (key === 'PEF-WU') handled.add('PEF-WU_ecologits')
  }

  // Indicateurs éventuels hors criteria (ex. clés inconnues) : repli.
  for (const [key, value] of Object.entries(indicators)) {
    if (handled.has(key)) continue
    rows.push({
      key,
      name: fallbackName(key),
      value,
      unit: unitFor(key),
      color: indicatorColor(key, value),
      extraEcologits: null,
    })
  }

  return rows
})

// Nom de repli pour les clés absentes de criteria.
function fallbackName(key) {
  if (key === 'PEF-WU_ecologits') return t('analysis.waterUsage')
  return String(key).replace(/^PEF-/, '')
}

// Formatage identique au panel de gauche.
function formatValue(v) {
  if (v === null || v === undefined) return '—'
  if (v === 0) return '0'
  const abs = Math.abs(v)
  if (abs >= 1e-3 && abs < 1e5) {
    // Séparateur décimal/triade conforme à la langue active (fr-FR / en…).
    return v.toLocaleString(locale.value, { maximumFractionDigits: 4 })
  }
  return v.toExponential(2)
}
</script>

<template>
  <div v-if="node && node.data" class="panel analysis-panel">
    <div class="panel-header">
      <h3>{{ nodeLabel }}</h3>
      <button class="close-btn" @click="store.clearSelection">✕</button>
    </div>
    <div class="panel-body">
      <!-- Niveau d'impact : juste sous le nom du nœud, coloré (rouge/jaune/vert) -->
      <div
        v-if="levelLabel"
        class="impact-level-label"
        :class="'impact-level-' + node.data.impactLevel"
      >
        {{ levelLabel }}
      </div>

      <!-- Fiabilité de la méthode de calcul -->
      <div v-if="node.data.confidence" class="confidence" :class="'confidence-' + node.data.confidence">
        <span v-if="node.data.confidence === 'high'">{{ $t('analysis.confidenceHigh') }}</span>
        <template v-else-if="node.data.confidence === 'medium'">
          <span class="confidence-title">{{ $t('analysis.confidenceMediumTitle') }}</span>
          <span class="confidence-detail">{{ $t('analysis.confidenceMediumDetail') }}</span>
        </template>
        <template v-else-if="node.data.confidence === 'low'">
          <span class="confidence-title">{{ $t('analysis.confidenceLowTitle') }}</span>
          <span class="confidence-detail">{{ $t('analysis.confidenceLowDetail') }}</span>
        </template>
        <span v-else-if="node.data.confidence === 'none'">
          {{ neutralMessage }}
        </span>
        <span v-else>{{ $t('analysis.confidenceGeneric', { level: node.data.confidence }) }}</span>
      </div>

      <!-- Indicateurs (PEF) : mêmes noms et même ordre que le panel de gauche -->
      <div v-if="orderedIndicators.length" class="indicators-box">
        <h4>{{ $t('analysis.indicators') }}</h4>
        <ul>
          <li v-for="row in orderedIndicators" :key="row.key" class="indicator-item">
            <span class="indicator-name">{{ row.name }}</span>
            <span class="indicator-value" :style="{ color: row.color }">
              {{ formatValue(row.value) }}
              <span v-if="row.unit" class="indicator-unit">{{ row.unit }}</span>
            </span>
            <span v-if="row.extraEcologits !== null" class="indicator-extra">
              + {{ formatValue(row.extraEcologits) }}
              <span class="indicator-unit">L (ecologits)</span>
            </span>
          </li>
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
.panel-body {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  min-height: 0;
}
.impact-level-label {
  font-size: 0.95rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
}
.impact-level-low { color: #38a169; }
.impact-level-medium { color: #d69e2e; }
.impact-level-high { color: #e53e3e; }
.confidence {
  display: block;
  font-size: 0.8rem;
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}
.confidence-high {
  background: #c6f6d5;
  color: #22543d;
}
.confidence-none {
  background: #e2e8f0;
  color: #4a5568;
}
.confidence-medium {
  background: #fefcbf;
  color: #744210;
}
.confidence-medium .confidence-title {
  display: block;
  font-weight: 600;
  margin-bottom: 0.15rem;
}
.confidence-medium .confidence-detail {
  display: block;
}
.confidence-low {
  background: #feebc8;
  color: #7b341e;
}
.confidence-low .confidence-title {
  display: block;
  font-weight: 600;
  margin-bottom: 0.15rem;
}
.confidence-low .confidence-detail {
  display: block;
}
.indicators-box {
  margin-top: 1rem;
  padding: 0.5rem;
  background: #f7fafc;
  border-radius: 6px;
  font-size: 0.8rem;
}
.indicators-box h4 {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
}
.indicators-box ul {
  list-style: none;
  padding-left: 0;
}
.indicator-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 0.75rem;
}
.indicator-name {
  font-weight: 600;
  color: #2d3748;
}
.indicator-value {
  font-variant-numeric: tabular-nums;
}
.indicator-extra {
  font-variant-numeric: tabular-nums;
}
.indicator-unit {
  color: #718096;
}
</style>
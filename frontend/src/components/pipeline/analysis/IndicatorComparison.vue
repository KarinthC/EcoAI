<script setup>
// Comparatif d'un indicateur :
//   - jauge : valeur totale du pipeline vs seuil mensuel par habitant ;
//   - barres : contribution de chaque nœud à cet indicateur.
// Présentation pure : les données sont passées en props par l'onglet.
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import useImpactColor from '@/composables/useImpactColor'

const props = defineProps({
  // Critère courant (issu de analysisResult.criteria).
  criterion: { type: Object, required: true },
  // Contributions par nœud (unité du critère) : [{ id, label, value }].
  nodeContributions: { type: Array, default: () => [] },
  // Contributions ecologits par nœud, en litres (eau uniquement) :
  // [{ id, label, value }]. Vide pour les autres critères.
  ecologitsContributions: { type: Array, default: () => [] },
})

const { t, locale } = useI18n()
const { ratioColor } = useImpactColor()

const value = computed(() => props.criterion?.value ?? 0)
const threshold = computed(() => props.criterion?.threshold_monthly ?? null)
const ratio = computed(() => props.criterion?.ratio ?? null)

// Contribution partielle : des nœuds ecologits ne rapportent pas ce critère,
// la valeur réelle est donc supérieure à celle affichée.
const hasPartial = computed(() => !!props.criterion?.has_partial)

// Largeur de la jauge : ratio plafonné à 100 % (au-delà = dépassement).
const gaugeWidth = computed(() => {
  if (ratio.value === null || ratio.value === undefined) return 0
  return Math.min(100, Math.max(0, ratio.value * 100))
})

// Couleur de la jauge. Un critère partiel ne doit PAS apparaître vert quand il
// n'est pas déjà problématique (fausse impression de sûreté) : on le grise,
// SAUF s'il est de niveau « high » (ratio >= 0.15, palier du backend), auquel
// cas la couleur rouge du gradient est conservée. Même règle que la Sidebar.
const PARTIAL_GRAY = '#4a5568'
const HIGH_RATIO = 0.15

const gaugeColor = computed(() => {
  if (hasPartial.value && !(ratio.value >= HIGH_RATIO)) {
    return PARTIAL_GRAY
  }
  return ratioColor(ratio.value)
})

// Valeur maximale d'une liste de contributions, pour normaliser les barres.
function maxValue(rows) {
  return rows.reduce((m, n) => Math.max(m, Math.abs(n.value || 0)), 0)
}

// Largeur d'une barre, normalisée sur le maximum de SA section (les deux
// sections — m³ eq et litres — ont des échelles distinctes).
function barWidth(v, rows) {
  const max = maxValue(rows)
  if (!max) return 0
  return (Math.abs(v) / max) * 100
}

function formatValue(v) {
  if (v === null || v === undefined) return '—'
  if (v === 0) return '0'
  const abs = Math.abs(v)
  if (abs >= 1e-3 && abs < 1e5) {
    return v.toLocaleString(locale.value, { maximumFractionDigits: 4 })
  }
  return v.toExponential(2)
}
</script>

<template>
  <div class="comparison">
    <!-- Jauge : valeur totale vs seuil mensuel par habitant -->
    <div class="gauge-block">
      <div class="gauge-header">
        <span class="gauge-value" :style="{ color: gaugeColor }">
          {{ formatValue(value) }}
          <span class="gauge-unit">{{ criterion.unit }}</span>
          <span v-if="hasPartial" class="partial-mark" :title="$t('sidebar.partialMark')">+ ?</span>
        </span>
        <span v-if="threshold" class="gauge-threshold">
          {{ $t('analysis.indicator.threshold') }} {{ formatValue(threshold) }} {{ criterion.unit }}
        </span>
      </div>
      <div class="gauge-track">
        <div class="gauge-fill" :style="{ width: gaugeWidth + '%', background: gaugeColor }"></div>
      </div>
      <div v-if="ratio !== null && ratio !== undefined" class="gauge-ratio">
        {{ $t('analysis.indicator.ratio') }} {{ formatValue(ratio) }}
      </div>
      <!-- Contribution partielle : nœuds ecologits sans ce critère -->
      <p v-if="hasPartial" class="partial-notice">
        {{ $t('sidebar.tooltipPartial') }}
      </p>
    </div>

    <!-- Barres : contribution de chaque nœud (unité du critère) -->
    <div class="bars-block">
      <h4>
        {{ $t('analysis.indicator.byNode') }}
        <span v-if="criterion.unit" class="bars-unit">({{ criterion.unit }})</span>
      </h4>
      <p v-if="!nodeContributions.length" class="bars-empty">
        {{ $t('analysis.indicator.noContribution') }}
      </p>
      <ul v-else class="bars-list">
        <li v-for="n in nodeContributions" :key="n.id" class="bar-item">
          <span class="bar-label">{{ n.label }}</span>
          <div class="bar-track">
            <div class="bar-fill" :style="{ width: barWidth(n.value, nodeContributions) + '%' }"></div>
          </div>
          <span class="bar-value">{{ formatValue(n.value) }}</span>
        </li>
      </ul>
    </div>

    <!-- Barres ecologits (eau en litres) : section distincte, unités non
         comparables à l'ACV (m³ eq) -> échelle de barres indépendante. -->
    <div v-if="ecologitsContributions.length" class="bars-block">
      <h4>
        {{ $t('analysis.indicator.byNode') }}
        <span class="bars-unit">(L ecologits)</span>
      </h4>
      <ul class="bars-list">
        <li v-for="n in ecologitsContributions" :key="n.id" class="bar-item">
          <span class="bar-label">{{ n.label }}</span>
          <div class="bar-track">
            <div
              class="bar-fill bar-fill-ecologits"
              :style="{ width: barWidth(n.value, ecologitsContributions) + '%' }"
            ></div>
          </div>
          <span class="bar-value">{{ formatValue(n.value) }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.comparison {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.gauge-block {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}
.gauge-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.5rem;
}
.gauge-value {
  font-size: 1.4rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.gauge-unit {
  font-size: 0.8rem;
  color: #718096;
}
.partial-mark {
  font-size: 1.1rem;
  color: #4a5568;
  font-weight: 700;
  cursor: help;
  margin-left: 0.25rem;
}
.partial-notice {
  margin: 0.5rem 0 0;
  font-size: 0.75rem;
  color: #b7791f;
  background: #fefcbf;
  border-radius: 4px;
  padding: 0.35rem 0.5rem;
}
.gauge-threshold {
  font-size: 0.75rem;
  color: #718096;
}
.gauge-track {
  height: 16px;
  border-radius: 4px;
  background: #edf2f7;
  overflow: hidden;
}
.gauge-fill {
  height: 100%;
  transition: width 0.3s ease;
}
.gauge-ratio {
  margin-top: 0.35rem;
  font-size: 0.75rem;
  color: #4a5568;
}
.bars-block {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}
.bars-block h4 {
  margin: 0 0 0.75rem;
}
.bars-unit {
  font-size: 0.75rem;
  font-weight: 400;
  color: #718096;
}
.bars-empty {
  color: #718096;
  font-style: italic;
  margin: 0;
}
.bars-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.bar-item {
  display: grid;
  grid-template-columns: 120px 1fr 90px;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
}
.bar-label {
  color: #4a5568;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.bar-track {
  height: 12px;
  border-radius: 3px;
  background: #edf2f7;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: #3182ce;
  transition: width 0.3s ease;
}
/* Section ecologits (eau en litres) : couleur neutre, non comparable à l'ACV. */
.bar-fill-ecologits {
  background: #4a5568;
}
.bar-value {
  text-align: right;
  font-variant-numeric: tabular-nums;
  color: #2d3748;
}
</style>

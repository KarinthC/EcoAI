<script setup>
// Comparatif d'un indicateur :
//   - deux jauges CSS : seuil mensuel par habitant + contribution au score PEF ;
//   - barres : contribution de chaque nœud à cet indicateur.
// Présentation pure : les données sont passées en props par l'onglet.
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import useImpactColor from '@/composables/useImpactColor'
import { protectionAreaKey } from '@/components/pipeline/analysis/protectionAreas.js'

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

// --- Jauge 1 : seuil mensuel ------------------------------------------------
// Largeur = ratio plafonné à 100 % (au-delà = dépassement).
const gaugeWidth = computed(() => {
  if (ratio.value === null || ratio.value === undefined) return 0
  return Math.min(100, Math.max(0, ratio.value * 100))
})

// Couleur de la jauge de seuil. Un critère partiel ne doit PAS apparaître vert
// quand il n'est pas déjà problématique (fausse impression de sûreté) : on le
// grise, SAUF s'il est de niveau « high » (ratio >= 0.15, palier du backend).
const PARTIAL_GRAY = '#4a5568'
const HIGH_RATIO = 0.15

const gaugeColor = computed(() => {
  if (hasPartial.value && !(ratio.value >= HIGH_RATIO)) return PARTIAL_GRAY
  return ratioColor(ratio.value)
})

// --- Jauge 2 : contribution au score PEF ------------------------------------
// Contribution en mPt (peut être négative : eau évitée).
const pefContribution = computed(() => props.criterion?.pef_contribution ?? 0)

// Échelle de remplissage : 0 -> 5 mPt (5 mPt = jauge pleine = impact élevé).
// Au-delà de 5 mPt, la jauge reste pleine (dépassement signalé par la couleur).
const PEF_FULL = 5

const pefWidth = computed(() => {
  const v = Math.abs(pefContribution.value)
  return Math.min(100, (v / PEF_FULL) * 100)
})

// Couleur de la jauge PEF : échelle log de 0.1 mPt (vert) à 5 mPt (rouge).
// Une contribution négative (crédit) est affichée en couleur neutre.
const PEF_COLOR_MIN = 0.1
const PEF_COLOR_MAX = 5

function pefColor(score) {
  if (score < 0) return PARTIAL_GRAY
  if (score <= 0) return 'hsl(120, 60%, 40%)'
  const lo = Math.log10(PEF_COLOR_MIN)
  const hi = Math.log10(PEF_COLOR_MAX)
  let t = (Math.log10(score) - lo) / (hi - lo)
  t = Math.min(1, Math.max(0, t))
  const hue = 120 * (1 - t) // 120° (vert) -> 0° (rouge)
  return `hsl(${hue}, 75%, 42%)`
}

// --- Interprétation ---------------------------------------------------------
// Seuils de « significativité » : 25 % du seuil mensuel et 1 mPt de score PEF.
const RATIO_SIGNIFICANT = 0.25
const PEF_SIGNIFICANT = 1

// Le critère est-il significatif sur chacune des deux jauges ?
const ratioSignificant = computed(() => (ratio.value ?? 0) >= RATIO_SIGNIFICANT)
const pefSignificant = computed(() => Math.abs(pefContribution.value) >= PEF_SIGNIFICANT)

// Clé i18n du cas d'interprétation (4 combinaisons possibles).
const interpretationKey = computed(() => {
  if (ratioSignificant.value && pefSignificant.value) return 'bothAbove'
  if (ratioSignificant.value) return 'ratioAbove'
  if (pefSignificant.value) return 'pefAbove'
  return 'bothBelow'
})

// Aire de protection du critère (santé humaine / écosystèmes / ressources),
// injectée dans la phrase d'interprétation. Repli générique si clé inconnue.
const protectionArea = computed(() => {
  const key = protectionAreaKey(props.criterion?.key)
  return key ? t(key) : t('analysis.protectionArea.generic')
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
    <!-- Jauge 1 : valeur totale vs seuil mensuel par habitant -->
    <div class="gauge-block">
      <div class="gauge-header">
        <span class="gauge-title">{{ $t('analysis.indicator.thresholdBar') }}</span>
        <span class="gauge-value" :style="{ color: gaugeColor }">
          {{ formatValue(value) }}
          <span class="gauge-unit">{{ criterion.unit }}</span>
          <span v-if="hasPartial" class="partial-mark" :title="$t('sidebar.partialMark')">+ ?</span>
        </span>
      </div>
      <div class="gauge-track">
        <div class="gauge-fill" :style="{ width: gaugeWidth + '%', background: gaugeColor }"></div>
      </div>
      <div class="gauge-foot">
        <span v-if="ratio !== null && ratio !== undefined" class="gauge-ratio">
          {{ $t('analysis.indicator.ratio') }} {{ formatValue(ratio) }}
        </span>
        <span v-if="threshold" class="gauge-threshold">
          {{ $t('analysis.indicator.threshold') }} {{ formatValue(threshold) }} {{ criterion.unit }}
        </span>
      </div>
      <p v-if="hasPartial" class="partial-notice">{{ $t('sidebar.tooltipPartial') }}</p>
    </div>

    <!-- Jauge 2 : contribution au score PEF (0 -> 100 mPt) -->
    <div class="gauge-block">
      <div class="gauge-header">
        <span class="gauge-title">{{ $t('analysis.indicator.pefBar') }}</span>
        <span class="gauge-value" :style="{ color: pefColor(pefContribution) }">
          {{ formatValue(pefContribution) }} <span class="gauge-unit">mPt</span>
        </span>
      </div>
      <div class="gauge-track">
        <div
          class="gauge-fill"
          :style="{ width: pefWidth + '%', background: pefColor(pefContribution) }"
        ></div>
      </div>
      <div class="gauge-foot">
        <span class="gauge-threshold">{{ $t('analysis.indicator.pefScale') }}</span>
      </div>
    </div>

    <!-- Interprétation : phrase selon les deux jauges (4 cas) -->
    <div class="interpretation" :class="`interpretation-${interpretationKey}`">
      <span class="interpretation-icon" aria-hidden="true">💡</span>
      <p class="interpretation-text">
        {{ $t(`analysis.indicator.interpretation.${interpretationKey}`, { area: protectionArea }) }}
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
/* Jauge (seuil mensuel / contribution PEF) */
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
.gauge-title {
  font-weight: 600;
  color: #2d3748;
}
.gauge-value {
  font-size: 1rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.gauge-unit {
  font-size: 0.75rem;
  font-weight: 400;
  color: #718096;
}
.partial-mark {
  font-size: 0.9rem;
  color: #4a5568;
  font-weight: 700;
  cursor: help;
  margin-left: 0.25rem;
}
.gauge-track {
  height: 14px;
  border-radius: 4px;
  background: #edf2f7;
  overflow: hidden;
}
.gauge-fill {
  height: 100%;
  transition: width 0.3s ease;
}
.gauge-foot {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.35rem;
  font-size: 0.7rem;
  color: #718096;
}
.partial-notice {
  margin: 0.5rem 0 0;
  font-size: 0.75rem;
  color: #b7791f;
  background: #fefcbf;
  border-radius: 4px;
  padding: 0.35rem 0.5rem;
}
/* Interprétation : encadré coloré selon le cas (4 combinaisons). */
.interpretation {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  border-left: 4px solid #a0aec0;
  background: #f7fafc;
}
.interpretation-icon {
  font-size: 1rem;
  line-height: 1.4;
}
.interpretation-text {
  margin: 0;
  font-size: 0.85rem;
  color: #2d3748;
}
/* Les deux jauges sous les seuils : impact faible. */
.interpretation-bothBelow {
  border-left-color: #38a169;
  background: #f0fff4;
}
/* Une seule jauge au-dessus : vigilance (orange). */
.interpretation-ratioAbove,
.interpretation-pefAbove {
  border-left-color: #dd6b20;
  background: #fffaf0;
}
/* Les deux jauges au-dessus : impact notable (rouge). */
.interpretation-bothAbove {
  border-left-color: #e53e3e;
  background: #fff5f5;
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


<script setup>
// Comparatif d'un indicateur :
//   - deux jauges CSS : seuil mensuel par habitant + contribution au score PEF ;
//   - camembert : contribution de chaque nœud à cet indicateur.
// Présentation pure : les données sont passées en props par l'onglet.
import { computed, defineAsyncComponent } from 'vue'
import { useI18n } from 'vue-i18n'
import useImpactColor from '@/composables/useImpactColor'
import { protectionAreaKey } from '@/components/pipeline/analysis/protectionAreas.js'
import IndicatorReference from '@/components/pipeline/analysis/IndicatorReference.vue'

// Chargement asynchrone : ECharts (~500 ko) n'est téléchargé qu'à l'ouverture
// d'un onglet d'indicateur, pas dans le bundle initial.
const NodeContributionPie = defineAsyncComponent(
  () => import('@/components/pipeline/analysis/NodeContributionPie.vue')
)

const props = defineProps({
  // Critère courant (issu de analysisResult.criteria).
  criterion: { type: Object, required: true },
  // Contributions par nœud (unité du critère) : [{ id, label, value }].
  nodeContributions: { type: Array, default: () => [] },
  // Contributions ecologits par nœud, en litres (eau uniquement) :
  // [{ id, label, value }]. Vide pour les autres critères.
  ecologitsContributions: { type: Array, default: () => [] },
  // Vrai si des contributions ecologits existent pour ce critère (eau en
  // litres). Comme pour un critère partiel, la valeur affichée est incomplète :
  // on grise la jauge PEF et on masque l'interprétation « les deux en dessous ».
  hasEcologits: { type: Boolean, default: false },
})

const { t, locale } = useI18n()
const { ratioColor } = useImpactColor()

const value = computed(() => props.criterion?.value ?? 0)
const threshold = computed(() => props.criterion?.threshold_monthly ?? null)
const ratio = computed(() => props.criterion?.ratio ?? null)

// Contribution partielle : des nœuds ecologits ne rapportent pas ce critère,
// la valeur réelle est donc supérieure à celle affichée.
const hasPartial = computed(() => !!props.criterion?.has_partial)

// Valeur incomplète : soit le critère est partiel (ecologits ne le remonte
// pas), soit ecologits remonte une contribution en litres (eau) non fusionnée
// avec l'ACV. Dans les deux cas, la valeur affichée est sous-estimée.
const isIncomplete = computed(() => hasPartial.value || props.hasEcologits)

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
  if (isIncomplete.value && !(ratio.value >= HIGH_RATIO)) return PARTIAL_GRAY
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

// Couleur de la jauge PEF affichée. Comme pour le seuil, un critère partiel ne
// doit PAS apparaître vert quand il n'est pas déjà significatif (fausse
// impression de sûreté) : on le grise, SAUF s'il dépasse déjà 1 mPt.
const pefGaugeColor = computed(() => {
  if (isIncomplete.value && !pefSignificant.value) return PARTIAL_GRAY
  return pefColor(pefContribution.value)
})

// Clé i18n du cas d'interprétation (4 combinaisons possibles). En présence
// d'une inconnue (critère partiel), on n'affiche PAS le cas « les deux en
// dessous » (vert) : la valeur réelle peut être supérieure, l'affirmation
// serait trompeuse.
const interpretationKey = computed(() => {
  if (ratioSignificant.value && pefSignificant.value) return 'bothAbove'
  if (ratioSignificant.value) return 'ratioAbove'
  if (pefSignificant.value) return 'pefAbove'
  if (isIncomplete.value) return null
  return 'bothBelow'
})

// Aire de protection du critère (santé humaine / écosystèmes / ressources),
// injectée dans la phrase d'interprétation. Repli générique si clé inconnue.
const protectionArea = computed(() => {
  const key = protectionAreaKey(props.criterion?.key)
  return key ? t(key) : t('analysis.protectionArea.generic')
})

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
          <span v-if="isIncomplete" class="partial-mark" :title="$t('sidebar.partialMark')">+ ?</span>
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

    <!-- Jauge 2 : contribution au score PEF (0 -> 5 mPt) -->
    <div class="gauge-block">
      <div class="gauge-header">
        <span class="gauge-title">{{ $t('analysis.indicator.pefBar') }}</span>
        <span class="gauge-value" :style="{ color: pefGaugeColor }">
          {{ formatValue(pefContribution) }} <span class="gauge-unit">mPt</span>
          <span v-if="isIncomplete" class="partial-mark" :title="$t('sidebar.partialMark')">+ ?</span>
        </span>
      </div>
      <div class="gauge-track">
        <div class="gauge-fill" :style="{ width: pefWidth + '%', background: pefGaugeColor }"></div>
      </div>
      <div class="gauge-foot">
        <span class="gauge-threshold">{{ $t('analysis.indicator.pefScale') }}</span>
      </div>
      <p v-if="hasPartial" class="partial-notice">{{ $t('sidebar.tooltipPartial') }}</p>
    </div>

    <!-- Interprétation : phrase selon les deux jauges (4 cas). Masquée quand
         le cas est indéterminé (critère partiel sous les deux seuils). -->
    <div
      v-if="interpretationKey"
      class="interpretation"
      :class="`interpretation-${interpretationKey}`"
    >
      <span class="interpretation-icon" aria-hidden="true">
        <!-- Icône Lucide « brain-cog » (cerveau + engrenage) : interprétation.
             Source : lucide-icons/lucide (licence ISC). -->
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none"
             stroke="currentColor" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
          <path d="m10.852 14.772-.383.923" />
          <path d="m10.852 9.228-.383-.923" />
          <path d="m13.148 14.772.382.924" />
          <path d="m13.531 8.305-.383.923" />
          <path d="m14.772 10.852.923-.383" />
          <path d="m14.772 13.148.923.383" />
          <path d="M17.598 6.5A3 3 0 1 0 12 5a3 3 0 0 0-5.63-1.446 3 3 0 0 0-.368 1.571 4 4 0 0 0-2.525 5.771" />
          <path d="M17.998 5.125a4 4 0 0 1 2.525 5.771" />
          <path d="M19.505 10.294a4 4 0 0 1-1.5 7.706" />
          <path d="M4.032 17.483A4 4 0 0 0 11.464 20c.18-.311.892-.311 1.072 0a4 4 0 0 0 7.432-2.516" />
          <path d="M4.5 10.291A4 4 0 0 0 6 18" />
          <path d="M6.002 5.125a3 3 0 0 0 .4 1.375" />
          <path d="m9.228 10.852-.923-.383" />
          <path d="m9.228 13.148-.923.383" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      </span>
      <p class="interpretation-text">
        {{ $t(`analysis.indicator.interpretation.${interpretationKey}`, { area: protectionArea }) }}
      </p>
    </div>

    <!-- Camembert nœuds (gauche) + références fondatrices (droite), 50/50 -->
    <div class="bottom-row">
      <div class="pie-card">
        <h4>
          {{ $t('analysis.indicator.byNode') }}
          <span v-if="criterion.unit" class="pie-unit">({{ criterion.unit }})</span>
        </h4>
        <NodeContributionPie :contributions="nodeContributions" :unit="criterion.unit" />
      </div>
      <IndicatorReference :criterion-key="criterion.key" />
    </div>

    <!-- Camembert ecologits (eau en litres) : section distincte, unités non
         comparables à l'ACV (m³ eq) -> graphique indépendant. -->
    <div v-if="ecologitsContributions.length" class="pie-card">
      <h4>
        {{ $t('analysis.indicator.byNode') }}
        <span class="pie-unit">(L ecologits)</span>
      </h4>
      <NodeContributionPie :contributions="ecologitsContributions" unit="L ecologits" />
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
  display: inline-flex;
  align-items: center;
  color: #4a5568;
  line-height: 1.4;
  flex-shrink: 0;
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
/* Camembert nœuds + références : deux blocs côte à côte, 50/50. */
.bottom-row {
  display: flex;
  gap: 1rem;
  align-items: stretch;
}
.bottom-row > * {
  flex: 1 1 50%;
  min-width: 0;
}
@media (max-width: 700px) {
  .bottom-row {
    flex-direction: column;
  }
}
.pie-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}
.pie-card h4 {
  margin: 0 0 0.75rem;
}
.pie-unit {
  font-size: 0.75rem;
  font-weight: 400;
  color: #718096;
}
</style>


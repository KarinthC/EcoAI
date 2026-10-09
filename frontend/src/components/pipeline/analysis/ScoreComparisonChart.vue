<script setup>
// Graphique de comparaison du single score PEF : le pipeline est comparé à des
// usages de référence (avion, ciment, bœuf). Chaque barre est une barre EMPILÉE
// dont les segments sont les contributions des indicateurs : on voit ainsi que
// les problèmes ne viennent pas du même indicateur selon l'usage.
//
// DEUX MODES D'AFFICHAGE (bouton de bascule) :
//   - 'absolute' (défaut) : valeurs brutes en mPt, échelle linéaire.
//   - 'percent' : tout est normalisé en % du pipeline (pipeline = 100 %). Utile
//     quand le single score s'étend sur plusieurs ordres de grandeur : l'échelle
//     reste bornée et comparable quelle que soit la taille du pipeline.
//
// - Bouton plein écran (élargissement du graphique).
// - Tooltip détaillé par indicateur.
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePipelineStore } from '@/stores/usePipelineStore'
import { criterionLabel } from '@/components/pipeline/criterionI18n.js'
import { indicatorColor } from '@/components/pipeline/analysis/indicatorColors.js'

import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent,
])

const store = usePipelineStore()
const { t, locale } = useI18n()

// Mode d'affichage : 'absolute' (mPt, défaut) ou 'percent' (% du pipeline).
const displayMode = ref('absolute')
const isExpanded = ref(false)

function toggleMode() {
  displayMode.value = displayMode.value === 'absolute' ? 'percent' : 'absolute'
}

function toggleExpand() {
  isExpanded.value = !isExpanded.value
}

// Single score du pipeline (mPt) : sert de référence (100 %).
const pipelineScore = computed(() => store.analysisResult?.single_score || null)
const pipelineTotal = computed(() => pipelineScore.value?.single_score || 0)

// Usages de référence (avion, ciment, bœuf), avec leur single score.
const referenceUsages = computed(() => store.analysisResult?.reference_usages || [])

// Ensemble des clés d'indicateurs présentes (pour l'axe des séries empilées).
// On se base sur les contributions du pipeline ET des références.
const indicatorKeys = computed(() => {
  const keys = new Set()
  for (const c of (pipelineScore.value?.contributions || [])) {
    if ((c.score || 0) > 0) keys.add(c.key)
  }
  for (const u of referenceUsages.value) {
    for (const c of (u.contributions || [])) {
      if ((c.score || 0) > 0) keys.add(c.key)
    }
  }
  return [...keys]
})

// Libellé traduit d'un indicateur (clé technique stable + repli backend FR).
function labelFor(key) {
  const c = (pipelineScore.value?.contributions || []).find((x) => x.key === key)
  return criterionLabel(t, key, c?.label || key)
}

// Construit une ligne (un usage) : { name, map: {key: score}, total }.
// `map` porte les contributions BRUTES (mPt) ; la conversion en % est faite à
// l'affichage (cf. option), pour garder les valeurs absolues dans le tooltip.
function buildRow(name, contributions, total) {
  const map = {}
  for (const c of (contributions || [])) {
    // Une barre empilée ne peut pas porter de segment négatif : on ignore les
    // contributions négatives (ex. eau évitée) à l'affichage.
    if ((c.score || 0) > 0) map[c.key] = c.score
  }
  return { name, map, total }
}

// Résout un libellé i18n avec repli : si la clé n'existe pas (traduction
// manquante ou backend plus ancien), on affiche un libellé de secours lisible
// plutôt que la clé technique brute (ex. « analysis.reference.cement1kg »).
function resolveLabel(key, fallback) {
  if (!key) return fallback
  const translated = t(key)
  return translated === key ? fallback : translated
}

// Lignes du graphique : pipeline en premier, puis les usages de référence.
// Le pipeline est mis en avant (libellé « VOTRE PIPELINE » en majuscules).
const rows = computed(() => {
  const list = []
  if (pipelineScore.value) {
    list.push({
      ...buildRow(t('analysis.reference.pipeline'), pipelineScore.value.contributions, pipelineTotal.value),
      isPipeline: true,
    })
  }
  for (const u of referenceUsages.value) {
    // Repli : on dérive un libellé lisible depuis l'id (ex. « cement_10kg »).
    const fallback = String(u.id || '').replace(/_/g, ' ')
    list.push({
      ...buildRow(resolveLabel(u.label_i18n, fallback), u.contributions, u.single_score),
      isPipeline: false,
    })
  }
  return list
})

// Convertit une contribution brute (mPt) en % du pipeline.
function toPercent(score) {
  if (!pipelineTotal.value) return 0
  return (score / pipelineTotal.value) * 100
}

// Valeur affichée d'une contribution selon le mode courant.
function displayValue(score) {
  return displayMode.value === 'percent' ? toPercent(score) : score
}

// Plafond de l'axe en mode % : au-delà, les barres sont tronquées au bord droit
// (ce qui indique visuellement qu'elles devraient continuer).
const PERCENT_AXIS_CAP = 200

// Plus grand usage exprimé en % du pipeline.
const maxPercent = computed(() => {
  let max = 0
  for (const r of rows.value) {
    const p = toPercent(r.total)
    if (p > max) max = p
  }
  return max
})

// Borne haute de l'axe en mode % :
//   - si le max réel dépasse le plafond (200 %), on borne l'axe à 200 % ;
//   - sinon l'axe est adaptatif (arrondi au-dessus, au moins 120 % pour toujours
//     voir le repère 100 %).
const percentAxisMax = computed(() => {
  if (maxPercent.value > PERCENT_AXIS_CAP) return PERCENT_AXIS_CAP
  return Math.max(120, Math.ceil(maxPercent.value / 20) * 20)
})

// Option ECharts : barres empilées horizontales, une série par indicateur.
// Les valeurs sont brutes (mPt) ou en % du pipeline selon le mode.
const option = computed(() => {
  const keys = indicatorKeys.value
  const names = rows.value.map((r) => r.name)
  const isPercent = displayMode.value === 'percent'

  const series = keys.map((key) => ({
    name: labelFor(key),
    type: 'bar',
    stack: 'total',
    barMaxWidth: 28,
    itemStyle: { color: indicatorColor(key) },
    emphasis: { focus: 'series' },
    data: rows.value.map((r) => displayValue(r.map[key] || 0)),
  }))

  // Repère vertical à 100 % : matérialise le pipeline comme référence (mode %).
  if (isPercent && series.length) {
    series[0].markLine = {
      silent: true,
      symbol: 'none',
      lineStyle: { color: '#2d3748', type: 'dashed', width: 1.5 },
      label: {
        formatter: t('analysis.reference.pipelineMarker'),
        position: 'insideEndTop',
        fontSize: 10,
        color: '#2d3748',
      },
      data: [{ xAxis: 100 }],
    }
  }

  // Axe des valeurs : borné en %, libre (min 0) en absolu.
  const xAxis = {
    type: 'value',
    min: 0,
    name: isPercent
      ? t('analysis.reference.axisUnitPercent')
      : t('analysis.reference.axisUnitAbsolute'),
    nameLocation: 'middle',
    nameGap: 28,
    axisLabel: { formatter: (v) => (isPercent ? `${v} %` : formatValue(v)) },
  }
  if (isPercent) xAxis.max = percentAxisMax.value

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      valueFormatter: (v) => (isPercent ? formatPercent(v) : formatValue(v)),
      // Le tooltip s'affiche SOUS le curseur : au-dessus, il serait coupé par
      // les onglets / le haut du conteneur. `confine` le garde dans le canvas.
      position: (point) => [point[0], point[1] + 16],
      confine: true,
    },
    legend: {
      type: 'scroll',
      bottom: 0,
      textStyle: { fontSize: 11 },
    },
    grid: { left: 8, right: 24, top: 16, bottom: 48, containLabel: true },
    xAxis,
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: {
        fontSize: 11,
        // Met en avant la ligne du pipeline (gras + majuscules).
        formatter: (name, index) => (rows.value[index]?.isPipeline ? `{pipeline|${name}}` : name),
        rich: {
          pipeline: { fontWeight: 'bold', fontSize: 12, color: '#2d3748' },
        },
      },
    },
    series,
  }
})

// Formatage d'un pourcentage (1 décimale).
function formatPercent(v) {
  if (v === null || v === undefined) return '—'
  return `${v.toLocaleString(locale.value, { maximumFractionDigits: 1 })} %`
}

// Formatage compact d'une valeur absolue (mPt) : notation scientifique hors
// plage « lisible ».
function formatValue(v) {
  if (v === null || v === undefined) return '—'
  if (v === 0) return '0'
  const abs = Math.abs(v)
  if (abs >= 1e-3 && abs < 1e5) {
    return v.toLocaleString(locale.value, { maximumFractionDigits: 2 })
  }
  return v.toExponential(2)
}
</script>

<template>
  <div v-if="pipelineScore" class="score-chart-card" :class="{ expanded: isExpanded }">
    <div class="chart-header">
      <span class="chart-title">{{ $t('analysis.reference.chartTitle') }}</span>
      <div class="chart-actions">
        <button class="chart-btn" @click="toggleMode">
          {{ displayMode === 'percent' ? $t('analysis.reference.modeAbsolute') : $t('analysis.reference.modePercent') }}
        </button>
        <button class="chart-btn" @click="toggleExpand">
          {{ isExpanded ? $t('analysis.reference.collapse') : $t('analysis.reference.expand') }}
        </button>
      </div>
    </div>

    <VChart class="chart" :option="option" autoresize />
  </div>
</template>

<style scoped>
.score-chart-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}
/* Mode élargi : le graphique occupe toute la hauteur disponible. */
.score-chart-card.expanded {
  position: fixed;
  inset: 0;
  z-index: 1500;
  border-radius: 0;
  padding: 1.5rem;
}
.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}
.chart-title {
  font-weight: 600;
  color: #2d3748;
}
.chart-actions {
  display: flex;
  gap: 0.4rem;
}
.chart-btn {
  padding: 0.25rem 0.6rem;
  background: #edf2f7;
  color: #2d3748;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}
.chart-btn:hover {
  background: #e2e8f0;
}
.chart {
  width: 100%;
  height: 320px;
}
.score-chart-card.expanded .chart {
  height: calc(100vh - 5rem);
}
</style>

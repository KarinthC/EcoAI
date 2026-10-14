<script setup>
// Heatmap « hotspots » : une ligne par nœud, une colonne par indicateur.
//
// La valeur d'une cellule est le POURCENTAGE du seuil mensuel par habitant
// atteint par le nœud sur l'indicateur, calculé côté backend
// (node.data.threshold_ratios, mêmes conversions d'unité que le ratio global).
// L'échelle est FIXE de 0 à 100 %, du jaune clair (0 %) au rouge très foncé
// (>= 100 %, plafonné) : on repère d'un coup d'œil les nœuds/indicateurs qui
// pèsent le plus sur le budget mensuel soutenable.
//
// Deux cas distincts :
//   - 0 % (le nœud a bien un impact nul) -> jaune clair (bas de l'échelle) ;
//   - clé ABSENTE de threshold_ratios (le nœud ne remonte pas cet indicateur,
//     ex. nœud ecologits) -> cellule GRISE « pas de données ».
//
// Les nœuds sans threshold_ratios (nœuds de représentation, ex. « Données »)
// sont EXCLUS de la heatmap.
//
// ECharts est importé de façon tree-shakable (heatmap + composants utiles).
// Ce composant est chargé en import asynchrone depuis AnalysisGlobalTab.vue
// pour isoler ECharts dans un chunk séparé.
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePipelineStore } from '@/stores/usePipelineStore'
import { criterionLabel } from '@/components/pipeline/criterionI18n.js'
import { resolveNodeType, nodeTypeLabelKey } from '@/components/pipeline/nodeTypes.js'
import { CRITERIA_ORDER } from '@/components/pipeline/analysis/indicatorColors.js'

import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { HeatmapChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, VisualMapComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, HeatmapChart, GridComponent, TooltipComponent, VisualMapComponent])

const store = usePipelineStore()
const { t, locale } = useI18n()

const isExpanded = ref(false)

function toggleExpand() {
  isExpanded.value = !isExpanded.value
}

// Échelle FIXE du ratio au seuil mensuel (%) : 0 -> jaune clair, 100 -> rouge.
const HEATMAP_MAX_PERCENT = 100

// Couleur des cellules « pas de données » (clé absente de threshold_ratios).
// Gris franc, nettement distinct du jaune clair du bas de l'échelle.
const NO_DATA_COLOR = '#9aa5b1'

// Dégradé jaune clair -> rouge très foncé (bas -> haut de l'échelle).
const HEATMAP_COLORS = ['#fff7bc', '#fec44f', '#fe9929', '#d95f0e', '#67000d']

// Colonnes : tous les indicateurs, dans l'ordre stable (grille constante).
const indicatorKeys = computed(() => CRITERIA_ORDER)

// Lignes : nœuds portant un bloc threshold_ratios (les nœuds de représentation
// en sont dépourvus et sont donc exclus). Les doublons de type sont numérotés.
const rows = computed(() => {
  const typeTotals = {}
  for (const node of store.nodes) {
    const typeKey = nodeTypeLabelKey(resolveNodeType(node.data))
    const typeId = typeKey || node.data?.label || node.id
    typeTotals[typeId] = (typeTotals[typeId] || 0) + 1
  }

  const typeCounters = {}
  const list = []
  for (const node of store.nodes) {
    const ratios = node.data?.threshold_ratios
    if (!ratios) continue
    const typeKey = nodeTypeLabelKey(resolveNodeType(node.data))
    const typeId = typeKey || node.data?.label || node.id
    typeCounters[typeId] = (typeCounters[typeId] || 0) + 1
    const baseLabel = typeKey ? t(typeKey) : (node.data?.label || node.id)
    const suffix = typeTotals[typeId] > 1 ? ` ${typeCounters[typeId]}` : ''
    list.push({
      id: node.id,
      label: `${baseLabel}${suffix}`,
      ratios,
    })
  }
  return list
})

// Libellé traduit d'un indicateur (clé technique stable + repli sur la clé).
function labelFor(key) {
  return criterionLabel(t, key, key)
}

// Données de la heatmap : un objet par cellule { value: [col, row, val], ... }.
// Une clé absente -> cellule GRISE « pas de données » : on force la couleur via
// `itemStyle` (ECharts applique sinon la couleur du visualMap, ce qui rendrait
// la cellule indiscernable d'une valeur faible). Une valeur > 100 % est
// plafonnée à 100 pour rester dans l'échelle (le rouge foncé signale le
// dépassement).
const heatmapData = computed(() => {
  const data = []
  rows.value.forEach((row, rowIndex) => {
    indicatorKeys.value.forEach((key, colIndex) => {
      const raw = row.ratios[key]
      if (raw === undefined || raw === null) {
        data.push({
          value: [colIndex, rowIndex, null],
          itemStyle: { color: NO_DATA_COLOR },
        })
      } else {
        data.push([colIndex, rowIndex, Math.min(raw, HEATMAP_MAX_PERCENT)])
      }
    })
  })
  return data
})

// Option ECharts : heatmap, échelle fixe, tooltip sous le curseur.
const option = computed(() => ({
  tooltip: {
    trigger: 'item',
    // Le tooltip s'affiche SOUS le curseur pour ne pas être coupé par les
    // onglets / le haut du conteneur. `confine` le garde dans le canvas.
    position: (point) => [point[0], point[1] + 16],
    confine: true,
    formatter: (params) => {
      // Une cellule peut être un tableau [col, row, val] (valeur normale) ou un
      // objet { value: [...] } (cellule « pas de données » avec itemStyle gris).
      const cell = Array.isArray(params.data) ? params.data : params.data.value
      const row = rows.value[cell[1]]
      const key = indicatorKeys.value[cell[0]]
      const value = cell[2]
      const valueText = value === null
        ? t('analysis.heatmap.noData')
        : `${formatValue(value)} %`
      return `${row?.label || ''}<br/>${labelFor(key)} : ${valueText}`
    },
  },
  grid: { left: 8, right: 16, top: 16, bottom: 64, containLabel: true },
  xAxis: {
    type: 'category',
    data: indicatorKeys.value.map((key) => labelFor(key)),
    axisLabel: { fontSize: 10, rotate: 45, interval: 0 },
    splitArea: { show: true },
  },
  yAxis: {
    type: 'category',
    data: rows.value.map((row) => row.label),
    axisLabel: { fontSize: 11 },
    splitArea: { show: true },
  },
  visualMap: {
    min: 0,
    max: HEATMAP_MAX_PERCENT,
    calculable: false,
    orient: 'horizontal',
    left: 'center',
    bottom: 0,
    text: [t('analysis.heatmap.legend'), ''],
    textStyle: { fontSize: 10 },
    inRange: { color: HEATMAP_COLORS },
  },
  series: [
    {
      type: 'heatmap',
      data: heatmapData.value,
      label: { show: false },
      emphasis: {
        itemStyle: { borderColor: '#2d3748', borderWidth: 1.5 },
      },
      // Cellules sans données : gris « pas de données » (distinct du blanc = 0).
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 1,
      },
    },
  ],
}))

// Formatage compact d'une valeur (mPt).
function formatValue(v) {
  if (v === null || v === undefined) return '—'
  if (v === 0) return '0'
  const abs = Math.abs(v)
  if (abs >= 1e-3 && abs < 1e5) {
    return v.toLocaleString(locale.value, { maximumFractionDigits: 3 })
  }
  return v.toExponential(2)
}
</script>

<template>
  <div v-if="rows.length" class="heatmap-card" :class="{ expanded: isExpanded }">
    <div class="chart-header">
      <span class="chart-title">{{ $t('analysis.heatmap.title') }}</span>
      <div class="chart-actions">
        <button class="chart-btn" @click="toggleExpand">
          {{ isExpanded ? $t('analysis.reference.collapse') : $t('analysis.reference.expand') }}
        </button>
      </div>
    </div>
    <VChart class="heatmap" :option="option" autoresize />
  </div>
</template>

<style scoped>
.heatmap-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}
/* Mode élargi : le graphique occupe tout l'écran. */
.heatmap-card.expanded {
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
.heatmap {
  width: 100%;
  height: 360px;
}
.heatmap-card.expanded .heatmap {
  height: calc(100vh - 5rem);
}
</style>

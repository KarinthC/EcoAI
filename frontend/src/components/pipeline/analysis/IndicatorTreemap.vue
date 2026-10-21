<script setup>
// Treemap hiérarchique des contributions PEF : une COLONNE par indicateur.
//
// Chaque indicateur est une série treemap indépendante, positionnée avec une
// largeur PROPORTIONNELLE à son score PEF global (mPt) : les indicateurs qui
// pèsent le plus occupent les colonnes les plus larges. À l'intérieur d'une
// colonne, la surface de chaque tuile est proportionnelle à la contribution PEF
// du nœud à cet indicateur (node.data.pef_contributions).
//
// Le nom de l'indicateur et son score PEF global sont affichés en haut de sa
// colonne (upperLabel). Une légende ECharts (une entrée par indicateur, même
// couleur que le graphique PEF du dessus) rappelle la correspondance couleur.
//
// Les contributions nulles ou négatives (ex. eau évitée) sont EXCLUES : une
// tuile ne peut pas porter de surface négative. Les nœuds sans
// pef_contributions (nœuds de représentation, ex. « Données ») sont ignorés.
//
// ECharts est importé de façon tree-shakable (treemap + composants utiles).
// Ce composant est chargé en import asynchrone depuis AnalysisGlobalTab.vue
// pour isoler ECharts dans un chunk séparé.
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePipelineStore } from '@/stores/usePipelineStore'
import { criterionLabel } from '@/components/pipeline/criterionI18n.js'
import { resolveNodeType, nodeTypeLabelKey } from '@/components/pipeline/nodeTypes.js'
import { indicatorColor } from '@/components/pipeline/analysis/indicatorColors.js'

import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { TreemapChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, TreemapChart, TooltipComponent, LegendComponent])

// Espace (en %) laissé entre deux colonnes d'indicateurs.
const COLUMN_GAP_PERCENT = 1

const store = usePipelineStore()
const { t, locale } = useI18n()

const isExpanded = ref(false)

function toggleExpand() {
  isExpanded.value = !isExpanded.value
}

// Libellé traduit d'un indicateur (clé technique stable + repli sur la clé).
function labelFor(key) {
  return criterionLabel(t, key, key)
}

// Libellé d'un nœud (type traduit, doublons numérotés).
function nodeLabel(node, counters, totals) {
  const typeKey = nodeTypeLabelKey(resolveNodeType(node.data))
  const typeId = typeKey || node.data?.label || node.id
  counters[typeId] = (counters[typeId] || 0) + 1
  const baseLabel = typeKey ? t(typeKey) : (node.data?.label || node.id)
  const suffix = totals[typeId] > 1 ? ` ${counters[typeId]}` : ''
  return `${baseLabel}${suffix}`
}

// Colonnes : une par indicateur, avec ses tuiles (nœuds) et son score PEF
// global (somme des contributions positives des nœuds à cet indicateur).
const columns = computed(() => {
  const typeTotals = {}
  for (const node of store.nodes) {
    const typeKey = nodeTypeLabelKey(resolveNodeType(node.data))
    const typeId = typeKey || node.data?.label || node.id
    typeTotals[typeId] = (typeTotals[typeId] || 0) + 1
  }

  const counters = {}
  const byIndicator = {}
  for (const node of store.nodes) {
    const contributions = node.data?.pef_contributions
    if (!contributions) continue
    const nLabel = nodeLabel(node, counters, typeTotals)
    for (const [key, value] of Object.entries(contributions)) {
      // Une tuile ne peut pas porter de surface nulle ou négative.
      if (!(value > 0)) continue
      if (!byIndicator[key]) byIndicator[key] = { key, total: 0, children: [] }
      byIndicator[key].total += value
      byIndicator[key].children.push({ name: nLabel, value })
    }
  }

  // On ne garde que les indicateurs à score global strictement positif.
  return Object.values(byIndicator).filter((c) => c.total > 0)
})

// Option ECharts : une série treemap par indicateur, largeur ∝ score PEF global.
const option = computed(() => {
  const cols = columns.value
  const grandTotal = cols.reduce((sum, c) => sum + c.total, 0)
  // Espace total réservé aux gouttières entre colonnes.
  const totalGap = cols.length > 1 ? COLUMN_GAP_PERCENT * (cols.length - 1) : 0
  const usableWidth = 100 - totalGap

  let cursor = 0
  const series = cols.map((col) => {
    // Largeur de la colonne ∝ score PEF global de l'indicateur.
    const width = grandTotal > 0 ? (col.total / grandTotal) * usableWidth : 0
    const left = cursor
    cursor += width + COLUMN_GAP_PERCENT

    const color = indicatorColor(col.key)
    const name = labelFor(col.key)

    return {
      name,
      type: 'treemap',
      roam: false,
      nodeClick: false,
      breadcrumb: { show: false },
      // Position et largeur calculées : la colonne occupe une part de l'espace
      // proportionnelle au score PEF global de l'indicateur.
      left: `${left}%`,
      right: `${100 - (left + width)}%`,
      top: 0,
      // Laisse la place à la légende en bas (en pixels).
      bottom: 28,
      // Nom de l'indicateur + score PEF global affichés en haut de la colonne.
      upperLabel: {
        show: true,
        height: 20,
        fontSize: 11,
        fontWeight: 'bold',
        color: '#fff',
        overflow: 'truncate',
        formatter: () => `${name} · ${formatValue(col.total)} mPt`,
      },
      label: {
        show: true,
        fontSize: 10,
        color: '#fff',
        overflow: 'truncate',
        formatter: (params) => params.data?.name || '',
      },
      itemStyle: { borderColor: '#fff', borderWidth: 1, gapWidth: 1 },
      emphasis: { itemStyle: { borderColor: '#2d3748', borderWidth: 1.5 } },
      // Couleur de la colonne = couleur de l'indicateur (partagée avec les
      // autres graphiques via indicatorColors.js).
      color: [color],
      // Chaque tuile reprend la couleur de SON indicateur (une seule teinte par
      // colonne) : on force la couleur par tuile, sinon ECharts applique des
      // variations de la palette.
      data: col.children.map((child) => ({
        name: child.name,
        value: child.value,
        itemStyle: { color },
      })),
    }
  })

  return {
    tooltip: {
      trigger: 'item',
      // Le tooltip s'affiche SOUS le curseur pour ne pas être coupé par les
      // onglets / le haut du conteneur. `confine` le garde dans le canvas.
      position: (point) => [point[0], point[1] + 16],
      confine: true,
      formatter: (params) => {
        const data = params.data || {}
        const valueText = `${formatValue(data.value)} mPt`
        return `${data.name || ''}<br/>${params.seriesName} : ${valueText}`
      },
    },
    // Légende : une entrée par indicateur, même couleur que le graphique PEF.
    legend: {
      type: 'scroll',
      bottom: 0,
      textStyle: { fontSize: 11 },
      data: cols.map((col) => ({
        name: labelFor(col.key),
        itemStyle: { color: indicatorColor(col.key) },
      })),
    },
    series,
  }
})

// Formatage compact d'une valeur (mPt).
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
  <div v-if="columns.length" class="treemap-card" :class="{ expanded: isExpanded }">
    <div class="chart-header">
      <span class="chart-title">{{ $t('analysis.treemap.title') }}</span>
      <div class="chart-actions">
        <button class="chart-btn" @click="toggleExpand">
          {{ isExpanded ? $t('analysis.reference.collapse') : $t('analysis.reference.expand') }}
        </button>
      </div>
    </div>
    <VChart class="treemap" :option="option" autoresize />
  </div>
</template>

<style scoped>
.treemap-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}
/* Mode élargi : le graphique occupe tout l'écran. */
.treemap-card.expanded {
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
.treemap {
  width: 100%;
  height: 360px;
}
.treemap-card.expanded .treemap {
  height: calc(100vh - 5rem);
}
</style>

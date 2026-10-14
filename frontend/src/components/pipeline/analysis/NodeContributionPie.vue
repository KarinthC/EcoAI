<script setup>
// Camembert de contribution par nœud pour un indicateur donné.
//
// Un secteur par nœud contributeur (valeur = contribution au critère). Les
// contributions négatives (ex. eau évitée) sont EXCLUES : un camembert ne peut
// pas porter de part négative.
//
// ECharts est importé de façon tree-shakable (uniquement le camembert et les
// composants utiles). Ce composant est lui-même chargé en import asynchrone
// depuis IndicatorComparison.vue pour isoler ECharts dans un chunk séparé.
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { nodeColor } from '@/components/pipeline/analysis/nodeColors.js'

import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent])

const props = defineProps({
  // Contributions par nœud : [{ id, label, value }].
  contributions: { type: Array, default: () => [] },
  // Unité affichée dans le tooltip (ex. « kg CO₂ eq » ou « L ecologits »).
  unit: { type: String, default: '' },
})

const { t, locale } = useI18n()

// Parts positives uniquement (un camembert ne peut pas porter de part négative).
const slices = computed(() =>
  props.contributions
    .filter((n) => (n.value || 0) > 0)
    .map((n, index) => ({
      id: n.id,
      name: n.label,
      value: n.value,
      itemStyle: { color: nodeColor(index) },
    }))
)

// Option ECharts : camembert, tooltip sous le curseur, légende en bas.
const option = computed(() => ({
  tooltip: {
    trigger: 'item',
    valueFormatter: (v) => formatValue(v),
    // Le tooltip s'affiche SOUS le curseur pour ne pas être coupé par les
    // onglets / le haut du conteneur. `confine` le garde dans le canvas.
    position: (point) => [point[0], point[1] + 16],
    confine: true,
  },
  legend: {
    type: 'scroll',
    bottom: 0,
    textStyle: { fontSize: 11 },
  },
  series: [
    {
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      itemStyle: { borderColor: '#fff', borderWidth: 1 },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 12, fontWeight: 'bold' },
      },
      data: slices.value,
    },
  ],
}))

// Formatage compact d'une valeur : notation scientifique hors plage lisible.
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
  <div class="pie-block">
    <p v-if="!slices.length" class="pie-empty">
      {{ t('analysis.indicator.noContribution') }}
    </p>
    <VChart v-else class="pie-chart" :option="option" autoresize />
  </div>
</template>

<style scoped>
.pie-block {
  width: 100%;
}
.pie-chart {
  width: 100%;
  height: 280px;
}
.pie-empty {
  color: #718096;
  font-style: italic;
  margin: 0;
}
</style>

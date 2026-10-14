// Tests de NodeIndicatorHeatmap : construction des lignes (nœuds) et colonnes
// (indicateurs), échelle fixe 0-100 %, plafonnement, cellules « pas de données »
// et exclusion des nœuds sans ratios. On mocke vue-echarts (rendu Canvas non
// supporté en jsdom) et on inspecte l'option passée au composant.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { usePipelineStore } from '@/stores/usePipelineStore'
import NodeIndicatorHeatmap from '@/components/pipeline/analysis/NodeIndicatorHeatmap.vue'

// Capture la dernière option reçue par <v-chart> (à chaque mise à jour).
let lastOption = null
vi.mock('vue-echarts', () => ({
  default: {
    name: 'VChart',
    props: ['option'],
    template: '<div class="vchart-stub"></div>',
    watch: {
      option: {
        immediate: true,
        handler(val) {
          lastOption = val
        },
      },
    },
  },
}))

vi.mock('echarts/core', () => ({ use: () => {} }))
vi.mock('echarts/renderers', () => ({ CanvasRenderer: {} }))
vi.mock('echarts/charts', () => ({ HeatmapChart: {} }))
vi.mock('echarts/components', () => ({
  GridComponent: {},
  TooltipComponent: {},
  VisualMapComponent: {},
}))

vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key) => key, locale: { value: 'fr' } }),
}))

const globalMocks = { mocks: { $t: (key) => key } }

function seedStore() {
  const store = usePipelineStore()
  store.createPipeline()
  store.addNode({
    id: 'n1',
    data: {
      nodeType: 'training',
      threshold_ratios: { 'PEF-GWP': 15.0, 'PEF-ADPe': 2.0 },
    },
  })
  store.addNode({
    id: 'n2',
    data: {
      nodeType: 'llm_call',
      // Nœud ecologits : seules quelques clés sont présentes.
      threshold_ratios: { 'PEF-GWP': 150.0 },
    },
  })
  // Nœud de représentation : pas de threshold_ratios -> exclu.
  store.addNode({ id: 'n3', data: { nodeType: 'datasource' } })
  return store
}

describe('NodeIndicatorHeatmap', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    lastOption = null
  })

  it('ne rend rien sans nœud contributif', () => {
    const store = usePipelineStore()
    store.createPipeline()
    const wrapper = mount(NodeIndicatorHeatmap, { global: globalMocks })
    expect(wrapper.find('.heatmap-card').exists()).toBe(false)
  })

  it('exclut les nœuds sans threshold_ratios', () => {
    seedStore()
    const wrapper = mount(NodeIndicatorHeatmap, { global: globalMocks })
    expect(wrapper.find('.heatmap-card').exists()).toBe(true)
    // 2 nœuds avec ratios (n1, n2) ; n3 (datasource) est exclu.
    expect(lastOption.yAxis.data).toHaveLength(2)
  })

  it('affiche une colonne par indicateur (CRITERIA_ORDER)', () => {
    seedStore()
    mount(NodeIndicatorHeatmap, { global: globalMocks })
    expect(lastOption.xAxis.data).toHaveLength(15)
  })

  it('utilise une échelle fixe 0-100 %', () => {
    seedStore()
    mount(NodeIndicatorHeatmap, { global: globalMocks })
    expect(lastOption.visualMap.min).toBe(0)
    expect(lastOption.visualMap.max).toBe(100)
  })

  it('plafonne les valeurs supérieures à 100 %', () => {
    seedStore()
    mount(NodeIndicatorHeatmap, { global: globalMocks })
    // n2 / PEF-GWP = 150 % -> plafonné à 100.
    const cell = lastOption.series[0].data.find(
      (d) => d[0] === 0 && d[1] === 1
    )
    expect(cell[2]).toBe(100)
  })

  it('marque les cellules absentes comme « pas de données » (gris)', () => {
    seedStore()
    mount(NodeIndicatorHeatmap, { global: globalMocks })
    // n2 ne porte que PEF-GWP : les autres colonnes sont absentes -> cellule
    // objet { value: [col, row, null], itemStyle: { color: gris } }.
    const cell = lastOption.series[0].data.find(
      (d) => !Array.isArray(d) && d.value[1] === 1 && d.value[2] === null
    )
    expect(cell).toBeTruthy()
    expect(cell.itemStyle.color).toBe('#9aa5b1')
  })

  it('crée une série de type heatmap', () => {
    seedStore()
    mount(NodeIndicatorHeatmap, { global: globalMocks })
    expect(lastOption.series[0].type).toBe('heatmap')
  })
})

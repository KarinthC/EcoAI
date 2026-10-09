// Tests de ScoreComparisonChart : construction des lignes (pipeline + usages de
// référence) et bascule d'échelle. On mocke vue-echarts (rendu Canvas non
// supporté en jsdom) et on inspecte l'option passée au composant.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { usePipelineStore } from '@/stores/usePipelineStore'
import ScoreComparisonChart from '@/components/pipeline/analysis/ScoreComparisonChart.vue'

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
vi.mock('echarts/charts', () => ({ BarChart: {} }))
vi.mock('echarts/components', () => ({
  GridComponent: {},
  TooltipComponent: {},
  LegendComponent: {},
  MarkLineComponent: {},
}))

vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key) => key, locale: { value: 'fr' } }),
}))

const globalMocks = { mocks: { $t: (key) => key } }

function seedStore() {
  const store = usePipelineStore()
  store.analysisResult = {
    single_score: {
      single_score: 100,
      contributions: [
        { key: 'PEF-GWP', label: 'GWP', score: 80 },
        { key: 'PEF-ADPe', label: 'ADPe', score: 20 },
      ],
    },
    reference_usages: [
      {
        id: 'beef_1kg',
        label_i18n: 'analysis.reference.beef1kg',
        single_score: 500,
        contributions: [
          { key: 'PEF-GWP', label: 'GWP', score: 400 },
          { key: 'PEF-ADPe', label: 'ADPe', score: 100 },
        ],
      },
    ],
  }
  return store
}

describe('ScoreComparisonChart', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    lastOption = null
  })

  it('ne rend rien sans single score', () => {
    const wrapper = mount(ScoreComparisonChart, { global: globalMocks })
    expect(wrapper.find('.score-chart-card').exists()).toBe(false)
  })

  it('construit une ligne par usage (pipeline + références)', () => {
    seedStore()
    const wrapper = mount(ScoreComparisonChart, { global: globalMocks })
    expect(wrapper.find('.score-chart-card').exists()).toBe(true)
    // 2 catégories sur l'axe Y : pipeline + bœuf.
    expect(lastOption.yAxis.data).toHaveLength(2)
  })

  it('crée une série empilée par indicateur', () => {
    seedStore()
    mount(ScoreComparisonChart, { global: globalMocks })
    expect(lastOption.series).toHaveLength(2)
    for (const s of lastOption.series) {
      expect(s.type).toBe('bar')
      expect(s.stack).toBe('total')
    }
  })

  it('utilise une échelle linéaire absolue par défaut', () => {
    seedStore()
    mount(ScoreComparisonChart, { global: globalMocks })
    expect(lastOption.xAxis.type).toBe('value')
    expect(lastOption.xAxis.min).toBe(0)
    // Pas de borne haute en mode absolu.
    expect(lastOption.xAxis.max).toBeUndefined()
  })

  it('affiche les valeurs absolues (mPt) par défaut', () => {
    seedStore()
    mount(ScoreComparisonChart, { global: globalMocks })
    const gwp = lastOption.series.find((s) => s.name === 'GWP')
    expect(gwp.data[0]).toBeCloseTo(80, 5)
    expect(gwp.data[1]).toBeCloseTo(400, 5)
  })

  it('bascule en % du pipeline au clic sur le bouton de mode', async () => {
    seedStore()
    const wrapper = mount(ScoreComparisonChart, { global: globalMocks })
    await wrapper.find('.chart-btn').trigger('click')
    // Pipeline : GWP=80 + ADPe=20 = 100 mPt -> 100 %.
    const gwp = lastOption.series.find((s) => s.name === 'GWP')
    expect(gwp.data[0]).toBeCloseTo(80, 5)
    // Bœuf : 500 mPt pour un pipeline de 100 mPt -> 500 %.
    expect(gwp.data[1]).toBeCloseTo(400, 5)
    // Borne haute présente en mode %.
    expect(lastOption.xAxis.max).toBeGreaterThanOrEqual(120)
  })

  it('ajoute un repère vertical à 100 % en mode %', async () => {
    seedStore()
    const wrapper = mount(ScoreComparisonChart, { global: globalMocks })
    await wrapper.find('.chart-btn').trigger('click')
    expect(lastOption.series[0].markLine.data[0].xAxis).toBe(100)
  })

  it('plafonne l\'axe à 200 % quand un usage dépasse', async () => {
    seedStore()
    const wrapper = mount(ScoreComparisonChart, { global: globalMocks })
    await wrapper.find('.chart-btn').trigger('click')
    // Bœuf = 500 % > 200 % -> axe plafonné à 200 %.
    expect(lastOption.xAxis.max).toBe(200)
  })

  it('garde un axe adaptatif quand aucun usage ne dépasse 200 %', async () => {
    const store = usePipelineStore()
    store.analysisResult = {
      single_score: {
        single_score: 100,
        contributions: [{ key: 'PEF-GWP', label: 'GWP', score: 100 }],
      },
      reference_usages: [
        {
          id: 'cement_10kg',
          label_i18n: 'analysis.reference.cement10kg',
          single_score: 50,
          contributions: [{ key: 'PEF-GWP', label: 'GWP', score: 50 }],
        },
      ],
    }
    const wrapper = mount(ScoreComparisonChart, { global: globalMocks })
    await wrapper.find('.chart-btn').trigger('click')
    // Max = 100 % -> axe adaptatif (au moins 120 %).
    expect(lastOption.xAxis.max).toBe(120)
  })

  it('bascule en plein écran au clic sur le bouton d\'agrandissement', async () => {
    seedStore()
    const wrapper = mount(ScoreComparisonChart, { global: globalMocks })
    const buttons = wrapper.findAll('.chart-btn')
    await buttons[1].trigger('click')
    expect(wrapper.find('.score-chart-card').classes()).toContain('expanded')
  })
})

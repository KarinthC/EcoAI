// Tests de NodeContributionPie : construction des parts (un secteur par nœud),
// exclusion des contributions négatives et message vide. On mocke vue-echarts
// (rendu Canvas non supporté en jsdom) et on inspecte l'option passée.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import NodeContributionPie from '@/components/pipeline/analysis/NodeContributionPie.vue'

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
vi.mock('echarts/charts', () => ({ PieChart: {} }))
vi.mock('echarts/components', () => ({
  TooltipComponent: {},
  LegendComponent: {},
}))

vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key) => key, locale: { value: 'fr' } }),
}))

const globalMocks = { mocks: { $t: (key) => key } }

describe('NodeContributionPie', () => {
  beforeEach(() => {
    lastOption = null
  })

  it('crée une part par nœud contributeur', () => {
    mount(NodeContributionPie, {
      props: {
        contributions: [
          { id: 'n1', label: 'Training', value: 30 },
          { id: 'n2', label: 'Inference', value: 20 },
        ],
      },
      global: globalMocks,
    })
    expect(lastOption.series[0].type).toBe('pie')
    expect(lastOption.series[0].data).toHaveLength(2)
    expect(lastOption.series[0].data[0].name).toBe('Training')
    expect(lastOption.series[0].data[0].value).toBe(30)
  })

  it('exclut les contributions négatives (part impossible)', () => {
    mount(NodeContributionPie, {
      props: {
        contributions: [
          { id: 'n1', label: 'Training', value: 30 },
          { id: 'n2', label: 'Water saved', value: -10 },
        ],
      },
      global: globalMocks,
    })
    expect(lastOption.series[0].data).toHaveLength(1)
    expect(lastOption.series[0].data[0].name).toBe('Training')
  })

  it('associe une couleur distincte à chaque nœud', () => {
    mount(NodeContributionPie, {
      props: {
        contributions: [
          { id: 'n1', label: 'A', value: 1 },
          { id: 'n2', label: 'B', value: 1 },
        ],
      },
      global: globalMocks,
    })
    const colors = lastOption.series[0].data.map((d) => d.itemStyle.color)
    expect(colors[0]).not.toBe(colors[1])
  })

  it('affiche un message quand aucun nœud ne contribue', () => {
    const wrapper = mount(NodeContributionPie, {
      props: { contributions: [] },
      global: globalMocks,
    })
    expect(wrapper.find('.pie-empty').exists()).toBe(true)
    expect(wrapper.find('.vchart-stub').exists()).toBe(false)
  })

  it('positionne le tooltip sous le curseur (confine)', () => {
    mount(NodeContributionPie, {
      props: { contributions: [{ id: 'n1', label: 'A', value: 1 }] },
      global: globalMocks,
    })
    expect(lastOption.tooltip.confine).toBe(true)
    expect(lastOption.tooltip.position([10, 20])).toEqual([10, 36])
  })
})

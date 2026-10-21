// Tests de IndicatorTreemap : une série treemap par indicateur (colonne), avec
// une largeur proportionnelle au score PEF global de l'indicateur, et des
// tuiles (nœuds) à contribution strictement positive. On mocke vue-echarts
// (rendu Canvas non supporté en jsdom) et on inspecte l'option passée.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { usePipelineStore } from '@/stores/usePipelineStore'
import IndicatorTreemap from '@/components/pipeline/analysis/IndicatorTreemap.vue'

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
vi.mock('echarts/charts', () => ({ TreemapChart: {} }))
vi.mock('echarts/components', () => ({ TooltipComponent: {}, LegendComponent: {} }))

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
      pef_contributions: { 'PEF-GWP': 1.5, 'PEF-ADPe': 0.2 },
    },
  })
  store.addNode({
    id: 'n2',
    data: {
      nodeType: 'llm_call',
      // Contribution négative (eau évitée) : exclue.
      pef_contributions: { 'PEF-GWP': 5.0, 'PEF-WU': -2.0 },
    },
  })
  // Nœud de représentation : pas de pef_contributions -> ignoré.
  store.addNode({ id: 'n3', data: { nodeType: 'datasource' } })
  return store
}

describe('IndicatorTreemap', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    lastOption = null
  })

  it('ne rend rien sans colonne', () => {
    const store = usePipelineStore()
    store.createPipeline()
    const wrapper = mount(IndicatorTreemap, { global: globalMocks })
    expect(wrapper.find('.treemap-card').exists()).toBe(false)
  })

  it('crée une série (colonne) par indicateur présent', () => {
    seedStore()
    mount(IndicatorTreemap, { global: globalMocks })
    // PEF-GWP et PEF-ADPe ont des contributions positives -> 2 colonnes.
    expect(lastOption.series).toHaveLength(2)
    expect(lastOption.series.every((s) => s.type === 'treemap')).toBe(true)
  })

  it('regroupe les nœuds en tuiles dans la colonne de leur indicateur', () => {
    seedStore()
    mount(IndicatorTreemap, { global: globalMocks })
    const gwp = lastOption.series.find((s) => s.name === 'PEF-GWP')
    // PEF-GWP : n1 (1.5) + n2 (5.0) -> 2 tuiles.
    expect(gwp.data).toHaveLength(2)
  })

  it('exclut les contributions nulles ou négatives', () => {
    seedStore()
    mount(IndicatorTreemap, { global: globalMocks })
    const hasNegative = lastOption.series.some((s) =>
      s.data.some((d) => d.value <= 0)
    )
    expect(hasNegative).toBe(false)
  })

  it('dimensionne la largeur des colonnes selon le score PEF global', () => {
    seedStore()
    mount(IndicatorTreemap, { global: globalMocks })
    // PEF-GWP total = 6.5 ; PEF-ADPe total = 0.2 -> GWP bien plus large.
    const gwp = lastOption.series.find((s) => s.name === 'PEF-GWP')
    const adpe = lastOption.series.find((s) => s.name === 'PEF-ADPe')
    const widthOf = (s) => 100 - parseFloat(s.left) - parseFloat(s.right)
    expect(widthOf(gwp)).toBeGreaterThan(widthOf(adpe))
  })

  it('affiche le nom de l\'indicateur en haut de colonne (upperLabel)', () => {
    seedStore()
    mount(IndicatorTreemap, { global: globalMocks })
    expect(lastOption.series[0].upperLabel.show).toBe(true)
  })

  it('affiche une légende avec une entrée par indicateur', () => {
    seedStore()
    mount(IndicatorTreemap, { global: globalMocks })
    expect(lastOption.legend.data).toHaveLength(2)
    expect(lastOption.legend.data.map((d) => d.name)).toEqual(
      expect.arrayContaining(['PEF-GWP', 'PEF-ADPe'])
    )
  })

  it('colore chaque tuile avec la couleur de son indicateur', () => {
    seedStore()
    mount(IndicatorTreemap, { global: globalMocks })
    const gwp = lastOption.series.find((s) => s.name === 'PEF-GWP')
    // Toutes les tuiles d'une colonne partagent la même couleur.
    const colors = new Set(gwp.data.map((d) => d.itemStyle.color))
    expect(colors.size).toBe(1)
  })
})

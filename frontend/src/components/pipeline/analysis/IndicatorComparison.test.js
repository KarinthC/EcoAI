// Tests de IndicatorComparison : jauge vs seuil et barres par nœud.
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import IndicatorComparison from '@/components/pipeline/analysis/IndicatorComparison.vue'

vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key) => key, locale: { value: 'fr' } }),
}))

// Les templates utilisent l'injection globale `$t` : on la fournit aux montages.
const globalMocks = { mocks: { $t: (key) => key } }

const criterion = {
  key: 'PEF-GWP',
  label: 'GWP',
  unit: 'kg CO₂ eq',
  value: 50,
  threshold_monthly: 100,
  ratio: 0.5,
}

describe('IndicatorComparison', () => {
  it('affiche la valeur et le seuil', () => {
    const wrapper = mount(IndicatorComparison, {
      props: { criterion, nodeContributions: [] },
      global: globalMocks,
    })
    expect(wrapper.find('.gauge-value').text()).toContain('50')
    expect(wrapper.find('.gauge-threshold').text()).toContain('100')
  })

  it('rend une barre par nœud contributeur', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion,
        nodeContributions: [
          { id: 'n1', label: 'Training', value: 30 },
          { id: 'n2', label: 'Inference', value: 20 },
        ],
      },
      global: globalMocks,
    })
    expect(wrapper.findAll('.bar-item')).toHaveLength(2)
  })

  it('affiche un message quand aucun nœud ne contribue', () => {
    const wrapper = mount(IndicatorComparison, {
      props: { criterion, nodeContributions: [] },
      global: globalMocks,
    })
    expect(wrapper.find('.bars-empty').exists()).toBe(true)
  })

  it('n\'affiche pas de marqueur partiel pour un critère complet', () => {
    const wrapper = mount(IndicatorComparison, {
      props: { criterion, nodeContributions: [] },
      global: globalMocks,
    })
    expect(wrapper.find('.partial-mark').exists()).toBe(false)
    expect(wrapper.find('.partial-notice').exists()).toBe(false)
  })

  it('marque « + ? » et affiche le message pour un critère partiel', () => {
    const wrapper = mount(IndicatorComparison, {
      props: { criterion: { ...criterion, has_partial: true }, nodeContributions: [] },
      global: globalMocks,
    })
    expect(wrapper.find('.partial-mark').exists()).toBe(true)
    expect(wrapper.find('.partial-notice').exists()).toBe(true)
  })

  it('grise la jauge d\'un critère partiel non problématique', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, has_partial: true, ratio: 0.05 },
        nodeContributions: [],
      },
      global: globalMocks,
    })
    // PARTIAL_GRAY = #4a5568 (même règle que la Sidebar).
    expect(wrapper.find('.gauge-value').attributes('style')).toContain('rgb(74, 85, 104)')
  })

  it('n\'affiche pas de section ecologits sans contributions en litres', () => {
    const wrapper = mount(IndicatorComparison, {
      props: { criterion, nodeContributions: [] },
      global: globalMocks,
    })
    expect(wrapper.findAll('.bars-block')).toHaveLength(1)
    expect(wrapper.find('.bar-fill-ecologits').exists()).toBe(false)
  })

  it('affiche une seconde section de barres pour l\'eau ecologits (litres)', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion,
        nodeContributions: [{ id: 'n1', label: 'Training', value: 30 }],
        ecologitsContributions: [
          { id: 'n2', label: 'LLM Call', value: 1200 },
          { id: 'n3', label: 'LLM Expert', value: 800 },
        ],
      },
      global: globalMocks,
    })
    // Deux sections : ACV (unité du critère) + ecologits (litres).
    expect(wrapper.findAll('.bars-block')).toHaveLength(2)
    expect(wrapper.findAll('.bar-fill-ecologits')).toHaveLength(2)
  })
})

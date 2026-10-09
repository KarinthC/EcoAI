// Tests de IndicatorComparison : deux jauges CSS (seuil + PEF) et barres par nœud.
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
  pef_contribution: 12.5,
  pef_share: 40,
}

describe('IndicatorComparison', () => {
  it('rend deux jauges (seuil + PEF)', () => {
    const wrapper = mount(IndicatorComparison, {
      props: { criterion, nodeContributions: [] },
      global: globalMocks,
    })
    expect(wrapper.findAll('.gauge-block')).toHaveLength(2)
  })

  it('remplit la jauge de seuil selon le ratio (50 % ici)', () => {
    const wrapper = mount(IndicatorComparison, {
      props: { criterion, nodeContributions: [] },
      global: globalMocks,
    })
    const fills = wrapper.findAll('.gauge-fill')
    expect(fills[0].attributes('style')).toContain('width: 50%')
  })

  it('plafonne la jauge de seuil à 100 % en cas de dépassement', () => {
    const wrapper = mount(IndicatorComparison, {
      props: { criterion: { ...criterion, value: 250, ratio: 2.5 }, nodeContributions: [] },
      global: globalMocks,
    })
    expect(wrapper.findAll('.gauge-fill')[0].attributes('style')).toContain('width: 100%')
  })

  it('remplit la jauge PEF selon la contribution (2.5 mPt -> 50 %)', () => {
    const wrapper = mount(IndicatorComparison, {
      props: { criterion: { ...criterion, pef_contribution: 2.5 }, nodeContributions: [] },
      global: globalMocks,
    })
    expect(wrapper.findAll('.gauge-fill')[1].attributes('style')).toContain('width: 50%')
  })

  it('plafonne la jauge PEF à 100 % au-delà de 5 mPt', () => {
    const wrapper = mount(IndicatorComparison, {
      props: { criterion: { ...criterion, pef_contribution: 12.5 }, nodeContributions: [] },
      global: globalMocks,
    })
    expect(wrapper.findAll('.gauge-fill')[1].attributes('style')).toContain('width: 100%')
  })

  it('grise la jauge de seuil d\'un critère partiel non problématique', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, has_partial: true, ratio: 0.05 },
        nodeContributions: [],
      },
      global: globalMocks,
    })
    // PARTIAL_GRAY = #4a5568.
    expect(wrapper.findAll('.gauge-fill')[0].attributes('style')).toContain('rgb(74, 85, 104)')
  })

  // --- Interprétation (4 cas) ------------------------------------------------
  // Seuils : ratio >= 0.25 (25 % du seuil) et |pef_contribution| >= 1 mPt.
  function interpretationClass(wrapper) {
    const el = wrapper.find('.interpretation')
    return [...el.classes()].find((c) => c.startsWith('interpretation-'))
  }

  it('cas « les deux au-dessus »', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, ratio: 0.5, pef_contribution: 2 },
        nodeContributions: [],
      },
      global: globalMocks,
    })
    expect(interpretationClass(wrapper)).toBe('interpretation-bothAbove')
  })

  it('cas « seuil au-dessus, PEF en dessous »', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, ratio: 0.5, pef_contribution: 0.5 },
        nodeContributions: [],
      },
      global: globalMocks,
    })
    expect(interpretationClass(wrapper)).toBe('interpretation-ratioAbove')
  })

  it('cas « PEF au-dessus, seuil en dessous »', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, ratio: 0.1, pef_contribution: 2 },
        nodeContributions: [],
      },
      global: globalMocks,
    })
    expect(interpretationClass(wrapper)).toBe('interpretation-pefAbove')
  })

  it('cas « les deux en dessous »', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, ratio: 0.1, pef_contribution: 0.5 },
        nodeContributions: [],
      },
      global: globalMocks,
    })
    expect(interpretationClass(wrapper)).toBe('interpretation-bothBelow')
  })

  it('une contribution PEF négative significative compte comme « au-dessus »', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, ratio: 0.1, pef_contribution: -2 },
        nodeContributions: [],
      },
      global: globalMocks,
    })
    expect(interpretationClass(wrapper)).toBe('interpretation-pefAbove')
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


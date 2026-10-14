// Tests de IndicatorComparison : deux jauges CSS (seuil + PEF) et camembert
// de contribution par nœud (ECharts mocké : rendu Canvas non supporté en jsdom).
import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import IndicatorComparison from '@/components/pipeline/analysis/IndicatorComparison.vue'

vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key) => key, locale: { value: 'fr' } }),
}))

// NodeContributionPie est chargé en import asynchrone et embarque ECharts : on
// le mocke par un stub qui expose les contributions reçues (props), sans rendu
// Canvas (non supporté en jsdom).
// NodeContributionPie est chargé en import asynchrone et embarque ECharts : on
// le remplace par un stub global (rendu Canvas non supporté en jsdom). Le stub
// expose les contributions reçues pour les assertions.
let lastPieProps = null
const NodeContributionPieStub = {
  name: 'NodeContributionPie',
  props: ['contributions', 'unit'],
  setup(props) {
    lastPieProps = props.contributions
    return () => null
  },
}

// Les templates utilisent l'injection globale `$t` : on la fournit aux montages.
// On stubbe aussi le camembert asynchrone (ECharts).
const globalMocks = {
  mocks: { $t: (key) => key },
  stubs: { NodeContributionPie: NodeContributionPieStub },
}

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

  it('grise la jauge PEF d\'un critère partiel non significatif', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, has_partial: true, pef_contribution: 0.2 },
        nodeContributions: [],
      },
      global: globalMocks,
    })
    // PARTIAL_GRAY = #4a5568.
    expect(wrapper.findAll('.gauge-fill')[1].attributes('style')).toContain('rgb(74, 85, 104)')
  })

  it('ne grise pas la jauge PEF d\'un critère partiel déjà significatif', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, has_partial: true, pef_contribution: 2 },
        nodeContributions: [],
      },
      global: globalMocks,
    })
    expect(wrapper.findAll('.gauge-fill')[1].attributes('style')).not.toContain('rgb(74, 85, 104)')
  })

  it('affiche le marqueur « + ? » sur la jauge PEF d\'un critère partiel', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, has_partial: true, pef_contribution: 0.2 },
        nodeContributions: [],
      },
      global: globalMocks,
    })
    // Un marqueur par jauge (seuil + PEF).
    expect(wrapper.findAll('.partial-mark')).toHaveLength(2)
  })

  // --- Eau : ecologits remonte une valeur en litres --------------------------
  it('grise les jauges quand ecologits remonte une valeur (eau)', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, key: 'PEF-WU', ratio: 0.05, pef_contribution: 0.2 },
        nodeContributions: [],
        hasEcologits: true,
      },
      global: globalMocks,
    })
    // PARTIAL_GRAY = #4a5568 sur les deux jauges.
    const fills = wrapper.findAll('.gauge-fill')
    expect(fills[0].attributes('style')).toContain('rgb(74, 85, 104)')
    expect(fills[1].attributes('style')).toContain('rgb(74, 85, 104)')
  })

  it('affiche le marqueur « + ? » quand ecologits remonte une valeur (eau)', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, key: 'PEF-WU', ratio: 0.05, pef_contribution: 0.2 },
        nodeContributions: [],
        hasEcologits: true,
      },
      global: globalMocks,
    })
    expect(wrapper.findAll('.partial-mark')).toHaveLength(2)
  })

  it('masque l\'interprétation « les deux en dessous » quand ecologits remonte une valeur', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, key: 'PEF-WU', ratio: 0.05, pef_contribution: 0.2 },
        nodeContributions: [],
        hasEcologits: true,
      },
      global: globalMocks,
    })
    expect(wrapper.find('.interpretation').exists()).toBe(false)
  })

  it('ne grise pas les jauges si ecologits est significatif (eau)', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, key: 'PEF-WU', ratio: 0.5, pef_contribution: 2 },
        nodeContributions: [],
        hasEcologits: true,
      },
      global: globalMocks,
    })
    const fills = wrapper.findAll('.gauge-fill')
    expect(fills[0].attributes('style')).not.toContain('rgb(74, 85, 104)')
    expect(fills[1].attributes('style')).not.toContain('rgb(74, 85, 104)')
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

  it('masque l\'interprétation « les deux en dessous » si critère partiel', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, has_partial: true, ratio: 0.1, pef_contribution: 0.5 },
        nodeContributions: [],
      },
      global: globalMocks,
    })
    expect(wrapper.find('.interpretation').exists()).toBe(false)
  })

  it('affiche quand même l\'interprétation si critère partiel mais significatif', () => {
    const wrapper = mount(IndicatorComparison, {
      props: {
        criterion: { ...criterion, has_partial: true, ratio: 0.5, pef_contribution: 0.5 },
        nodeContributions: [],
      },
      global: globalMocks,
    })
    expect(interpretationClass(wrapper)).toBe('interpretation-ratioAbove')
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

  it('transmet les contributions par nœud au camembert', async () => {
    const contributions = [
      { id: 'n1', label: 'Training', value: 30 },
      { id: 'n2', label: 'Inference', value: 20 },
    ]
    mount(IndicatorComparison, {
      props: { criterion, nodeContributions: contributions },
      global: globalMocks,
    })
    await flushPromises()
    expect(lastPieProps).toEqual(contributions)
  })

  it('n\'affiche pas de section ecologits sans contributions en litres', async () => {
    const wrapper = mount(IndicatorComparison, {
      props: { criterion, nodeContributions: [] },
      global: globalMocks,
    })
    await flushPromises()
    expect(wrapper.findAll('.pie-card')).toHaveLength(1)
  })

  it('affiche une seconde section camembert pour l\'eau ecologits (litres)', async () => {
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
    await flushPromises()
    // Deux sections : ACV (unité du critère) + ecologits (litres).
    expect(wrapper.findAll('.pie-card')).toHaveLength(2)
  })
})


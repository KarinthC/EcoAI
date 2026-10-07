// Tests de GlobalScoreCard : affichage du single score et des contributions.
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { usePipelineStore } from '@/stores/usePipelineStore'
import GlobalScoreCard from '@/components/pipeline/analysis/GlobalScoreCard.vue'

vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key) => key, locale: { value: 'fr' } }),
}))

// Les templates utilisent l'injection globale `$t` : on la fournit aux montages.
const globalMocks = { mocks: { $t: (key) => key } }

describe('GlobalScoreCard', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('n\'affiche rien sans single_score', () => {
    const store = usePipelineStore()
    store.analysisResult = { criteria: [] }
    const wrapper = mount(GlobalScoreCard, { global: globalMocks })
    expect(wrapper.find('.score-card').exists()).toBe(false)
  })

  it('affiche la valeur du single score', () => {
    const store = usePipelineStore()
    store.analysisResult = {
      single_score: {
        single_score: 12.5,
        contributions: [
          { key: 'PEF-GWP', label: 'GWP', score: 10 },
          { key: 'PEF-ADPe', label: 'ADPe', score: 2.5 },
        ],
      },
    }
    const wrapper = mount(GlobalScoreCard, { global: globalMocks })
    expect(wrapper.find('.score-value').text()).toContain('12,5')
  })

  it('rend une sous-délimitation par contribution positive', () => {
    const store = usePipelineStore()
    store.analysisResult = {
      single_score: {
        single_score: 10,
        contributions: [
          { key: 'PEF-GWP', label: 'GWP', score: 10 },
          { key: 'PEF-ADPe', label: 'ADPe', score: 0 },
        ],
      },
    }
    const wrapper = mount(GlobalScoreCard, { global: globalMocks })
    // La contribution nulle est exclue de la barre empilée.
    expect(wrapper.findAll('.score-segment')).toHaveLength(1)
  })
})

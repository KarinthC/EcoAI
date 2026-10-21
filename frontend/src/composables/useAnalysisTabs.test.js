// Tests du composable useAnalysisTabs : dérivation des onglets et navigation.
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { usePipelineStore } from '@/stores/usePipelineStore'
import useAnalysisTabs from '@/composables/useAnalysisTabs'

// On mocke vue-i18n : `t` renvoie la clé, ce qui suffit pour vérifier la
// structure des onglets sans dépendre des traductions.
vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key) => key }),
}))

describe('useAnalysisTabs', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('expose toujours les onglets fixes global et graph', () => {
    const store = usePipelineStore()
    store.analysisResult = { criteria: [] }
    const { tabs } = useAnalysisTabs()
    const ids = tabs.value.map((t) => t.id)
    expect(ids).toEqual(['global', 'graph'])
  })

  it('ajoute un onglet par critère après les onglets fixes', () => {
    const store = usePipelineStore()
    store.analysisResult = {
      criteria: [
        { key: 'PEF-GWP', label: 'GWP' },
        { key: 'PEF-WU', label: 'Water' },
      ],
    }
    const { tabs } = useAnalysisTabs()
    const ids = tabs.value.map((t) => t.id)
    expect(ids).toEqual(['global', 'graph', 'PEF-GWP', 'PEF-WU'])
  })

  it('selectTab met à jour l\'onglet actif du store', () => {
    const store = usePipelineStore()
    store.analysisResult = { criteria: [{ key: 'PEF-GWP', label: 'GWP' }] }
    const { activeTab, selectTab } = useAnalysisTabs()
    expect(activeTab.value).toBe('global')
    selectTab('PEF-GWP')
    expect(store.activeAnalysisTab).toBe('PEF-GWP')
    expect(activeTab.value).toBe('PEF-GWP')
  })
})

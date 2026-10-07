// Tests du store : gestion de l'onglet d'analyse actif.
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { usePipelineStore } from '@/stores/usePipelineStore'

describe('usePipelineStore - onglet d\'analyse', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('démarre sur l\'onglet global', () => {
    const store = usePipelineStore()
    expect(store.activeAnalysisTab).toBe('global')
  })

  it('setAnalysisTab change l\'onglet actif', () => {
    const store = usePipelineStore()
    store.setAnalysisTab('PEF-WU')
    expect(store.activeAnalysisTab).toBe('PEF-WU')
  })

  it('clearAnalysis réinitialise l\'onglet sur global', () => {
    const store = usePipelineStore()
    store.setAnalysisTab('PEF-WU')
    store.clearAnalysis()
    expect(store.activeAnalysisTab).toBe('global')
  })
})

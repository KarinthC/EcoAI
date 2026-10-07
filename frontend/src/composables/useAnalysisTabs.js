// frontend/src/composables/useAnalysisTabs.js
//
// Dérive la liste des onglets d'analyse depuis le résultat d'analyse et gère
// l'onglet actif (état porté par le store, partagé avec la Sidebar).
//
// Onglets :
//   - 'global' : analyse globale (note single score + synthèse).
//   - 'graph'  : graphe parcourable (canevas VueFlow).
//   - <clé de critère> : un onglet par indicateur (comparatif dédié).
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePipelineStore } from '@/stores/usePipelineStore'
import { criterionLabel } from '@/components/pipeline/criterionI18n.js'

export default function useAnalysisTabs() {
  const store = usePipelineStore()
  const { t } = useI18n()

  // Onglets fixes (toujours présents en mode analyse).
  const fixedTabs = computed(() => [
    { id: 'global', label: t('analysis.tabs.global') },
    { id: 'graph', label: t('analysis.tabs.graph') },
  ])

  // Un onglet par critère, dans l'ordre stable fourni par le backend.
  const indicatorTabs = computed(() =>
    (store.analysisResult?.criteria || []).map((c) => ({
      id: c.key,
      label: criterionLabel(t, c.key, c.label),
      criterion: c,
    }))
  )

  const tabs = computed(() => [...fixedTabs.value, ...indicatorTabs.value])

  const activeTab = computed(() => store.activeAnalysisTab)

  function selectTab(tabId) {
    store.setAnalysisTab(tabId)
  }

  return {
    tabs,
    activeTab,
    selectTab,
  }
}

<script setup>
import { ref, computed } from 'vue'
import { usePipelineStore } from '@/stores/usePipelineStore'

const store = usePipelineStore()
const expanded = ref(false)

const criteria = computed(() => store.analysisResult?.criteria || [])
const globalLevel = computed(() => store.analysisResult?.global_level || 'low')

// Compte des critères au-delà du budget mensuel (ratio >= 1).
const redCount = computed(() =>
  criteria.value.filter(c => (c.ratio || 0) >= 1).length
)
</script>

<template>
  <Transition name="slide-up">
    <div
      v-if="store.analysisResult"
      class="analysis-overlay"
      :class="[{ collapsed: !expanded }, `global-${globalLevel}`]"
    >
      <div class="overlay-header" @click="expanded = !expanded">
        <span class="overlay-title">
          {{ $t('overlay.suggestions') }}
          <span class="global-badge" :class="`badge-${globalLevel}`">
            {{ $t('overlay.criteriaBeyondBudget', { count: redCount }) }}
          </span>
        </span>
        <button class="toggle-btn">{{ expanded ? '▾' : '▸' }}</button>
      </div>

      <div v-if="expanded" class="overlay-body">
        <div v-if="store.analysisResult.suggestions?.length" class="suggestions">
          <h4>{{ $t('overlay.reduceImpact') }}</h4>
          <ul>
            <li v-for="(s, idx) in store.analysisResult.suggestions" :key="idx">{{ s }}</li>
          </ul>
        </div>
        <div v-else class="suggestions-empty">
          {{ $t('overlay.noSuggestion') }}
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.analysis-overlay {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  max-height: 40vh;
  background: rgba(255,255,255,0.97);
  backdrop-filter: blur(4px);
  border-top: 4px solid #a0aec0;
  padding: 0.5rem 1rem;
  z-index: 20;
  display: flex;
  flex-direction: column;
  transition: max-height 0.3s ease, padding 0.3s ease, border-color 0.3s ease;
}
/* Couleur de bordure du bloc = niveau global (pire facteur) */
.analysis-overlay.global-low { border-top-color: #48bb78; }
.analysis-overlay.global-medium { border-top-color: #ed8936; }
.analysis-overlay.global-high { border-top-color: #e53e3e; }

.collapsed {
  max-height: 3rem;
  padding: 0.2rem 1rem;
}
.overlay-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}
.overlay-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
}
.global-badge {
  font-size: 0.8rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  color: #fff;
}
.badge-low { background: #48bb78; }
.badge-medium { background: #ed8936; }
.badge-high { background: #e53e3e; }

.toggle-btn {
  background: none; border: none;
  font-size: 1.2rem; cursor: pointer;
}
.overlay-body {
  overflow-y: auto;
  max-height: calc(40vh - 3rem);
}

.suggestions h4 { margin: 0.5rem 0; }
.suggestions ul { margin: 0; padding-left: 1.2rem; }
.suggestions-empty { color: #718096; font-style: italic; margin: 0.5rem 0; }
.slide-up-enter-active, .slide-up-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
<script setup>
import { ref } from 'vue'
import { usePipelineStore } from '@/stores/usePipelineStore'

const store = usePipelineStore()
const expanded = ref(true)
</script>

<template>
  <Transition name="slide-up">
    <div v-if="store.analysisResult" class="analysis-overlay" :class="{ collapsed: !expanded }">
      <div class="overlay-header" @click="expanded = !expanded">
        <span class="total-impact">
          🌍 Empreinte carbone totale : <strong>{{ store.analysisResult.total_impact_kg }} kgCO₂</strong>
        </span>
        <button class="toggle-btn">{{ expanded ? '▾' : '▸' }}</button>
      </div>
      <div v-if="expanded" class="overlay-body">
        <div v-if="store.analysisResult.suggestions?.length" class="suggestions">
          <h4>Suggestions pour réduire l'impact :</h4>
          <ul>
            <li v-for="(s, idx) in store.analysisResult.suggestions" :key="idx">{{ s }}</li>
          </ul>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.analysis-overlay {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  max-height: 30vh;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(4px);
  border-top: 2px solid #48bb78;
  padding: 0.5rem 1rem;
  z-index: 20;
  display: flex;
  flex-direction: column;
  transition: max-height 0.3s ease, padding 0.3s ease;
}
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
.toggle-btn {
  background: none; border: none;
  font-size: 1.2rem; cursor: pointer;
}
.overlay-body {
  overflow-y: auto;
  max-height: calc(30vh - 3rem);
}
.suggestions h4 { margin: 0.5rem 0; }
.suggestions ul { margin: 0; padding-left: 1.2rem; }
.slide-up-enter-active, .slide-up-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
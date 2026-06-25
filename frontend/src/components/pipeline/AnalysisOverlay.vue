<script setup>
import { usePipelineStore } from '@/stores/usePipelineStore'
const store = usePipelineStore()
</script>

<template>
  <Transition name="slide-up">
    <div v-if="store.analysisResult" class="analysis-overlay">
      <div class="total-impact">
        🌍 Empreinte carbone totale : <strong>{{ store.analysisResult.total_impact_kg }} kgCO₂</strong>
      </div>
      <div v-if="store.analysisResult.suggestions?.length" class="suggestions">
        <h4>Suggestions pour réduire l'impact :</h4>
        <ul>
          <li v-for="(s, idx) in store.analysisResult.suggestions" :key="idx">{{ s }}</li>
        </ul>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.analysis-overlay {
  background: white;
  border-top: 2px solid #48bb78;
  padding: 1rem;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 20;
}
.total-impact {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}
.suggestions h4 {
  margin: 0.5rem 0;
}
.suggestions ul {
  margin: 0;
  padding-left: 1.2rem;
}
.slide-up-enter-active, .slide-up-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
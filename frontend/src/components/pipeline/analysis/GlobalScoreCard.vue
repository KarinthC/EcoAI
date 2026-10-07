<script setup>
// Carte « note générale » : single score ACV brut + barre empilée montrant la
// contribution de chaque indicateur au score. Présentation pure (aucun calcul
// métier) : les valeurs proviennent de store.analysisResult.single_score.
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePipelineStore } from '@/stores/usePipelineStore'
import { criterionLabel } from '@/components/pipeline/criterionI18n.js'

const store = usePipelineStore()
const { t, locale } = useI18n()

const singleScore = computed(() => store.analysisResult?.single_score || null)

// Contributions positives uniquement (une contribution nulle n'a pas de
// largeur dans la barre empilée).
const contributions = computed(() =>
  (singleScore.value?.contributions || []).filter((c) => (c.score || 0) > 0)
)

const total = computed(() => singleScore.value?.single_score || 0)

// Part (%) d'une contribution dans le score total, pour la largeur de segment.
function share(score) {
  if (!total.value) return 0
  return (score / total.value) * 100
}

// Couleur stable par indicateur (teinte répartie sur le cercle chromatique).
function segmentColor(index, count) {
  const hue = count > 0 ? Math.round((360 / count) * index) : 0
  return `hsl(${hue}, 65%, 55%)`
}

function labelFor(c) {
  return criterionLabel(t, c.key, c.label)
}

function formatValue(v) {
  if (v === null || v === undefined) return '—'
  if (v === 0) return '0'
  const abs = Math.abs(v)
  if (abs >= 1e-3 && abs < 1e5) {
    return v.toLocaleString(locale.value, { maximumFractionDigits: 4 })
  }
  return v.toExponential(2)
}
</script>

<template>
  <div v-if="singleScore" class="score-card">
    <div class="score-header">
      <span class="score-title">{{ $t('analysis.global.singleScore') }}</span>
      <span class="score-value">{{ formatValue(total) }}</span>
    </div>

    <!-- Barre empilée : une sous-délimitation par indicateur contributif -->
    <div v-if="contributions.length" class="score-bar">
      <div
        v-for="(c, idx) in contributions"
        :key="c.key"
        class="score-segment"
        :style="{ width: share(c.score) + '%', background: segmentColor(idx, contributions.length) }"
        :title="`${labelFor(c)} : ${formatValue(c.score)}`"
      ></div>
    </div>

    <!-- Légende : contribution de chaque indicateur au single score -->
    <ul class="score-legend">
      <li v-for="(c, idx) in contributions" :key="c.key" class="legend-item">
        <span class="legend-dot" :style="{ background: segmentColor(idx, contributions.length) }"></span>
        <span class="legend-label">{{ labelFor(c) }}</span>
        <span class="legend-value">{{ formatValue(c.score) }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.score-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}
.score-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}
.score-title {
  font-weight: 600;
  color: #2d3748;
}
.score-value {
  font-size: 1.6rem;
  font-weight: 700;
  color: #2d3748;
  font-variant-numeric: tabular-nums;
}
.score-bar {
  display: flex;
  height: 18px;
  border-radius: 4px;
  overflow: hidden;
  background: #edf2f7;
}
.score-segment {
  height: 100%;
}
.score-legend {
  list-style: none;
  padding: 0;
  margin: 0.75rem 0 0;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  flex-shrink: 0;
}
.legend-label {
  flex: 1;
  color: #4a5568;
}
.legend-value {
  font-variant-numeric: tabular-nums;
  color: #2d3748;
  font-weight: 600;
}
</style>

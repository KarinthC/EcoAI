<script setup>
import useDragAndDrop from '@/composables/useDnD'
import { usePipelineStore } from '@/stores/usePipelineStore'
import { ref, computed } from 'vue'

const store = usePipelineStore()

const analyzing = ref(false)

async function toggleAnalysis() {
  if (store.isAnalyzing) {
    store.clearAnalysis()
  } else {
    analyzing.value = true
    try {
      await store.analyzePipeline()
    } finally {
      analyzing.value = false
    }
  }
}

// Info-bulle « ? » : rendue en position fixe pour éviter tout clipping par
// les conteneurs défilables (liste des critères, sidebar).
const tooltip = ref({ visible: false, x: 0, y: 0, criterion: null })

function showTooltip(event, criterion) {
  const rect = event.currentTarget.getBoundingClientRect()
  const width = 220
  // Par défaut à droite de l'icône ; bascule à gauche si ça déborde.
  let x = rect.right + 8
  if (x + width > window.innerWidth) {
    x = rect.left - width - 8
  }
  // Remonte le tooltip s'il déborde par le bas.
  let y = rect.top
  const estimatedHeight = 150
  if (y + estimatedHeight > window.innerHeight) {
    y = Math.max(8, window.innerHeight - estimatedHeight - 8)
  }
  tooltip.value = { visible: true, x, y, criterion }
}

function hideTooltip() {
  tooltip.value = { ...tooltip.value, visible: false }
}

// Colorisation de la sidebar selon le PIRE facteur (ratio le plus élevé).
const asideClass = computed(() => {
  if (!store.isAnalyzing || !store.analysisResult) return ''
  const level = store.analysisResult.global_level || 'low'
  return `sidebar-${level}`
})

// Libellé textuel correspondant au niveau global.
const globalLabel = computed(() => {
  const level = store.analysisResult?.global_level || 'low'
  if (level === 'high') return 'Impact élevé'
  if (level === 'medium') return 'Impact plutôt élevé'
  return 'Impact faible'
})

// Critères ACV affichés à égalité.
const criteria = computed(() => store.analysisResult?.criteria || [])

// Couleur d'une valeur via échelle LOGARITHMIQUE sur `ratio` (valeur/seuil).
function ratioColor(ratio) {
  if (ratio === null || ratio === undefined) return '#4a5568'
  if (ratio <= 0) return 'hsl(120, 60%, 40%)'
  const lo = Math.log10(0.01)
  const hi = Math.log10(1)
  let t = (Math.log10(ratio) - lo) / (hi - lo)
  t = Math.min(1, Math.max(0, t))
  const hue = 120 * (1 - t) // 120° (vert) -> 0° (rouge)
  return `hsl(${hue}, 75%, 42%)`
}

// Formatage compact : notation scientifique hors plage « lisible ».
function formatValue(v) {
  if (v === null || v === undefined) return '—'
  if (v === 0) return '0'
  const abs = Math.abs(v)
  if (abs >= 1e-3 && abs < 1e5) {
    return v.toLocaleString('fr-FR', { maximumFractionDigits: 4 })
  }
  return v.toExponential(2)
}

const { onDragStart } = useDragAndDrop()
</script>

<template>
  <aside :class="asideClass">
    <div class="description" v-if="!store.isAnalyzing">Glissez-déposez ces nœuds sur le canvas.</div>

    <div class="nodes" v-if="!store.isAnalyzing">
      <div
        class="sidebar-node sidebar-node-datasource"
        :draggable="true"
        @dragstart="onDragStart($event, 'custom', 'Données')"
      >
        Données
      </div>

      <div
        class="sidebar-node sidebar-node-ml"
        :draggable="true"
        @dragstart="onDragStart($event, 'custom', 'Modèle ML')"
      >
        Modèle ML
      </div>

      <div
        class="sidebar-node sidebar-node-operator"
        :draggable="true"
        @dragstart="onDragStart($event, 'custom', 'Opérateur')"
      >
        Opérateur
      </div>

      <div
        class="sidebar-node sidebar-node-operator"
        :draggable="true"
        @dragstart="onDragStart($event, 'custom', 'Préprocessing')"
      >
        Préprocessing
      </div>

      <div
        class="sidebar-node sidebar-node-operator"
        :draggable="true"
        @dragstart="onDragStart($event, 'custom', 'Entrainement')"
      >
        Entrainement
      </div>

      <div
        class="sidebar-node sidebar-node-operator"
        :draggable="true"
        @dragstart="onDragStart($event, 'custom', 'Inférence')"
      >
        Inférence
      </div>
       <div class="sidebar-node sidebar-node-operator" :draggable="true"
       @dragstart="onDragStart($event, 'custom', 'LLM Call')">
       LLM Call
      </div>
      
      <div class="sidebar-node sidebar-node-operator" :draggable="true"
      @dragstart="onDragStart($event, 'custom', 'LLM Expert')">
      LLM Expert
      </div>

       <div class="sidebar-node sidebar-node-operator" :draggable="true"
       @dragstart="onDragStart($event, 'custom', 'Video Generation')">
       Video Generation
      </div>
    </div>
    

    <div v-if="store.isAnalyzing" class="analysis-summary">
      <!-- Libellé du niveau global (couleur de fond = pire facteur) -->
      <div class="impact-level-label">{{ globalLabel }}</div>

      <!-- Liste des critères ACV, tous affichés à égalité -->
      <div class="criteria-list">
        <div
          v-for="c in criteria"
          :key="c.key"
          class="criterion-item"
          :class="{ 'is-partial': c.has_partial }"
        >
          <div class="criterion-head">
            <span class="criterion-label">{{ c.label }}</span>
            <span
              class="info-icon"
              tabindex="0"
              role="button"
              aria-label="Détail du critère"
              @mouseenter="showTooltip($event, c)"
              @mouseleave="hideTooltip"
              @focus="showTooltip($event, c)"
              @blur="hideTooltip"
            >?</span>
          </div>

          <div class="criterion-value-row">
            <span class="criterion-value" :style="{ color: ratioColor(c.ratio) }">
              {{ formatValue(c.value) }}
            </span>
            <span v-if="c.has_partial" class="partial-mark" title="Contribution partielle">+ ?</span>
            <span class="criterion-unit">{{ c.unit }}</span>
          </div>

          <!-- Eau : contribution ecologits affichée séparément (en litres).
               Unité propre (L) car non fusionnable avec l'ACV (m³ eq). -->
          <div
            v-if="c.value_ecologits !== null && c.value_ecologits !== undefined"
            class="criterion-extra"
          >
            <span class="criterion-value criterion-value-ecologits">
              + {{ formatValue(c.value_ecologits) }}
            </span>
            <span class="criterion-unit">L (ecologits)</span>
          </div>
        </div>
      </div>
    </div>

    <div class="sidebar-footer">
    <button class="analyze-btn" @click="toggleAnalysis" :disabled="analyzing">
      <span v-if="analyzing">⏳ Analyse...</span>
      <span v-else>{{ store.isAnalyzing ? '🔙 Retour à l\'édition' : '🔍 Lancer l\'analyse' }}</span>
    </button>
  </div>

    <!-- Info-bulle de critère : en position fixe pour ne jamais être clippée -->
    <Teleport to="body">
      <div
        v-if="tooltip.visible && tooltip.criterion"
        class="criterion-tooltip"
        :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
        role="tooltip"
      >
        <strong>{{ tooltip.criterion.label }}</strong>
        <span class="tooltip-desc">{{ tooltip.criterion.description }}</span>
        <span class="tooltip-line">
          Seuil mensuel / habitant :
          {{ formatValue(tooltip.criterion.threshold_monthly) }} {{ tooltip.criterion.unit }}
        </span>
        <span v-if="tooltip.criterion.has_partial" class="tooltip-partial">
          ⚠️ Contribution partielle : les nœuds ecologits ne remontent pas ce critère.
          La valeur réelle est donc plus élevée.
        </span>
      </div>
    </Teleport>
  </aside>
</template>

<style scoped>

.analyze-btn {
  width: 100%;
  padding: 0.5rem;
  background: white;
  color: #2d3748;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}
.analyze-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}


aside {
  color: #fff;
  font-weight: 700;
  border-right: 1px solid #eee;
  padding: 15px 10px;
  font-size: 12px;
  background: #10b981bf;
  box-shadow: 0 5px 10px #0000004d;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

aside .description {
  margin-bottom: 10px;
}

aside .nodes > * {
  margin-bottom: 10px;
  cursor: grab;
  font-weight: 500;
  box-shadow: 5px 5px 10px 2px #00000040;
}

.analysis-summary {
  color: white;
  padding: 0.5rem 0;
  text-align: center;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

/* Libellé du niveau global, compact pour ne pas décaler la liste */
.impact-level-label {
  font-size: 1rem;
  font-weight: 700;
  text-align: center;
  padding: 0.15rem 0 0.4rem;
  letter-spacing: 0.02em;
}

/* Liste verticale défilable des critères ACV */
.criteria-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  text-align: left;
  font-weight: 500;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 2px;
}
.criterion-item {
  background: #ffffff;
  border-radius: 6px;
  padding: 0.35rem 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}
.criterion-item.is-partial {
  border: 1px dashed #a0aec0;
}
.criterion-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.3rem;
}
.criterion-label {
  font-size: 0.75rem;
  color: #2d3748;
  line-height: 1.1;
}
.criterion-value-row {
  display: flex;
  align-items: baseline;
  gap: 0.3rem;
  margin-top: 0.1rem;
}
.criterion-value {
  font-weight: 700;
  font-size: 0.95rem;
  font-variant-numeric: tabular-nums;
}
.criterion-unit {
  font-size: 0.68rem;
  color: #4a5568;
}
.partial-mark {
  font-size: 0.95rem;
  color: #a0aec0;
  font-weight: 700;
  cursor: help;
}
.criterion-extra {
  display: flex;
  align-items: baseline;
  gap: 0.3rem;
  margin-top: 0.1rem;
}
.criterion-value-ecologits {
  /* Contribution ecologits (litres) : non comparable au seuil (m³ eq),
     donc affichée en couleur neutre, pas de code couleur d'impact. */
  color: #4a5568;
}

/* Info-bulle du critère (dans la sidebar) */
.info-icon {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 15px; height: 15px;
  border-radius: 50%;
  background: #cbd5e0;
  color: #2d3748;
  font-size: 0.68rem;
  font-weight: 700;
  cursor: help;
  flex-shrink: 0;
}

.sidebar-node {
  margin-bottom: 10px;
  cursor: grab;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 6px;
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.15);
  color: white;
}

.sidebar-node-datasource {
  background: #3182ce;
}
.sidebar-node-result {
  background: #805ad5;
}
.sidebar-node-ml {
  background: #38a169;
}
.sidebar-node-operator {
  background: #dd6b20;   
}

.sidebar-low { background: #38a169 !important; }
.sidebar-medium { background: #d69e2e !important; }
.sidebar-high { background: #e53e3e !important; }



.sidebar-footer {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid rgba(255,255,255,0.3);
}

/* En mode analyse, le bandeau de suggestions (AnalysisOverlay) se superpose en
   bas de l'écran : on réserve sa hauteur repliée pour ne pas masquer le bouton. */
aside.sidebar-low,
aside.sidebar-medium,
aside.sidebar-high {
  padding-bottom: 3.4rem;
}

@media screen and (min-width: 640px) {
  aside {
    min-width: 15%;
  }
}

@media screen and (max-width: 639px) {
  aside .nodes {
    display: flex;
    flex-direction: row;
    gap: 5px;
  }
}

</style>

<!-- Styles du tooltip téléporté hors du composant : non scoped -->
<style>
.criterion-tooltip {
  position: fixed;
  z-index: 2000;
  width: 220px;
  background: #1a202c;
  color: #fff;
  padding: 0.5rem 0.6rem;
  border-radius: 6px;
  font-size: 0.72rem;
  line-height: 1.3;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
  pointer-events: none;
}
.criterion-tooltip .tooltip-desc { color: #cbd5e0; font-weight: 400; }
.criterion-tooltip .tooltip-line { color: #f6e05e; }
.criterion-tooltip .tooltip-partial { color: #fbbf24; }
</style>
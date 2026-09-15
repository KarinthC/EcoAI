<script setup>
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { usePipelineStore } from '@/stores/usePipelineStore'
import { nodeFields } from '@/components/pipeline/nodeConfig.js'

const props = defineProps({
  id: String,
  data: Object
})

const store = usePipelineStore()

// Paramètres affichés dans l'ORDRE des champs définis (nodeFields) et avec
// leurs LIBELLÉS, afin d'éviter l'ordre arbitraire des clés de l'objet après
// un rechargement. Seuls les champs remplis sont affichés.
const orderedParams = computed(() => {
  const params = props.data?.params || {}
  const fields = nodeFields[props.data?.label] || []
  const isFilled = (v) => v !== undefined && v !== null && v !== ''

  const rows = []
  for (const f of fields) {
    if (isFilled(params[f.key])) {
      rows.push({ key: f.key, label: f.label, value: params[f.key] })
    }
  }
  // Clés présentes mais absentes de la config (sécurité) : affichage brut.
  for (const [k, v] of Object.entries(params)) {
    if (!fields.some(f => f.key === k) && isFilled(v)) {
      rows.push({ key: k, label: k, value: v })
    }
  }
  return rows
})

function handleClick() {
  store.selectNode(props.id)
}
</script>

<template>
  <div class="custom-node" @click.stop="handleClick">
    <div v-if="data.impactLevel" class="impact-badge" :class="'impact-' + data.impactLevel"></div>
    <div class="node-header">{{ data.label }}</div>
    <div class="node-body">
      <small v-if="orderedParams.length">
        <div v-for="row in orderedParams" :key="row.key" class="param-line">
          {{ row.label }}: {{ row.value }}
        </div>
      </small>
      <small v-else class="hint">Cliquer pour configurer</small>
    </div>
    <Handle type="target" :position="Position.Left" />
    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<style scoped>
.custom-node {
  position: relative;
  background: white;
  border: 2px solid #3182ce;
  border-radius: 8px;
  padding: 8px 12px;
  min-width: 120px;
  text-align: center;
  font-family: sans-serif;
}
.node-header {
  font-weight: bold;
  font-size: 0.9em;
}
.node-body {
  font-size: 0.75em;
  color: #a0aec0;
  margin-top: 4px;
}
.param-line {
  display: block;
  font-size: 0.7rem;
  color: #4a5568;
  margin: 2px 0;
}
.impact-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid white;
  z-index: 10;
}
.impact-low { background: #48bb78; }
.impact-medium { background: #f6e05e; }
.impact-high { background: #fc8181; }

</style>
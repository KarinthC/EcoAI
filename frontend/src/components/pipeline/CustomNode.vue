<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Handle, Position } from '@vue-flow/core'
import { usePipelineStore } from '@/stores/usePipelineStore'
import { nodeFields } from '@/components/pipeline/nodeConfig.js'
import { resolveNodeType, nodeTypeLabelKey } from '@/components/pipeline/nodeTypes.js'

const props = defineProps({
  id: String,
  data: Object
})

const store = usePipelineStore()
const { t } = useI18n()

// ID STABLE du type de nœud (depuis data.nodeType, ou rétro-compatibilité via
// l'ancien data.label français). Jamais traduit.
const nodeTypeId = computed(() => resolveNodeType(props.data))

// Libellé traduit affiché en en-tête du nœud.
const nodeLabel = computed(() => {
  const key = nodeTypeLabelKey(nodeTypeId.value)
  return key ? t(key) : (props.data?.label || '')
})

// Paramètres affichés dans l'ORDRE des champs définis (nodeFields), avec leurs
// LIBELLÉS résolus via i18n (clé `labelKey`). Seuls les champs remplis le sont.
const orderedParams = computed(() => {
  const params = props.data?.params || {}
  const fields = nodeFields[nodeTypeId.value] || []
  const isFilled = (v) => v !== undefined && v !== null && v !== ''

  // Valeur d'option lisible : pour un <select> à options { value, label } ou
  // { value, labelKey } (ex. sous-type d'Operator), on affiche le libellé de
  // l'option ; sinon la valeur brute.
  const displayValue = (field, value) => {
    const options = field.options || []
    const opt = options.find((o) => o && typeof o === 'object' && o.value === value)
    if (!opt) return value
    if (opt.labelKey) return t(opt.labelKey)
    return opt.label ?? value
  }

  const rows = []
  for (const f of fields) {
    if (isFilled(params[f.key])) {
      rows.push({
        key: f.key,
        label: f.labelKey ? t(f.labelKey) : f.key,
        value: displayValue(f, params[f.key]),
      })
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
    <div class="node-header">{{ nodeLabel }}</div>
    <div class="node-body">
      <small v-if="orderedParams.length">
        <div v-for="row in orderedParams" :key="row.key" class="param-line">
          {{ row.label }}: {{ row.value }}
        </div>
      </small>
      <small v-else class="hint">{{ $t('node.configure') }}</small>
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
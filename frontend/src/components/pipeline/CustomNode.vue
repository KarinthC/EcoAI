<script setup>
import { Handle, Position, useNode } from '@vue-flow/core'
import { usePipelineStore } from '@/stores/usePipelineStore'

const props = defineProps({
  id: String,
  data: Object
})

const store = usePipelineStore()

function handleClick() {
  store.selectNode(props.id)
}
</script>

<template>
  <div class="custom-node" @click.stop="handleClick">
    <div class="node-header">{{ data.label }}</div>
    <div class="node-body">
      <small v-if="data.params && Object.keys(data.params).length">
        <div v-for="(val, key) in data.params" :key="key" class="param-line">
          {{ key }}: {{ val }}
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

</style>
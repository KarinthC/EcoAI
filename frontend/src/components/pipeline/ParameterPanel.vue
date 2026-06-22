<script setup>
import { ref, watch } from 'vue'
import { usePipelineStore } from '@/stores/usePipelineStore'

const props = defineProps({
  node: Object  // le nœud sélectionné, ou null si rien n'est sélectionné
})

const emit = defineEmits(['close'])

const store = usePipelineStore()

// Formulaire local
const params = ref({})

// Quand le nœud change, initialiser le formulaire
watch(() => props.node, (newNode) => {
  if (newNode && newNode.data.params) {
    params.value = { ...newNode.data.params }
  } else {
    params.value = {}
  }
}, { immediate: true })

function save() {
  if (props.node) {
    store.updateNodeData(props.node.id, { params: { ...params.value } })
    emit('close')
  }
}

// Champs spécifiques selon le type
const fields = {
  'Données': [
    { key: 'format', label: 'Format', type: 'text', placeholder: 'CSV, JSON...' },
    { key: 'taille', label: 'Taille (Go)', type: 'number', placeholder: '2' },
    { key: 'echantillons', label: 'Échantillons', type: 'number', placeholder: '10000' }
  ],
  'Entrainement': [
    { key: 'modele', label: 'Modèle', type: 'text', placeholder: 'RNN, CNN...' },
    { key: 'parametres', label: 'Paramètres', type: 'number', placeholder: '28000' },
    { key: 'epochs', label: 'Epochs', type: 'number', placeholder: '300' },
    { key: 'batch_size', label: 'Batch size', type: 'number', placeholder: '50' }
  ],
  'Inférence': [
    { key: 'modele_utilise', label: 'Modèle utilisé', type: 'text', placeholder: 'Nom du modèle' },
    { key: 'taille_lot', label: 'Taille du lot', type: 'number', placeholder: '1000' }
  ]
}
</script>

<template>
  <div v-if="node" class="panel">
    <div class="panel-header">
      <h3>{{ node.data.label }}</h3>
      <button class="close-btn" @click="emit('close')">✕</button>
    </div>

    <div class="panel-body">
      <div v-for="field in fields[node.data.label]" :key="field.key" class="field">
        <label>{{ field.label }}</label>
        <input
          :type="field.type"
          v-model="params[field.key]"
          :placeholder="field.placeholder"
        />
      </div>
    </div>

    <div class="panel-footer">
      <button class="btn-save" @click="save">💾 Appliquer</button>
      <button class="btn-delete" @click="store.removeNode(node.id); emit('close')">🗑️ Supprimer</button>
    </div>
  </div>
</template>

<style scoped>
.panel {
  width: 280px;
  background: white;
  border-left: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
}
.panel-header h3 {
  margin: 0;
  font-size: 1rem;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
}
.panel-body {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}
.field {
  margin-bottom: 1rem;
}
.field label {
  display: block;
  font-size: 0.8rem;
  color: #4a5568;
  margin-bottom: 0.25rem;
}
.field input {
  width: 100%;
  padding: 0.4rem;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  font-size: 0.9rem;
}
.panel-footer {
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  gap: 0.5rem;
}
.btn-save {
  flex: 1;
  padding: 0.5rem;
  background: #3182ce;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.btn-delete {
  padding: 0.5rem;
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
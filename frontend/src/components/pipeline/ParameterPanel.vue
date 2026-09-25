<script setup>
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePipelineStore } from '@/stores/usePipelineStore'
import { nodeFields, VIDEO_MODELS } from '@/components/pipeline/nodeConfig.js'
import { resolveNodeType, nodeTypeLabelKey } from '@/components/pipeline/nodeTypes.js'

const props = defineProps({
  node: Object
})

const emit = defineEmits(['close'])
const store = usePipelineStore()
const { t } = useI18n()

// ID STABLE du type de nœud (avec rétro-compatibilité des anciens graphes).
const nodeTypeId = computed(() => resolveNodeType(props.node?.data))

// Champs de config du nœud courant.
const fields = computed(() => nodeFields[nodeTypeId.value] || [])

// Sous-types d'Operator dont les champs sont de type « calcul local » (ACV).
const LOCAL_SUBTYPES = ['preprocessing', 'data_transformation', 'training', 'inference_local']
// Sous-types d'Operator dont les champs sont de type « appel API » (ecologits).
const API_SUBTYPES = ['inference_api', 'llm_call']
// Sous-types d'Operator dont les champs sont de type « génération vidéo ».
const VIDEO_SUBTYPES = ['video_generation']

// Clés des champs propres à chaque famille de sous-type d'Operator.
const LOCAL_FIELD_KEYS = ['eco:serverId', 'eco:gpuModel', 'eco:gpuCount', 'eco:executionTimeSec', 'eco:gpuUtilization']
const API_FIELD_KEYS = ['eco:provider', 'eco:modelName', 'eco:callCount', 'eco:outputTokens', 'eco:requestLatency']
const VIDEO_FIELD_KEYS = ['eco:modelName', 'eco:callCount', 'eco:resolution', 'eco:duration', 'eco:withAudio']

// Médias de stockage portant un impact (le serveur de stockage n'a de sens
// que pour ceux-là : LIG SUMMER est un parc HDD/SSD).
const IMPACTFUL_MEDIUMS = ['ssd', 'hdd']

// Champs réellement affichés : affichage conditionnel selon le type de nœud.
const visibleFields = computed(() => {
  // Nœud Data : le serveur de stockage n'apparaît que pour SSD/HDD.
  if (nodeTypeId.value === 'data') {
    const medium = params.value['eco:storageMedium']
    return fields.value.filter(
      (f) => f.key !== 'eco:storageServer' || IMPACTFUL_MEDIUMS.includes(medium)
    )
  }

  if (nodeTypeId.value !== 'operator') return fields.value

  const subtype = params.value.subtype
  if (!subtype) {
    // Tant qu'aucun sous-type n'est choisi, on n'affiche que le sélecteur.
    return fields.value.filter((f) => f.key === 'subtype')
  }
  let allowed
  if (LOCAL_SUBTYPES.includes(subtype)) allowed = LOCAL_FIELD_KEYS
  else if (API_SUBTYPES.includes(subtype)) allowed = API_FIELD_KEYS
  else if (VIDEO_SUBTYPES.includes(subtype)) allowed = VIDEO_FIELD_KEYS
  else allowed = []
  return fields.value.filter((f) => f.key === 'subtype' || allowed.includes(f.key))
})

// Libellé traduit du nœud (en-tête du panneau).
const nodeLabel = computed(() => {
  const key = nodeTypeLabelKey(nodeTypeId.value)
  return key ? t(key) : (props.node?.data?.label || '')
})

// Formulaire local
const params = ref({})

// Initialisation des paramètres quand le nœud change
watch(() => props.node, (newNode) => {
  if (newNode && newNode.data && newNode.data.params) {
    params.value = { ...newNode.data.params }
  } else {
    params.value = {}
  }
}, { immediate: true })

// Réinitialiser la valeur du champ dépendant si le parent change
watch(params, (newParams, oldParams) => {
  if (!props.node) return
  // Changement de sous-type d'Operator : les listes de modèles diffèrent
  // (LLM vs vidéo), on vide le modèle pour éviter une valeur incohérente.
  if (newParams.subtype !== oldParams?.subtype) {
    params.value['eco:modelName'] = ''
  }
  // Changement de média de stockage : le serveur ne concerne que SSD/HDD.
  if (newParams['eco:storageMedium'] !== oldParams?.['eco:storageMedium']
      && !IMPACTFUL_MEDIUMS.includes(newParams['eco:storageMedium'])) {
    params.value['eco:storageServer'] = ''
  }
  for (const field of fields.value) {
    if (field.dependsOn && newParams[field.dependsOn] !== oldParams?.[field.dependsOn]) {
      const validOptions = field.optionsMapping?.[newParams[field.dependsOn]] || []
      if (!validOptions.includes(newParams[field.key])) {
        params.value[field.key] = ''
      }
    }
  }
}, { deep: true })

// Un champ dépendant est désactivé tant que son parent n'est pas renseigné.
// Exception : le modèle d'un Operator vidéo n'a pas de parent (liste dédiée).
function isFieldDisabled(field) {
  if (field.key === 'eco:modelName' && VIDEO_SUBTYPES.includes(params.value.subtype)) {
    return false
  }
  return Boolean(field.dependsOn) && !params.value[field.dependsOn]
}

function getFieldOptions(field) {
  // Cas particulier : le champ modèle d'un Operator vidéo utilise une liste
  // dédiée (pas de dépendance à un fournisseur).
  if (field.key === 'eco:modelName' && VIDEO_SUBTYPES.includes(params.value.subtype)) {
    return VIDEO_MODELS
  }
  if (field.dependsOn && field.optionsMapping) {
    const parentValue = params.value[field.dependsOn]
    return field.optionsMapping[parentValue] || []
  }
  if (field.options) {
    return field.options
  }
  return []
}

// Une option peut être soit une simple chaîne, soit un objet { value, label }.
// On normalise ici pour que le rendu du <select> gère les deux formats.
function optOptionValue(opt) {
  return opt && typeof opt === 'object' ? opt.value : opt
}

function optOptionLabel(opt) {
  if (opt && typeof opt === 'object') {
    // Options i18n : { value, labelKey } -> libellé traduit.
    if (opt.labelKey) return t(opt.labelKey)
    return opt.label
  }
  return opt
}

// Sauvegarde les paramètres
function save() {
  if (props.node) {
    store.updateNodeData(props.node.id, { params: { ...params.value } })
    emit('close')
  }
}
</script>

<template>
  <div v-if="node" class="panel">
    <div class="panel-header">
      <h3>{{ nodeLabel }}</h3>
      <button class="close-btn" @click="emit('close')">✕</button>
    </div>

    <div class="panel-body">
      <div v-for="field in visibleFields" :key="field.key" class="field">
        <label>{{ field.labelKey ? $t(field.labelKey) : field.key }}</label>

        <!-- Menu déroulant si type === 'select' -->
        <select
          v-if="field.type === 'select'"
          v-model="params[field.key]"
          class="field-select"
          :disabled="isFieldDisabled(field)"
        >
          <option value="" disabled selected v-if="!params[field.key]">
            {{ $t('panel.choose') }}
          </option>
          <option
            v-for="opt in getFieldOptions(field)"
            :key="optOptionValue(opt)"
            :value="optOptionValue(opt)"
          >{{ optOptionLabel(opt) }}</option>
        </select>

        <!-- Sinon, champ texte/nombre -->
        <input
          v-else
          :type="field.type"
          v-model="params[field.key]"
          :placeholder="field.placeholder"
        />
      </div>
    </div>

    <div class="panel-footer">
      <button class="btn-save" @click="save">{{ $t('panel.apply') }}</button>
      <button class="btn-delete" @click="store.removeNode(node.id); emit('close')">{{ $t('panel.delete') }}</button>
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
.field select.field-select {
  width: 100%;
  padding: 0.4rem;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  font-size: 0.9rem;
  background: white;
  /* Couleur de texte explicite : sans elle, le select hérite d'une couleur
     claire (contexte sombre) et devient blanc sur blanc. */
  color: #2d3748;
  cursor: pointer;
}
/* Les <option> ne suivent pas toujours la couleur du <select> selon le
   navigateur/OS : on force la couleur et le fond pour garantir la lisibilité. */
.field select.field-select option {
  color: #2d3748;
  background: white;
}
.field select.field-select:focus {
  outline: none;
  border-color: #3182ce;
  box-shadow: 0 0 0 2px rgba(49, 130, 206, 0.2);
}
</style>
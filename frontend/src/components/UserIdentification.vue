<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import UsernameModal from './UsernameModal.vue'

const status = ref('loading')  // 'loading' | 'online' | 'error'
const username = ref(null)

async function checkConnection() {
  try {
    const response = await axios.get('/api/session')
    username.value = response.data.username
    status.value = 'online'
  } catch {
    status.value = 'error'
  }
}

function onUsernameSet(name) {
  username.value = name
}

onMounted(() => checkConnection())
</script>

<template>
  <div
    class="indicator"
    :title="
      status === 'online' && username
        ? `Connecté en tant que ${username}`
        : status === 'online'
          ? 'Anonyme - Cliquez pour choisir un nom'
          : status === 'error'
            ? 'Serveur inaccessible'
            : 'Connexion en cours...'
    "
  >
    <span v-if="status === 'online' && username" class="username">
      {{ username }}
    </span>
    <span v-else-if="status === 'online'" class="anonymous" @click="showModal = true">
      Anonyme
    </span>
    <span v-else-if="status === 'loading'" class="label">Connexion...</span>
    <span v-else class="label">Hors ligne</span>
  </div>

  <!-- La modale s'affiche si l'utilisateur est en ligne mais sans nom -->
  <UsernameModal
    v-if="status === 'online' && !username"
    @username-set="onUsernameSet"
  />
</template>

<style scoped>
.indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: #e2e8f0;
  padding: 4px 10px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
}
.username {
  color: white;
  font-weight: 500;
}

.anonymous {
  color: #a0aec0;
  font-style: italic;
  cursor: pointer;
  border-bottom: 1px dashed #718096;
}

.anonymous:hover {
  color: #e2e8f0;
}

.label {
  color: #a0aec0;
}
</style>
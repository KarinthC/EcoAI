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
  gap: 8px;
  position: fixed;
  top: 3.5rem;  /* décalé pour laisser la place au ConnectionIndicator */
  right: 1rem;
  font-size: 0.85rem;
  color: #555;
  background: white;
  padding: 6px 12px;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.username {
  color: #2d3748;
  font-weight: 500;
}

.anonymous {
  color: #a0aec0;
  font-style: italic;
  cursor: pointer;
  border-bottom: 1px dashed #cbd5e0;
}

.anonymous:hover {
  color: #4a5568;
}

.label {
  color: #718096;
}
</style>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const status = ref('loading')  // 'loading' | 'online' | 'error'
const sessionInfo = ref(null)

async function checkConnection() {
  try {
    const response = await axios.get('/api/session')
    sessionInfo.value = response.data
    status.value = 'online'
  } catch {
    status.value = 'error'
  }
}

onMounted(() => checkConnection())
</script>

<template>
  <div
    class="indicator"
    :title="
      status === 'online'
        ? 'Session active'
        : status === 'error'
          ? 'Serveur inaccessible'
          : 'Connexion en cours...'
    "
  >
    <span class="dot" :class="status"></span>
    <span v-if="sessionInfo" class="user-id">
      Utilisateur #{{ sessionInfo.user_id }}
    </span>
    <span v-else-if="status === 'loading'" class="label">Connexion...</span>
    <span v-else class="label">Hors ligne</span>
  </div>
</template>

<style scoped>
.indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  position: fixed;
  top: 1rem;
  right: 1rem;
  font-size: 0.85rem;
  color: #555;
  background: white;
  padding: 6px 12px;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #a0aec0;  /* gris = loading */
  flex-shrink: 0;
}

.dot.online {
  background: #48bb78;  /* vert */
}

.dot.error {
  background: #f56565;  /* rouge */
}

.label {
  color: #718096;
}

.user-id {
  color: #2d3748;
  font-weight: 500;
}
</style>
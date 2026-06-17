<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const status = ref('loading')  // 'loading' | 'online' | 'error'

async function checkConnection() {
  try {
    await axios.get('/api/health')
    status.value = 'online'
  } catch {
    status.value = 'error'
  }
}

onMounted(() => checkConnection())
</script>

<template>
  <div class="indicator" :title="status === 'online' ? 'Connecté' : status === 'error' ? 'Erreur serveur' : 'Vérification...'">
    <span class="dot" :class="status"></span>
    <span class="label">API</span>
  </div>
</template>

<style scoped>
.indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  position: fixed;
  top: 1rem;
  right: 1rem;
  font-size: 0.85rem;
  color: #555;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #a0aec0;  /* gris = loading */
}

.dot.online {
  background: #48bb78;  /* vert */
}

.dot.error {
  background: #f56565;  /* rouge */
}
</style>
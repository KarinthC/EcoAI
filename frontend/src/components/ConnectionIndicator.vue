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
  font-size: 0.8rem;
  color: #a0aec0;
  padding: 4px 10px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.15);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #a0aec0;
  flex-shrink: 0;
}

.dot.online {
  background: #48bb78;
}

.dot.error {
  background: #f56565;
}

.label {
  color: #e2e8f0;
}
</style>
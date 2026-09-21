<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()
const status = ref('loading')  // 'loading' | 'online' | 'error'

const statusTitle = computed(() => {
  if (status.value === 'online') return t('connection.connected')
  if (status.value === 'error') return t('connection.serverError')
  return t('connection.checking')
})

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
  <div class="indicator" :title="statusTitle">
    <span class="dot" :class="status"></span>
    <span class="label">{{ $t('connection.api') }}</span>
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
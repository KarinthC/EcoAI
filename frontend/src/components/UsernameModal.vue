<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()
const emit = defineEmits(['username-set'])

const username = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.post('/api/username', { username: username.value })
    emit('username-set', response.data.username)
  } catch (e) {
    if (e.response && e.response.data.error) {
      error.value = e.response.data.error
    } else {
      error.value = t('username.networkError')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="modal-overlay">
    <div class="modal">
      <h2>{{ $t('username.welcome') }}</h2>
      <p>{{ $t('username.chooseName') }}</p>
      <form @submit.prevent="submit">
        <input
          v-model="username"
          type="text"
          :placeholder="$t('username.placeholder')"
          minlength="2"
          maxlength="50"
          required
          :disabled="loading"
        />
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">
          {{ loading ? $t('username.saving') : $t('username.submit') }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: white;
  color: #2d3748; 
  padding: 2rem;
  border-radius: 8px;
  text-align: center;
  max-width: 400px;
  width: 90%;
}
input {
  width: 100%;
  padding: 0.5rem;
  margin: 0.5rem 0;
}
button {
  padding: 0.5rem 1.5rem;
  cursor: pointer;
}
.error {
  color: #e53e3e;
  font-size: 0.85rem;
}
</style>
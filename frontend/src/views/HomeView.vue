<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// États réactifs
const apiStatus = ref('Chargement...')
const isLoading = ref(true)
const error = ref(null)

// Fonction pour récupérer l'état de l'API
async function checkHealth() {
  try {
    const response = await axios.get('/api/health')
    apiStatus.value = response.data.status
  } catch (e) {
    error.value = 'Impossible de contacter le serveur.'
    apiStatus.value = 'Erreur'
  } finally {
    isLoading.value = false
  }
}

// Appel au montage du composant
onMounted(() => {
  checkHealth()
})
</script>

<template>
  <div class="home">
    <h1>Estimation Carbone</h1>
    
    <!-- État de chargement -->
    <div v-if="isLoading" class="status loading">
      Connexion au serveur...
    </div>

    <!-- État d'erreur -->
    <div v-else-if="error" class="status error">
      {{ error }}
    </div>

    <!-- État succès -->
    <div v-else class="status success">
      API connectée – Statut : {{ apiStatus }}
    </div>
  </div>
</template>

<style scoped>
.home {
  max-width: 600px;
  margin: 2rem auto;
  text-align: center;
  font-family: sans-serif;
}

.status {
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.loading {
  background: #e2e8f0;
  color: #333;
}

.error {
  background: #fed7d7;
  color: #c53030;
}

.success {
  background: #c6f6d5;
  color: #276749;
}
</style>
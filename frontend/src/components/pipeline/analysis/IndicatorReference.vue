<script setup>
// Encart « Références fondatrices » d'un indicateur : liste de liens vers les
// articles / rapports de référence du domaine (cf. indicatorReferences.js).
// Présentation pure : la clé du critère est passée en prop par l'onglet.
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { indicatorReferences } from '@/components/pipeline/analysis/indicatorReferences.js'

const props = defineProps({
  // Clé technique stable du critère (ex. « PEF-GWP »).
  criterionKey: { type: String, required: true },
})

const { t } = useI18n()

// Références du critère (tableau vide si aucune -> encart masqué).
const references = computed(() => indicatorReferences(props.criterionKey))

// Résolution du libellé i18n avec repli : si la clé est absente, on affiche la
// clé brute plutôt qu'un libellé vide (robustesse si une source est ajoutée
// avant sa traduction).
function sourceLabel(sourceKey) {
  const translated = t(sourceKey)
  return translated === sourceKey ? sourceKey : translated
}
</script>

<template>
  <div v-if="references.length" class="reference-card">
    <h4>{{ $t('analysis.reference.title') }}</h4>
    <ul class="reference-list">
      <li v-for="ref in references" :key="ref.url" class="reference-item">
        <span class="reference-icon" aria-hidden="true">
          <!-- Icône Lucide « book-open » (licence ISC). -->
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none"
               stroke="currentColor" stroke-width="2"
               stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 7v14" />
            <path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z" />
          </svg>
        </span>
        <a
          class="reference-link"
          :href="ref.url"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ sourceLabel(ref.sourceKey) }}
        </a>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.reference-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}
.reference-card h4 {
  margin: 0 0 0.75rem;
}
.reference-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.reference-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}
.reference-icon {
  display: inline-flex;
  align-items: center;
  color: #4a5568;
  flex-shrink: 0;
  margin-top: 0.1rem;
}
.reference-link {
  font-size: 0.8rem;
  color: #2b6cb0;
  text-decoration: none;
  line-height: 1.4;
}
.reference-link:hover {
  text-decoration: underline;
}
</style>

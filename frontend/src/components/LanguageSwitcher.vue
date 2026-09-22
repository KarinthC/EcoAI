<script setup>
import { computed } from 'vue'
import i18n, { setLocale, SUPPORTED_LOCALES } from '@/i18n'

// On lit la ref de locale GLOBALE directement depuis l'instance i18n de l'app.
// C'est la même ref que celle utilisée par $t : le rendu est donc garanti
// réactif au changement, sans dépendre du scope retourné par useI18n().
const locale = computed(() => i18n.global.locale.value)

// Code court affiché sur le bouton (FR / EN) + libellé complet natif, utilisé
// pour l'accessibilité et l'infobulle. On évite volontairement les drapeaux :
// un drapeau désigne un pays, pas une langue (ambigu, non conventionnel).
const LANGUAGES = {
  fr: { short: 'FR', full: 'Français' },
  en: { short: 'EN', full: 'English' },
}

const options = computed(() =>
  SUPPORTED_LOCALES.map((code) => ({
    code,
    short: LANGUAGES[code]?.short || code.toUpperCase(),
    full: LANGUAGES[code]?.full || code.toUpperCase(),
  }))
)

function select(code) {
  if (code !== locale.value) setLocale(code)
}
</script>

<template>
  <div
    class="lang-switcher"
    role="group"
      :aria-label="$t('language.label')"
    >
    <button
      v-for="opt in options"
      :key="opt.code"
      type="button"
      class="lang-btn"
      :class="{ active: opt.code === locale }"
      :title="opt.full"
      :aria-pressed="opt.code === locale"
      @click="select(opt.code)"
    >
      {{ opt.short }}
    </button>
  </div>
</template>

<style scoped>
.lang-switcher {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 3px;
  border-radius: 8px;
  /* Rail légèrement creusé sur le fond sombre de l'en-tête. */
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.lang-btn {
  appearance: none;
  border: 1px solid transparent;
  background: transparent;
  color: #a0aec0;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  line-height: 1;
  padding: 5px 9px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease,
    box-shadow 0.15s ease, border-color 0.15s ease;
}
.lang-btn:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.08);
}

.lang-btn:focus-visible {
  outline: none;
  border-color: #63b3ed;
  box-shadow: 0 0 0 2px rgba(99, 179, 237, 0.4);
}

/* Option active : mise en relief (fond clair, ombre portée, texte foncé) et
   bordure d'accent pour bien marquer la sélection. */
.lang-btn.active {
  color: #1a202c;
  background: #ffffff;
  border-color: #63b3ed;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(99, 179, 237, 0.5);
  cursor: default;
}

.lang-btn.active:hover {
  background: #ffffff;
}
</style>


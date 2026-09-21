// frontend/src/i18n/index.js
// Configuration i18n (vue-i18n v9, Composition API).
//
// Langue par défaut : français. Langue de secours : français.
// La langue initiale est détectée depuis le localStorage (choix explicite de
// l'utilisateur) puis, à défaut, depuis la langue du navigateur.
import { createI18n } from 'vue-i18n'
import fr from './locales/fr.json'
import en from './locales/en.json'

export const SUPPORTED_LOCALES = ['fr', 'en']
const DEFAULT_LOCALE = 'fr'
const STORAGE_KEY = 'ecoai-locale'

// Détecte la langue initiale : préférence sauvegardée > navigateur > défaut.
function detectLocale() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved && SUPPORTED_LOCALES.includes(saved)) return saved
  } catch {
    /* localStorage indisponible (SSR / mode privé) : on ignore. */
  }
  const browser = (navigator.language || '').slice(0, 2).toLowerCase()
  return SUPPORTED_LOCALES.includes(browser) ? browser : DEFAULT_LOCALE
}

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: detectLocale(),
  fallbackLocale: DEFAULT_LOCALE,
  messages: { fr, en },
})

// Change la langue active et la persiste.
export function setLocale(locale) {
  if (!SUPPORTED_LOCALES.includes(locale)) return
  i18n.global.locale.value = locale
  document.documentElement.setAttribute('lang', locale)
  try {
    localStorage.setItem(STORAGE_KEY, locale)
  } catch {
    /* ignore */
  }
}

export default i18n

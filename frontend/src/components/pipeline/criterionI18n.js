// frontend/src/components/pipeline/criterionI18n.js
//
// Traduction des critères ACV (PEF) exposés par le backend.
//
// Le backend envoie, pour chaque critère, une `key` TECHNIQUE STABLE
// (ex. « PEF-GWP ») ainsi qu'un `label` et une `description` en FRANÇAIS.
// On résout ici le libellé / l'explication dans la langue active à partir de
// la clé, avec repli sur la valeur fournie par le backend si la clé est
// inconnue (robustesse si le backend ajoute un critère avant le front).
//
// Les clés de traduction vivent sous « criteria.<KEY>.label|description ».

/** Clé i18n d'un critère, ou null si la clé est absente. */
export function criterionLabelKey(key) {
  return key ? `criteria.${key}.label` : null
}

/** Clé i18n de la description d'un critère, ou null si la clé est absente. */
export function criterionDescriptionKey(key) {
  return key ? `criteria.${key}.description` : null
}

/**
 * Résout le libellé traduit d'un critère.
 * @param {Function} t         fonction de traduction vue-i18n
 * @param {string}   key       clé technique stable (ex. « PEF-GWP »)
 * @param {string}   fallback  libellé backend (français), repli
 */
export function criterionLabel(t, key, fallback = '') {
  const k = criterionLabelKey(key)
  if (!k) return fallback
  const translated = t(k)
  // vue-i18n renvoie la clé elle-même si absente : on préfère alors le repli.
  return translated === k ? fallback : translated
}

/**
 * Résout l'explication (info-bulle) traduite d'un critère.
 * @param {Function} t         fonction de traduction vue-i18n
 * @param {string}   key       clé technique stable (ex. « PEF-GWP »)
 * @param {string}   fallback  description backend (français), repli
 */
export function criterionDescription(t, key, fallback = '') {
  const k = criterionDescriptionKey(key)
  if (!k) return fallback
  const translated = t(k)
  return translated === k ? fallback : translated
}

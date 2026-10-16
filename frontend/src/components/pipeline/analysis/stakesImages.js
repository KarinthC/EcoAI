// frontend/src/components/pipeline/analysis/stakesImages.js
//
// Images d'illustration par critère PEF, affichées en dégradé dans le coin
// inférieur droit de l'encart « Enjeux » (cf. StakesCard.vue).
//
// Les images vivent dans `src/assets/stakes/` et sont importées ici : Vite les
// bundle et les hashe automatiquement (cache-busting).
//
// Un critère peut porter PLUSIEURS images (tableau) : la première est affichée
// par défaut, les suivantes sont prévues pour un futur fondu enchaîné. Un
// critère absent du mapping n'affiche aucune image (repli silencieux).
//
// Chaque image est décrite par un objet { src, position } :
//   - src      : URL de l'image (import Vite) ;
//   - position : valeur CSS `object-position` (cadrage), pour choisir la zone
//                visible (ex. « top right » pour montrer le haut de l'image).
//                Défaut : « center ».

import climateImg from '@/assets/stakes/a-man-carries-his-cat-across-a-flooded-road-in-wellampitiya-on-the-outskirts-of-colombo-on.webp'

const STAKES_IMAGES = {
  'PEF-GWP': [{ src: climateImg, position: 'top' }],
}

/**
 * Images d'illustration d'un critère PEF.
 * @param {string} key  clé technique stable (ex. « PEF-GWP »)
 * @returns {{src: string, position: string}[]} tableau d'images (vide si aucune)
 */
export function stakesImages(key) {
  return STAKES_IMAGES[key] || []
}

/**
 * Image principale d'un critère PEF (première du tableau).
 * @param {string} key  clé technique stable (ex. « PEF-GWP »)
 * @returns {{src: string, position: string}|null} image, ou null si aucune
 */
export function stakesImage(key) {
  return stakesImages(key)[0] || null
}

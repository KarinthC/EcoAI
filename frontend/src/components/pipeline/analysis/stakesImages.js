// frontend/src/components/pipeline/analysis/stakesImages.js
//
// Image d'illustration par critère PEF, affichée en dégradé dans le coin
// inférieur droit de l'encart « Enjeux » (cf. StakesCard.vue).
//
// Les images vivent dans `src/assets/stakes/` et sont importées ici : Vite les
// bundle et les hashe automatiquement (cache-busting).
//
// Chaque image est décrite par un objet { src, focal, focalWide, zoom } :
//   - src       : URL de l'image (import Vite) ;
//   - focal     : point focal en PIXELS de l'image source { x, y }, utilisé en
//                 mode normal (petite fenêtre). L'image doit être composée pour
//                 que le sujet reste lisible autour de ce point ;
//   - focalWide : point focal en FRACTION de l'image { x, y } (0–1), utilisé en
//                 mode large (submersion) via object-position. Optionnel :
//                 repli sur `focal` (converti en fraction par le composant) ;
//   - zoom      : facteur d'échelle en mode normal (1 = taille réelle, 0.5 =
//                 moitié). Plus la valeur est petite, moins l'image est zoomée.
//                 Défaut : 1.
//   - reveal    : durées de l'effet de révélation, en millisecondes
//                 { pulseMs, quoteMs }. `pulseMs` = temps de survol avant que
//                 l'image submerge le bloc ; `quoteMs` = temps d'affichage de
//                 la citation. Chaque champ est optionnel : absent, il retombe
//                 sur les valeurs par défaut de useStakesReveal.js.
//
// Un critère absent du mapping n'affiche aucune image (repli silencieux).
import climateImg from '@/assets/stakes/flood.webp'
import ozone from '@/assets/stakes/ozone.webp'
import fossil from '@/assets/stakes/bagdad.webp'
import PM from '@/assets/stakes/PM.webp'

const STAKES_IMAGES = {
  'PEF-GWP': {
    src: climateImg,
    focal: { x: 750, y: 370 },
    // 960/1920 et 450/900 : centre de l'image source (1920×900).
    focalWide: { x: 0.5, y: 0.5 },
    zoom: 0.25,
    reveal: { pulseMs: 5000, quoteMs: 10000 },
  },
  'PEF-ODP':{
    src: ozone,
    focal: { x: 800, y: 400 },
    focalWide: { x: 1, y: 1 },
    zoom: 0.17,
    // Citation longue : on laisse plus de temps de lecture.
    reveal: { pulseMs: 5000, quoteMs: 35000 },
  },
  'PEF-ADPf':{
    src: fossil,
    focal: { x: 800, y: 500 },
    focalWide: { x: 1, y: 1 },
    zoom: 0.17,
    // Citation longue : on laisse plus de temps de lecture.
    reveal: { pulseMs: 5000, quoteMs: 30000 },    

  },
  'PEF-PM':{
    src: PM,
    focal: { x: 1200, y: 200 },
    focalWide: { x: 1, y: 1 },
    zoom: 0.25,
    // Citation longue : on laisse plus de temps de lecture.
    reveal: { pulseMs: 5000, quoteMs: 25000 },    

  }
}

/**
 * Image d'illustration d'un critère PEF.
 * @param {string} key  clé technique stable (ex. « PEF-GWP »)
 * @returns {{
 *   src: string,
 *   focal: {x: number, y: number},
 *   focalWide?: {x: number, y: number},
 *   zoom: number,
 *   reveal?: {pulseMs?: number, quoteMs?: number},
 * }|null}
 */
export function stakesImage(key) {
  return STAKES_IMAGES[key] || null
}

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
//   - focalWide : point focal (px) utilisé en mode élargi (submersion), où le
//                 cadrage diffère fortement. Optionnel : repli sur `focal` ;
//   - zoom      : facteur d'échelle en mode normal (1 = taille réelle, 0.5 =
//                 moitié). Plus la valeur est petite, moins l'image est zoomée.
//                 Défaut : 1.
//
// Un critère absent du mapping n'affiche aucune image (repli silencieux).
import climateImg from '@/assets/stakes/flood.webp'

const STAKES_IMAGES = {
  'PEF-GWP': {
    src: climateImg,
    focal: { x: 750, y: 370 },
    focalWide: { x: 960, y: 450 },
    zoom: 0.25,
  },
}

/**
 * Image d'illustration d'un critère PEF.
 * @param {string} key  clé technique stable (ex. « PEF-GWP »)
 * @returns {{
 *   src: string,
 *   focal: {x: number, y: number},
 *   focalWide?: {x: number, y: number},
 *   zoom: number,
 * }|null}
 */
export function stakesImage(key) {
  return STAKES_IMAGES[key] || null
}

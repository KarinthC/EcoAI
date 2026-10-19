// frontend/src/components/pipeline/analysis/stakesImages.js
//
// Image d'illustration par critère PEF, affichée en dégradé dans le coin
// inférieur droit de l'encart « Enjeux » (cf. StakesCard.vue).
//
// Les images vivent dans `src/assets/stakes/` et sont importées ici : Vite les
// bundle et les hashe automatiquement (cache-busting).
//
// Chaque image est décrite par un objet { src, focal } :
//   - src   : URL de l'image (import Vite) ;
//   - focal : point focal en PIXELS de l'image source { x, y }. Il sert de
//             point d'intérêt : le cadre (petit carré comme bloc agrandi) est
//             centré dessus via `object-position`. L'image doit donc être
//             composée pour que le sujet reste lisible autour de ce point, et
//             couvrir un ratio allant de 1:1 à 20:9.
//
// Un critère absent du mapping n'affiche aucune image (repli silencieux).

const STAKES_IMAGES = {
  // Exemple de structure (à compléter avec les images de démonstration) :
  // 'PEF-GWP': { src: climateImg, focal: { x: 1000, y: 400 } },
}

/**
 * Image d'illustration d'un critère PEF.
 * @param {string} key  clé technique stable (ex. « PEF-GWP »)
 * @returns {{src: string, focal: {x: number, y: number}}|null} image, ou null
 */
export function stakesImage(key) {
  return STAKES_IMAGES[key] || null
}

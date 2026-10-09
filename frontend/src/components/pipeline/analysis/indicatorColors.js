// frontend/src/components/pipeline/analysis/indicatorColors.js
//
// Couleur STABLE par indicateur PEF, partagée par tous les graphiques d'analyse.
//
// Une couleur fixe par clé technique garantit que le même indicateur a la même
// teinte partout (barres empilées, légendes, futurs graphiques) : c'est ce qui
// permet de « lire » la contribution d'un indicateur d'un usage à l'autre.
//
// La teinte est répartie sur le cercle chromatique selon l'ordre de CRITERIA_KEYS
// (ordre stable côté backend), avec une saturation/luminosité constantes.

// Ordre stable des critères (identique à backend common.CRITERIA_KEYS).
export const CRITERIA_ORDER = [
  'PEF-GWP',
  'PEF-ODP',
  'PEF-PM',
  'PEF-AP',
  'PEF-Epf',
  'PEF-Epm',
  'PEF-Ept',
  'PEF-IR',
  'PEF-POCP',
  'PEF-CTUh-nc',
  'PEF-ADPf',
  'PEF-ADPe',
  'PEF-WU',
  'PEF-CTUe',
  'PEF-CTUh-c',
]

// Couleur d'un indicateur : teinte dérivée de sa position dans l'ordre stable.
export function indicatorColor(key) {
  const idx = CRITERIA_ORDER.indexOf(key)
  if (idx < 0) return '#a0aec0'
  const hue = Math.round((360 / CRITERIA_ORDER.length) * idx)
  return `hsl(${hue}, 65%, 55%)`
}

// frontend/src/components/pipeline/analysis/protectionAreas.js
//
// Aire de protection (protection area) de chaque critère PEF, selon la méthode
// EF 3.1 (JRC 2023, Recommandation (UE) 2021/2279).
//
// La méthode EF 3.1 rattache chaque catégorie d'impact à l'une des trois aires
// de protection, et la pondération WF_i reflète l'importance relative de cette
// aire :
//   - 'humanHealth' : santé humaine
//   - 'ecosystems'  : écosystèmes
//   - 'resources'   : ressources
//
// Ce mapping sert à expliquer concrètement ce que représente la contribution
// d'un critère au score PEF (bilan environnemental global).

// Aire de protection d'un critère (clé i18n sous « analysis.protectionArea »).
const PROTECTION_AREA = {
  // Santé humaine
  'PEF-GWP': 'humanHealth',
  'PEF-ODP': 'humanHealth',
  'PEF-IR': 'humanHealth',
  'PEF-POCP': 'humanHealth',
  'PEF-PM': 'humanHealth',
  'PEF-CTUh-c': 'humanHealth',
  'PEF-CTUh-nc': 'humanHealth',
  // Écosystèmes
  'PEF-AP': 'ecosystems',
  'PEF-Epf': 'ecosystems',
  'PEF-Epm': 'ecosystems',
  'PEF-Ept': 'ecosystems',
  'PEF-CTUe': 'ecosystems',
  'PEF-WU': 'ecosystems',
  // Ressources
  'PEF-ADPf': 'resources',
  'PEF-ADPe': 'resources',
}

// Clé i18n de l'aire de protection d'un critère, ou null si inconnue.
export function protectionAreaKey(criterionKey) {
  const area = PROTECTION_AREA[criterionKey]
  return area ? `analysis.protectionArea.${area}` : null
}

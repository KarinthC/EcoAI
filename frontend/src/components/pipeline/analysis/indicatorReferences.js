// frontend/src/components/pipeline/analysis/indicatorReferences.js
//
// Références fondatrices par critère PEF : article scientifique ou rapport de
// référence du domaine, affiché dans l'onglet dédié à l'indicateur.
//
// Les URLs sont des données techniques (hors i18n) ; le libellé de chaque
// source est résolu via i18n à partir de `sourceKey` (clé sous
// « analysis.reference.source »), avec repli sur la clé brute si absente.
//
// Un critère peut porter PLUSIEURS références (tableau) : l'ordre du tableau
// est l'ordre d'affichage. Un critère absent du mapping n'affiche aucun encart.
//
// Règle : toute entrée DOIT avoir une URL non vide (jamais de lien vide).

const REFERENCES = {
  'PEF-GWP': [
    {
      url: 'https://www.ipcc.ch/report/ar5/wg1/',
      sourceKey: 'analysis.reference.source.ipccAr5',
    },
  ],
  'PEF-ODP': [
    {
      url: 'https://digitallibrary.un.org/record/761754',
      sourceKey: 'analysis.reference.source.wmoOzone1998',
    },
  ],
  'PEF-PM': [
    {
      url: 'https://www.sciencedirect.com/science/article/abs/pii/S1352231007008667',
      sourceKey: 'analysis.reference.source.vanZelm2008',
    },
  ],
  'PEF-AP': [
    {
      url: 'https://link.springer.com/article/10.1065/lca2005.06.215',
      sourceKey: 'analysis.reference.source.seppala2006',
    },
    {
      url: 'https://link.springer.com/article/10.1007/s11367-008-0025-9',
      sourceKey: 'analysis.reference.source.posch2008',
    },
  ],
  'PEF-Epf': [
    {
      url: 'https://www.researchgate.net/publication/302559709_ReCiPE_2008_A_life_cycle_impact_assessment_method_which_comprises_harmonised_category_indicators_at_the_midpoint_and_the_endpoint_level',
      sourceKey: 'analysis.reference.source.struijsRecipe2008',
    },
  ],
  'PEF-Epm': [
    {
      url: 'https://www.researchgate.net/publication/302559709_ReCiPE_2008_A_life_cycle_impact_assessment_method_which_comprises_harmonised_category_indicators_at_the_midpoint_and_the_endpoint_level',
      sourceKey: 'analysis.reference.source.struijsRecipe2008',
    },
  ],
  'PEF-Ept': [
    {
      url: 'https://link.springer.com/article/10.1065/lca2005.06.215',
      sourceKey: 'analysis.reference.source.seppala2006',
    },
    {
      url: 'https://link.springer.com/article/10.1007/s11367-008-0025-9',
      sourceKey: 'analysis.reference.source.posch2008',
    },
  ],
  'PEF-IR': [
    {
      url: 'https://op.europa.eu/en/publication-detail/-/publication/b2b86b52-4f18-4b4e-a134-b1c81ad8a1b2',
      sourceKey: 'analysis.reference.source.externe1995',
    },
  ],
  'PEF-POCP': [
    {
      url: 'https://www.sciencedirect.com/science/article/abs/pii/S1352231007008667',
      sourceKey: 'analysis.reference.source.vanZelm2008',
    },
  ],
  'PEF-CTUh-nc': [
    {
      url: 'https://link.springer.com/article/10.1007/s11367-008-0038-4',
      sourceKey: 'analysis.reference.source.rosenbaum2008',
    },
  ],
  'PEF-ADPf': [
    {
      url: 'https://web.universiteitleiden.nl/cml/ssp/projects/lca2/report_abiotic_depletion_web.pdf',
      sourceKey: 'analysis.reference.source.vanOers2002',
    },
  ],
  'PEF-ADPe': [
    {
      url: 'https://web.universiteitleiden.nl/cml/ssp/projects/lca2/report_abiotic_depletion_web.pdf',
      sourceKey: 'analysis.reference.source.vanOers2002',
    },
  ],
  'PEF-WU': [
    {
      url: 'https://link.springer.com/article/10.1007/s11367-017-1333-8',
      sourceKey: 'analysis.reference.source.boulay2018',
    },
  ],
  'PEF-CTUe': [
    {
      url: 'https://link.springer.com/article/10.1007/s11367-008-0038-4',
      sourceKey: 'analysis.reference.source.rosenbaum2008',
    },
  ],
  'PEF-CTUh-c': [
    {
      url: 'https://link.springer.com/article/10.1007/s11367-008-0038-4',
      sourceKey: 'analysis.reference.source.rosenbaum2008',
    },
  ],
}

/**
 * Références fondatrices d'un critère PEF.
 * @param {string} key  clé technique stable (ex. « PEF-GWP »)
 * @returns {Array<{url: string, sourceKey: string}>} tableau (vide si aucune)
 */
export function indicatorReferences(key) {
  return REFERENCES[key] || []
}

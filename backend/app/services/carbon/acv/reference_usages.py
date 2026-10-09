# backend/app/services/carbon/acv/reference_usages.py
"""Usages de référence ACV pour contextualiser le single score du pipeline.

Le single score PEF est sans dimension : il n'a de sens que comparé à d'autres
systèmes. On fournit ici des processus de référence dont les impacts PEF sont
issus de la même méthode (EF 3.1) et des mêmes bases que le projet
(EIME v6.3 / CODDE-2023-02 / NegaOctet 2023-02), afin que la comparaison soit
méthodologiquement valable.

Chaque usage expose ses impacts par catégorie PEF (unités brutes EF 3.1). Le
single score est calculé par `compute_single_score()` : on réutilise ainsi
EXACTEMENT la même formule (NF/WF EF 3.1) que le pipeline.

SOURCES :
  - Avion : processus « aircraft, passenger, medium-haul, economy, 1 p*km »
    (base CODDE/NegaOctet, méthode EF 3.1). Valeurs pour 1 passager·km.
    HYPOTHÈSE : un vol moyen-courrier parcourt ~800 km/h -> on multiplie les
    impacts par 800 pour obtenir « 1 heure d'avion ».
  - Ciment : processus « 1 kg de ciment » (base CODDE, méthode EF 3.1),
    mis à l'échelle de 10 kg pour un ordre de grandeur plus parlant.
  - Bœuf : processus « 1 kg Beef minced steak 15% fat raw » (méthode EF 3.1).

NOTE : l'eau (PEF-WU) de l'avion est NÉGATIVE (crédit d'eau évitée) : elle est
conservée dans le calcul du score mais exclue de l'affichage des barres.
"""

from .single_score import compute_single_score

# Distance parcourue par un vol moyen-courrier en 1 heure (km).
# HYPOTHÈSE explicite : vitesse moyenne ~800 km/h.
AIRCRAFT_KM_PER_HOUR = 800.0

# Impacts PEF pour 1 passager·km (avion moyen-courrier, classe économique).
_AIRCRAFT_PER_PKM = {
    'PEF-AP': 3.6974184697552344e-4,      # mol H+ eq
    'PEF-GWP': 0.10933155608887393,       # kg CO2 eq
    'PEF-CTUe': 0.22686484889429467,      # CTUe
    'PEF-Epf': 2.580647151684157e-6,      # kg P eq
    'PEF-Epm': 1.5182761038073385e-4,     # kg N eq
    'PEF-Ept': 0.0016387097126380865,     # mol N eq
    'PEF-CTUh-c': 9.640965249069601e-12,  # CTUh
    'PEF-CTUh-nc': 1.3947565576689897e-10,  # CTUh
    'PEF-IR': 0.0033014281073986316,      # kBq U235 eq
    'PEF-ODP': 2.456272854815656e-9,      # kg CFC11 eq
    'PEF-PM': 6.919258372381472e-10,      # disease incidence
    'PEF-POCP': 5.983303858071564e-4,     # kg NMVOC eq
    'PEF-ADPf': 1.423135044809777,        # MJ (net calorific)
    'PEF-ADPe': 1.3577636967411012e-8,    # kg Sb eq
    'PEF-WU': -0.014368868001476801,      # m3 world eq (négatif : eau évitée)
}

# Impacts PEF pour 1 kg de ciment.
_CEMENT_PER_KG = {
    'PEF-AP': 0.0010511217780096642,      # mol H+ eq
    'PEF-GWP': 0.6607536573192991,        # kg CO2 eq
    'PEF-CTUe': 0.3131982134352221,       # CTUe
    'PEF-Epf': 1.076332509172786e-4,      # kg P eq
    'PEF-Epm': 3.474518307734049e-4,      # kg N eq
    'PEF-Ept': 0.0040999568704415765,     # mol N eq
    'PEF-CTUh-c': 3.9033175654713394e-11, # CTUh
    'PEF-CTUh-nc': 2.997817867692122e-9,  # CTUh
    'PEF-IR': 0.06525125519551538,        # kBq U235 eq
    'PEF-ODP': 1.8692697323409058e-9,     # kg CFC11 eq
    'PEF-PM': 5.517152773613519e-9,       # disease incidence
    'PEF-POCP': 0.001076213408789746,     # kg NMVOC eq
    'PEF-ADPf': 1.638180766725762,        # MJ (net calorific)
    'PEF-ADPe': 1.3727436873608685e-7,    # kg Sb eq
    'PEF-WU': 0.01391689707246968,        # m3 world eq
}

# Impacts PEF pour 1 kg de bœuf (steak haché 15% MG, cru).
_BEEF_PER_KG = {
    'PEF-AP': 0.45955630076535264,        # mol H+ eq
    'PEF-GWP': 30.42624853472553,         # kg CO2 eq
    'PEF-CTUe': 86.9178859198404,         # CTUe
    'PEF-Epf': 8.525939645609758e-4,      # kg P eq
    'PEF-Epm': 0.09196385359438658,       # kg N eq
    'PEF-Ept': 2.068890735687956,         # mol N eq
    'PEF-CTUh-c': 2.09470689043637e-9,    # CTUh
    'PEF-CTUh-nc': 4.314904014569789e-7,  # CTUh
    'PEF-IR': 0.0046376283592291425,      # kBq U235 eq
    'PEF-ODP': 2.622835816211783e-9,      # kg CFC11 eq
    'PEF-PM': 3.075261588390259e-6,       # disease incidence
    'PEF-POCP': 0.036457360760937293,     # kg NMVOC eq
    'PEF-ADPf': 0.18766110286753138,      # MJ (net calorific)
    'PEF-ADPe': 6.155248961679513e-8,     # kg Sb eq
    'PEF-WU': 1.619919429428842,          # m3 world eq
}


def _scale(indicators: dict, factor: float) -> dict:
    """Met à l'échelle tous les indicateurs d'un processus."""
    return {key: value * factor for key, value in indicators.items()}


# Usages de référence exposés au front. `label_i18n` est une clé i18n résolue
# côté frontend (aucun libellé français en dur ici).
REFERENCE_USAGES = [
    {
        'id': 'aircraft_1h',
        'label_i18n': 'analysis.reference.aircraft1h',
        'indicators': _scale(_AIRCRAFT_PER_PKM, AIRCRAFT_KM_PER_HOUR),
    },
    {
        'id': 'cement_10kg',
        'label_i18n': 'analysis.reference.cement10kg',
        'indicators': _scale(_CEMENT_PER_KG, 10.0),
    },
    {
        'id': 'beef_1kg',
        'label_i18n': 'analysis.reference.beef1kg',
        'indicators': dict(_BEEF_PER_KG),
    },
]


def compute_reference_scores() -> list:
    """Calcule le single score PEF de chaque usage de référence.

    Réutilise `compute_single_score()` pour garantir une formule identique à
    celle du pipeline (NF/WF EF 3.1). Retourne une liste :
        [{'id', 'label_i18n', 'single_score', 'contributions'}, ...]
    """
    results = []
    for usage in REFERENCE_USAGES:
        # On construit des « critères » au format attendu par compute_single_score
        # (clé + valeur) à partir des indicateurs bruts du processus.
        criteria = [
            {'key': key, 'value': value}
            for key, value in usage['indicators'].items()
        ]
        score = compute_single_score(criteria)
        results.append({
            'id': usage['id'],
            'label_i18n': usage['label_i18n'],
            'single_score': score['single_score'],
            'contributions': score['contributions'],
        })
    return results

# backend/app/services/carbon/acv/storage.py
"""Nœuds de stockage — « Données persistantes » (HDD) et « Données SSD temporaires » (SSD).

Modèle ACV paramétrique couvrant les 16 catégories d'impact EF 3.1, adapté des
valeurs de l'ACV du stockage SUMMER. L'impact est décomposé en trois postes :

    Impact_total[cat] = Impact_fabrication[cat]
                      + Impact_usage[cat]
                      + Impact_fin_de_vie[cat]

    fab[cat]   = V(To) × F_fab[cat, média] × M_efficacite × M_replication × M_sauvegarde
    usage[cat] = V(To) × D(an) × kWh_par_To_an × F_elec[cat]
    fin[cat]   = END_OF_LIFE_RATIO × fab[cat]

avec :
    V          : volume logique (To) — dérivé du champ `taille` (Go) du front
    D          : durée de stockage (années)
    F_fab      : facteur de fabrication par To logique (tableau FAB_PER_TO)
    F_elec     : facteur d'impact par kWh (mix électrique FR, réutilisé des GPUs)

NOTE 1 : `kWh_par_To_an` (11,2 / 33,6) INTÈGRE déjà le PUE 1,28 (puissance
disques+baies × 8760 h × PUE, cf. §3.3 de l'ACV SUMMER). Le PUE ne doit donc
PAS être remultiplié dans le poste usage.

NOTE 2 : on réutilise FRENCH_MIX_PER_KWH (rapport GPUs) plutôt que le mix FR
2023 du tableau 3.2, afin de garder un mix électrique cohérent entre TOUS les
nœuds. Conséquence : le poste usage est légèrement supérieur aux valeurs de
l'ACV SUMMER (GWP 8,56 vs 8,0 pour 1 To HDD/an) ; la fabrication, poste
dominant, reste identique.

Les deux nœuds partagent le même moteur via `compute_storage(media, params)` :

Toutes les valeurs sont des ordres de grandeur destinés à être remplacés par
des données réelles : la confiance est donc volontairement 'medium'.
"""

import logging

from ..common import get_level_from_indicators
from .gpu_models import FRENCH_MIX_PER_KWH

logger = logging.getLogger(__name__)

# PUE du DC-IMAG 2023 (non paramétrable : hypothèse fixe du modèle).
PUE = 1.28

# Fin de vie : forfaitaire, +5 % de l'impact de fabrication.
END_OF_LIFE_RATIO = 0.05

# Conversion Go -> To (l'ACV raisonne par To logique, le front saisit des Go).
GO_PER_TO = 1000.0

# Conversion jours -> années (pour exprimer l'usage en kWh/To/an).
JOURS_PER_AN = 365.0

# Durée par défaut du stockage temporaire (SSD/scratch) si non fournie.
# Convention HPC/cloud : les données de scratch sont purgées après ~30 jours.
DUREE_SSD_TEMPORAIRE_JOURS = 30

# ------------------------------------------------------------
# Facteurs de fabrication par To logique (tableau 3.1 de l'ACV SUMMER).
# Basés sur Boavizta (données ADEME IMPACTS) et extrapolation enterprise.
# Clés = clés PEF internes utilisées dans tout le projet.
# ------------------------------------------------------------
FAB_PER_TO = {
    'HDD': {  # WORK / Extensive
        'PEF-GWP': 1.0e+1,      # kg CO2 eq
        'PEF-ODP': 1.0e-7,      # kg CFC-11 eq
        'PEF-IR': 1.0e+0,       # kBq U235 eq
        'PEF-POCP': 2.0e-2,     # kg NMVOC eq
        'PEF-PM': 4.0e-7,       # disease incidences
        'PEF-CTUh-c': 4.0e-9,   # CTUh
        'PEF-CTUh-nc': 4.0e-8,  # CTUh
        'PEF-AP': 1.0e-1,       # mol H+ eq
        'PEF-Epf': 1.0e-2,      # kg P eq
        'PEF-Epm': 2.0e-2,      # kg N eq
        'PEF-Ept': 2.0e-1,      # mol N eq
        'PEF-CTUe': 1.0e+2,     # CTUe
        'PEF-LU': 1.0e+0,       # usage des sols (exclu de l'agrégat affiché)
        'PEF-WU': 5.0e-2,       # m3 eq
        'PEF-ADPf': 1.2e+2,     # MJ
        'PEF-ADPe': 1.0e-4,     # kg Sb eq
    },
    'SSD': {  # SCRATCH / Intensive (NVMe)
        'PEF-GWP': 7.5e+1,      # kg CO2 eq
        'PEF-ODP': 7.5e-7,      # kg CFC-11 eq
        'PEF-IR': 7.5e+0,       # kBq U235 eq
        'PEF-POCP': 1.5e-1,     # kg NMVOC eq
        'PEF-PM': 3.0e-6,       # disease incidences
        'PEF-CTUh-c': 4.5e-8,   # CTUh
        'PEF-CTUh-nc': 4.5e-7,  # CTUh
        'PEF-AP': 7.5e-1,       # mol H+ eq
        'PEF-Epf': 7.5e-2,      # kg P eq
        'PEF-Epm': 1.5e-1,      # kg N eq
        'PEF-Ept': 1.5e+0,      # mol N eq
        'PEF-CTUe': 7.5e+2,     # CTUe
        'PEF-LU': 7.5e+0,       # usage des sols (exclu de l'agrégat affiché)
        'PEF-WU': 1.5e+0,       # m3 eq
        'PEF-ADPf': 9.0e+2,     # MJ
        'PEF-ADPe': 7.5e-3,     # kg Sb eq
    },
}

# ------------------------------------------------------------
# Paramètres média (tableaux 3.3 et 3.4 de l'ACV SUMMER).
#   kwh_per_to_year : consommation électrique par To logique et par an
#                     (puissance disques+baies × 8760 × PUE)
#   m_efficacite    : déduplication + compression + RAID
#   m_replication   : réplication synchrone
#   m_sauvegarde    : sauvegarde (option)
# Seuls les facteurs de FABRICATION sont affectés par ces multiplicateurs.
# ------------------------------------------------------------
MEDIA = {
    'HDD': {
        'kwh_per_to_year': 11.2,
        'm_efficacite': 0.7,
        'm_replication': 1.0,
        'm_sauvegarde': 1.0,
    },
    'SSD': {
        'kwh_per_to_year': 33.6,
        'm_efficacite': 0.5,
        'm_replication': 2.0,
        'm_sauvegarde': 1.0,
    },
}


def compute_storage(media: str, params: dict) -> dict:
    """Calcule les 16 indicateurs PEF du stockage pour un média donné.

    Args:
        media: 'HDD' (persistant/extensive) ou 'SSD' (temporaire/intensive).
        params: dict envoyé par le front, avec :
            - taille      : volume logique en Go (converti en To en interne)
            - duree_jours : durée de stockage en jours (SSD / temporaire)
            - duree_ans   : durée de stockage en années (HDD / persistant)
            (les champs `nom`, `format`, `serveur_stockage` sont ignorés par le
            calcul mais conservés pour la traçabilité et les recommandations.)

    La durée est exprimée en JOURS pour le stockage temporaire (SSD/scratch,
    purgé après ~30 jours) et en ANNÉES pour le stockage persistant (HDD).
    Si `duree_ans` est fourni, il est prioritaire (rétro-compatibilité).

    Returns:
        dict au format attendu par l'orchestrateur
        (impact_kg, indicators, method, confidence, level).
    """
    if media not in MEDIA:
        raise ValueError(f"Média inconnu : {media}. Disponibles : {list(MEDIA)}")

    volume_to = float(params.get('taille') or 0) / GO_PER_TO

    # Durée : priorité à `duree_ans` (rétro-compat), sinon `duree_jours`.
    # Pour le SSD, aucune durée fournie -> défaut = durée scratch (30 jours).
    if params.get('duree_ans') not in (None, ''):
        duree_ans = float(params.get('duree_ans') or 0)
        duree_jours = duree_ans * JOURS_PER_AN
    elif params.get('duree_jours') not in (None, ''):
        duree_jours = float(params.get('duree_jours') or 0)
        duree_ans = duree_jours / JOURS_PER_AN
    elif media == 'SSD':
        duree_jours = float(DUREE_SSD_TEMPORAIRE_JOURS)
        duree_ans = duree_jours / JOURS_PER_AN
    else:
        duree_jours = 0.0
        duree_ans = 0.0

    config = MEDIA[media]
    fab_coeff = (
        config['m_efficacite']
        * config['m_replication']
        * config['m_sauvegarde']
    )

    # Énergie totale consommée (kWh). `kwh_per_to_year` intègre déjà le PUE
    # (cf. §3.3 de l'ACV : 1,0 W/To × 8760 h × 1,28 = 11,2 kWh/To/an).
    energy_kwh = volume_to * duree_ans * config['kwh_per_to_year']

    indicators = {}
    for key, fab_per_to in FAB_PER_TO[media].items():
        fabrication = volume_to * fab_per_to * fab_coeff
        fin_de_vie = END_OF_LIFE_RATIO * fabrication
        usage = energy_kwh * FRENCH_MIX_PER_KWH[key]
        indicators[key] = fabrication + fin_de_vie + usage

    gwp = indicators['PEF-GWP']

    return {
        'impact_kg': round(gwp, 6),
        'indicators': indicators,
        'method': 'acv',
        # Valeurs partiellement extrapolées (13 catégories non-GWP par ratios
        # issus de la littérature ACV électronique) -> confiance moyenne.
        'confidence': 'medium',
        'level': get_level_from_indicators(indicators),
    }


def compute_hdd(params: dict) -> dict:
    """Nœud « Données persistantes » : stockage HDD (WORK / Extensive)."""
    return compute_storage('HDD', params)


def compute_ssd(params: dict) -> dict:

    """Nœud « Données SSD temporaires » : stockage SSD NVMe (SCRATCH / Intensive)."""
    return compute_storage('SSD', params)

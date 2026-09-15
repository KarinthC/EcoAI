# backend/app/services/carbon/acv/gpu_models.py
"""Modèles ACV des GPUs serveurs + moteur de calcul générique.

Les données proviennent du rapport ADEME/AltImpact (Mars 2026) au format
standardisé PEF (Product Environmental Footprint).

Chaque GPU dispose de :
  - `embedded_total_card` : impacts embarqués totaux pour 1 carte entière
    (fabrication + distribution + fin de vie).
  - `tdp_w` : puissance thermique de conception (Watts).

Les facteurs d'usage du mix électrique français (2021) sont communs à tous
les GPUs (pour 1 kWh consommé).

La fonction `compute_acv` reproduit le modèle de l'exemple fourni :
    impact_total(indicateur) = impact_embarqué(indicateur) / durée_de_vie
                             + facteur_usage(indicateur) * puissance_kW
appliqué pour 1 GPU.heure, puis mis à l'échelle du nombre d'heures demandé.

IMPORTANT : le GWP (PEF-GWP) n'a pas de statut supérieur aux autres
indicateurs. Il est simplement exposé sous la clé technique `impact_kg`
pour l'agrégat `total_impact_kg` du front (transition en cours).
"""

import logging

from . import parametric

logger = logging.getLogger(__name__)

# Hypothèses par défaut (issues du rapport ADEME)
DEFAULT_LIFETIME_HOURS = 3 * 365 * 24  # 26 280 heures
DEFAULT_CHARGE = 1.0       # 100% de charge (fraction, pas de pourcentage)
DEFAULT_REGION = 'FR'

# ------------------------------------------------------------
# Facteurs d'usage du mix électrique français 2021 (pour 1 kWh)
# Source : Tableau 16 (page 44) du rapport ADEME/AltImpact
# ------------------------------------------------------------
FRENCH_MIX_PER_KWH = {
    "PEF-AP": 5.12e-4,        # mol H+ eq
    "PEF-GWP": 1.08e-1,       # kg CO2 eq
    "PEF-CTUe": 1.65e-1,      # CTUe
    "PEF-PM": 1.36e-8,        # Disease occurrence
    "PEF-Epf": 2.63e-6,       # kg P eq
    "PEF-Epm": 6.81e-5,       # kg N eq
    "PEF-Ept": 1.17e-3,       # mol N eq
    "PEF-CTUh-c": 1.69e-11,   # CTUh
    "PEF-CTUh-nc": 4.23e-10,  # CTUh
    "PEF-IR": 1.43e+0,        # kBq U235 eq
    "PEF-LU": 4.94e-3,        # No dimension
    "PEF-ODP": 1.02e-9,       # kg CFC-11 eq
    "PEF-POCP": 2.02e-4,      # kg NMVOC eq (corrigé)
    "PEF-ADPf": 1.14e+1,      # MJ
    "PEF-ADPe": 1.05e-7,      # kg Sb eq
    "PEF-WU": 1.76e-2,        # m3 eq
}

# ------------------------------------------------------------
# Modèles ACV des GPUs serveurs
# ------------------------------------------------------------
GPUS = {
    "GTX 1080 Ti": {
        "tdp_w": 250,
        # Impacts embarqués totaux pour 1 carte entière.
        # Source : Tableau 36 (page 72) du rapport ADEME/AltImpact.
        "embedded_total_card": {
            "PEF-AP": 6.79e-1,        # mol H+ eq
            "PEF-GWP": 9.58e+1,       # kg CO2 eq
            "PEF-CTUe": 1.97e+3,      # CTUe
            "PEF-PM": 3.77e-6,        # Disease occurrence
            "PEF-Epf": 9.98e-4,       # kg P eq
            "PEF-Epm": 1.14e-1,       # kg N eq
            "PEF-Ept": 9.96e-1,       # mol N eq
            "PEF-CTUh-c": 1.15e-5,    # CTUh
            "PEF-CTUh-nc": 3.67e-6,   # CTUh
            "PEF-IR": 1.99e+2,        # kBq U235 eq
            "PEF-LU": 8.26e+0,        # No dimension
            "PEF-ODP": 1.82e-5,       # kg CFC-11 eq
            "PEF-POCP": 2.97e-1,      # kg NMVOC eq
            "PEF-ADPf": 1.24e+3,      # MJ
            "PEF-ADPe": 5.22e-3,      # kg Sb eq
            "PEF-WU": 4.56e+2,        # m3 eq
        },
    },
    # Carte non documentée « prête à l'emploi » dans le rapport : ses impacts
    # embarqués sont reconstruits via le MODÈLE PARAMÉTRIQUE ADEME (Tableau 42).
    # `tdp_w` = TDP de la carte ENTIÈRE (H100 NVL = 2 x 350 W = 700 W).
    "H100 NVL 96Go": {
        "tdp_w": parametric.PARAMETRIC_GPUS["H100 NVL 96Go"]["tdp_w"],
        "embedded_total_card": parametric.embedded_total_card("H100 NVL 96Go"),
    },
}


# ------------------------------------------------------------
# Parc serveurs : chaque serveur expose 1 à N types de GPUs.
# À ajuster quand les parcs LIG réels seront connus.
# ------------------------------------------------------------
SERVERS = {
    "lig1": ["GTX 1080 Ti"],
    "lig2": ["GTX 1080 Ti"],
    "lig3": ["GTX 1080 Ti"],
    "lig4": ["GTX 1080 Ti"],
    "lig5": ["GTX 1080 Ti"],
    "lig6": ["GTX 1080 Ti"],
    "lig7": ["GTX 1080 Ti"],
    "lig8": ["GTX 1080 Ti"],
    "lig9": ["GTX 1080 Ti"],
    "lig10": ["H100 NVL 96Go"],
}


def available_gpus(server_id: str) -> list:
    """Retourne la liste des GPUs disponibles sur un serveur.

    Lève une erreur explicite si le serveur est inconnu.
    """
    if server_id not in SERVERS:
        raise ValueError(f"Serveur inconnu : {server_id}. Disponibles : {list(SERVERS)}")
    return SERVERS[server_id]


def gpu_exists_on_server(server_id: str, gpu_type: str) -> bool:
    """Vérifie qu'un type de GPU est bien présent sur le serveur donné."""
    return gpu_type in available_gpus(server_id)


def _usage_factors(region: str) -> dict:
    """Retourne les facteurs d'usage de l'électricité selon la région.

    Seul le mix français est documenté pour l'instant ; toute autre région
    lève une erreur explicite plutôt que de renvoyer des valeurs inventées.
    """
    if region == 'FR':
        return FRENCH_MIX_PER_KWH
    raise ValueError(f"Mix électrique non documenté pour la région : {region}")


def compute_acv(
    gpu_key: str,
    hours: float = 1.0,
    charge: float = DEFAULT_CHARGE,
    region: str = DEFAULT_REGION,
    lifetime_hours: float = DEFAULT_LIFETIME_HOURS,
    nb_gpu: int = 1,
) -> dict:
    """Calcule l'ensemble des indicateurs ACV pour `hours` heures sur `nb_gpu` cartes.

    Les GPUs sont supposés tourner en parallèle pendant la même durée `hours`.

    Args:
        gpu_key: clé dans `GPUS` (ex: "GTX 1080 Ti").
        hours: nombre d'heures d'utilisation active (par GPU).
        charge: taux de charge en fraction (0..1).
        region: région du mix électrique (seul 'FR' documenté).
        lifetime_hours: durée de vie hypothétique du GPU (heures).
        nb_gpu: nombre de cartes identiques utilisées en parallèle.

    Returns:
        dict contenant :
          - `indicators` : dict de TOUS les indicateurs PEF sur la durée demandée.
          - `energy_kwh` : énergie électrique consommée (kWh).
          - `gpu_key`, `hours`, `charge`, `region`, `nb_gpu` : traçabilité des hypothèses.
    """
    if gpu_key not in GPUS:
        raise ValueError(f"GPU inconnu : {gpu_key}. Disponibles : {list(GPUS)}")

    gpu = GPUS[gpu_key]
    usage = _usage_factors(region)

    tdp_w = gpu["tdp_w"]
    power_kw = (tdp_w * charge) / 1000.0

    # Impacts embarqués répartis sur 1 heure active de la durée de vie.
    embedded_per_hour = {
        k: v / lifetime_hours for k, v in gpu["embedded_total_card"].items()
    }
    # Impacts de l'électricité consommée pendant 1 heure.
    use_per_hour = {k: v * power_kw for k, v in usage.items()}

    # Total pour 1 GPU.heure, puis mise à l'échelle (heures x nombre de GPUs).
    total_per_hour = {
        k: embedded_per_hour[k] + use_per_hour[k]
        for k in gpu["embedded_total_card"]
    }
    scale = hours * nb_gpu
    indicators = {k: v * scale for k, v in total_per_hour.items()}

    energy_kwh = power_kw * scale

    return {
        "indicators": indicators,
        "energy_kwh": energy_kwh,
        "gpu_key": gpu_key,
        "hours": hours,
        "charge": charge,
        "region": region,
        "nb_gpu": nb_gpu,
    }

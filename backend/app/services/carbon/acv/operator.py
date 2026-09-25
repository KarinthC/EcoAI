"""Nœud « Opérateur » — calcul d'impact via le modèle ACV.

L'opérateur représente l'exécution d'une charge sur un GPU serveur documenté
(ACV), comme l'entraînement ou l'inférence, MAIS :

  - la charge (taux d'utilisation) est paramétrable par l'utilisateur
    (défaut 100% si vide ou absent) ;
  - si aucun paramètre matériel n'est fourni (pas de GPU / pas d'heures),
    l'impact est NUL : un opérateur peut n'avoir qu'un nom et ne tourner
    nulle part.

Paramètres attendus (envoyés par le front) :
  - nom       : nom libre de l'opérateur (n'intervient pas dans le calcul)
  - server_id : identifiant du serveur (ex: "lig1")
  - gpu_type  : type de GPU disponible sur le serveur (ex: "GTX 1080 Ti")
  - nb_gpu    : nombre de GPUs utilisés en parallèle
  - heures    : nombre d'heures d'utilisation (par GPU)
  - charge    : taux de charge en pourcent (0..100), défaut 100
"""

import logging

from ..common import get_level_from_indicators
from .gpu_models import compute_acv, available_gpus, gpu_exists_on_server
from .moma_adapter import moma_operator_to_acv

logger = logging.getLogger(__name__)

# Taux de charge par défaut (pourcent) : 100%.
DEFAULT_CHARGE_PERCENT = 100.0


def _impact_nul() -> dict:
    """Résultat neutre : aucun impact (opérateur non déployé)."""
    return {
        'impact_kg': 0.0,
        'indicators': {},
        'method': 'acv',
        'confidence': 'high',
        'level': 'low',
    }


def compute(params: dict) -> dict:
    # Traduction des paramètres MoMa (`eco:*`) vers les clés ACV attendues.
    acv_params = moma_operator_to_acv(params)

    # Sans matériel renseigné, l'opérateur ne tourne nulle part : impact nul.
    server_id = acv_params.get('server_id')
    gpu_type = acv_params.get('gpu_type')
    heures = acv_params.get('heures')

    if not server_id or not gpu_type or heures in (None, '', 0, '0'):
        return _impact_nul()

    heures = float(heures)
    nb_gpu = int(acv_params.get('nb_gpu') or 1)

    # Taux de charge : vide/absent -> 100%. Saisi en pourcent, converti en fraction.
    charge_percent = acv_params.get('charge')
    if charge_percent in (None, ''):
        charge_percent = DEFAULT_CHARGE_PERCENT
    charge = max(0.0, min(1.0, float(charge_percent) / 100.0))

    if not gpu_exists_on_server(server_id, gpu_type):
        raise ValueError(
            f"Le GPU '{gpu_type}' n'est pas disponible sur le serveur '{server_id}' "
            f"(disponibles : {available_gpus(server_id)})"
        )

    acv = compute_acv(gpu_type, hours=heures, charge=charge, nb_gpu=nb_gpu)
    indicators = acv['indicators']
    gwp = indicators['PEF-GWP']

    return {
        'impact_kg': round(gwp, 6),
        'indicators': indicators,
        'method': 'acv',
        'confidence': 'high',
        'level': get_level_from_indicators(indicators),
    }

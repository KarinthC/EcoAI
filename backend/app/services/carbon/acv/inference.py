# backend/app/services/carbon/acv/inference.py
"""Nœud « Inférence » — calcul d'impact via le modèle ACV.

L'impact est dérivé du temps d'inférence sur un GPU serveur documenté (ACV).
La charge est imposée côté backend (33% pour l'inférence), conformément
aux hypothèses du rapport ADEME.

Paramètres attendus (envoyés par le front) :
  - server_id : identifiant du serveur (ex: "lig1")
  - gpu_type  : type de GPU disponible sur le serveur (ex: "GTX 1080 Ti")
  - nb_gpu    : nombre de GPUs utilisés en parallèle
  - heures    : nombre d'heures d'utilisation (par GPU)
"""

import logging

from ..common import get_level_from_indicators
from .gpu_models import compute_acv, available_gpus, gpu_exists_on_server
from .moma_adapter import moma_operator_to_acv

logger = logging.getLogger(__name__)

# Charge imposée pour l'inférence (fraction).
INFERENCE_CHARGE = 0.33


def compute(params: dict) -> dict:
    # Traduction des paramètres MoMa (`eco:*`) vers les clés ACV attendues.
    acv_params = moma_operator_to_acv(params)

    server_id = acv_params.get('server_id') or 'lig1'
    gpu_type = acv_params.get('gpu_type') or available_gpus(server_id)[0]
    heures = float(acv_params.get('heures') or 1.0)
    nb_gpu = int(acv_params.get('nb_gpu') or 1)

    if not gpu_exists_on_server(server_id, gpu_type):
        raise ValueError(
            f"Le GPU '{gpu_type}' n'est pas disponible sur le serveur '{server_id}' "
            f"(disponibles : {available_gpus(server_id)})"
        )

    acv = compute_acv(gpu_type, hours=heures, charge=INFERENCE_CHARGE, nb_gpu=nb_gpu)
    indicators = acv['indicators']
    gwp = indicators['PEF-GWP']

    return {
        'impact_kg': round(gwp, 6),
        'indicators': indicators,
        'method': 'acv',
        'confidence': 'high',
        'level': get_level_from_indicators(indicators),
    }

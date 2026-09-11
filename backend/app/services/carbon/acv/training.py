# backend/app/services/carbon/acv/training.py
"""Nœud « Entrainement » — calcul d'impact via le modèle ACV.

L'impact est dérivé du temps d'entraînement sur un GPU serveur documenté (ACV).
La charge est imposée côté backend (100% pour l'entraînement), conformément
aux hypothèses du rapport ADEME.

Paramètres attendus (envoyés par le front) :
  - server_id : identifiant du serveur (ex: "lig1")
  - gpu_type  : type de GPU disponible sur le serveur (ex: "GTX 1080 Ti")
  - nb_gpu    : nombre de GPUs utilisés en parallèle
  - heures    : nombre d'heures d'utilisation (par GPU)
"""

import logging

from ..common import get_level
from .gpu_models import compute_acv, available_gpus, gpu_exists_on_server

logger = logging.getLogger(__name__)

# Charge imposée pour l'entraînement (fraction).
TRAINING_CHARGE = 1.0


def compute(params: dict) -> dict:
    server_id = params.get('server_id') or 'lig1'
    gpu_type = params.get('gpu_type') or available_gpus(server_id)[0]
    heures = float(params.get('heures') or 1.0)
    nb_gpu = int(params.get('nb_gpu') or 1)

    if not gpu_exists_on_server(server_id, gpu_type):
        raise ValueError(
            f"Le GPU '{gpu_type}' n'est pas disponible sur le serveur '{server_id}' "
            f"(disponibles : {available_gpus(server_id)})"
        )

    acv = compute_acv(gpu_type, hours=heures, charge=TRAINING_CHARGE, nb_gpu=nb_gpu)
    indicators = acv['indicators']
    # GWP comme clé technique pour l'agrégat du front (transition en cours).
    gwp = indicators['PEF-GWP']

    message = (
        f"Impact ACV pour {heures:.2f} h d'entraînement sur "
        f"{nb_gpu} x {gpu_type} (serveur {server_id}, charge 100%, mix FR)."
    )
    if gwp >= 20:
        message += " Impact GWP élevé : réduire la durée ou optimiser le GPU."

    return {
        'impact_kg': round(gwp, 6),
        'energy_kwh': round(acv['energy_kwh'], 6),
        'indicators': indicators,
        'method': 'acv',
        'confidence': 'high',
        'level': get_level(gwp),
        'message': message,
    }

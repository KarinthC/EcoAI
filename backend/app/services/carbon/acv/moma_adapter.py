"""Adaptateur des paramètres MoMa vers les paramètres ACV.

Les nœuds Operator MoMa portent leurs paramètres sous forme d'extensions
préfixées `eco:` (ex. `eco:executionTimeSec`, `eco:gpuModel`). Les modules ACV
existants (`training.py`, `inference.py`, `operator.py`) attendent des clés
historiques (`heures`, `gpu_type`, `server_id`, `nb_gpu`, `charge`).

Ce module centralise la traduction pour éviter de dupliquer la logique dans
chaque nœud. Il ne fait AUCUN calcul : uniquement du renommage de clés.
"""


def moma_operator_to_acv(params: dict) -> dict:
    """Traduit les paramètres d'un Operator MoMa vers les clés ACV attendues.

    Args:
        params: dict du front, avec les extensions `eco:` :
            - eco:serverId        : identifiant du serveur (ex. "lig1")
            - eco:gpuModel        : type de GPU (ex. "GTX 1080 Ti")
            - eco:gpuCount        : nombre de GPUs en parallèle
            - eco:executionTimeSec: durée d'exécution en secondes
            - eco:gpuUtilization  : taux de charge en pourcent (0..100)

    Returns:
        dict avec les clés ACV : server_id, gpu_type, nb_gpu, heures, charge.
    """
    execution_time_sec = params.get('eco:executionTimeSec')
    heures = None
    if execution_time_sec not in (None, ''):
        heures = float(execution_time_sec) / 3600.0

    return {
        'server_id': params.get('eco:serverId'),
        'gpu_type': params.get('eco:gpuModel'),
        'nb_gpu': params.get('eco:gpuCount'),
        'heures': heures,
        'charge': params.get('eco:gpuUtilization'),
    }

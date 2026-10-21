"""Tests unitaires simples pour la famille ACV.

Couvrent :
  - le moteur de calcul ACV (compute_acv) et sa linéarité en heures / nb_gpu ;
  - la validation serveur/GPU ;
  - les nœuds training et inference (charges imposées, structure de retour).
"""

import pytest

from app.services.carbon.acv.gpu_models import (
    compute_acv,
    available_gpus,
    gpu_exists_on_server,
)
from app.services.carbon.acv import training, inference


# ---------------------------------------------------------------------------
# Moteur ACV
# ---------------------------------------------------------------------------

def test_compute_acv_structure():
    r = compute_acv('GTX 1080 Ti', hours=1.0, nb_gpu=1)
    assert 'indicators' in r
    assert 'energy_kwh' in r
    assert 'PEF-GWP' in r['indicators']
    assert r['indicators']['PEF-GWP'] > 0
    assert r['energy_kwh'] > 0


def test_compute_acv_scales_with_hours_and_nb_gpu():
    base = compute_acv('GTX 1080 Ti', hours=1.0, nb_gpu=1)['indicators']['PEF-GWP']
    x6 = compute_acv('GTX 1080 Ti', hours=2.0, nb_gpu=3)['indicators']['PEF-GWP']
    # Linéarité : 2h * 3 GPUs = x6
    assert x6 == pytest.approx(base * 6, rel=1e-9)


def test_compute_acv_unknown_gpu_raises():
    with pytest.raises(ValueError, match="GPU inconnu"):
        compute_acv('RTX 9999')


# ---------------------------------------------------------------------------
# Parc serveurs
# ---------------------------------------------------------------------------

def test_servers_helpers():
    assert 'GTX 1080 Ti' in available_gpus('lig1')
    assert gpu_exists_on_server('lig1', 'GTX 1080 Ti') is True
    assert gpu_exists_on_server('lig1', 'A100') is False


def test_unknown_server_raises():
    with pytest.raises(ValueError, match="Serveur inconnu"):
        available_gpus('lig99')


# ---------------------------------------------------------------------------
# Nœuds Entrainement / Inférence
#
# Les nœuds Operator MoMa portent leurs paramètres sous forme d'extensions
# `eco:` (cf. moma_adapter.py). Les tests ci-dessous utilisent ce contrat.
# ---------------------------------------------------------------------------

def _operator_params(server_id, gpu_type, nb_gpu, heures):
    """Construit des paramètres Operator MoMa (`eco:`) depuis des valeurs ACV."""
    return {
        'eco:serverId': server_id,
        'eco:gpuModel': gpu_type,
        'eco:gpuCount': nb_gpu,
        'eco:executionTimeSec': heures * 3600,
    }


def test_training_node():
    r = training.compute(_operator_params('lig3', 'GTX 1080 Ti', 2, 4))
    assert r['method'] == 'acv'
    assert r['confidence'] == 'high'
    assert r['indicators']['PEF-GWP'] > 0
    # impact_kg est arrondi à 6 décimales -> tolérance relative.
    assert r['impact_kg'] == pytest.approx(r['indicators']['PEF-GWP'], rel=1e-5)


def test_inference_node():
    r = inference.compute(_operator_params('lig1', 'GTX 1080 Ti', 1, 10))
    assert r['method'] == 'acv'
    assert r['confidence'] == 'high'
    assert r['indicators']['PEF-GWP'] > 0


def test_inference_lower_impact_than_training():
    """À params égaux, l'inférence (charge 33%) impacte moins que l'entraînement (100%)."""
    params = _operator_params('lig1', 'GTX 1080 Ti', 1, 5)
    assert inference.compute(params)['impact_kg'] < training.compute(params)['impact_kg']


def test_node_rejects_gpu_not_on_server():
    with pytest.raises(ValueError, match="n'est pas disponible"):
        training.compute(_operator_params('lig1', 'A100', 1, 1))


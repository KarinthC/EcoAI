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
# ---------------------------------------------------------------------------

def test_training_node():
    r = training.compute({'server_id': 'lig3', 'gpu_type': 'GTX 1080 Ti', 'nb_gpu': 2, 'heures': 4})
    assert r['method'] == 'acv'
    assert r['confidence'] == 'high'
    assert r['indicators']['PEF-GWP'] > 0
    assert r['impact_kg'] == pytest.approx(r['indicators']['PEF-GWP'], rel=1e-6)


def test_inference_node():
    r = inference.compute({'server_id': 'lig1', 'gpu_type': 'GTX 1080 Ti', 'nb_gpu': 1, 'heures': 10})
    assert r['method'] == 'acv'
    assert r['confidence'] == 'high'
    assert r['indicators']['PEF-GWP'] > 0


def test_inference_lower_impact_than_training():
    """À params égaux, l'inférence (charge 33%) impacte moins que l'entraînement (100%)."""
    params = {'server_id': 'lig1', 'gpu_type': 'GTX 1080 Ti', 'nb_gpu': 1, 'heures': 5}
    assert inference.compute(params)['impact_kg'] < training.compute(params)['impact_kg']


def test_node_rejects_gpu_not_on_server():
    with pytest.raises(ValueError, match="n'est pas disponible"):
        training.compute({'server_id': 'lig1', 'gpu_type': 'A100'})

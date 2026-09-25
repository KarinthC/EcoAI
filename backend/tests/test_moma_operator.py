"""Tests unitaires pour l'adaptateur MoMa -> ACV et le dispatch des Operator.

Les nœuds Operator MoMa portent leurs paramètres sous forme d'extensions `eco:`
(ex. `eco:executionTimeSec`). L'adaptateur traduit ces clés vers les clés ACV
attendues par les modules de calcul (`heures`, `gpu_type`, etc.).
"""

from app.services.carbon.acv.moma_adapter import moma_operator_to_acv
from app.services.carbon.orchestrator import _compute_node


def _operator_node(subtype, params):
    merged = {'subtype': subtype, **params}
    return {'id': '1', 'data': {'nodeType': 'operator', 'params': merged}}


def test_adapter_converts_execution_time_to_hours():
    """La durée d'exécution en secondes est convertie en heures."""
    acv = moma_operator_to_acv({'eco:executionTimeSec': 3600})
    assert acv['heures'] == 1.0


def test_adapter_maps_gpu_fields():
    """Les champs GPU MoMa sont renommés vers les clés ACV."""
    acv = moma_operator_to_acv({
        'eco:serverId': 'lig1',
        'eco:gpuModel': 'GTX 1080 Ti',
        'eco:gpuCount': 2,
        'eco:gpuUtilization': 50,
    })
    assert acv['server_id'] == 'lig1'
    assert acv['gpu_type'] == 'GTX 1080 Ti'
    assert acv['nb_gpu'] == 2
    assert acv['charge'] == 50


def test_adapter_empty_execution_time_is_none():
    """Une durée absente donne `heures=None` (impact nul en aval)."""
    acv = moma_operator_to_acv({})
    assert acv['heures'] is None


def test_operator_training_has_impact():
    """Un Operator de sous-type training produit un impact positif."""
    r = _compute_node(_operator_node('training', {
        'eco:serverId': 'lig1',
        'eco:gpuModel': 'GTX 1080 Ti',
        'eco:gpuCount': 1,
        'eco:executionTimeSec': 3600,
    }))
    assert r['impact_kg'] > 0.0
    assert r['method'] == 'acv'


def test_operator_without_hardware_is_neutral():
    """Un Operator sans matériel renseigné n'a aucun impact."""
    r = _compute_node(_operator_node('training', {}))
    assert r['impact_kg'] == 0.0


def test_operator_unknown_subtype_is_neutral():
    """Un sous-type inconnu est traité comme neutre (pas de faux impact)."""
    r = _compute_node(_operator_node('inconnu', {'eco:executionTimeSec': 3600}))
    assert r['impact_kg'] == 0.0
    assert r['computed'] is False

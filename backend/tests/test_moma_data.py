"""Tests unitaires pour le nœud MoMa « Data » (stockage des données persistées).

Le nœud Data ne porte un impact que si les données sont stockées sur un média
calculé (SSD ou HDD). Pour les autres médias (cloud, tape), l'impact est nul et
le nœud est marqué `computed=False`.

La confiance dépend du serveur de stockage : 'medium' si un serveur est
renseigné, 'low' sinon.
"""

from app.services.carbon.acv.storage import compute_data
from app.services.carbon.orchestrator import compute_impact


def _data_node(params):
    return {'id': '1', 'data': {'nodeType': 'data', 'params': params}}


def test_data_cloud_medium_is_neutral():
    """Média non calculé (cloud) : neutre dans un premier temps."""
    r = compute_data({
        'eco:contentSize': 100,
        'eco:storageMedium': 'cloud',
        'eco:retentionDays': 30,
    })
    assert r['impact_kg'] == 0.0
    assert r['computed'] is False
    assert r['reason'] == 'not_computed'


def test_data_missing_medium_is_neutral_with_reason():
    """Sans support sélectionné : neutre, avec la cause 'missing_medium'."""
    r = compute_data({'eco:contentSize': 100})
    assert r['impact_kg'] == 0.0
    assert r['computed'] is False
    assert r['reason'] == 'missing_medium'


def test_data_ssd_has_impact():
    """Données sur SSD : impact strictement positif et calculé."""
    r = compute_data({
        'eco:contentSize': 1000,
        'eco:storageMedium': 'ssd',
        'eco:retentionDays': 30,
    })
    assert r['impact_kg'] > 0.0
    assert r.get('computed', True) is True
    assert r['method'] == 'acv'


def test_data_hdd_has_impact():
    """Données sur HDD : impact strictement positif."""
    r = compute_data({
        'eco:contentSize': 1000,
        'eco:storageMedium': 'hdd',
        'eco:retentionDays': 30,
    })
    assert r['impact_kg'] > 0.0


def test_data_without_server_is_low_confidence():
    """Sans serveur de stockage, la confiance retombe à 'low'."""
    r = compute_data({
        'eco:contentSize': 1000,
        'eco:storageMedium': 'ssd',
        'eco:retentionDays': 30,
    })
    assert r['confidence'] == 'low'


def test_data_with_server_is_medium_confidence():
    """Avec un serveur de stockage, la confiance est 'medium'."""
    r = compute_data({
        'eco:contentSize': 1000,
        'eco:storageMedium': 'ssd',
        'eco:retentionDays': 30,
        'eco:storageServer': 'LIG SUMMER',
    })
    assert r['confidence'] == 'medium'


def test_data_linear_in_volume():
    """L'impact croît avec le volume stocké."""
    base = compute_data({
        'eco:contentSize': 1000, 'eco:storageMedium': 'ssd', 'eco:retentionDays': 30,
    })['impact_kg']
    triple = compute_data({
        'eco:contentSize': 3000, 'eco:storageMedium': 'ssd', 'eco:retentionDays': 30,
    })['impact_kg']
    assert triple > base


def test_data_node_via_orchestrator():
    """Le nœud Data est bien dispatché par l'orchestrateur."""
    result = compute_impact({'nodes': [_data_node({
        'eco:contentSize': 1000, 'eco:storageMedium': 'ssd', 'eco:retentionDays': 30,
    })]})
    assert result['total_impact_kg'] > 0.0

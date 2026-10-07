"""Tests du single score ACV (note générale).

Couvrent :
  - la structure de retour (single_score + contributions) ;
  - la linéarité (doublement d'un R_i -> doublement de sa contribution) ;
  - les cas limites (liste vide, valeurs nulles) ;
  - l'exclusion de l'eau ecologits (clé dédiée, non comparable aux seuils).
"""

import pytest

from app.services.carbon.acv.single_score import compute_single_score
from app.services.carbon.common import ACV_CRITERIA, WATER_ECOLOGITS_KEY


def _criterion(key, value):
    """Construit un critère minimal tel que produit par l'orchestrateur."""
    meta = ACV_CRITERIA[key]
    return {'key': key, 'label': meta['label'], 'value': value}


def test_single_score_structure():
    criteria = [_criterion('PEF-GWP', 10.0), _criterion('PEF-ADPe', 0.5)]
    result = compute_single_score(criteria)
    assert 'single_score' in result
    assert 'contributions' in result
    assert len(result['contributions']) == 2
    for c in result['contributions']:
        assert {'key', 'label', 'value', 'normalized', 'weight', 'score'} <= set(c)


def test_single_score_linearity():
    """Doubler la valeur d'un critère double sa contribution au score."""
    base = compute_single_score([_criterion('PEF-GWP', 10.0)])
    doubled = compute_single_score([_criterion('PEF-GWP', 20.0)])
    assert doubled['single_score'] == pytest.approx(base['single_score'] * 2, rel=1e-9)


def test_single_score_is_sum_of_contributions():
    criteria = [_criterion('PEF-GWP', 10.0), _criterion('PEF-ADPe', 0.5)]
    result = compute_single_score(criteria)
    total = sum(c['score'] for c in result['contributions'])
    assert result['single_score'] == pytest.approx(total, rel=1e-12)


def test_single_score_empty_criteria():
    result = compute_single_score([])
    assert result['single_score'] == 0.0
    assert result['contributions'] == []


def test_single_score_zero_values():
    criteria = [_criterion('PEF-GWP', 0.0), _criterion('PEF-ADPe', 0.0)]
    result = compute_single_score(criteria)
    assert result['single_score'] == 0.0
    # Les critères nuls restent présents (sous-délimitation à 0 côté front).
    assert len(result['contributions']) == 2


def test_single_score_ignores_ecologits_water():
    """L'eau ecologits (litres) n'entre pas dans le single score."""
    criteria = [
        _criterion('PEF-GWP', 10.0),
        {'key': WATER_ECOLOGITS_KEY, 'label': 'eau', 'value': 1000.0},
    ]
    result = compute_single_score(criteria)
    keys = [c['key'] for c in result['contributions']]
    assert WATER_ECOLOGITS_KEY not in keys


def test_single_score_order_follows_criteria_keys():
    """Les contributions suivent l'ordre d'affichage stable (CRITERIA_KEYS)."""
    criteria = [_criterion('PEF-ADPe', 0.5), _criterion('PEF-GWP', 10.0)]
    result = compute_single_score(criteria)
    keys = [c['key'] for c in result['contributions']]
    assert keys.index('PEF-GWP') < keys.index('PEF-ADPe')

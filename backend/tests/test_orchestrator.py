"""Tests de l'orchestrateur : rattachement des contributions PEF aux critères.

Couvrent `_attach_pef_contributions` :
  - présence des champs `pef_contribution` (mPt) et `pef_share` (%) ;
  - cohérence avec `compute_single_score` (mêmes valeurs) ;
  - contribution négative conservée (eau évitée) ;
  - critère sans contribution PEF (ex. PEF-LU) -> 0.0 ;
  - part nulle quand le score total est nul (pas de division par zéro).
"""

import pytest

from app.services.carbon.orchestrator import _attach_pef_contributions
from app.services.carbon.acv.single_score import compute_single_score


def _criterion(key, value):
    """Critère minimal tel que produit par _build_criteria."""
    return {'key': key, 'value': value}


def test_attach_pef_contributions_adds_fields():
    criteria = [_criterion('PEF-GWP', 10.0), _criterion('PEF-ADPe', 0.5)]
    single_score = compute_single_score(criteria)
    _attach_pef_contributions(criteria, single_score)
    for c in criteria:
        assert 'pef_contribution' in c
        assert 'pef_share' in c


def test_attach_pef_contributions_matches_single_score():
    """La contribution rattachée est exactement celle du single score (mPt)."""
    criteria = [_criterion('PEF-GWP', 10.0)]
    single_score = compute_single_score(criteria)
    _attach_pef_contributions(criteria, single_score)
    expected = single_score['contributions'][0]['score']
    assert criteria[0]['pef_contribution'] == pytest.approx(expected, rel=1e-12)


def test_attach_pef_contributions_share_sums_to_100():
    """Les parts des contributions positives somment à ~100 % du score total."""
    criteria = [_criterion('PEF-GWP', 10.0), _criterion('PEF-ADPe', 0.5)]
    single_score = compute_single_score(criteria)
    _attach_pef_contributions(criteria, single_score)
    total_share = sum(c['pef_share'] for c in criteria)
    assert total_share == pytest.approx(100.0, rel=1e-9)


def test_attach_pef_contributions_negative_kept():
    """Une contribution négative (eau évitée) est conservée telle quelle."""
    criteria = [_criterion('PEF-WU', -10.0)]
    single_score = compute_single_score(criteria)
    _attach_pef_contributions(criteria, single_score)
    assert criteria[0]['pef_contribution'] < 0.0


def test_attach_pef_contributions_unknown_key_is_zero():
    """Un critère absent des contributions (ex. PEF-LU) reçoit 0.0."""
    criteria = [_criterion('PEF-LU', 5.0)]
    single_score = compute_single_score(criteria)
    _attach_pef_contributions(criteria, single_score)
    assert criteria[0]['pef_contribution'] == 0.0
    assert criteria[0]['pef_share'] == 0.0


def test_attach_pef_contributions_zero_total_share():
    """Score total nul : la part vaut 0 (pas de division par zéro)."""
    criteria = [_criterion('PEF-GWP', 0.0)]
    single_score = compute_single_score(criteria)
    _attach_pef_contributions(criteria, single_score)
    assert criteria[0]['pef_share'] == 0.0

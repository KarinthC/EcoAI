"""Tests de l'orchestrateur : rattachement des contributions PEF aux critères.

Couvrent `_attach_pef_contributions` :
  - présence des champs `pef_contribution` (mPt) et `pef_share` (%) ;
  - cohérence avec `compute_single_score` (mêmes valeurs) ;
  - contribution négative conservée (eau évitée) ;
  - critère sans contribution PEF (ex. PEF-LU) -> 0.0 ;
  - part nulle quand le score total est nul (pas de division par zéro).

Couvrent `_attach_node_threshold_ratios` (heatmap nœuds × indicateurs) :
  - présence du bloc `threshold_ratios` par nœud ;
  - ratio en % du seuil mensuel par habitant ;
  - clés réellement présentes uniquement ;
  - nœud sans indicateurs -> pas de bloc ;
  - indicateur sans seuil (ex. PEF-LU) et eau ecologits exclus.
"""

import pytest

from app.services.carbon.orchestrator import (
    _attach_pef_contributions,
    _attach_node_threshold_ratios,
    _attach_node_pef_contributions,
)
from app.services.carbon.acv.single_score import compute_single_score
from app.services.carbon.common import ACV_CRITERIA, WATER_ECOLOGITS_KEY


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


# --- Ratio au seuil mensuel par nœud (heatmap nœuds × indicateurs) ----------

def test_attach_node_threshold_ratios_adds_block():
    """Un nœud portant des indicateurs reçoit un bloc threshold_ratios."""
    nodes = [{'id': '1', 'indicators': {'PEF-GWP': 10.0}}]
    _attach_node_threshold_ratios(nodes)
    assert 'threshold_ratios' in nodes[0]
    assert isinstance(nodes[0]['threshold_ratios'], dict)


def test_attach_node_threshold_ratios_value_in_percent():
    """Le ratio vaut (valeur / seuil mensuel) × 100, en %."""
    value = 10.0
    nodes = [{'id': '1', 'indicators': {'PEF-GWP': value}}]
    _attach_node_threshold_ratios(nodes)
    meta = ACV_CRITERIA['PEF-GWP']
    expected = value / meta['pb_monthly'] * 100.0
    assert nodes[0]['threshold_ratios']['PEF-GWP'] == pytest.approx(expected, rel=1e-12)


def test_attach_node_threshold_ratios_only_present_keys():
    """Seules les clés réellement présentes apparaissent (pas de clé à 0)."""
    nodes = [{'id': '1', 'indicators': {'PEF-GWP': 10.0}}]
    _attach_node_threshold_ratios(nodes)
    assert 'PEF-GWP' in nodes[0]['threshold_ratios']
    assert 'PEF-ADPe' not in nodes[0]['threshold_ratios']


def test_attach_node_threshold_ratios_skips_nodes_without_indicators():
    """Un nœud sans indicateurs (représentation) ne reçoit pas de bloc."""
    nodes = [{'id': '1'}, {'id': '2', 'indicators': {}}]
    _attach_node_threshold_ratios(nodes)
    assert 'threshold_ratios' not in nodes[0]
    assert 'threshold_ratios' not in nodes[1]


def test_attach_node_threshold_ratios_excludes_water_ecologits():
    """L'eau ecologits (litres) n'est pas comparable au seuil (m³ eq)."""
    nodes = [{'id': '1', 'indicators': {WATER_ECOLOGITS_KEY: 1000.0}}]
    _attach_node_threshold_ratios(nodes)
    assert WATER_ECOLOGITS_KEY not in nodes[0]['threshold_ratios']


def test_attach_node_threshold_ratios_excludes_key_without_threshold():
    """Un indicateur sans seuil mensuel (ex. PEF-LU) est ignoré."""
    nodes = [{'id': '1', 'indicators': {'PEF-LU': 5.0}}]
    _attach_node_threshold_ratios(nodes)
    assert 'PEF-LU' not in nodes[0]['threshold_ratios']


# --- Contributions PEF par nœud (treemap) -----------------------------------

def test_attach_node_pef_contributions_adds_block():
    """Un nœud portant des indicateurs reçoit un bloc pef_contributions."""
    nodes = [{'id': '1', 'indicators': {'PEF-GWP': 10.0, 'PEF-ADPe': 0.5}}]
    _attach_node_pef_contributions(nodes)
    assert 'pef_contributions' in nodes[0]
    assert isinstance(nodes[0]['pef_contributions'], dict)


def test_attach_node_pef_contributions_matches_single_score():
    """Les valeurs égalent le single score calculé sur les indicateurs du nœud."""
    nodes = [{'id': '1', 'indicators': {'PEF-GWP': 10.0}}]
    _attach_node_pef_contributions(nodes)
    expected = compute_single_score([{'key': 'PEF-GWP', 'value': 10.0}])
    assert nodes[0]['pef_contributions']['PEF-GWP'] == pytest.approx(
        expected['contributions'][0]['score'], rel=1e-12
    )


def test_attach_node_pef_contributions_only_present_keys():
    """Seules les clés réellement présentes apparaissent (pas de clé à 0)."""
    nodes = [{'id': '1', 'indicators': {'PEF-GWP': 10.0}}]
    _attach_node_pef_contributions(nodes)
    assert 'PEF-GWP' in nodes[0]['pef_contributions']
    assert 'PEF-ADPe' not in nodes[0]['pef_contributions']


def test_attach_node_pef_contributions_skips_nodes_without_indicators():
    """Un nœud sans indicateurs (représentation) ne reçoit pas de bloc."""
    nodes = [{'id': '1'}, {'id': '2', 'indicators': {}}]
    _attach_node_pef_contributions(nodes)
    assert 'pef_contributions' not in nodes[0]
    assert 'pef_contributions' not in nodes[1]


def test_attach_node_pef_contributions_sum_equals_node_score():
    """La somme des contributions d'un nœud égale son single score."""
    nodes = [{'id': '1', 'indicators': {'PEF-GWP': 10.0, 'PEF-ADPe': 0.5}}]
    _attach_node_pef_contributions(nodes)
    total = sum(nodes[0]['pef_contributions'].values())
    expected = compute_single_score([
        {'key': 'PEF-GWP', 'value': 10.0},
        {'key': 'PEF-ADPe', 'value': 0.5},
    ])['single_score']
    assert total == pytest.approx(expected, rel=1e-12)

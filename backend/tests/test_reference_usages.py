"""Tests des usages de référence ACV (avion, ciment, bœuf).

Couvrent :
  - la structure de retour (id, label_i18n, single_score, contributions) ;
  - la cohérence méthodologique (même formule PEF que le pipeline) ;
  - les ordres de grandeur (le bœuf domine largement l'avion et le ciment) ;
  - l'hypothèse de conversion de l'avion (1 p·km -> 1 h à 800 km/h).
"""

import pytest

from app.services.carbon.acv.reference_usages import (
    AIRCRAFT_KM_PER_HOUR,
    REFERENCE_USAGES,
    compute_reference_scores,
)
from app.services.carbon.acv.single_score import compute_single_score


def test_reference_scores_structure():
    results = compute_reference_scores()
    assert len(results) == len(REFERENCE_USAGES)
    for r in results:
        assert {'id', 'label_i18n', 'single_score', 'contributions'} <= set(r)
        assert r['single_score'] > 0


def test_reference_scores_match_single_score_formula():
    """Le score de référence utilise EXACTEMENT la formule du pipeline."""
    usage = next(u for u in REFERENCE_USAGES if u['id'] == 'cement_10kg')
    criteria = [{'key': k, 'value': v} for k, v in usage['indicators'].items()]
    expected = compute_single_score(criteria)['single_score']
    actual = next(r for r in compute_reference_scores() if r['id'] == 'cement_10kg')
    assert actual['single_score'] == pytest.approx(expected, rel=1e-12)


def test_beef_dominates_other_usages():
    """1 kg de bœuf a un single score bien supérieur à 10 kg de ciment."""
    scores = {r['id']: r['single_score'] for r in compute_reference_scores()}
    assert scores['beef_1kg'] > scores['cement_10kg']
    assert scores['beef_1kg'] > scores['aircraft_1h']


def test_aircraft_scales_with_distance():
    """L'avion est mis à l'échelle de la distance parcourue en 1 heure."""
    usage = next(u for u in REFERENCE_USAGES if u['id'] == 'aircraft_1h')
    # GWP de 1 p·km = 0.1093... ; ×800 km/h.
    assert usage['indicators']['PEF-GWP'] == pytest.approx(0.10933155608887393 * AIRCRAFT_KM_PER_HOUR)

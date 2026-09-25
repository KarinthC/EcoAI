"""Tests unitaires pour les nœuds neutres MoMa (représentation, sans calcul).

Les nœuds de représentation (Dataset, ML Model, Result Type, Analytical Pattern,
Task, User) servent uniquement à décrire le pipeline : ils ne portent aucun
modèle d'impact. Ils doivent donc :
  - retourner un impact nul (0.0) ;
  - signaler `computed=False` (exclu de l'affichage d'impact côté front) ;
  - exposer `confidence='none'` et `method='placeholder'`.
"""

from app.services.carbon.orchestrator import compute_impact, _compute_node


def _node(node_type, params=None):
    return {'id': '1', 'data': {'nodeType': node_type, 'params': params or {}}}


def test_dataset_is_neutral():
    """Le nœud Dataset est neutre : impact 0, non calculé."""
    r = _compute_node(_node('dataset', {'eco:name': 'ds'}))
    assert r['impact_kg'] == 0.0
    assert r['computed'] is False
    assert r['method'] == 'placeholder'
    assert r['confidence'] == 'none'


def test_ml_model_is_neutral():
    """« ML Model » est un nœud de représentation : pas d'impact, non calculé."""
    result = compute_impact({'nodes': [_node('ml_model', {'eco:name': 'm'})]})
    node = result['nodes'][0]
    assert node['impact_kg'] == 0.0
    assert node['computed'] is False
    assert node['confidence'] == 'none'
    assert result['total_impact_kg'] == 0.0


def test_meta_nodes_are_neutral():
    """Les nœuds méta (pattern, task, user) sont neutres."""
    for node_type in ('analytical_pattern', 'task', 'user'):
        r = _compute_node(_node(node_type))
        assert r['computed'] is False
        assert r['impact_kg'] == 0.0


def test_unknown_node_is_neutral():
    """Un nœud non répertorié ne doit PAS afficher de faux « impact faible »."""
    node = compute_impact({'nodes': [_node('inconnu')]})['nodes'][0]
    assert node['computed'] is False
    assert node['confidence'] == 'none'


def test_neutral_node_does_not_affect_total():
    """Un pipeline composé d'un seul nœud neutre a un impact total nul."""
    result = compute_impact({'nodes': [_node('dataset')]})
    assert result['total_impact_kg'] == 0.0
    assert result['nodes'][0]['computed'] is False

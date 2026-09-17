"""Tests unitaires pour le nœud « Données » (représentation, sans calcul).

Le nœud « Données » sert uniquement à représenter une étape données dans le
pipeline : il ne porte aucun modèle d'impact tant que celui-ci n'est pas
implémenté. Il doit donc :
  - retourner un impact nul (0.0) ;
  - signaler `computed=False` (exclu de l'affichage d'impact côté front) ;
  - exposer `confidence='none'` et `method='placeholder'`.
"""

from app.services.carbon.acv.datasource import compute
from app.services.carbon.orchestrator import compute_impact, NODE_COMPUTERS


def test_datasource_registered():
    """Le label « Données » doit être dispatché vers le nœud datasource."""
    assert 'Données' in NODE_COMPUTERS


def test_datasource_zero_impact():
    """Aucun impact, quelle que soit la saisie."""
    r = compute({'nom': 'Dataset', 'format': 'CSV', 'taille': 500})
    assert r['impact_kg'] == 0.0


def test_datasource_not_computed():
    """Le nœud est signalé comme non calculé."""
    r = compute({'taille': 500})
    assert r['computed'] is False


def test_datasource_metadata():
    """Métadonnées neutres attendues par le front."""
    r = compute({})
    assert r['method'] == 'placeholder'
    assert r['confidence'] == 'none'
    assert r['level'] == 'low'
    assert isinstance(r['message'], str) and r['message']


def test_modele_ml_is_neutral():
    """« Modèle ML » est un nœud de représentation : pas d'impact, non calculé."""
    pipeline = {
        'nodes': [
            {'id': '1', 'data': {'label': 'Modèle ML', 'params': {'nom': 'm', 'version': 1}}},
        ]
    }
    result = compute_impact(pipeline)
    node = result['nodes'][0]
    assert node['impact_kg'] == 0.0
    assert node['computed'] is False
    assert node['confidence'] == 'none'
    assert result['total_impact_kg'] == 0.0


def test_unknown_node_is_neutral():
    """Un nœud non répertorié ne doit PAS afficher de faux « impact faible »."""
    pipeline = {'nodes': [{'id': 'x', 'data': {'label': 'Inconnu', 'params': {}}}]}
    node = compute_impact(pipeline)['nodes'][0]
    assert node['computed'] is False
    assert node['confidence'] == 'none'


def test_datasource_does_not_affect_total():
    """Un pipeline composé du seul nœud « Données » a un impact total nul."""
    pipeline = {
        'nodes': [
            {'id': '1', 'data': {'label': 'Données', 'params': {'taille': 1000}}},
        ]
    }
    result = compute_impact(pipeline)
    assert result['total_impact_kg'] == 0.0
    assert result['nodes'][0]['computed'] is False
    assert result['nodes'][0]['impact_kg'] == 0.0

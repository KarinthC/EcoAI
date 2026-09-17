# backend/app/services/carbon/acv/datasource.py
"""Nœud « Données » — nœud de représentation, SANS calcul d'impact.

Ce nœud sert uniquement à représenter une étape « données » dans le pipeline
(volume, format, nom). Il n'a PAS encore de modèle de calcul derrière : son
impact est neutre (0) et il est exclu de l'affichage d'impact côté front
(flag `computed=False`).

Il est rattaché au sous-package ACV par cohérence de rangement, mais il
n'utilise ni données ACV ni ecologits tant que le modèle n'est pas implémenté.
"""


def compute(params: dict) -> dict:
    """Retourne un résultat neutre : aucun impact, aucune prise en compte.

    Args:
        params: dict du front (conservé pour la traçabilité). Les clés
            attendues (`nom`, `format`, `taille`) ne sont pas utilisées ici.

    Returns:
        dict au format de l'orchestrateur, avec `computed=False` pour signaler
        au front que ce nœud ne doit pas être compté ni affiché comme impactant.
    """
    return {
        'impact_kg': 0.0,
        'computed': False,
        'method': 'placeholder',
        'confidence': 'none',
        'level': 'low',
        'message': "Nœud de représentation du pipeline : aucun impact calculé.",
    }

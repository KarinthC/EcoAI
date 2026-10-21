# backend/app/services/carbon/acv/single_score.py
"""Single score PEF : agrégation des critères en une valeur unique (mPt).

Méthodologie officielle (méthode EF 3.1, JRC 2023, Recommandation (UE)
2021/2279) :
    Pour chaque catégorie d'impact i :
        R_i : résultat caractérisé (ex. kg CO₂ eq, mol H⁺ eq, ...).
        N_i = R_i / NF_i   (normalisation : NF_i = impact annuel moyen d'un
                            citoyen mondial pour la catégorie i)
        S_i = N_i × WF_i   (pondération : WF_i = importance relative, en %)
    Single score :
        S = Σ_i S_i = Σ_i (R_i / NF_i × WF_i)

Le score est exprimé en MILLI-POINTS (mPt) : S × 1000.

Les facteurs NF_i et WF_i proviennent de `common.PEF_NORMALIZATION` et
`common.PEF_WEIGHTING` (EF 3.1). Ils sont documentés et sourcés : toute
modification doit être accompagnée d'un test.

NOTE : une contribution peut être NÉGATIVE (ex. eau évitée). Elle est
conservée telle quelle dans le score (méthodologiquement valide), mais le
front l'exclut de l'affichage des barres empilées (une barre ne peut pas être
négative).
"""

from ..common import (
    CRITERIA_KEYS,
    PEF_NORMALIZATION,
    PEF_WEIGHTING,
    WATER_ECOLOGITS_KEY,
)
def _normalization_factor(key: str) -> float:
    """Facteur de normalisation NF_i (EF 3.1). 0.0 si le critère est inconnu."""
    return PEF_NORMALIZATION.get(key, 0.0)


def _weighting_factor(key: str) -> float:
    """Facteur de pondération WF_i (EF 3.1). 0.0 si le critère est inconnu."""
    return PEF_WEIGHTING.get(key, 0.0)
def compute_single_score(criteria: list) -> dict:
    """Calcule le single score PEF (mPt) et la contribution de chaque indicateur.

    `criteria` est la liste produite par l'orchestrateur : chaque entrée porte
    au minimum `key` et `value` (valeur affichée, déjà convertie). L'eau
    ecologits (clé dédiée, en litres) est ignorée : non comparable aux seuils.

    Retourne un dict :
        {
          'single_score': float,          # S en mPt (Σ S_i × 1000)
          'contributions': [              # une entrée par critère contributif
            {'key', 'label', 'value', 'normalized', 'weight', 'score'},
            ...
          ],
        }

    `score` est la contribution en mPt. Les contributions sont ordonnées comme
    CRITERIA_KEYS (ordre d'affichage stable côté front). Les critères de score
    nul sont conservés (utile pour afficher une sous-délimitation à 0).
    """
    contributions = []
    total = 0.0

    for criterion in criteria:
        key = criterion.get('key')
        if not key or key == WATER_ECOLOGITS_KEY:
            continue

        value = criterion.get('value') or 0.0
        nf = _normalization_factor(key)
        weight = _weighting_factor(key)
        if not nf:
            # Critère sans facteur PEF (ex. PEF-LU) : contribution nulle.
            normalized = 0.0
            score = 0.0
        else:
            normalized = value / nf
            score = normalized * weight

        contributions.append({
            'key': key,
            'label': criterion.get('label', key),
            'value': value,
            'normalized': normalized,
            'weight': weight,
            # Contribution en mPt (×1000) pour un affichage lisible.
            'score': score * 1000.0,
        })
        total += score

    # Ordre stable : on suit CRITERIA_KEYS quand la clé y figure.
    order = {key: idx for idx, key in enumerate(CRITERIA_KEYS)}
    contributions.sort(key=lambda c: order.get(c['key'], len(order)))

    return {
        'single_score': total * 1000.0,
        'contributions': contributions,
    }


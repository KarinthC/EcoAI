# backend/app/services/carbon/acv/single_score.py
"""Single score ACV : agrégation des critères PEF en une valeur unique.

Principe (méthodologie ACV classique, cf. openLCA / ReCiPe) :

    Pour chaque catégorie d'impact i :
        R_i : résultat caractérisé (ex. kg CO₂ eq, mol H⁺ eq, ...).
        N_i = R_i × NF_i   (normalisation : NF_i = facteur de normalisation)
        S_i = N_i × W_i    (pondération : W_i = poids de la catégorie)
    Single score :
        S = Σ_i S_i = Σ_i (R_i × NF_i × W_i)

Le single score est SANS DIMENSION : il n'a de sens que comparé à lui-même
(entre pipelines, ou par rapport à une échelle de référence).

HYPOTHÈSES (à remplacer par des facteurs ADEME/PEF sourcés dès qu'ils seront
disponibles) :
  - Normalisation : NF_i = 1 / seuil mensuel par habitant (déjà défini dans
    common.ACV_CRITERIA[key]['pb_monthly']). On réutilise ainsi la même
    référence que le calcul des ratios de criticité, ce qui garantit la
    cohérence de l'échelle.
  - Pondération : W_i = 1 pour tous les critères (aucune hiérarchie imposée
    tant qu'aucune source de pondération n'est retenue).

Ces hypothèses sont volontairement explicites : toute modification des facteurs
doit être sourcée (référence ou hypothèse documentée) et accompagnée d'un test.
"""

from ..common import ACV_CRITERIA, CRITERIA_KEYS, WATER_ECOLOGITS_KEY

# Poids par critère (W_i). Valeur 1.0 par défaut : aucune pondération imposée.
# Clé absente -> 1.0 (cf. _weight_for).
WEIGHTS = {key: 1.0 for key in CRITERIA_KEYS}


def _normalization_factor(key: str) -> float:
    """Facteur de normalisation NF_i = 1 / seuil mensuel par habitant.

    Retourne 0.0 si le critère n'a pas de seuil (contribution nulle au score).
    """
    meta = ACV_CRITERIA.get(key)
    if not meta:
        return 0.0
    pb_monthly = meta.get('pb_monthly')
    if not pb_monthly:
        return 0.0
    return 1.0 / pb_monthly


def _weight_for(key: str) -> float:
    """Poids W_i d'un critère (1.0 par défaut)."""
    return WEIGHTS.get(key, 1.0)


def compute_single_score(criteria: list) -> dict:
    """Calcule le single score ACV et la contribution de chaque indicateur.

    `criteria` est la liste produite par l'orchestrateur : chaque entrée porte
    au minimum `key` et `value` (valeur affichée, déjà convertie). L'eau
    ecologits (clé dédiée, en litres) est ignorée : non comparable aux seuils.

    Retourne un dict :
        {
          'single_score': float,          # S = Σ S_i (sans dimension)
          'contributions': [              # une entrée par critère contributif
            {'key', 'label', 'value', 'normalized', 'weight', 'score'},
            ...
          ],
        }

    Les contributions sont ordonnées comme CRITERIA_KEYS (ordre d'affichage
    stable côté front). Les critères de score nul sont conservés (utile pour
    afficher une sous-délimitation à 0 dans la barre empilée).
    """
    contributions = []
    total = 0.0

    for criterion in criteria:
        key = criterion.get('key')
        if not key or key == WATER_ECOLOGITS_KEY:
            continue

        value = criterion.get('value') or 0.0
        nf = _normalization_factor(key)
        weight = _weight_for(key)
        normalized = value * nf
        score = normalized * weight

        contributions.append({
            'key': key,
            'label': criterion.get('label', key),
            'value': value,
            'normalized': normalized,
            'weight': weight,
            'score': score,
        })
        total += score

    # Ordre stable : on suit CRITERIA_KEYS quand la clé y figure.
    order = {key: idx for idx, key in enumerate(CRITERIA_KEYS)}
    contributions.sort(key=lambda c: order.get(c['key'], len(order)))

    return {
        'single_score': total,
        'contributions': contributions,
    }

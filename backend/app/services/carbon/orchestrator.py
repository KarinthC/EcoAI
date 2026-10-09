# backend/app/services/carbon/orchestrator.py
import logging

# Famille ACV (données ACV documentées, multi-indicateurs)
from .acv import (
    datasource as acv_datasource,
    training as acv_training,
    inference as acv_inference,
    operator as acv_operator,
    storage as acv_storage,
)
from .acv.single_score import compute_single_score
from .acv.reference_usages import compute_reference_scores
# Famille Ecologits (estimations, vouées à évoluer)
from .ecologits import llm_call, llm_expert, video
from .common import (
    ACV_CRITERIA, CRITERIA_KEYS, ECOLOGITS_CRITERIA, WATER_ECOLOGITS_KEY,
)

logger = logging.getLogger(__name__)

# Familles de méthodes :
#   - ACV : nœuds dont toutes les contributions aux critères sont connues.
#   - ecologits : nœuds dont SEULES quelques contributions (GWP/ADPe/ADPf/eau)
#     sont remontées -> les autres critères sont donc partiels.
ACV_METHOD = 'acv'
ECOLOGITS_METHOD = 'ecologits'

# Dispatch explicite label -> fonction compute.
# Les nœuds sont regroupés par famille : ACV (stable) puis Ecologits (volatile).
NODE_COMPUTERS = {
    # Nœuds de représentation, sans calcul (impact neutre).
    'Données': acv_datasource.compute,
    'Modèle ML': acv_datasource.compute,
    'Données persistantes': acv_storage.compute_hdd,
    'Données SSD temporaires': acv_storage.compute_ssd,
    'Entrainement': acv_training.compute,
    'Inférence': acv_inference.compute,
    'Opérateur': acv_operator.compute,
    # --- Famille Ecologits (voués à changer) ---
    'LLM Call': llm_call.compute,
    'LLM Expert': llm_expert.compute,
    'Video Generation': video.compute, 
}


def _aggregate_indicators(nodes_analysis: list) -> dict:
    """Agrège les indicateurs de tous les nœuds qui en exposent.

    Additionne indicateur par indicateur. Les clés sont désormais des clés de
    critères ACV (PEF-*) : les contributions ACV et ecologits (GWP, ADPe, ADPf)
    sont volontairement fusionnées car exprimées dans les MÊMES unités. L'eau
    ecologits reste sous sa clé dédiée `PEF-WU_ecologits` (litres).

    Les valeurs sont laissées en pleine précision (pas d'arrondi à 6 décimales
    qui écraserait les petits indicateurs comme PEF-PM ou PEF-CTUh-c).
    """
    total = {}
    for node in nodes_analysis:
        for key, value in node.get('indicators', {}).items():
            total[key] = total.get(key, 0.0) + value
    # PEF-LU (usage des sols) est exclu de l'agrégat affiché (pas de seuil ADEME).
    total.pop('PEF-LU', None)
    return total


def _has_ecologits_node(nodes_analysis: list) -> bool:
    """Vrai si au moins un nœud ecologits est présent dans l'analyse."""
    return any(node.get('method') == ECOLOGITS_METHOD for node in nodes_analysis)


def _build_criteria(total_indicators: dict, has_ecologits: bool) -> list:
    """Construit la liste des critères affichables (à égalité) pour le front.

    Pour chaque critère ACV :
      - value_acv        : contribution ACV seule (en unité brute ACV)
      - value_ecologits  : contribution ecologits seule (si critère remonté)
      - value_total      : somme (ACV + ecologits) en unité ACV
      - display_factor   : conversion appliquée avant affichage (ex. m³ -> L)
      - value_display    : valeur totale convertie pour l'affichage
      - ratio            : value_total / seuil mensuel par habitant
      - has_partial      : True si des contributions manquent (ecologits présent
                           et critère non remonté par ecologits)
      - tooltip          : explication du critère
    """
    criteria = []
    for key in CRITERIA_KEYS:
        meta = ACV_CRITERIA[key]
        value_acv = total_indicators.get(key, 0.0)

        display_factor = meta.get('display_factor', 1.0)
        value_display = value_acv * display_factor

        # Eau : la contribution ecologits (WCF, en litres) est affichée comme
        # une ligne SÉPARÉE de la contribution ACV (PEF-WU, en m³ eq).
        # Méthodologies et unités différentes -> aucune fusion ni conversion.
        value_ecologits_display = None
        if key == 'PEF-WU':
            wcf = total_indicators.get(WATER_ECOLOGITS_KEY, 0.0)
            if wcf:
                value_ecologits_display = wcf

        # Le seuil est converti dans la MÊME unité que la valeur affichée
        # (ex. m³ -> L) pour que le ratio soit cohérent.
        pb_monthly = meta.get('pb_monthly')
        threshold_display = pb_monthly * display_factor if pb_monthly else None

        # Le ratio porte sur la contribution ACV seule : l'unité ecologits
        # (litres) n'est pas comparable au seuil (m³ eq).
        ratio = None
        if threshold_display:
            ratio = value_display / threshold_display

        # Un critère est partiel si des contributions ne sont pas comptées.
        # ecologits ne remonte que GWP / ADPe / ADPf / eau : les autres critères
        # sont donc sous-estimés dès qu'un nœud ecologits existe.
        is_reported_by_ecologits = (key in ECOLOGITS_CRITERIA) or (key == 'PEF-WU')
        has_partial = has_ecologits and not is_reported_by_ecologits

        criteria.append({
            'key': key,
            'label': meta['label'],
            'unit': meta['unit'],
            'description': meta['description'],
            # Valeurs en pleine précision : le front gère le formatage (les
            # indicateurs s'étendent sur de nombreux ordres de grandeur).
            'value': value_display,
            'value_ecologits': value_ecologits_display,
            'ratio': ratio,
            'threshold_monthly': threshold_display,
            'has_partial': has_partial,
        })
    return criteria


def _attach_pef_contributions(criteria: list, single_score: dict) -> None:
    """Rattache à chaque critère sa contribution au single score PEF.

    Ajoute deux champs à chaque critère (mutation en place) :
      - pef_contribution : contribution de l'indicateur au single score (mPt),
                           telle que calculée par compute_single_score() ;
      - pef_share        : part de cette contribution dans le score total (%).

    La contribution peut être NÉGATIVE (ex. eau évitée) : elle est conservée
    telle quelle (méthodologiquement valide) ; le front la signale sans dessiner
    de segment négatif. Un critère absent des contributions (ex. PEF-LU) reçoit
    0.0. L'eau ecologits (clé dédiée) n'entre pas dans le single score.
    """
    by_key = {c['key']: c for c in single_score.get('contributions', [])}
    total = single_score.get('single_score', 0.0)
    for criterion in criteria:
        contribution = by_key.get(criterion['key'])
        score = contribution['score'] if contribution else 0.0
        criterion['pef_contribution'] = score
        # Part du score total : indéfinie si le score total est nul.
        criterion['pef_share'] = (score / total * 100.0) if total else 0.0


def _global_level(criteria: list) -> str:
    """Couleur globale : celle du PIRE facteur (ratio valeur/seuil le plus haut).

    - ratio max >= 1        -> 'high'   (rouge) : dépasse le budget mensuel
    - ratio max >= 0.1      -> 'medium' (orange) : proche du budget
    - sinon                 -> 'low'    (vert) : largement sous le budget
    """
    ratios = [c['ratio'] for c in criteria
              if c.get('ratio') is not None]
    if not ratios:
        return 'low'
    worst = max(ratios)
    if worst >= 1.0:
        return 'high'
    if worst >= 0.1:
        return 'medium'
    return 'low'


def compute_impact(pipeline: dict) -> dict:
    total_impact = 0.0
    nodes_analysis = []

    for node in pipeline.get('nodes', []):
        label = node.get('data', {}).get('label', '')
        params = node.get('data', {}).get('params', {})
        node_id = node['id']

        compute_func = NODE_COMPUTERS.get(label)
        if not compute_func:
            # Nœud non répertorié : traité comme un nœud de représentation
            # (aucun calcul, donc exclu de l'affichage d'impact).
            nodes_analysis.append({
                'id': node_id,
                'impact_kg': 0.0,
                'computed': False,
                'level': 'low',
                'method': 'placeholder',
                'confidence': 'none',
            })
            continue

        try:
            result = compute_func(params)
            # Lecture défensive : un compute() défaillant (dict incomplet) ne
            # doit jamais faire échouer toute l'analyse. On retombe sur des
            # valeurs neutres si les clés attendues sont absentes.
            node_impact = float(result.get('impact_kg', 0.0))
            # Par défaut un nœud est calculé ; `computed=False` signale un nœud
            # de représentation (aucun modèle) à exclure de l'affichage d'impact.
            node_computed = result.get('computed', True)
            node_entry = {
                'id': node_id,
                'impact_kg': node_impact,
                'computed': node_computed,
                'level': result.get('level', 'low'),
                # Métadonnées de méthode (prépare l'UI : ecologits = peu précis).
                'method': result.get('method', 'unknown'),
                'confidence': result.get('confidence', 'unknown'),
            }
        except Exception as e:
            logger.error(f"Erreur lors du calcul du nœud {label} (id={node_id}): {e}")
            # En cas d'erreur, on n'affiche pas de faux niveau d'impact.
            nodes_analysis.append({
                'id': node_id,
                'impact_kg': 0.0,
                'computed': False,
                'level': 'low',
                'method': 'unknown',
                'confidence': 'none',
            })
            continue

        # Bloc d'indicateurs : tous les critères portés par le nœud.
        if 'indicators' in result:
            node_entry['indicators'] = result['indicators']

        nodes_analysis.append(node_entry)
        total_impact += node_impact

    # Suggestions globales.
    # On renvoie des CODES de suggestion (et non du texte français) afin que le
    # frontend les traduise dans la langue active. `params` porte les éventuelles
    # valeurs à interpoler. Le format est volontairement proche de
    # {'code': ..., 'params': {...}} : le front résout « suggestions.<code> ».
    global_suggestions = []
    if total_impact > 30:
        global_suggestions.append({
            'code': 'veryHighFootprint',
            'params': {'impact': round(total_impact, 2)},
        })
    if total_impact > 10:
        global_suggestions.append({
            'code': 'reduceEpochsOrBatch',
            'params': {},
        })

    # Agrégat de tous les critères + construction de l'affichage "à égalité".
    total_indicators = _aggregate_indicators(nodes_analysis)
    has_ecologits = _has_ecologits_node(nodes_analysis)
    criteria = _build_criteria(total_indicators, has_ecologits)

    # Single score ACV (note générale) : agrégation normalisée + pondérée des
    # critères, avec la contribution de chaque indicateur (barre empilée front).
    single_score = compute_single_score(criteria)

    # On rattache à chaque critère sa contribution au single score PEF (mPt) et
    # sa part du score total (%). Le front affiche ainsi, dans l'onglet d'un
    # indicateur, une barre « contribution au score PEF » cohérente avec la
    # barre empilée de l'analyse globale (mêmes NF/WF EF 3.1).
    _attach_pef_contributions(criteria, single_score)

    # Usages de référence (avion, ciment, bœuf) : même formule PEF, pour
    # contextualiser le single score du pipeline.
    reference_usages = compute_reference_scores()

    return {
        'total_impact_kg': round(total_impact, 2),
        'total_indicators': total_indicators,
        'criteria': criteria,
        'single_score': single_score,
        'reference_usages': reference_usages,
        'has_ecologits_node': has_ecologits,
        'global_level': _global_level(criteria),
        'nodes': nodes_analysis,
        'suggestions': global_suggestions
    }
# backend/app/services/carbon/orchestrator.py
import logging

# Famille ACV (données ACV documentées, multi-indicateurs)
from .acv import datasource as acv_datasource, training as acv_training, inference as acv_inference
# Famille Ecologits (estimations, vouées à évoluer)
from .ecologits import llm_call, llm_expert, video
from .equivalences import compute_global_equivalences, format_equivalences

logger = logging.getLogger(__name__)

# Dispatch explicite label -> fonction compute.
# Les nœuds sont regroupés par famille : ACV (stable) puis Ecologits (volatile).
NODE_COMPUTERS = {
    # --- Famille ACV ---
    'Données': acv_datasource.compute,
    'Entrainement': acv_training.compute,
    'Inférence': acv_inference.compute,
    # --- Famille Ecologits (voués à changer) ---
    'LLM Call': llm_call.compute,
    'LLM Expert': llm_expert.compute,
    'Video Generation': video.compute, 
}


def _aggregate_indicators(nodes_analysis: list) -> dict:
    """Agrège les indicateurs ACV de tous les nœuds qui en exposent.

    Additionne indicateur par indicateur. Seuls les nœuds portant une clé
    `indicators` (nœuds ACV) sont inclus : les indicateurs ecologits ne sont
    pas comparables et ne sont donc pas mélangés ici.
    """
    total = {}
    for node in nodes_analysis:
        for key, value in node.get('indicators', {}).items():
            total[key] = total.get(key, 0.0) + value
    return {k: round(v, 6) for k, v in total.items()}


def compute_impact(pipeline: dict) -> dict:
    total_impact = 0.0
    nodes_analysis = []

    for node in pipeline.get('nodes', []):
        label = node.get('data', {}).get('label', '')
        params = node.get('data', {}).get('params', {})
        node_id = node['id']

        compute_func = NODE_COMPUTERS.get(label)
        if not compute_func:
            nodes_analysis.append({
                'id': node_id,
                'impact_kg': 0.0,
                'level': 'low',
                'message': f"Type de nœud inconnu : {label}"
            })
            continue

        try:
            result = compute_func(params)
        except Exception as e:
            logger.error(f"Erreur lors du calcul du nœud {label} (id={node_id}): {e}")
            nodes_analysis.append({
                'id': node_id,
                'impact_kg': 0.0,
                'level': 'low',
                'message': f"Erreur de calcul : {e}"
            })
            continue

        node_impact = result['impact_kg']
        node_entry = {
            'id': node_id,
            'impact_kg': node_impact,
            'level': result['level'],
            'message': result.get('message', ''),
            # Métadonnées de méthode (prépare l'UI : ecologits = peu précis).
            'method': result.get('method', 'unknown'),
            'confidence': result.get('confidence', 'unknown'),
        }

        # Enrichissement piloté par le CONTENU du résultat (pas par le label) :
        # ajouter un nœud ne casse donc rien ici.
        if 'energy_kwh' in result:
            node_entry['energy_kwh'] = result['energy_kwh']
            node_entry['equivalences'] = format_equivalences(node_impact, result['energy_kwh'])

        # Bloc ACV complet : tous les indicateurs, pas seulement le GWP.
        if 'indicators' in result:
            node_entry['indicators'] = result['indicators']

        nodes_analysis.append(node_entry)
        total_impact += node_impact

    # Suggestions globales
    global_suggestions = []
    if total_impact > 30:
        global_suggestions.append("L'empreinte totale est très élevée. Pensez à utiliser des modèles pré-entraînés.")
    if total_impact > 10:
        global_suggestions.append("Réduire le nombre d'epochs ou la taille du batch peut significativement baisser l'impact.")

    # Équivalences globales basées sur ecologits
    equivalences = compute_global_equivalences(total_impact)

    return {
        'total_impact_kg': round(total_impact, 2),
        'total_indicators': _aggregate_indicators(nodes_analysis),
        'nodes': nodes_analysis,
        'suggestions': global_suggestions,
        'equivalences': equivalences
    }
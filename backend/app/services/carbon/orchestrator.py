# backend/app/services/carbon/orchestrator.py
import logging
from .common import compute_equivalences
from . import datasource, training, inference, llm_call, llm_expert

logger = logging.getLogger(__name__)

# Mapping label -> fonction compute
#liste des noeuds
NODE_COMPUTERS = {
    'Données': datasource.compute,
    'Entrainement': training.compute,
    'Inférence': inference.compute,
    'LLM Call': llm_call.compute,
    'LLM Expert': llm_expert.compute,
}

def compute_impact(pipeline: dict) -> dict:
    total_impact = 0.0
    nodes_analysis = []

    for node in pipeline.get('nodes', []):
        label = node.get('data', {}).get('label', '')
        params = node.get('data', {}).get('params', {})
        node_id = node['id']

        compute_func = NODE_COMPUTERS.get(label)
        if not compute_func:
            # Nœud inconnu : impact nul
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

        nodes_analysis.append({
            'id': node_id,
            'impact_kg': result['impact_kg'],
            'level': result['level'],
            'message': result.get('message', '')
        })
        total_impact += result['impact_kg']

    # Suggestions globales
    global_suggestions = []
    if total_impact > 30:
        global_suggestions.append("L'empreinte totale est très élevée. Pensez à utiliser des modèles pré-entraînés.")
    if total_impact > 10:
        global_suggestions.append("Réduire le nombre d'epochs ou la taille du batch peut significativement baisser l'impact.")

    equivalences = compute_equivalences(total_impact)

    return {
        'total_impact_kg': round(total_impact, 2),
        'nodes': nodes_analysis,
        'suggestions': global_suggestions,
        'equivalences': equivalences
    }
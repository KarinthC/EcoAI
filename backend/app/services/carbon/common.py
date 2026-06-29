import logging

logger = logging.getLogger(__name__)

def get_level(impact_kg: float) -> str:
    if impact_kg < 0.1:
        return 'low'
    elif impact_kg < 1.0:
        return 'medium'
    else:
        return 'high'

def extract_gwp(impacts) -> float:
    """Extrait la valeur GWP (kgCO₂eq) d'un objet Impacts ecologits.
    Retourne 0.0 si l'objet est None ou mal formé."""
    if impacts is None:
        logger.warning("extract_gwp : impacts est None")
        return 0.0
    try:
        if hasattr(impacts.gwp, 'value'):
            gwp_range = impacts.gwp.value
            return (gwp_range.min + gwp_range.max) / 2
        else:
            return impacts.gwp.magnitude
    except Exception as e:
        logger.error(f"Erreur extraction GWP : {e}")
        return 0.0

def compute_equivalences(total_impact_kg: float) -> dict:
    return {
        'km_voiture': round(total_impact_kg * 4.5, 1),
        'heures_streaming': round(total_impact_kg * 2.3, 1),
        'repas_equivalent': round(total_impact_kg * 0.1, 1)
    }
# backend/app/services/carbon/common.py

def get_level(impact_kg: float) -> str:
    """Détermine le niveau de criticité en fonction de l'impact."""
    if impact_kg < 0.1:
        return 'low'
    elif impact_kg < 1.0:
        return 'medium'
    else:
        return 'high'

def extract_gwp(impacts) -> float:
    """Extrait la valeur GWP (kgCO₂eq) d'un objet Impacts ecologits.
    Prend en charge les RangeValue (moyenne min/max) ou les valeurs fixes."""
    if hasattr(impacts.gwp, 'value'):
        gwp_range = impacts.gwp.value
        return (gwp_range.min + gwp_range.max) / 2
    return impacts.gwp.magnitude

def compute_equivalences(total_impact_kg: float) -> dict:
    """Retourne les équivalences grand public."""
    return {
        'km_voiture': round(total_impact_kg * 4.5, 1),
        'heures_streaming': round(total_impact_kg * 2.3, 1),
        'repas_equivalent': round(total_impact_kg * 0.1, 1)
    }
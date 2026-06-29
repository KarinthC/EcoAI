# backend/app/services/carbon/inference.py
from .common import get_level

def compute(params: dict) -> dict:
    COEFFS = {'base': 0.1, 'par_lot': 0.0002}
    impact = COEFFS['base']
    taille_lot = float(params.get('taille_lot', 0))
    impact += taille_lot * COEFFS['par_lot']
    
    message = ''
    if impact >= 20:
        message = f"Impact élevé pour l'inférence ({impact:.1f} kgCO₂)."
    
    return {
        'impact_kg': round(impact, 4),
        'level': get_level(impact),
        'message': message
    }
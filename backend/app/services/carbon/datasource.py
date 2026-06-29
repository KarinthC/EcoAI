# backend/app/services/carbon/datasource.py
from .common import get_level

def compute(params: dict) -> dict:
    COEFFS = {'base': 0.0, 'par_go': 0.01}
    impact = COEFFS['base']
    taille = float(params.get('taille', 0))
    impact += taille * COEFFS['par_go']
    
    message = ''
    if impact >= 20:
        message = f"Impact élevé ({impact:.1f} kgCO₂). Réduire la taille des données ?"
    
    return {
        'impact_kg': round(impact, 4),
        'level': get_level(impact),
        'message': message
    }
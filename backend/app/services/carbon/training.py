# backend/app/services/carbon/training.py
from .common import get_level

def compute(params: dict) -> dict:
    COEFFS = {'base': 0.5, 'par_param': 0.0001, 'par_epoch': 0.05, 'par_batch': 0.001}
    impact = COEFFS['base']
    nb_param = float(params.get('parametres', 0))
    nb_epochs = float(params.get('epochs', 0))
    batch_size = float(params.get('batch_size', 1))
    
    impact += nb_param * COEFFS['par_param']
    impact += nb_epochs * COEFFS['par_epoch']
    impact += batch_size * COEFFS['par_batch']
    
    message = ''
    if impact >= 20:
        message = f"L'impact du nœud Entrainement est élevé ({impact:.1f} kgCO₂). Essayez de réduire les paramètres."
    
    return {
        'impact_kg': round(impact, 4),
        'level': get_level(impact),
        'message': message
    }
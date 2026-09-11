# backend/app/services/carbon/acv/datasource.py
"""Nœud « Données » — provisoirement rattaché à la famille ACV.

Le calcul actuel reste une estimation forfaitaire (stockage/mouvement de
données), il ne consomme pas encore de données ACV. Il est placé dans le
sous-package ACV car il n'utilise pas ecologits et est destiné à évoluer
vers un modèle ACV (stockage, transfert, déduplication...).
"""

from ..common import get_level


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
        # Pas encore d'indicators ACV tant que le modèle n'est pas implémenté.
        'method': 'acv',
        'confidence': 'low',
        'level': get_level(impact),
        'message': message,
    }

# backend/app/services/carbon/common.py
import logging

logger = logging.getLogger(__name__)

# Zone de mix électrique par défaut : WOR = moyenne mondiale (comportement ecologits).
DEFAULT_LOCATION = "WOR"


def normalize_location(location) -> str:
    """Normalise un code de localisation datacenter (ISO 3166-1 alpha-3).

    Retourne DEFAULT_LOCATION ("WOR") si la valeur est absente, vide ou None.
    La valeur est mise en majuscules pour tolérer les saisies en minuscules.
    """
    if location is None:
        return DEFAULT_LOCATION
    location = str(location).strip().upper()
    return location or DEFAULT_LOCATION


def get_level(impact_kg: float) -> str:
    """Détermine le niveau de criticité en fonction de l'impact."""
    if impact_kg < 0.1:
        return 'low'
    elif impact_kg < 1.0:
        return 'medium'
    else:
        return 'high'

def _extract_value(impact_obj) -> float:
    """
    Extrait une valeur numérique d'un objet d'impact ecologits.
    Gère à la fois les RangeValue (avec .min/.max), les valeurs simples (float),
    et le cas où value est None.
    """
    # Certains attributs d'impact peuvent avoir une propriété 'value'
    if hasattr(impact_obj, 'value'):
        val = impact_obj.value
        logger.debug(f"_extract_value: impact_obj.value = {val} (type={type(val)})")
        
        # Gérer le cas où val est None
        if val is None:
            logger.warning("impact_obj.value is None, returning 0.0")
            return 0.0
        
        if hasattr(val, 'mean'):
            return float(val.mean)
        # Si c'est un objet avec .min et .max (RangeValue)
        if hasattr(val, 'min') and hasattr(val, 'max'):
            return (val.min + val.max) / 2
        
        # Si c'est une valeur simple (float, int)
        elif isinstance(val, (int, float)):
            return float(val)
        else:
            logger.warning(f"Type de value inattendu: {type(val)}, tentative de conversion forcée")
            try:
                return float(val)
            except (ValueError, TypeError) as e:
                logger.error(f"Impossible de convertir en float: {val}, erreur: {e}")
                return 0.0

    # Fallback : utiliser la magnitude si disponible
    if hasattr(impact_obj, 'magnitude'):
        mag = impact_obj.magnitude
        logger.debug(f"_extract_value: using magnitude = {mag}")
        if mag is not None:
            return float(mag)
        else:
            logger.warning("magnitude is None, returning 0.0")
            return 0.0

    # Dernier recours : conversion directe
    logger.warning(f"Aucune valeur trouvée, tentative de conversion directe de {impact_obj}")
    try:
        return float(impact_obj)
    except (ValueError, TypeError) as e:
        logger.error(f"Échec de la conversion directe: {impact_obj}, erreur: {e}")
        return 0.0

def extract_gwp(impacts) -> float:
    """Extrait la valeur GWP (kgCO₂eq) d'un objet Impacts ecologits."""
    logger.debug(f"extract_gwp: impacts.gwp = {impacts.gwp}")
    return _extract_value(impacts.gwp)

def extract_energy(impacts) -> float:
    """Extrait l'énergie (kWh) d'un objet Impacts ecologits."""
    logger.debug(f"extract_energy: impacts.energy = {impacts.energy}")
    return _extract_value(impacts.energy)
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


# ---------------------------------------------------------------------------
# Critères ACV (PEF) + limites planétaires par habitant (approche ADEME/SRC).
#
# Les facteurs proviennent du rapport ADEME « Analyses de cycle de vie de GPU
# pour l'intelligence artificielle » (Tableau 8 : limites planétaires par
# habitant, base 8,06E+09 habitants). On les ramène au MOIS (÷12) pour former
# le budget mensuel moyen d'un habitant du monde.
#
# Structure (clé technique -> métadonnées) :
#   unit         : unité affichée
#   label        : libellé court du critère
#   description  : explication affichée dans l'info-bulle
#   pb_monthly   : seuil mensuel par habitant (facteur annuel ADEME ÷ 12)
#   display_factor : facteur de conversion appliqué avant affichage (ex. m³ -> L)
#
# NOTE : « PEF-LU » (usage des sols) est volontairement exclu (pas de facteur
# fourni par l'ADEME dans le tableau de référence).
# ---------------------------------------------------------------------------
MONTHS_PER_YEAR = 12


def _monthly(annual_per_capita: float) -> float:
    """Convertit un facteur limite planétaire annuel/habitant en budget mensuel."""
    return annual_per_capita / MONTHS_PER_YEAR


ACV_CRITERIA = {
    'PEF-GWP': {
        'unit': 'kg CO₂ eq',
        'label': 'Changement climatique',
        'description': "Potentiel de réchauffement global (GWP), indicateur le plus courant de l'empreinte carbone.",
        'pb_monthly': _monthly(8.45e2),
    },
    'PEF-ODP': {
        'unit': 'kg CFC-11 eq',
        'label': "Appauvrissement de l'ozone",
        'description': "Destruction de la couche d'ozone stratosphérique.",
        'pb_monthly': _monthly(6.69e-2),
    },
    'PEF-PM': {
        'unit': 'disease incidences',
        'label': 'Particules fines',
        'description': "Émissions de particules fines et leur impact sur la santé humaine.",
        'pb_monthly': _monthly(6.40e-5),
    },
    'PEF-AP': {
        'unit': 'mol H⁺ eq',
        'label': 'Acidification',
        'description': "Acidification des sols et des eaux (pluies acides).",
        'pb_monthly': _monthly(1.24e2),
    },
    'PEF-Epf': {
        'unit': 'kg P eq',
        'label': 'Eutrophisation eau douce',
        'description': "Enrichissement en phosphore des eaux douces.",
        'pb_monthly': _monthly(7.21e-1),
    },
    'PEF-Epm': {
        'unit': 'kg N eq',
        'label': 'Eutrophisation marine',
        'description': "Enrichissement en azote des eaux marines.",
        'pb_monthly': _monthly(2.49e1),
    },
    'PEF-Ept': {
        'unit': 'mol N eq',
        'label': 'Eutrophisation terrestre',
        'description': "Enrichissement en azote des milieux terrestres.",
        'pb_monthly': _monthly(7.60e2),
    },
    'PEF-IR': {
        'unit': 'kBq U-235 eq',
        'label': 'Rayonnements ionisants',
        'description': "Impact sur la santé humaine des rayonnements ionisants.",
        'pb_monthly': _monthly(6.54e4),
    },
    'PEF-POCP': {
        'unit': 'kg NMVOC eq',
        'label': 'Ozone photochimique',
        'description': "Formation d'ozone troposphérique (smog) affectant la santé humaine.",
        'pb_monthly': _monthly(5.05e1),
    },
    'PEF-CTUh-nc': {
        'unit': 'CTUh',
        'label': 'Toxicité humaine (non cancer.)',
        'description': "Effets toxiques non cancérigènes sur la santé humaine.",
        'pb_monthly': _monthly(5.09e-4),
    },
    'PEF-ADPf': {
        'unit': 'MJ',
        'label': 'Épuisement fossile',
        'description': "Épuisement des ressources abiotiques fossiles (énergie primaire).",
        'pb_monthly': _monthly(2.78e4),
    },
    'PEF-ADPe': {
        'unit': 'kg Sb eq',
        'label': 'Épuisement minéraux/métaux',
        'description': "Épuisement des ressources minérales et métalliques.",
        'pb_monthly': _monthly(2.72e-2),
    },
    'PEF-WU': {
        'unit': 'm³ eq',
        'label': "Utilisation de l'eau",
        'description': (
            "Consommation d'eau douce. L'ACV (PEF-WU, en m³ eq) et la "
            "contribution ecologits (WCF, en litres) ne sont pas fusionnées "
            "car issues de méthodologies différentes : elles sont affichées "
            "côte à côte comme deux contributions distinctes."
        ),
        'pb_monthly': _monthly(2.26e4),
    },
    'PEF-CTUe': {
        'unit': 'CTUe',
        'label': 'Écotoxicité eau douce',
        'description': "Effets écotoxicologiques sur les écosystèmes d'eau douce.",
        'pb_monthly': _monthly(1.62e4),
    },
    'PEF-CTUh-c': {
        'unit': 'CTUh',
        'label': 'Toxicité humaine (cancer.)',
        'description': "Effets toxiques cancérigènes sur la santé humaine.",
        'pb_monthly': _monthly(1.19e-4),
    },
}

# Liste ordonnée des clés de critères ACV affichables.
CRITERIA_KEYS = list(ACV_CRITERIA.keys())

# Contribution ecologits de l'eau, exposée sous une clé distincte (litres),
# volontairement NON fusionnée avec PEF-WU (m³ eq) faute d'unités comparables.
WATER_ECOLOGITS_KEY = 'PEF-WU_ecologits'

# Critères qu'ecologits est capable de remonter (mêmes unités que l'ACV) :
# utilisés pour déterminer quels critères peuvent être fusionnés.
ECOLOGITS_CRITERIA = {
    'PEF-GWP': 'gwp',
    'PEF-ADPe': 'adpe',
    'PEF-ADPf': 'pe',
}



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


def _extract_optional(impacts, attr: str) -> float:
    """Extrait une valeur optionnelle d'un ImpactOutput (0.0 si absente/None)."""
    obj = getattr(impacts, attr, None)
    if obj is None:
        return 0.0
    try:
        return _extract_value(obj)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Impossible d'extraire l'indicateur '{attr}' : {e}")
        return 0.0


def extract_ecologits_indicators(impacts, nb_call: int = 1) -> dict:
    """Construit le bloc `indicators` ecologits sous les clés de critères ACV.

    - PEF-GWP / PEF-ADPe / PEF-ADPf : mêmes unités que l'ACV -> fusionnables.
    - PEF-WU_ecologits : eau en litres (WCF), volontairement séparée de PEF-WU.

    Les valeurs sont mises à l'échelle du nombre d'appels.
    """
    gwp = _extract_optional(impacts, 'gwp')
    adpe = _extract_optional(impacts, 'adpe')
    pe = _extract_optional(impacts, 'pe')
    wcf = _extract_optional(impacts, 'wcf')

    return {
        'PEF-GWP': nb_call * gwp,
        'PEF-ADPe': nb_call * adpe,
        'PEF-ADPf': nb_call * pe,
        WATER_ECOLOGITS_KEY: nb_call * wcf,
    }
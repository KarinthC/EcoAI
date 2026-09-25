# backend/app/services/carbon/ecologits/video.py
import logging
from ecologits.estimations import video_impacts

from ..common import (

    get_level_from_indicators, extract_gwp, normalize_location,
    extract_ecologits_indicators,
)

logger = logging.getLogger(__name__)


def compute(params: dict) -> dict:
    # Paramètres MoMa (`eco:*`) avec repli sur les clés historiques.
    model_name = params.get('eco:modelName') or params.get('model_name')
    nb_call = int(params.get('eco:callCount') or params.get('nb_call') or 1)

    if not model_name:
        raise ValueError("model_name est obligatoire pour Video Generation")

    resolution = params.get('eco:resolution') or params.get('resolution', '1080p')
    duration = int(params.get('eco:duration') or params.get('duration') or 10)

    # Gestion de with_audio
    with_audio_param = params.get('eco:withAudio', params.get('with_audio', 'true'))
    if isinstance(with_audio_param, str):
        with_audio = with_audio_param.lower() == 'true'
    else:
        with_audio = bool(with_audio_param)

    # Paramètres optionnels
    kwargs = {}
    # Localisation du datacenter (ISO 3166-1 alpha-3). WOR (monde) par défaut.
    kwargs['datacenter_location'] = normalize_location(params.get('datacenter_location'))
    if 'datacenter_pue' in params and params['datacenter_pue'] is not None:
        try:
            kwargs['datacenter_pue'] = float(params['datacenter_pue'])
        except (ValueError, TypeError):
            pass
    if 'datacenter_wue' in params and params['datacenter_wue'] is not None:
        try:
            kwargs['datacenter_wue'] = float(params['datacenter_wue'])
        except (ValueError, TypeError):
            pass

    try:
        impacts = video_impacts(
            model_name=model_name,
            resolution=resolution,
            duration=duration,
            with_audio=with_audio,
            **kwargs
        )
    except Exception as e:
        logger.exception("Erreur lors de l'appel à video_impacts")
        raise

    gwp_kg = nb_call * extract_gwp(impacts)
    indicators = extract_ecologits_indicators(impacts, nb_call)

    return {
        'impact_kg': round(gwp_kg, 6),
        'indicators': indicators,
        'method': 'ecologits',
        'confidence': 'low',
        'level': get_level_from_indicators(indicators),
    }

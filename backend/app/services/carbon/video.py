# backend/app/services/carbon/video.py
import logging
from ecologits.estimations import video_impacts
from .common import get_level, extract_gwp, extract_energy

logger = logging.getLogger(__name__)

def compute(params: dict) -> dict:
    model_name = params.get('model_name')
    if not model_name:
        raise ValueError("model_name est obligatoire pour Video Generation")

    resolution = params.get('resolution', '1080p')
    duration = int(params.get('duration') or 10)

    # Gestion de with_audio
    with_audio_param = params.get('with_audio', 'true')
    if isinstance(with_audio_param, str):
        with_audio = with_audio_param.lower() == 'true'
    else:
        with_audio = bool(with_audio_param)

    # Paramètres optionnels
    kwargs = {}
    if 'datacenter_location' in params and params['datacenter_location']:
        kwargs['datacenter_location'] = params['datacenter_location']
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

    gwp_kg = extract_gwp(impacts)
    energy_kwh = extract_energy(impacts)
    level = get_level(gwp_kg)

    # Construction du message avec conseils personnalisés
    suggestions = []
    
    # Conseil basé sur le niveau d'impact
    if level == 'high':
        suggestions.append(f"L'impact de la génération vidéo est élevé ({gwp_kg:.4f} kgCO₂).")
    elif level == 'medium':
        suggestions.append(f"L'impact de la génération vidéo est modéré ({gwp_kg:.4f} kgCO₂).")
    
    # Conseils spécifiques selon les paramètres
    if resolution in ('1080p', '4k'):
        suggestions.append("Essayez de réduire la résolution (ex: 720p au lieu de 1080p).")
    
    if duration > 30:
        suggestions.append("Une durée plus courte réduirait significativement l'impact.")
    
    if with_audio:
        suggestions.append("Générer sans audio peut réduire l'empreinte carbone.")
    
    # Assemblage du message final
    message = " ".join(suggestions) if suggestions else "Impact estimé via ecologits (Video Generation)."

    return {
        'impact_kg': round(gwp_kg, 6),
        'energy_kwh': round(energy_kwh, 6),
        'level': level,
        'message': message
    }
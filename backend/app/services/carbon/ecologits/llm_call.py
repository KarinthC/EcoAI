# backend/app/services/carbon/ecologits/llm_call.py
import logging
from ecologits.tracers.utils import llm_impacts

from ..common import (

    get_level_from_indicators, extract_gwp, normalize_location,
    extract_ecologits_indicators,
)

logger = logging.getLogger(__name__)


def compute(params: dict) -> dict:
    # Paramètres MoMa (`eco:*`) avec repli sur les clés historiques.
    provider = params.get('eco:provider') or params.get('provider')
    model = params.get('eco:modelName') or params.get('model')
    nb_call = int(params.get('eco:callCount') or params.get('nb_call') or 1)

    # Protéger contre les null : utilise la valeur par défaut si None ou absent
    output_tokens = int(params.get('eco:outputTokens') or params.get('output_tokens') or 100)
    request_latency = float(params.get('eco:requestLatency') or params.get('request_latency') or 100)

    # Localisation du datacenter (back uniquement, non exposée dans le frontend).
    # Détermine le mix électrique utilisé par ecologits ; WOR (monde) par défaut.
    datacenter_location = normalize_location(params.get('datacenter_location'))

    if not provider or not model:
        raise ValueError("provider et model sont obligatoires pour LLM Call")

    impacts = llm_impacts(
        provider=provider,
        model_name=model,
        output_token_count=output_tokens,
        request_latency=request_latency,
        electricity_mix_zone=datacenter_location
    )

    gwp_kg = nb_call * extract_gwp(impacts)
    indicators = extract_ecologits_indicators(impacts, nb_call)

    # Modèle non reconnu par ecologits : impacts à None -> impact nul. On
    # expose un message explicite pour que le front distingue « pas de
    # données » d'un impact réellement nul.
    unsupported = getattr(impacts, 'gwp', None) is None
    message = (
        "Modèle non supporté par ecologits : aucun impact calculé."
        if unsupported else ""
    )

    return {
        'impact_kg': round(gwp_kg, 6),
        'indicators': indicators,
        'method': 'ecologits',
        'confidence': 'low',
        'level': get_level_from_indicators(indicators),
        'message': message,
    }


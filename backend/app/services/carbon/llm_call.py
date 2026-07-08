# backend/app/services/carbon/llm_call.py
import logging
from ecologits.tracers.utils import llm_impacts
from .common import get_level, extract_gwp, extract_energy

logger = logging.getLogger(__name__)

def compute(params: dict) -> dict:
    provider = params.get('provider')
    model = params.get('model')
    nb_call = int(params.get('nb_call') or 1)

    # Protéger contre les null : utilise la valeur par défaut si None ou absent
    output_tokens = int(params.get('output_tokens') or 100)
    request_latency = float(params.get('request_latency') or 100)

    if not provider or not model:
        raise ValueError("provider et model sont obligatoires pour LLM Call")

    impacts = llm_impacts(
        provider=provider,
        model_name=model,
        output_token_count=output_tokens,
        request_latency=request_latency
    )

    gwp_kg   = nb_call * extract_gwp(impacts)
    energy_kwh = nb_call * extract_energy(impacts)   # nouvelle fonction à ajouter dans common.py

    return {
        'impact_kg': round(gwp_kg, 6),
        'energy_kwh': round(energy_kwh, 6),
        'level': get_level(gwp_kg),
        'message': f"Impact estimé via ecologits (LLM Call)"
    }
# backend/app/services/carbon/llm_call.py
import logging
from ecologits.tracers.utils import llm_impacts
from ecologits.impacts import Impacts
from .common import get_level, extract_gwp

logger = logging.getLogger(__name__)

def compute(params: dict) -> dict:
    provider = params.get('provider')
    model = params.get('model')
    if not provider or not model:
        raise ValueError("Provider et model sont obligatoires pour LLM Call")
    
    output_tokens = int(params.get('output_tokens', 100))
    request_latency = float(params.get('request_latency', 100))
    
    impacts: Impacts = llm_impacts(
        provider=provider,
        model_name=model,
        output_token_count=output_tokens,
        request_latency=request_latency
    )
    impact = extract_gwp(impacts)
    message = f"Impact estimé via ecologits (LLM Call)"
    
    return {
        'impact_kg': round(impact, 4),
        'level': get_level(impact),
        'message': message
    }
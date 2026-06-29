# backend/app/services/carbon/llm_expert.py
import logging
from ecologits.impacts.llm import compute_llm_impacts
from .common import get_level, extract_gwp

logger = logging.getLogger(__name__)

def compute(params: dict) -> dict:
    active_params = float(params.get('active_params', 0))
    total_params = float(params.get('total_params', 0))
    output_tokens = int(params.get('output_tokens', 100))
    request_latency = float(params.get('request_latency', 100))
    
    mix_gwp = float(params.get('mix_gwp', 0.508759))
    mix_adpe = float(params.get('mix_adpe', 0.00004420127244))
    mix_pe = float(params.get('mix_pe', 4.484))
    
    # PUE moyen mondial ~1.58, WUE ~1.8 L/kWh, etc. Ajuste selon tes sources.
    datacenter_pue = float(params.get('datacenter_pue', 1.58))
    datacenter_wue = float(params.get('datacenter_wue', 1.8))
    if_electricity_mix_wue = float(params.get('if_electricity_mix_wue', 0.0))  # souvent indisponible

    impacts = compute_llm_impacts(
        model_active_parameter_count=active_params,
        model_total_parameter_count=total_params,
        output_token_count=output_tokens,
        request_latency=request_latency,
        if_electricity_mix_gwp=mix_gwp,
        if_electricity_mix_adpe=mix_adpe,
        if_electricity_mix_pe=mix_pe,
        if_electricity_mix_wue=if_electricity_mix_wue,
        datacenter_pue=datacenter_pue,
        datacenter_wue=datacenter_wue
    )
    impact = extract_gwp(impacts)
    message = f"Impact estimé via ecologits (LLM Expert)"
    
    return {
        'impact_kg': round(impact, 4),
        'level': get_level(impact),
        'message': message
    }
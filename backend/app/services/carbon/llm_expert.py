# backend/app/services/carbon/llm_expert.py
import logging
from ecologits.impacts.llm import compute_llm_impacts
from .common import get_level, extract_gwp, extract_energy

logger = logging.getLogger(__name__)

def compute(params: dict) -> dict:
    active_params = float(params.get('active_params', 7))      # 7 milliards par défaut (ex: LLaMA-7B)
    total_params   = float(params.get('total_params', 10))     # 10 milliards
    output_tokens  = int(params.get('output_tokens', 250))     # 250 tokens
    request_latency = float(params.get('request_latency', 100)) # ms
    nb_call = int(params.get('nb_call') or 1)

    
    mix_gwp = float(params.get('mix_gwp' or 0.508759))
    mix_adpe = float(params.get('mix_adpe' or 0.00004420127244))
    mix_pe = float(params.get('mix_pe' or 4.484))
    
    # PUE moyen mondial ~1.58, WUE ~1.8 L/kWh, etc. Ajuste selon tes sources.
    datacenter_pue = float(params.get('datacenter_pue' or 1.58))
    datacenter_wue = float(params.get('datacenter_wue' or 1.8))
    if_electricity_mix_wue = float(params.get('if_electricity_mix_wue' or 0.0))  # souvent indisponible

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

    gwp_kg   = nb_call * extract_gwp(impacts)
    energy_kwh =nb_call * extract_energy(impacts)

    return {
        'impact_kg': round(gwp_kg, 6),
        'energy_kwh': round(energy_kwh, 6),
        'level': get_level(gwp_kg),
        'message': f"Impact estimé via ecologits (LLM Expert)"
    }
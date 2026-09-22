# backend/app/services/carbon/ecologits/llm_expert.py
import logging
from ecologits.impacts.llm import compute_llm_impacts
from ecologits.electricity_mix_repository import electricity_mixes

from ..common import (

    get_level_from_indicators, extract_gwp, normalize_location,
    extract_ecologits_indicators,
)

logger = logging.getLogger(__name__)


def compute(params: dict) -> dict:
    active_params = float(params.get('active_params', 7))      # 7 milliards par défaut (ex: LLaMA-7B)
    total_params = float(params.get('total_params', 10))       # 10 milliards
    output_tokens = int(params.get('output_tokens', 250))      # 250 tokens
    request_latency = float(params.get('request_latency', 100))  # ms
    nb_call = int(params.get('nb_call') or 1)

    # Localisation du datacenter : determine le mix electrique (GWP, ADPe, PE, WUE).
    # WOR (moyenne mondiale) par defaut si non fourni.
    datacenter_location = normalize_location(params.get('datacenter_location'))
    mix = electricity_mixes.find_electricity_mix(zone=datacenter_location)
    if mix is None:
        logger.warning(
            "Zone de mix electrique inconnue '%s', repli sur WOR",
            datacenter_location
        )
        mix = electricity_mixes.find_electricity_mix(zone="WOR")

    mix_gwp = mix.gwp
    mix_adpe = mix.adpe
    mix_pe = mix.pe

    # PUE moyen mondial ~1.58, WUE ~1.8 L/kWh, etc. Ajuste selon tes sources.
    datacenter_pue = float(params.get('datacenter_pue') or 1.58)
    datacenter_wue = float(params.get('datacenter_wue') or 1.8)
    if_electricity_mix_wue = mix.wue

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

    gwp_kg = nb_call * extract_gwp(impacts)
    indicators = extract_ecologits_indicators(impacts, nb_call)

    return {
        'impact_kg': round(gwp_kg, 6),
        'indicators': indicators,
        'method': 'ecologits',
        'confidence': 'low',
        'level': get_level_from_indicators(indicators),
    }

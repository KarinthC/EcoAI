# backend/app/services/carbon/equivalences.py

# Coefficients issus du fichier utils.py (sources documentées)
RUNNING_ENERGY_KM_PER_KJ = 1 / 294          # 1 km pour 294 kJ (course)
WALKING_ENERGY_KM_PER_KJ = 1 / 196          # 1 km pour 196 kJ (marche)
EV_ENERGY_KM_PER_KWH = 1 / 0.17             # 1 km pour 0.17 kWh (voiture électrique)
STREAMING_HOURS_PER_KGCO2 = 15.6            # 15.6 h de streaming pour 1 kgCO2eq
# Équivalences globales (pour la sidebar, facultatives)
KM_VOITURE_PER_KGCO2 = 4.5   # approximation voiture thermique (on peut garder l'ancien coef)
REPAS_PER_KGCO2 = 0.1        # conservé pour la compatibilité


def format_equivalences(gwp_kg: float, energy_kwh: float) -> dict:
    """
    Retourne un dictionnaire d'équivalences compréhensibles à partir du GWP (kgCO2eq)
    et de l'énergie (kWh) d'un appel LLM.
    """
    eq = {}

    # Streaming (basé sur le GWP)
    streaming_hours = gwp_kg * STREAMING_HOURS_PER_KGCO2
    if streaming_hours >= 1:
        eq['streaming'] = f"{streaming_hours:.1f} h de streaming"
    elif streaming_hours >= 1/60:
        eq['streaming'] = f"{streaming_hours*60:.1f} min de streaming"
    else:
        eq['streaming'] = f"{streaming_hours*3600:.0f} s de streaming"

    # Équivalences basées sur l'énergie (kWh -> kJ)
    energy_kj = energy_kwh * 3600

    # Marche
    walk_km = energy_kj * WALKING_ENERGY_KM_PER_KJ
    if walk_km >= 1:
        eq['walking'] = f"marcher {walk_km:.2f} km"
    else:
        eq['walking'] = f"marcher {walk_km*1000:.0f} m"

    # Course
    run_km = energy_kj * RUNNING_ENERGY_KM_PER_KJ
    if run_km >= 1:
        eq['running'] = f"courir {run_km:.2f} km"
    else:
        eq['running'] = f"courir {run_km*1000:.0f} m"

    # Voiture électrique
    ev_km = energy_kwh * EV_ENERGY_KM_PER_KWH
    if ev_km >= 1:
        eq['ev'] = f"parcourir {ev_km:.1f} km en voiture électrique"
    else:
        eq['ev'] = f"parcourir {ev_km*1000:.0f} m en voiture électrique"

    return eq


def compute_global_equivalences(total_gwp_kg: float) -> dict:
    """
    Équivalences globales affichées dans la sidebar.
    Pour l'instant, nous conservons les trois indicateurs simples,
    mais nous utilisons des coefficients plus précis pour le streaming.
    """
    return {
        'km_voiture': round(total_gwp_kg * KM_VOITURE_PER_KGCO2, 1),
        'heures_streaming': round(total_gwp_kg * STREAMING_HOURS_PER_KGCO2, 1),
        'repas_equivalent': round(total_gwp_kg * REPAS_PER_KGCO2, 1)
    }
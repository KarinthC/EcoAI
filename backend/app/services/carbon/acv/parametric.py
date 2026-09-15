"""Modèle paramétrique ADEME/AltImpact (Tableau 42) pour les GPUs non documentés.

Le rapport ADEME/AltImpact fournit les impacts ACV « prêts à l'emploi » de 8
cartes analysées en détail. Pour les cartes qui n'y figurent pas (ex. NVIDIA
H100 NVL), le rapport propose un MODÈLE PARAMÉTRIQUE : on reconstruit les
impacts embarqués (fabrication + transport + fin de vie) à partir de
paramètres physiques (poids, surfaces, distances de transport).

Les impacts à l'USAGE (électricité) ne sont PAS couverts ici : ils restent
calculés par `compute_acv` via le TDP et le mix électrique.

Contenu :
  - FACTEURS          : impacts par unité et par élément (Tableau 42, p.80).
                        Clés = clés PEF internes (PEF-AP, PEF-GWP, ...).
  - PARAMETRIC_GPUS   : paramètres physiques par carte (pour 1 CARTE entière).
  - compute_gpu_impacts(params) : applique le modèle paramétrique.
"""

# ------------------------------------------------------------------
# Facteurs d'impact par unité et par élément (Tableau 42, page 80).
# Clés = clés PEF internes utilisées dans tout le projet.
# Unités :
#   boitier_kg / radiateur_kg / transport_amont_kg / fin_de_vie_kg  : 1 kg
#   pcb_cm2                                                        : 1 cm²
#   gpu_mm2 / vram_mm2                                            : 1 mm²
#   transport_*_kgkm                                              : 1 kg.km
# ------------------------------------------------------------------
FACTEURS = {
    "PEF-AP": {
        "boitier_kg": 7.28e-2, "radiateur_kg": 2.18e-1, "pcb_cm2": 5.76e-4,
        "gpu_mm2": 2.40e-4, "vram_mm2": 1.90e-4, "transport_amont_kg": 1.74e-3,
        "transport_camion_kgkm": 3.19e-7, "transport_bateau_kgkm": 5.34e-7,
        "transport_avion_kgkm": 8.77e-6, "fin_de_vie_kg": 3.16e-2,
    },
    "PEF-GWP": {
        "boitier_kg": 7.82, "radiateur_kg": 5.74, "pcb_cm2": 7.30e-2,
        "gpu_mm2": 4.32e-2, "vram_mm2": 3.45e-2, "transport_amont_kg": 2.61e-1,
        "transport_camion_kgkm": 5.04e-5, "transport_bateau_kgkm": 1.33e-5,
        "transport_avion_kgkm": 2.11e-3, "fin_de_vie_kg": 1.48,
    },
    "PEF-CTUe": {
        "boitier_kg": 4.04, "radiateur_kg": 4.20, "pcb_cm2": 1.03,
        "gpu_mm2": 5.52e-1, "vram_mm2": 4.40e-1, "transport_amont_kg": 1.76e-1,
        "transport_camion_kgkm": 3.39e-5, "transport_bateau_kgkm": 7.92e-6,
        "transport_avion_kgkm": 1.37e-3, "fin_de_vie_kg": 7.62,
    },
    "PEF-PM": {
        "boitier_kg": 4.57e-7, "radiateur_kg": 1.36e-6, "pcb_cm2": 3.12e-9,
        "gpu_mm2": 1.32e-9, "vram_mm2": 1.05e-9, "transport_amont_kg": 1.50e-8,
        "transport_camion_kgkm": 2.59e-12, "transport_bateau_kgkm": 2.76e-12,
        "transport_avion_kgkm": 5.44e-11, "fin_de_vie_kg": 9.40e-8,
    },
    "PEF-Epf": {
        "boitier_kg": 1.72e-4, "radiateur_kg": 1.50e-3, "pcb_cm2": 2.38e-7,
        "gpu_mm2": 1.35e-7, "vram_mm2": 1.07e-7, "transport_amont_kg": 9.78e-8,
        "transport_camion_kgkm": 1.89e-11, "transport_bateau_kgkm": 4.46e-12,
        "transport_avion_kgkm": 7.44e-10, "fin_de_vie_kg": 3.01e-5,
    },
    "PEF-Epm": {
        "boitier_kg": 6.95e-2, "radiateur_kg": 6.04e-2, "pcb_cm2": 5.51e-4,
        "gpu_mm2": 2.99e-4, "vram_mm2": 2.38e-4, "transport_amont_kg": 9.01e-3,
        "transport_camion_kgkm": 1.50e-7, "transport_bateau_kgkm": 1.22e-7,
        "transport_avion_kgkm": 3.95e-6, "fin_de_vie_kg": 2.11e-2,
    },
    "PEF-Ept": {
        "boitier_kg": 6.32e-3, "radiateur_kg": 5.22e-3, "pcb_cm2": 5.17e-5,
        "gpu_mm2": 2.87e-5, "vram_mm2": 2.29e-5, "transport_amont_kg": 8.22e-4,
        "transport_camion_kgkm": 1.64e-6, "transport_bateau_kgkm": 1.34e-6,
        "transport_avion_kgkm": 4.32e-5, "fin_de_vie_kg": 1.44e-2,
    },
    "PEF-CTUh-c": {
        "boitier_kg": 2.00e-6, "radiateur_kg": 2.15e-5, "pcb_cm2": 4.83e-9,
        "gpu_mm2": 1.63e-10, "vram_mm2": 3.23e-12, "transport_amont_kg": 4.66e-12,
        "transport_camion_kgkm": 8.85e-16, "transport_bateau_kgkm": 1.89e-16,
        "transport_avion_kgkm": 3.19e-14, "fin_de_vie_kg": 5.58e-9,
    },
    "PEF-CTUh-nc": {
        "boitier_kg": 3.03e-6, "radiateur_kg": 2.78e-6, "pcb_cm2": 2.91e-9,
        "gpu_mm2": 2.65e-10, "vram_mm2": 1.87e-10, "transport_amont_kg": 5.77e-10,
        "transport_camion_kgkm": 9.58e-14, "transport_bateau_kgkm": 4.28e-14,
        "transport_avion_kgkm": 1.67e-12, "fin_de_vie_kg": 2.32e-7,
    },
    "PEF-IR": {
        "boitier_kg": 3.41, "radiateur_kg": 3.25, "pcb_cm2": 1.06e-1,
        "gpu_mm2": 2.67e-3, "vram_mm2": 2.89e-4, "transport_amont_kg": 6.35e-4,
        "transport_camion_kgkm": 1.23e-7, "transport_bateau_kgkm": 2.63e-8,
        "transport_avion_kgkm": 3.89e-6, "fin_de_vie_kg": 1.20e-1,
    },
    "PEF-LU": {
        "boitier_kg": 7.62e-1, "radiateur_kg": 3.54, "pcb_cm2": 2.55e-4,
        "gpu_mm2": 1.72e-4, "vram_mm2": 1.37e-4, "transport_amont_kg": 0.0,
        "transport_camion_kgkm": 0.0, "transport_bateau_kgkm": 0.0,
        "transport_avion_kgkm": 0.0, "fin_de_vie_kg": 6.61,
    },
    "PEF-ODP": {
        "boitier_kg": 1.21e-6, "radiateur_kg": 1.15e-6, "pcb_cm2": 1.62e-8,
        "gpu_mm2": 1.89e-8, "vram_mm2": 1.50e-8, "transport_amont_kg": 4.00e-10,
        "transport_camion_kgkm": 7.72e-14, "transport_bateau_kgkm": 1.65e-14,
        "transport_avion_kgkm": 2.44e-12, "fin_de_vie_kg": 1.36e-7,
    },
    "PEF-POCP": {
        "boitier_kg": 2.49e-2, "radiateur_kg": 2.99e-2, "pcb_cm2": 1.91e-4,
        "gpu_mm2": 9.40e-5, "vram_mm2": 7.48e-5, "transport_amont_kg": 2.28e-3,
        "transport_camion_kgkm": 4.14e-7, "transport_bateau_kgkm": 3.45e-7,
        "transport_avion_kgkm": 1.06e-5, "fin_de_vie_kg": 5.29e-3,
    },
    "PEF-ADPf": {
        "boitier_kg": 2.20, "radiateur_kg": 8.50e1, "pcb_cm2": 9.99e-1,
        "gpu_mm2": 5.65e-1, "vram_mm2": 4.50e-1, "transport_amont_kg": 3.64e1,
        "transport_camion_kgkm": 7.03e-4, "transport_bateau_kgkm": 1.63e-4,
        "transport_avion_kgkm": 2.95e-2, "fin_de_vie_kg": 1.90e1,
    },
    "PEF-ADPe": {
        "boitier_kg": 4.96e-4, "radiateur_kg": 1.87e-3, "pcb_cm2": 2.13e-5,
        "gpu_mm2": 1.94e-7, "vram_mm2": 9.51e-10, "transport_amont_kg": 1.03e-8,
        "transport_camion_kgkm": 1.98e-12, "transport_bateau_kgkm": 4.62e-13,
        "transport_avion_kgkm": 8.31e-11, "fin_de_vie_kg": 3.43e-6,
    },
    "PEF-WU": {
        "boitier_kg": 4.32, "radiateur_kg": 1.05e1, "pcb_cm2": 3.15e-2,
        "gpu_mm2": 1.50e-2, "vram_mm2": 1.33e-2, "transport_amont_kg": 9.90e-4,
        "transport_camion_kgkm": 1.91e-7, "transport_bateau_kgkm": 4.20e-8,
        "transport_avion_kgkm": 8.38e-6, "fin_de_vie_kg": 7.02,
    },
}


# ------------------------------------------------------------------
# Paramètres physiques par carte (modèle paramétrique ADEME).
# IMPORTANT : tous les paramètres décrivent UNE carte entière.
#   - surface_gpu_mm2 / surface_vram_mm2 incluent tous les dies de la carte
#     (une carte dual-GPU comme le H100 NVL compte donc 2 dies GPU).
#   - tdp_w = TDP de la carte ENTIÈRE (pour le H100 NVL : 2 x 350 = 700 W).
#
# Ajouter ici toute nouvelle carte non documentée « prête à l'emploi ».
# ------------------------------------------------------------------
PARAMETRIC_GPUS = {
    "H100 NVL 96Go": {
        "poids_carte_kg": 1.69,
        "part_radiateur": 0.533,
        "surface_pcb_cm2": 296.0,
        "surface_gpu_mm2": 814.0 * 2,        # 2 dies GH100 par carte (dual-GPU)
        "surface_vram_mm2": 6 * 86.25 * 2,   # 6 dies HBM3/GPU, 86.25 mm²/die, x2
        "distance_avion_km": 9908.0,         # Shenzhen -> Paris
        "distance_camion_km": 1000.0,
        "distance_bateau_km": 0.0,
        "tdp_w": 700,                        # carte dual-GPU (2 x 350 W)
    },
}


def compute_gpu_impacts(params: dict) -> dict:
    """Calcule les 16 indicateurs PEF embarqués pour UNE carte graphique.

    Couvre : fabrication (boîtier, radiateur, PCB, GPU, VRAM), transport amont,
    distribution (avion/camion/bateau) et fin de vie. NE couvre PAS l'usage.

    Args:
        params: dict avec les clés :
            - poids_carte_kg    (float, kg)
            - part_radiateur    (float 0..1)
            - surface_pcb_cm2   (float, cm²)
            - surface_gpu_mm2   (float, mm², tous dies confondus)
            - surface_vram_mm2  (float, mm², tous dies confondus)
            - distance_avion_km  (float, km)
            - distance_camion_km (float, km)
            - distance_bateau_km (float, km)

    Returns:
        dict {clé PEF: impact embarqué total pour 1 carte}.
    """
    poids = params["poids_carte_kg"]
    masse_radiateur = poids * params["part_radiateur"]
    masse_boitier = poids - masse_radiateur  # approximation (reste du poids)

    impacts = {}
    for ind, fact in FACTEURS.items():
        impacts[ind] = (
            masse_boitier * fact["boitier_kg"]
            + masse_radiateur * fact["radiateur_kg"]
            + params["surface_pcb_cm2"] * fact["pcb_cm2"]
            + params["surface_gpu_mm2"] * fact["gpu_mm2"]
            + params["surface_vram_mm2"] * fact["vram_mm2"]
            + poids * fact["transport_amont_kg"]
            + (poids * params["distance_avion_km"]) * fact["transport_avion_kgkm"]
            + (poids * params["distance_camion_km"]) * fact["transport_camion_kgkm"]
            + (poids * params["distance_bateau_km"]) * fact["transport_bateau_kgkm"]
            + poids * fact["fin_de_vie_kg"]
        )
    return impacts


def embedded_total_card(gpu_key: str) -> dict:
    """Impacts embarqués totaux (fabrication + transport + fin de vie) pour 1 carte.

    Compatible avec le format `embedded_total_card` de `gpu_models.GPUS`.
    """
    if gpu_key not in PARAMETRIC_GPUS:
        raise ValueError(
            f"GPU paramétrique inconnu : {gpu_key}. "
            f"Disponibles : {list(PARAMETRIC_GPUS)}"
        )
    return compute_gpu_impacts(PARAMETRIC_GPUS[gpu_key])

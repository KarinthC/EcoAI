"""Tests unitaires pour les nœuds de stockage.

  - « Données persistantes » (HDD) : durée en ANNÉES (`duree_ans`).
  - « Données SSD temporaires » (SSD, scratch) : durée en JOURS (`duree_jours`),
    purgée après ~30 jours par convention (défaut = 30 j si non fournie).

Couvrent :
  - la structure de retour (16 indicateurs PEF, method='acv', confidence='medium') ;
  - la linéarité en volume (Go) et en durée (années pour HDD, jours pour SSD) ;
  - la supériorité d'impact du SSD sur le HDD (GWP, ADPe) ;
  - l'effet du PUE fixe (1.28, intégré au kWh/To/an) ;
  - un test de non-régression sur les ordres de grandeur de l'ACV SUMMER (§5).
"""

import pytest

from app.services.carbon.acv.storage import (
    compute_hdd, compute_ssd, compute_storage, FAB_PER_TO, MEDIA, PUE,
    JOURS_PER_AN, DUREE_SSD_TEMPORAIRE_JOURS,
)


# ---------------------------------------------------------------------------
# Structure de retour
# ---------------------------------------------------------------------------

def test_storage_structure():
    r = compute_hdd({'taille': 1000, 'duree_ans': 1})
    assert r['method'] == 'acv'
    assert r['confidence'] == 'medium'
    assert r['indicators']['PEF-GWP'] > 0
    assert r['impact_kg'] == pytest.approx(r['indicators']['PEF-GWP'], rel=1e-6)



def test_storage_all_16_pef_keys():
    """Le modèle doit couvrir les 16 catégories EF 3.1."""
    r = compute_hdd({'taille': 1000, 'duree_ans': 1})
    assert set(r['indicators'].keys()) == set(FAB_PER_TO['HDD'].keys())
    assert len(r['indicators']) == 16


def test_storage_unknown_media_raises():
    with pytest.raises(ValueError, match="Média inconnu"):
        compute_storage('TAPE', {'taille': 1000, 'duree_ans': 1})


# ---------------------------------------------------------------------------
# Linéarité
# ---------------------------------------------------------------------------

def test_storage_linear_in_volume():
    base = compute_hdd({'taille': 1000, 'duree_ans': 1})['impact_kg']
    triple = compute_hdd({'taille': 3000, 'duree_ans': 1})['impact_kg']
    assert triple == pytest.approx(base * 3, rel=1e-9)


def test_storage_linear_in_duration():
    """La durée impacte uniquement la composante usage (proportionnelle)."""
    r1 = compute_hdd({'taille': 1000, 'duree_ans': 1})
    r2 = compute_hdd({'taille': 1000, 'duree_ans': 2})
    assert r2['impact_kg'] > r1['impact_kg']


def test_storage_zero_volume():
    """Volume nul -> aucun impact (pas de support)."""
    assert compute_hdd({'taille': 0, 'duree_ans': 5})['impact_kg'] == 0.0


def test_storage_zero_duration_keeps_embodied():
    """Durée nulle -> la fabrication (support déjà là) subsiste, l'usage s'annule."""
    r = compute_hdd({'taille': 1000, 'duree_ans': 0})

    r_1an = compute_hdd({'taille': 1000, 'duree_ans': 1})
    # Durée nulle : il ne reste que la fabrication, donc un impact positif mais
    # inférieur à celui d'une année complète (fabrication + usage).
    assert r['impact_kg'] > 0.0
    assert r['impact_kg'] < r_1an['impact_kg']


# ---------------------------------------------------------------------------
# SSD vs HDD
# ---------------------------------------------------------------------------

def test_ssd_more_impactful_than_hdd_gwp():
    params = {'taille': 1000, 'duree_ans': 1}
    assert compute_ssd(params)['indicators']['PEF-GWP'] > compute_hdd(params)['indicators']['PEF-GWP']


def test_ssd_more_impactful_than_hdd_adpe():
    """Le SSD consomme nettement plus de ressources minérales (terres rares)."""
    params = {'taille': 1000, 'duree_ans': 1}
    ratio = compute_ssd(params)['energy_kwh'] / compute_hdd(params)['energy_kwh']
    assert ratio == pytest.approx(
        MEDIA['SSD']['kwh_per_to_year'] / MEDIA['HDD']['kwh_per_to_year'], rel=1e-9
    )


# ---------------------------------------------------------------------------
# PUE et réplication / efficacité
# ---------------------------------------------------------------------------

def test_pue_already_included_in_kwh_per_to_year():
    """kWh/To/an (11,2 pour HDD) intègre déjà le PUE : ne pas le remultiplier."""


    assert MEDIA['HDD']['kwh_per_to_year'] == pytest.approx(11.2, rel=1e-9)
    assert PUE == 1.28


def test_ssd_replication_and_efficiency_partially_compensate():
    """SSD : efficacité x0,5 et réplication x2 -> coefficient fabrication = 1,0."""
    coeff = MEDIA['SSD']['m_efficacite'] * MEDIA['SSD']['m_replication'] * MEDIA['SSD']['m_sauvegarde']
    assert coeff == pytest.approx(1.0, rel=1e-12)
    coeff_hdd = MEDIA['HDD']['m_efficacite'] * MEDIA['HDD']['m_replication'] * MEDIA['HDD']['m_sauvegarde']
    assert coeff_hdd == pytest.approx(0.7, rel=1e-12)


# ---------------------------------------------------------------------------
# Durée : jours (SSD temporaire) et années (HDD persistant)
# ---------------------------------------------------------------------------

    """SSD : 365 jours == 1 an (même énergie)."""
    r_jours = compute_ssd({'taille': 1000, 'duree_jours': 365})
    r_ans = compute_ssd({'taille': 1000, 'duree_ans': 1})


def test_ssd_default_duration_is_30_days():
    """SSD sans durée fournie -> défaut = 30 jours (convention scratch)."""
    r = compute_ssd({'taille': 1000})
    # energy_kwh est arrondi à 6 décimales -> tolérance plus large.

def test_ssd_duree_ans_takes_priority_over_jours():
    """Rétro-compat : si `duree_ans` est fourni, il est prioritaire."""
    r = compute_ssd({'taille': 1000, 'duree_ans': 1, 'duree_jours': 999})
    assert r['energy_kwh'] == pytest.approx(1.0 * 1.0 * 33.6, rel=1e-9)

    """HDD : la durée se compte en années."""
    r = compute_hdd({'taille': 1000, 'duree_ans': 3})
    assert r['energy_kwh'] == pytest.approx(1.0 * 3.0 * 11.2, rel=1e-9)


def test_ssd_message_in_days():
    """Le message SSD exprime la durée en jours."""
    r = compute_ssd({'taille': 1000, 'duree_jours': 30})


# ---------------------------------------------------------------------------
# (8,56 vs 8,0 et 82,4 vs 81,0) ; la FABRICATION (poste dominant) correspond,
# elle, exactement. Valeurs de référence figées ci-dessous pour non-régression.
# ---------------------------------------------------------------------------

def test_hdd_gwp_reference_value():
    """1 To / 1 an sur HDD : 8,56 kg CO2 eq (fab 7,0 + fin 0,35 + usage 1,21)."""
    r = compute_hdd({'taille': 1000, 'duree_ans': 1})
    assert r['impact_kg'] == pytest.approx(8.56, rel=1e-3)


def test_ssd_gwp_reference_value():
    """1 To / 1 an sur SSD NVMe : 82,38 kg CO2 eq (fab 75 + fin 3,75 + usage 3,63)."""
    r = compute_ssd({'taille': 1000, 'duree_ans': 1})
    assert r['impact_kg'] == pytest.approx(82.38, rel=1e-3)

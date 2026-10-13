from __future__ import annotations

import math
from typing import Any

# Conservative, explicitly labelled assumptions. These are theoretical bounds,
# not measured reaction yields.
PEI_NITROGEN_MASS_FRACTION = 0.3252  # ideal C2H5N repeat-unit limit; supplier/conversion basis must be confirmed
MOLAR_MASS_N = 14.0067
MOLAR_MASS_HCHO = 30.026
STOICHIOMETRY_UPPER_BOUNDS = {"conservative_1_hcho_per_n": 1.0, "max_2_hcho_per_n": 2.0}

PEI_GROUP_DISTRIBUTION_ASSUMPTIONS = {
    "primary_amine_fraction_of_n": 0.60,
    "secondary_amine_fraction_of_n": 0.30,
    "tertiary_amine_fraction_of_n": 0.10,
    "accessible_primary_fraction": 0.80,
    "accessible_secondary_fraction": 0.50,
    "accessible_tertiary_fraction": 0.20,
    "basis": "linear PEI approximation; supplier PEI is usually a branched/salt mixture and must be validated",
}

def pei_group_capacity_g_m2(
    pei_active_g_m2: float,
    primary_fraction: float = 0.60,
    secondary_fraction: float = 0.30,
    tertiary_fraction: float = 0.20,
    primary_accessibility: float = 0.80,
    secondary_accessibility: float = 0.50,
    tertiary_accessibility: float = 0.20,
) -> dict[str, float]:
    """Group-resolved stoichiometric HCHO capacity upper bound.

    This is a theoretical capacity, not an equilibrium yield or measured reduction.
    Stoichiometries are labelled approximations: primary amine <= 2 HCHO,
    secondary amine <= 1 HCHO, tertiary amine is assumed to contribute only via equilibrium adducts.
    """
    if pei_active_g_m2 < 0:
        raise ValueError("PEI active mass must be non-negative")
    for name, value in [
        ("primary_fraction", primary_fraction), ("secondary_fraction", secondary_fraction), ("tertiary_fraction", tertiary_fraction)]:
        if value < 0:
            raise ValueError(name + " must be non-negative")
    if abs(primary_fraction + secondary_fraction + tertiary_fraction - 1.0) > 1e-9:
        raise ValueError("amine fractions must sum to 1")
    nitrogen_g = nitrogen_mass_g(pei_active_g_m2)
    nitrogen_mol = nitrogen_g / MOLAR_MASS_N
    group_mol = {
        "primary": nitrogen_mol * primary_fraction,
        "secondary": nitrogen_mol * secondary_fraction,
        "tertiary": nitrogen_mol * tertiary_fraction,
    }
    max_hcho_mol = (
        group_mol["primary"] * 2.0 * primary_accessibility
        + group_mol["secondary"] * 1.0 * secondary_accessibility
        + group_mol["tertiary"] * 0.5 * tertiary_accessibility
    )
    max_hcho_g = max_hcho_mol * MOLAR_MASS_HCHO
    return {
        "pei_active_g_m2": pei_active_g_m2,
        "nitrogen_g_m2": nitrogen_g,
        "primary_amine_mmol_m2": group_mol["primary"] * 1000.0,
        "secondary_amine_mmol_m2": group_mol["secondary"] * 1000.0,
        "tertiary_amine_mmol_m2": group_mol["tertiary"] * 1000.0,
        "theoretical_max_hcho_g_m2": max_hcho_g,
        "approximate_group_stoichiometry": "primary <=2, secondary <=1, tertiary <=0.5, all modulated by accessibility",
    }


def nitrogen_mass_g(pei_active_g_m2: float) -> float:
    return pei_active_g_m2 * PEI_NITROGEN_MASS_FRACTION


def theoretical_formaldehyde_capacity(
    pei_active_g_m2: float,
    stoichiometry_upper_bound: float = 1.0,
    group_availability: float = 1.0,
    irreversibility_fraction: float = 1.0,
) -> dict[str, float]:
    """Upper bound for chemically available formaldehyde binding.

    Capacity is labelled as a theoretical upper bound. group_availability and
    irreversibility_fraction are uncertain model inputs, not measured data.
    """
    if pei_active_g_m2 < 0:
        raise ValueError("PEI active mass must be non-negative")
    if not 0 <= stoichiometry_upper_bound <= 2:
        raise ValueError("stoichiometry upper bound must be in [0, 2]")
    if not 0 <= group_availability <= 1:
        raise ValueError("group availability must be in [0, 1]")
    if not 0 <= irreversibility_fraction <= 1:
        raise ValueError("irreversibility fraction must be in [0, 1]")

    nitrogen_g = nitrogen_mass_g(pei_active_g_m2)
    nitrogen_mol = nitrogen_g / MOLAR_MASS_N
    max_stoichiometric_g = nitrogen_mol * stoichiometry_upper_bound * MOLAR_MASS_HCHO
    available_g = max_stoichiometric_g * group_availability
    effective_g = available_g * irreversibility_fraction
    return {
        "pei_active_g_m2": pei_active_g_m2,
        "nitrogen_g_m2": nitrogen_g,
        "nitrogen_mmol_m2": nitrogen_mol * 1000.0,
        "theoretical_max_hcho_g_m2": max_stoichiometric_g,
        "group_availability_fraction": group_availability,
        "irreversibility_fraction": irreversibility_fraction,
        "accessible_reversible_adjusted_capacity_g_m2": effective_g,
        "note": "theoretical upper bound; not measured reaction yield or efficacy",
    }

from __future__ import annotations

import math
from typing import Any

# Conservative, explicitly labelled assumptions. These are theoretical bounds,
# not measured reaction yields.
PEI_NITROGEN_MASS_FRACTION = 0.232558  # approximate N content of PEI repeating unit
MOLAR_MASS_N = 14.0067
MOLAR_MASS_HCHO = 30.026
STOICHIOMETRY_UPPER_BOUNDS = {"conservative_1_hcho_per_n": 1.0, "max_2_hcho_per_n": 2.0}


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

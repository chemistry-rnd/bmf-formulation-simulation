from __future__ import annotations

from typing import Any

from .formulations import FORMULATIONS, SUPPLIER_ASSUMPTIONS


def purchased_mass(active_mass_g: float, supplier_solids_fraction: float) -> float:
    """Mass of purchased solution/dispersion needed to deliver active mass."""
    if supplier_solids_fraction <= 0:
        raise ValueError("supplier solids fraction must be positive")
    return active_mass_g / supplier_solids_fraction


def mass_balance_for(formula_id: str, wet_application_g_m2: float | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if formula_id not in FORMULATIONS:
        raise ValueError(f"unknown formula: {formula_id}")
    formula = FORMULATIONS[formula_id]
    if wet_application_g_m2 is None:
        wet_application_g_m2 = formula.wet_application_g_m2
    if wet_application_g_m2 < 0:
        raise ValueError("wet application must be non-negative")

    edge_area_m2 = SUPPLIER_ASSUMPTIONS["edge_thickness_m"] * SUPPLIER_ASSUMPTIONS["linear_piece_length_m"]
    pei_pct = formula.mass_fractions["pei_active"]
    acrylic_pct = formula.mass_fractions["acrylic_dry_solids"]
    wetter_pct = formula.mass_fractions["nonionic_wetter"]
    other_pct = formula.mass_fractions["other_nonvolatile_binder"]
    water_pct = formula.mass_fractions["water_carrier"]

    component_rows = []
    for component, pct in formula.mass_fractions.items():
        component_rows.append(
            {
                "formula": formula_id,
                "formula_name": formula.name,
                "wet_application_g_m2": wet_application_g_m2,
                "component": component,
                "mass_fraction_pct": pct,
                "mass_g_per_m2": wet_application_g_m2 * pct / 100.0,
                "mass_g_per_linear_m_16mm": wet_application_g_m2 * pct / 100.0 * edge_area_m2,
            }
        )

    pei_active_g = wet_application_g_m2 * pei_pct / 100.0
    acrylic_dry_g = wet_application_g_m2 * acrylic_pct / 100.0
    wetter_g = wet_application_g_m2 * wetter_pct / 100.0
    other_g = wet_application_g_m2 * other_pct / 100.0
    water_declared_g = wet_application_g_m2 * water_pct / 100.0

    pei_solution_g = purchased_mass(pei_active_g, SUPPLIER_ASSUMPTIONS["pei_solution_active_mass_fraction"])
    acrylic_dispersion_g = purchased_mass(acrylic_dry_g, SUPPLIER_ASSUMPTIONS["acrylic_dispersion_dry_solids_mass_fraction"])
    water_from_pei_g = pei_solution_g - pei_active_g
    water_from_acrylic_g = acrylic_dispersion_g - acrylic_dry_g
    free_water_g = water_declared_g - water_from_pei_g - water_from_acrylic_g

    total_nonvolatile_g = pei_active_g + acrylic_dry_g + wetter_g + other_g
    water_sum_g = water_from_pei_g + water_from_acrylic_g + free_water_g

    if abs(water_sum_g - water_declared_g) > 1e-9:
        raise ValueError("water reconciliation failed")
    if free_water_g < -1e-9:
        raise ValueError("negative free water; formulation is physically inconsistent")

    derived = {
        "formula": formula_id,
        "wet_application_g_m2": wet_application_g_m2,
        "pei_active_g_m2": pei_active_g,
        "acrylic_dry_g_m2": acrylic_dry_g,
        "nonionic_wetter_g_m2": wetter_g,
        "other_nonvolatile_g_m2": other_g,
        "total_nonvolatile_g_m2": total_nonvolatile_g,
        "total_water_g_m2": water_declared_g,
        "pei_solution_purchased_g_m2": pei_solution_g,
        "acrylic_dispersion_purchased_g_m2": acrylic_dispersion_g,
        "water_from_pei_solution_g_m2": water_from_pei_g,
        "water_from_acrylic_dispersion_g_m2": water_from_acrylic_g,
        "free_water_g_m2": free_water_g,
        "edge_area_m2_per_linear_m": edge_area_m2,
        "mass_per_linear_m_g": wet_application_g_m2 * edge_area_m2,
        "mass_fraction_sum_pct": sum(formula.mass_fractions.values()),
    }
    return component_rows, derived


def mass_balance_all(formula_ids: list[str], wet_overrides: dict[str, float] | None = None) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    derived: dict[str, dict[str, Any]] = {}
    overrides = wet_overrides or {}
    for fid in formula_ids:
        r, d = mass_balance_for(fid, overrides.get(fid))
        rows.extend(r)
        derived[fid] = d
    return rows, derived

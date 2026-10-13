from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import qmc

from .chemistry import theoretical_formaldehyde_capacity
from .formulations import SUPPLIER_ASSUMPTIONS
from .transport import drying_time_h, hcho_residual_fraction, peak_swelling_risk_index


MODEL_VERSION = "bmf-cpu-v0.3.0"


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    pei_active_pct: float
    acrylic_dry_pct: float
    wetter_pct: float
    water_pct: float
    wet_application_g_m2: float
    compatibility_note: str


def _water_from_purchased(pei_active_pct: float, acrylic_dry_pct: float, total_mass: float = 100.0) -> tuple[float, float, float]:
    pei_active = total_mass * pei_active_pct / 100.0
    acrylic_dry = total_mass * acrylic_dry_pct / 100.0
    pei_solution_water = pei_active  # 50% solution
    acrylic_dispersion_water = acrylic_dry
    required_water = pei_solution_water + acrylic_dispersion_water
    return pei_active, acrylic_dry, required_water


def build_candidate(
    candidate_id: str,
    pei_active_pct: float,
    acrylic_dry_pct: float,
    wet_application_g_m2: float,
    wetter_pct: float = 0.1,
) -> dict[str, Any]:
    if pei_active_pct < 0 or pei_active_pct > 20:
        raise ValueError("PEI active percentage must be 0-20")
    if acrylic_dry_pct < 0 or acrylic_dry_pct > 30:
        raise ValueError("acrylic dry percentage must be 0-30")
    if wet_application_g_m2 < 10 or wet_application_g_m2 > 40:
        raise ValueError("wet application must be 10-40 g/m2")
    if wetter_pct < 0:
        raise ValueError("wetter percentage must be non-negative")

    total_nonvol = pei_active_pct + acrylic_dry_pct + wetter_pct
    water_pct = 100.0 - total_nonvol
    pei_active_mass, acrylic_dry_mass, required_water = _water_from_purchased(pei_active_pct, acrylic_dry_pct, 100.0)

    if water_pct < 0:
        return {"candidate_id": candidate_id, "status": "INFEASIBLE", "reason": "negative water fraction"}
    if required_water > water_pct + 1e-9:
        return {"candidate_id": candidate_id, "status": "INFEASIBLE", "reason": "water in purchased solutions exceeds water/carrier fraction"}
    if SUPPLIER_ASSUMPTIONS["pei_solution_active_mass_fraction"] <= 0 or SUPPLIER_ASSUMPTIONS["acrylic_dispersion_dry_solids_mass_fraction"] <= 0:
        return {"candidate_id": candidate_id, "status": "INFEASIBLE", "reason": "invalid supplier concentration"}

    if pei_active_pct > 0 and acrylic_dry_pct > 0:
        compatibility = "UNKNOWN (PEI with anionic acrylic dispersion: require jar test, pH, viscosity and storage stability)"
    else:
        compatibility = "not constrained by PEI/acrylic mixing; shelf stability still unverified experimentally"
    capacity = theoretical_formaldehyde_capacity(
        pei_active_g_m2=wet_application_g_m2 * pei_active_pct / 100.0,
        group_availability=0.6,
        irreversibility_fraction=0.7,
        stoichiometry_upper_bound=1.0,
    )
    water_load = wet_application_g_m2 * water_pct / 100.0
    active_mass = wet_application_g_m2 * (pei_active_pct + acrylic_dry_pct) / 100.0
    residual = hcho_residual_fraction(
        capacity_g_m2=capacity["accessible_reversible_adjusted_capacity_g_m2"],
        wet_application_g_m2=wet_application_g_m2,
        barrier_factor=min(0.9, acrylic_dry_pct / 40.0),
        diffusion_factor=1.0,
        temperature_c=23.0,
    )
    swelling = peak_swelling_risk_index(water_load_g_m2=water_load, board_density_kg_m3=650.0, thickness_mm=16.0, barrier_factor=min(0.9, acrylic_dry_pct / 40.0))
    dry = drying_time_h(water_load_g_m2=water_load, evaporation_rate_factor=1.0, temperature_c=23.0, humidity_fraction=0.5)
    cost_index = active_mass + 0.05 * water_load
    robustness = 1.0 - (capacity["theoretical_max_hcho_g_m2"] - capacity["accessible_reversible_adjusted_capacity_g_m2"]) / max(capacity["theoretical_max_hcho_g_m2"], 1e-9)

    return {
        "candidate_id": candidate_id,
        "status": "FEASIBLE",
        "pei_active_pct": pei_active_pct,
        "acrylic_dry_pct": acrylic_dry_pct,
        "wetter_pct": wetter_pct,
        "water_pct": water_pct,
        "wet_application_g_m2": wet_application_g_m2,
        "pei_active_g_m2": wet_application_g_m2 * pei_active_pct / 100.0,
        "acrylic_dry_g_m2": wet_application_g_m2 * acrylic_dry_pct / 100.0,
        "water_load_g_m2": water_load,
        "active_mass_g_m2": active_mass,
        "theoretical_capacity_g_m2": capacity["accessible_reversible_adjusted_capacity_g_m2"],
        "hcho_residual_fraction_mid": residual,
        "peak_swelling_risk_index": swelling,
        "drying_time_h_mid": dry,
        "cost_index": cost_index,
        "robustness_index": robustness,
        "compatibility_status": compatibility,
        "water_margin_pct": water_pct - required_water,
    }


def screen_candidates(n_candidates: int, seed: int) -> list[dict[str, Any]]:
    if n_candidates < 1:
        raise ValueError("n_candidates must be positive")
    sampler = qmc.LatinHypercube(d=3, seed=seed)
    unit = sampler.random(n=n_candidates)
    rows = []
    for i, (u_pei, u_acr, u_dose) in enumerate(unit):
        candidate = build_candidate(
            f"X-{i + 1:04d}",
            0.0 + 20.0 * float(u_pei),
            0.0 + 30.0 * float(u_acr),
            10.0 + 30.0 * float(u_dose),
        )
        rows.append(candidate)
    return rows


def search_candidates(n_candidates: int, seed: int) -> list[dict[str, Any]]:
    if n_candidates < 1:
        raise ValueError("n_candidates must be positive")
    sampler = qmc.LatinHypercube(d=3, seed=seed)
    unit = sampler.random(n=n_candidates)
    rows = []
    for i, (u_pei, u_acr, u_dose) in enumerate(unit):
        pei = 0.0 + 20.0 * float(u_pei)
        acr = 0.0 + 30.0 * float(u_acr)
        dose = 10.0 + 30.0 * float(u_dose)
        candidate = build_candidate(f"X-{i + 1:04d}", pei, acr, dose)
        if candidate.get("status") == "FEASIBLE":
            rows.append(candidate)
    return rows


def select_distinct(candidates: list[dict[str, Any]], reference: list[dict[str, Any]], max_new: int = 3) -> list[dict[str, Any]]:
    if not candidates:
        return []
    # Candidate must improve at least one normalized objective over all references.
    all_items = reference + candidates
    def values(item):
        return (
            1.0 - item["hcho_residual_fraction_mid"],
            1.0 - item["peak_swelling_risk_index"],
            1.0 - (item["drying_time_h_mid"] / 24.0),
            1.0 / max(item["active_mass_g_m2"], 1e-9),
            1.0 / max(item["cost_index"], 1e-9),
        )
    # Normalize per combined pool.
    arrays = np.array([values(x) for x in all_items], dtype=float)
    mins = arrays.min(axis=0)
    maxs = arrays.max(axis=0)
    ranges = np.where(maxs - mins > 0, maxs - mins, 1.0)
    norm = (arrays - mins) / ranges
    ref_norm = norm[:len(reference)]
    cand_norm = norm[len(reference):]
    ref_best = ref_norm.max(axis=0)

    eligible = []
    for idx, cand in enumerate(candidates):
        improvements = int((cand_norm[idx] > ref_best + 0.05).sum())
        if improvements >= 1:
            eligible.append((idx, cand, cand_norm[idx]))

    selected: list[dict[str, Any]] = []
    if not eligible:
        return selected
    eligible.sort(key=lambda x: float(cand_norm[x[0]].sum()), reverse=True)
    for idx, cand, _ in eligible[:max_new]:
        cand.pop("__norm", None)
        selected.append(cand)
    return selected
    return selected

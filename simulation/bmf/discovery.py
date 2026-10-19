from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.stats import qmc

from .chemistry import theoretical_formaldehyde_capacity
from .formulations import SUPPLIER_ASSUMPTIONS
from .transport import drying_time_h, hcho_residual_fraction, peak_swelling_risk_index

MODEL_VERSION = "bmf-cpu-v0.5.0"
DISCOVERY_SCHEMA_VERSION = "formula-id-v1"
FUNCTIONAL_RESIDUAL_LIMIT = 0.90
MIN_PEI_FOR_MODELLED_HCHO = 2.0
BASELINE_A_CAPACITY_THRESHOLD = 0.05


def discovery_labels(used_ids: set[str], count: int) -> list[str]:
    """Letters for discovered candidates that never collide with formulation ids.

    Formulation ids occupy A..F, so discovered candidates start at the first
    free letter. Labels stay per-run and are not stable across runs; the stable
    identity is ``stable_formula_id``.
    """
    labels: list[str] = []
    index = 0
    while len(labels) < count:
        letter = chr(ord("A") + index)
        index += 1
        if letter not in used_ids:
            labels.append(letter)
    return labels


@dataclass(frozen=True)
class FunctionalStatus:
    mass_balance_status: str
    functional_status: str
    compatibility_status: str
    model_support_status: str
    lab_validation_status: str
    selection_status: str
    rejection_reason: str


def _water_from_purchased(pei_active_pct: float, acrylic_dry_pct: float, total_mass: float = 100.0) -> tuple[float, float, float]:
    pei_active = total_mass * pei_active_pct / 100.0
    acrylic_dry = total_mass * acrylic_dry_pct / 100.0
    required_water = pei_active + acrylic_dry
    return pei_active, acrylic_dry, required_water


def stable_formula_id(candidate: dict[str, Any], schema_version: str = DISCOVERY_SCHEMA_VERSION) -> str:
    payload = {
        "schema_version": schema_version,
        "supplier_basis": candidate.get("supplier_basis", "default_seed_assumptions"),
        "pei_active_pct": round(float(candidate["pei_active_pct"]), 3),
        "acrylic_dry_pct": round(float(candidate["acrylic_dry_pct"]), 3),
        "wetter_pct": round(float(candidate["wetter_pct"]), 3),
        "wet_application_g_m2": round(float(candidate["wet_application_g_m2"]), 3),
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:10]
    return f"BMF-{digest}"


def build_candidate(
    candidate_id: str,
    pei_active_pct: float,
    acrylic_dry_pct: float,
    wet_application_g_m2: float,
    wetter_pct: float = 0.1,
    functional_residual_limit: float = FUNCTIONAL_RESIDUAL_LIMIT,
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
    _pei, _acrylic, required_water = _water_from_purchased(pei_active_pct, acrylic_dry_pct, 100.0)

    mass_balance_status = "VALID"
    rejection_reason = "no rejection"
    if water_pct < 0:
        mass_balance_status = "INVALID"
        rejection_reason = "negative water fraction"
    elif required_water > water_pct + 1e-9:
        mass_balance_status = "INVALID"
        rejection_reason = "water in purchased PEI/acrylic solutions exceeds water/carrier fraction"

    if pei_active_pct > 0 and acrylic_dry_pct > 0:
        compatibility_status = "REQUIRES_COMPATIBILITY_TEST"
        compatibility_note = "PEI with anionic acrylic dispersion: jar test, pH, viscosity and storage stability required"
    else:
        compatibility_status = "COMPOSITION_ONLY"
        compatibility_note = "shelf stability still unverified experimentally"

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

    # Functional status is not a real measurement; it is a mechanistic screen.
    if mass_balance_status != "VALID":
        functional_status = "SCREEN_FAIL"
        functional_reason = rejection_reason
    elif pei_active_pct < MIN_PEI_FOR_MODELLED_HCHO:
        functional_status = "UNKNOWN" if acrylic_dry_pct > 0 else "SCREEN_FAIL"
        functional_reason = "barrier-only claim requires calibrated permeability; not a verified HCHO reduction"
    elif residual >= functional_residual_limit:
        functional_status = "SCREEN_FAIL"
        functional_reason = f"residual HCHO surrogate {residual:.3f} exceeds limit {functional_residual_limit:.2f}"
    elif capacity["accessible_reversible_adjusted_capacity_g_m2"] < BASELINE_A_CAPACITY_THRESHOLD * theoretical_formaldehyde_capacity(
        pei_active_g_m2=10.0, group_availability=0.6, irreversibility_fraction=0.7, stoichiometry_upper_bound=1.0
    )["accessible_reversible_adjusted_capacity_g_m2"]:
        functional_status = "SCREEN_FAIL"
        functional_reason = "theoretical PEI/HCHO capacity below screening threshold"
    else:
        functional_status = "SCREEN_PASS"
        functional_reason = "mechanistic screen passes; still not an experimentally demonstrated HCHO reduction"

    candidate = {
        "candidate_id": candidate_id,
        "status": "FEASIBLE" if mass_balance_status == "VALID" else "INVALID",
        "mass_balance_status": mass_balance_status,
        "functional_status": functional_status,
        "functional_reason": functional_reason,
        "compatibility_status": compatibility_status,
        "compatibility_note": compatibility_note,
        "model_support_status": "MODELLED",
        "lab_validation_status": "NOT_TESTED",
        "selection_status": "REJECTED",
        "rejection_reason": rejection_reason,
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
        "water_margin_pct": water_pct - required_water,
        "supplier_basis": "default_seed_assumptions",
        "stable_formula_id": None,
        "candidate_rank": None,
        "display_label": None,
        "source_run_id": None,
    }
    candidate["stable_formula_id"] = stable_formula_id(candidate)
    return candidate


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


def select_distinct(candidates: list[dict[str, Any]], reference: list[dict[str, Any]], max_new: int = 5) -> list[dict[str, Any]]:
    eligible: list[dict[str, Any]] = []
    for cand in candidates:
        if cand.get("mass_balance_status") != "VALID":
            cand["selection_status"] = "REJECTED"
            cand["rejection_reason"] = cand.get("rejection_reason", "mass balance invalid")
            continue
        if cand.get("functional_status") != "SCREEN_PASS":
            cand["selection_status"] = "REJECTED"
            cand.setdefault("rejection_reason", cand.get("functional_reason", "functional screen failed"))
            continue
        if cand.get("compatibility_status") == "REQUIRES_COMPATIBILITY_TEST":
            cand["selection_reason"] = "compatibility testing required; candidate remains a research candidate only"
        else:
            cand["selection_reason"] = "no PEI/acrylic incompatibility gate applied, but shelf stability still unverified"
        eligible.append(cand)

    # Raw physically meaningful objectives, all oriented higher-is-better.
    def raw_metrics(item):
        return (
            1.0 - float(item["hcho_residual_fraction_mid"]),
            -float(item["water_load_g_m2"]),
            -float(item["peak_swelling_risk_index"]),
            -float(item["drying_time_h_mid"]),
            -float(item["active_mass_g_m2"]),
            -float(item["cost_index"]),
            float(item["robustness_index"]),
        )

    all_items = reference + eligible
    if not eligible:
        for item in candidates:
            item["selection_status"] = "REJECTED"
            item.setdefault("rejection_reason", item.get("rejection_reason", "no eligible candidate"))
        return []
    raw = np.array([raw_metrics(x) for x in all_items], dtype=float)
    mins = raw.min(axis=0)
    maxs = raw.max(axis=0)
    ranges = np.where(maxs - mins > 0, maxs - mins, 1.0)
    norm = (raw - mins) / ranges
    ref_norm = norm[:len(reference)]
    cand_norm = norm[len(reference):]
    ref_best = ref_norm.max(axis=0) if len(reference) else np.zeros(raw.shape[1])

    candidates_with_norm = [(idx, cand, cand_norm[idx]) for idx, cand in enumerate(eligible)]
    pareto_indices = []
    for idx, cand, cn in candidates_with_norm:
        dominated = False
        # Compare against references.
        for r in range(len(reference)):
            if np.all(ref_norm[r] >= cn) and np.any(ref_norm[r] > cn):
                dominated = True
                break
        # Compare against other eligible candidates.
        if not dominated:
            for jdx, other, on in candidates_with_norm:
                if idx == jdx:
                    continue
                if np.all(on >= cn) and np.any(on > cn):
                    dominated = True
                    break
        if not dominated:
            pareto_indices.append((idx, cand, cn))

    if not pareto_indices:
        for item in eligible:
            item["selection_status"] = "REJECTED"
            item.setdefault("rejection_reason", "not Pareto-optimal in combined pool")
        return []

    # Diversity on normalized parameter space.
    selected: list[dict[str, Any]] = []
    chosen_params = []
    for _idx, cand, _cn in sorted(pareto_indices, key=lambda z: float(z[2].sum()), reverse=True):
        if len(selected) >= 5:
            break
        param = np.array([
            cand["pei_active_pct"] / 20.0,
            cand["acrylic_dry_pct"] / 30.0,
            (cand["wet_application_g_m2"] - 10.0) / 30.0,
        ], dtype=float)
        if chosen_params and min(float(np.linalg.norm(param - p)) for p in chosen_params) < 0.15:
            continue
        chosen_params.append(param)
        cand["selection_status"] = "SELECTED"
        cand.setdefault("selection_reason", "Pareto and diversity gates passed; experimental validation required")
        selected.append(cand)

    for cand in candidates:
        if cand not in selected and cand.get("selection_status") == "REVIEW_REQUIRED":
            pass
        elif cand not in selected and cand.get("mass_balance_status") == "VALID":
            cand["selection_status"] = "REJECTED"
            cand.setdefault("rejection_reason", "not selected after Pareto and diversity gates")
    # candidate_rank/display labels are assigned by caller; guard placeholders.
    for cand in selected:
        cand.setdefault("candidate_rank", None)
        cand.setdefault("display_label", None)
        cand.setdefault("source_run_id", None)
    return selected

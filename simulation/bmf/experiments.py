from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import qmc

from .chemistry import theoretical_formaldehyde_capacity
from .formulations import FORMULATIONS, ALL_FORMULATIONS
from .mass_balance import mass_balance_for
from .transport import drying_time_h, hcho_residual_fraction, peak_swelling_risk_index

MODEL_VERSION = "bmf-cpu-v0.1.0"


def _scale_unit(series: np.ndarray, low: float, high: float) -> np.ndarray:
    return low + (high - low) * series


def run_virtual_experiments(
    formula_ids: list[str],
    n_scenarios: int,
    seed: int,
    mode: str = "pilot",
) -> list[dict[str, Any]]:
    if n_scenarios < 1 or n_scenarios > 10000:
        raise ValueError("n_scenarios must be in [1, 10000]")
    rng = np.random.default_rng(seed)
    sampler = qmc.LatinHypercube(d=10, seed=seed)
    base_unit = sampler.random(n=n_scenarios)

    rows: list[dict[str, Any]] = []
    for fid in formula_ids:
        formula = FORMULATIONS[fid]
        # Deterministic per-formula random offset while preserving reproducibility.
        unit = (base_unit + qmc.LatinHypercube(d=10, seed=seed + ord(fid)).random(n=n_scenarios)) / 2.0
        unit = np.clip(unit, 0.0, 1.0)

        temperature = _scale_unit(unit[:, 0], 18.0, 30.0)
        humidity = _scale_unit(unit[:, 1], 0.35, 0.80)
        board_density = _scale_unit(unit[:, 2], 580.0, 720.0)
        thickness_mm = _scale_unit(unit[:, 3], 14.0, 18.0)
        dose_variation = _scale_unit(unit[:, 4], 0.85, 1.15)
        pei_availability = _scale_unit(unit[:, 5], 0.20, 1.00)
        acrylic_barrier = _scale_unit(unit[:, 6], 0.00, 0.85)
        diffusion_factor = _scale_unit(unit[:, 7], 0.70, 1.30)
        evaporation_factor = _scale_unit(unit[:, 8], 0.60, 1.40)
        cost_coeff = _scale_unit(unit[:, 9], 0.80, 1.25)

        # Vary stoichiometric interpretation as a stated uncertainty range.
        stoich = rng.choice(np.array([1.0, 2.0]), size=n_scenarios, p=np.array([0.7, 0.3]))
        reversibility = _scale_unit(rng.random(n_scenarios), 0.20, 0.95)

        _, derived = mass_balance_for(fid, formula.wet_application_g_m2 * 1.0)
        wet_base = float(derived["wet_application_g_m2"])
        pei_base = float(derived["pei_active_g_m2"])
        water_base = float(derived["total_water_g_m2"])
        nonvolatile_base = float(derived["total_nonvolatile_g_m2"])

        for i in range(n_scenarios):
            wet = wet_base * float(dose_variation[i])
            pei = pei_base * float(dose_variation[i])
            water = water_base * float(dose_variation[i])
            capacity = theoretical_formaldehyde_capacity(
                pei_active_g_m2=pei,
                stoichiometry_upper_bound=float(stoich[i]),
                group_availability=float(pei_availability[i]),
                irreversibility_fraction=float(reversibility[i]),
            )
            cap = float(capacity["accessible_reversible_adjusted_capacity_g_m2"])
            max_cap = float(capacity["theoretical_max_hcho_g_m2"])
            residual = hcho_residual_fraction(
                capacity_g_m2=cap,
                wet_application_g_m2=wet,
                barrier_factor=float(acrylic_barrier[i]),
                diffusion_factor=float(diffusion_factor[i]),
                temperature_c=float(temperature[i]),
            )
            swelling = peak_swelling_risk_index(
                water_load_g_m2=water,
                board_density_kg_m3=float(board_density[i]),
                thickness_mm=float(thickness_mm[i]),
                barrier_factor=float(acrylic_barrier[i]),
            )
            dry = drying_time_h(
                water_load_g_m2=water,
                evaporation_rate_factor=float(evaporation_factor[i]),
                temperature_c=float(temperature[i]),
                humidity_fraction=float(humidity[i]),
            )
            nonvolatile = nonvolatile_base * float(dose_variation[i])
            active_mass = pei + nonvolatile - pei  # PEI + acrylic dry (if any) via component recompute below
            # Recompute active consumption directly from original percentages.
            active_consumption = wet * (formula.mass_fractions["pei_active"] + formula.mass_fractions["acrylic_dry_solids"]) / 100.0
            cost_index = active_consumption * float(cost_coeff[i]) + 0.05 * water
            rows.append(
                {
                    "scenario_id": f"{fid}-{i + 1:06d}",
                    "formula": fid,
                    "formula_name": formula.name,
                    "run_mode": mode,
                    "seed": seed,
                    "temperature_c": float(temperature[i]),
                    "relative_humidity_fraction": float(humidity[i]),
                    "board_density_kg_m3": float(board_density[i]),
                    "edge_thickness_mm": float(thickness_mm[i]),
                    "dose_variation_fraction": float(dose_variation[i]),
                    "wet_application_g_m2": wet,
                    "water_load_g_m2": water,
                    "pei_active_g_m2": pei,
                    "acrylic_dry_g_m2": wet * formula.mass_fractions["acrylic_dry_solids"] / 100.0,
                    "nonvolatile_mass_g_m2": nonvolatile,
                    "stoichiometry_upper_bound_hcho_per_n": float(stoich[i]),
                    "group_availability_fraction": float(pei_availability[i]),
                    "irreversibility_fraction": float(reversibility[i]),
                    "theoretical_max_capacity_g_m2": max_cap,
                    "accessible_capacity_g_m2": cap,
                    "hcho_residual_fraction_predicted": residual,
                    "peak_swelling_risk_index": swelling,
                    "drying_time_h_predicted": dry,
                    "active_mass_consumption_g_m2": active_consumption,
                    "cost_index": cost_index,
                    "model_version": MODEL_VERSION,
                    "result_status": "virtual; not a measured outcome",
                }
            )
    return rows

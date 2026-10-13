from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from .chemistry import theoretical_formaldehyde_capacity
from .experiments import MODEL_VERSION
from .formulations import FORMULATIONS
from .mass_balance import mass_balance_for
from .transport import hcho_residual_fraction, peak_swelling_risk_index, drying_time_h
from .formulations import FORMULATIONS
from .mass_balance import mass_balance_for
from .transport import hcho_residual_fraction, peak_swelling_risk_index, drying_time_h


def aggregate_properties(df: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for formula, group in df.groupby("formula", sort=True):
        rows.append(
            {
                "formula": formula,
                "formula_name": group["formula_name"].iloc[0],
                "n_scenarios": int(len(group)),
                "model_version": MODEL_VERSION,
                "water_load_g_m2_mean": float(group["water_load_g_m2"].mean()),
                "water_load_g_m2_p05": float(group["water_load_g_m2"].quantile(0.05)),
                "water_load_g_m2_p95": float(group["water_load_g_m2"].quantile(0.95)),
                "hcho_residual_fraction_mean": float(group["hcho_residual_fraction_predicted"].mean()),
                "hcho_residual_fraction_p05": float(group["hcho_residual_fraction_predicted"].quantile(0.05)),
                "hcho_residual_fraction_p95": float(group["hcho_residual_fraction_predicted"].quantile(0.95)),
                "peak_swelling_risk_mean": float(group["peak_swelling_risk_index"].mean()),
                "peak_swelling_risk_p95": float(group["peak_swelling_risk_index"].quantile(0.95)),
                "drying_time_h_mean": float(group["drying_time_h_predicted"].mean()),
                "drying_time_h_p95": float(group["drying_time_h_predicted"].quantile(0.95)),
                "active_mass_consumption_g_m2_mean": float(group["active_mass_consumption_g_m2"].mean()),
                "cost_index_mean": float(group["cost_index"].mean()),
                "robustness_residual_cv": float(group["hcho_residual_fraction_predicted"].std(ddof=0) / max(group["hcho_residual_fraction_predicted"].mean(), 1e-9)),
                "note": "predicted aggregates from virtual scenarios; not measured outcomes",
            }
        )
    return rows


def sensitivity_analysis(df_summary: pd.DataFrame, base_capacity: dict[str, float], seed: int) -> list[dict[str, Any]]:
    """One-factor perturbation around the representative baseline."""
    rng = np.random.default_rng(seed + 7919)
    rows: list[dict[str, Any]] = []
    for fid in df_summary["formula"].tolist():
        formula_obj = FORMULATIONS[fid]
        mass_rows, derived = mass_balance_for(fid, formula_obj.wet_application_g_m2)
        base_water = float(derived["total_water_g_m2"])
        base_pei = float(derived["pei_active_g_m2"])
        base_cap = theoretical_formaldehyde_capacity(pei_active_g_m2=base_pei).get("accessible_reversible_adjusted_capacity_g_m2", 0.0)
        # Base residual with midpoint uncertainty.
        base_residual = hcho_residual_fraction(capacity_g_m2=base_cap, wet_application_g_m2=derived["wet_application_g_m2"], barrier_factor=0.3, diffusion_factor=1.0)
        base_swelling = peak_swelling_risk_index(water_load_g_m2=base_water, board_density_kg_m3=650.0, thickness_mm=16.0, barrier_factor=0.3)
        base_drying = drying_time_h(water_load_g_m2=base_water, evaporation_rate_factor=1.0, temperature_c=23.0, humidity_fraction=0.5)
        factors = {
            "pei_availability_-20pct": ({"group_availability": 0.8}, {}),
            "pei_availability_+20pct": ({"group_availability": 1.0}, {}),
            "acrylic_barrier_-20pct": ({"barrier_factor": 0.1}, {}),
            "acrylic_barrier_+20pct": ({"barrier_factor": 0.5}, {}),
            "water_load_-20pct": ({"water_load": 0.8}, {}),
            "water_load_+20pct": ({"water_load": 1.2}, {}),
        }
        for name, (pert, _) in factors.items():
            cap_mult = pert.get("group_availability", 1.0)
            barrier = pert.get("barrier_factor", 0.3)
            water_mult = pert.get("water_load", 1.0)
            water = base_water * water_mult
            cap = base_cap * cap_mult
            residual = hcho_residual_fraction(capacity_g_m2=cap, wet_application_g_m2=derived["wet_application_g_m2"], barrier_factor=barrier, diffusion_factor=1.0)
            swelling = peak_swelling_risk_index(water_load_g_m2=water, board_density_kg_m3=650.0, thickness_mm=16.0, barrier_factor=barrier)
            drying = drying_time_h(water_load_g_m2=water, evaporation_rate_factor=1.0, temperature_c=23.0, humidity_fraction=0.5)
            rows.append(
                {
                    "formula": fid,
                    "scenario": "baseline_one_factor_perturbation",
                    "parameter_perturbation": name,
                    "base_hcho_residual_fraction": base_residual,
                    "perturbed_hcho_residual_fraction": residual,
                    "delta_hcho_residual_fraction": residual - base_residual,
                    "base_peak_swelling_risk_index": base_swelling,
                    "perturbed_peak_swelling_risk_index": swelling,
                    "delta_peak_swelling_risk_index": swelling - base_swelling,
                    "base_drying_time_h": base_drying,
                    "perturbed_drying_time_h": drying,
                    "delta_drying_time_h": drying - base_drying,
                    "model_version": MODEL_VERSION,
                }
            )
    return rows


def pareto_table(summary_df: pd.DataFrame) -> pd.DataFrame:
    # Metrics where higher is better.
    emission_reduction = 1.0 - summary_df["hcho_residual_fraction_mean"]
    robustness = 1.0 - summary_df["robustness_residual_cv"].clip(upper=1.0)
    # Normalize each metric to [0, 1].
    def norm_higher_better(x):
        span = x.max() - x.min()
        if span == 0:
            return pd.Series(0.5, index=x.index)
        return (x - x.min()) / span

    def norm_lower_better(x):
        span = x.max() - x.min()
        if span == 0:
            return pd.Series(0.5, index=x.index)
        return (x.max() - x) / span

    water_term = norm_lower_better(summary_df["peak_swelling_risk_p95"])
    drying_term = norm_lower_better(summary_df["drying_time_h_p95"])
    active_term = norm_lower_better(summary_df["active_mass_consumption_g_m2_mean"])
    cost_term = norm_lower_better(summary_df["cost_index_mean"])
    reduction_term = norm_higher_better(emission_reduction)
    robustness_term = norm_higher_better(robustness)

    out = summary_df[["formula", "formula_name"]].copy()
    out["potential_emission_reduction_score"] = reduction_term
    out["water_load_swelling_risk_score"] = water_term
    out["drying_time_score"] = drying_term
    out["active_substance_consumption_score"] = active_term
    out["cost_score"] = cost_term
    out["robustness_score"] = robustness_term
    out["pareto_optimal"] = True
    # Simple dominance: a formula is dominated if another has >= all scores and > at least one.
    scores = out[
        [
            "potential_emission_reduction_score",
            "water_load_swelling_risk_score",
            "drying_time_score",
            "active_substance_consumption_score",
            "cost_score",
            "robustness_score",
        ]
    ]
    for i in out.index:
        dominated = False
        for j in out.index:
            if i == j:
                continue
            if (scores.loc[j] >= scores.loc[i]).all() and (scores.loc[j] > scores.loc[i]).any():
                dominated = True
                break
        out.loc[i, "pareto_optimal"] = not dominated
    return out

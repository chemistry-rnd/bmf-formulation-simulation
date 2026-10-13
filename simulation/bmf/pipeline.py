from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .analysis import aggregate_properties, pareto_table, sensitivity_analysis
from .experiments import MODEL_VERSION, run_virtual_experiments
from .formulations import FORMULATIONS, ALL_FORMULATIONS
from .mass_balance import mass_balance_all


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _assumptions() -> dict[str, Any]:
    return {
        "source": "PR #4 BMF candidate formulations (research input, not laboratory data)",
        "result_type": "virtual computational screen, not experimental measurement",
        "models_are_not_replacements_for_laboratory_tests": True,
        "available_ingredients": {
            id_: {
                "name": f.name,
                "intended_use": f.use,
                "nominal_wet_application_g_m2": f.wet_application_g_m2,
                "mass_fractions_pct": f.mass_fractions,
            }
            for id_, f in FORMULATIONS.items()
        },
        "supplier_and_material_assumptions": {
            "pei_solution_active_mass_fraction": 0.50,
            "acrylic_dispersion_dry_solids_mass_fraction": 0.50,
            "nonionic_wetter_mass_fraction": 1.00,
            "pei_nitrogen_mass_fraction": 0.232558,
            "stoichiometry_upper_bound_hcho_per_nitrogen": "1 to 2, selected with stated uncertainty",
            "group_availability_fraction_range": [0.20, 1.00],
            "irreversibility_fraction_range": [0.20, 0.95],
            "edge_thickness_m": 0.016,
            "scenario_parameter_ranges": {
                "temperature_c": [18, 30],
                "relative_humidity_fraction": [0.35, 0.80],
                "board_density_kg_m3": [580, 720],
                "edge_thickness_mm": [14, 18],
                "dose_variation_fraction": [0.85, 1.15],
            },
        },
        "functions": {
            "capacity": "theoretical upper bound using available nitrogen groups; not reaction yield",
            "moisture": "parametric evaporation model with SciPy solve_ivp",
            "hcho_transfer": "bounded surrogate for residual emission fraction",
            "swelling": "risk proxy from water volume fraction; not measured swelling",
            "drying": "parametric drying-time estimate",
        },
        "missing_inputs_not_invented": [
            "reaction kinetics and rate constants",
            "measured diffusion coefficients in the exact LDSP and coating",
            "laboratory swelling, emission and VOC measurements",
            "toxicology, compatibility and storage stability data",
            "exact commercial grades and batch rheology",
        ],
    }


def run_pipeline(
    output_dir: Path,
    formula_ids: list[str],
    n_scenarios: int,
    seed: int,
    mode: str = "pilot",
) -> dict[str, Any]:
    if mode not in {"mock", "pilot", "full"}:
        raise ValueError("mode must be mock, pilot or full")
    for fid in formula_ids:
        if fid not in FORMULATIONS:
            raise ValueError(f"unknown formula: {fid}")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "plots").mkdir(parents=True, exist_ok=True)

    # Stage A
    mass_rows, derived = mass_balance_all(formula_ids)
    mass_df = pd.DataFrame(mass_rows)
    mass_df.to_csv(output_dir / "mass_balance.csv", index=False, float_format="%.12g")

    # Stage D
    if mode == "mock":
        # Deterministic tiny sample while keeping the same public artifact names.
        n_eff = min(n_scenarios, 25)
    else:
        n_eff = n_scenarios
    experiment_rows = run_virtual_experiments(formula_ids, n_eff, seed, mode)
    exp_df = pd.DataFrame(experiment_rows)
    exp_df.to_csv(output_dir / "virtual_experiments.csv", index=False, float_format="%.12g")

    # Aggregates and property predictions
    prop_rows = aggregate_properties(exp_df)
    prop_df = pd.DataFrame(prop_rows)
    prop_df.to_csv(output_dir / "property_predictions.csv", index=False, float_format="%.12g")

    # Sensitivity
    # Build baseline derived water and capacity inputs for each formula.
    from .formulations import FORMULATIONS as F

    sens_rows = sensitivity_analysis(prop_df, {}, seed)
    sens_df = pd.DataFrame(sens_rows)
    sens_df.to_csv(output_dir / "sensitivity.csv", index=False, float_format="%.12g")

    # Pareto
    pareto_df = pareto_table(prop_df)
    pareto_df.to_csv(output_dir / "pareto.csv", index=False, float_format="%.12g")

    # Assumptions
    assumptions = _assumptions()
    (output_dir / "assumptions.json").write_text(
        json.dumps(assumptions, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Plots
    hist_path = output_dir / "plots" / "hcho_residual_hist.png"
    plt.figure(figsize=(7, 4))
    for fid in formula_ids:
        subset = exp_df[exp_df["formula"] == fid]
        plt.hist(subset["hcho_residual_fraction_predicted"], bins=30, alpha=0.45, label=fid)
    plt.xlabel("Predicted residual HCHO fraction (dimensionless)")
    plt.ylabel("Scenario count")
    plt.title("Virtual scenario distribution (not measured emissions)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(hist_path, dpi=120)
    plt.close()

    pareto_path = output_dir / "plots" / "pareto_scores.png"
    plt.figure(figsize=(7, 4))
    labels = pareto_df["formula"].tolist()
    metrics = ["potential_emission_reduction_score", "water_load_swelling_risk_score", "drying_time_score", "cost_score", "robustness_score"]
    x = np.arange(len(labels))
    width = 0.15
    for k, metric in enumerate(metrics):
        plt.bar(x + k * width, pareto_df[metric].to_numpy(), width, label=metric.replace("_score", ""))
    plt.xticks(x + width * 2, labels)
    plt.ylim(0, 1.1)
    plt.ylabel("Normalized score (predicted)")
    plt.title("Pareto characteristic scores (virtual)")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(pareto_path, dpi=120)
    plt.close()

    # Report
    report_path = output_dir / "report.md"
    limitations_path = output_dir / "limitations.md"
    best_pareto = pareto_df.loc[pareto_df["pareto_optimal"] == True, "formula"].tolist()
    properties_lines = [
        "| Formula | Mean residual HCHO | p05-p95 residual | Mean water load g/m2 | p95 swelling risk | Mean drying time h | Active mass g/m2 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in prop_df.iterrows():
        properties_lines.append(
            "| {formula} | {res:.3f} | {p05:.3f}-{p95:.3f} | {water:.2f} | {swell:.4f} | {dry:.2f} | {active:.2f} |".format(
                formula=r["formula"],
                res=r["hcho_residual_fraction_mean"],
                p05=r["hcho_residual_fraction_p05"],
                p95=r["hcho_residual_fraction_p95"],
                water=r["water_load_g_m2_mean"],
                swell=r["peak_swelling_risk_p95"],
                dry=r["drying_time_h_mean"],
                active=r["active_mass_consumption_g_m2_mean"],
            )
        )
    properties_markdown = "\n".join(properties_lines)

    report = f"""# BMF formulation simulation report

Model version: `{MODEL_VERSION}`
Mode: `{mode}`
Random seed: `{seed}`
Scenario count per formula: `{n_eff}`
Formulas: {", ".join(formula_ids)}
Source commit: `{git_commit()}`
Generated: {datetime.now(timezone.utc).isoformat()}

## Result status

All values below are **virtual model predictions** from a CPU parameter screen. They are not laboratory measurements, safety evidence, or proof of efficacy.

## Mass balance stage

{mass_df.groupby('formula')['mass_g_per_m2'].sum().to_string() if False else 'Mass-balance rows and derived component masses are stored in `mass_balance.csv`.'}

Formula A/B/C mass fractions sum to 100 % on the stated basis; water includes water in purchased polymer dispersions and PEI solutions.

## Predicted properties (aggregates)

{properties_markdown}

## Pareto screen

Pareto-optimal candidates: {", ".join(best_pareto) if best_pareto else "none"}.

Pareto characteristics: potential emission reduction, water load/swelling risk, drying time, active substance consumption, cost, and robustness to parameter uncertainty.

## Interpretation boundary

Use this screen to prioritize laboratory tests. It does not assign safe, production-ready, or regulatory status to any formula.
"""
    report_path.write_text(report, encoding="utf-8")

    limitations = """# Limitations

- This is a computational study, not experimental confirmation of formulation properties.
- Formaldehyde capacities are theoretical upper bounds adjusted by uncertain availability and reversibility fractions.
- No reaction kinetics, measured diffusion coefficients, or laboratory swelling/emission data were available; they were not invented.
- Swelling, drying time, cost and residual emission are surrogate indicators.
- Compatibility of PEI with anionic acrylic emulsions, pH, VOC, odor, toxicity and storage stability were not modelled and must be verified.
- Rankings may change under different parameter assumptions; see `sensitivity.csv`.
- Formula C, and to a lesser extent B, may be impractical at the listed acrylic solids without alternate binders.
"""
    limitations_path.write_text(limitations, encoding="utf-8")

    # Manifest with hashes
    artifact_paths = [
        "mass_balance.csv",
        "virtual_experiments.csv",
        "property_predictions.csv",
        "sensitivity.csv",
        "pareto.csv",
        "assumptions.json",
        "report.md",
        "limitations.md",
        "plots/hcho_residual_hist.png",
        "plots/pareto_scores.png",
    ]
    files_hash = {rel: sha256_file(output_dir / rel) for rel in artifact_paths}
    manifest = {
        "model_name": "BMF CPU formulation simulation",
        "model_version": MODEL_VERSION,
        "source_commit": git_commit(),
        "mode": mode,
        "seed": seed,
        "n_scenarios_requested": n_scenarios,
        "n_scenarios_executed_per_formula": n_eff,
        "formulas": formula_ids,
        "python_artifact_layout": artifact_paths,
        "sha256": files_hash,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "generated_artifact_is_virtual": True,
    }
    (output_dir / "model_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    # Add hashes for all artifacts including sha256 manifest? Write sums excluding itself.
    all_for_hash = artifact_paths + ["model_manifest.json"]
    sums_lines = []
    for rel in all_for_hash:
        sums_lines.append(f"{sha256_file(output_dir / rel)}  {rel}")
    (output_dir / "sha256sums.txt").write_text("\n".join(sums_lines) + "\n", encoding="utf-8")

    return {
        "output_dir": str(output_dir),
        "files": all_for_hash,
        "n_scenarios": n_eff,
        "formulas": formula_ids,
    }

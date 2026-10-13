from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .experiments import MODEL_VERSION

REPORT_MANIFEST_NAME = "report-manifest.json"
RESEARCH_REPORT_NAME = "BMF-Research-Report.md"
EXPERT_BRIEF_NAME = "expert-feedback-brief.md"
TARGET_RECONCILIATION_NAME = "target-reconciliation.csv"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_artifacts(input_dir: Path) -> dict[str, Any]:
    required = {
        "mass_balance.csv",
        "virtual_experiments.csv",
        "property_predictions.csv",
        "sensitivity.csv",
        "pareto.csv",
        "assumptions.json",
        "model_manifest.json",
    }
    missing = [name for name in required if not (input_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(f"missing simulation artifacts: {missing}")
    discovered_path = input_dir / "discovered_candidates.json"
    candidates = []
    if discovered_path.is_file():
        candidates = json.loads(discovered_path.read_text(encoding="utf-8"))

    return {
        "mass_balance": pd.read_csv(input_dir / "mass_balance.csv"),
        "experiments": pd.read_csv(input_dir / "virtual_experiments.csv"),
        "properties": pd.read_csv(input_dir / "property_predictions.csv"),
        "sensitivity": pd.read_csv(input_dir / "sensitivity.csv"),
        "pareto": pd.read_csv(input_dir / "pareto.csv"),
        "assumptions": json.loads((input_dir / "assumptions.json").read_text(encoding="utf-8")),
        "manifest": json.loads((input_dir / "model_manifest.json").read_text(encoding="utf-8")),
        "candidates": candidates,
    }


def aggregate_from_experiments(experiments: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for formula, group in experiments.groupby("formula", sort=True):
        rows.append(
            {
                "formula": formula,
                "n": int(len(group)),
                "hcho_residual_p05": float(group["hcho_residual_fraction_predicted"].quantile(0.05)),
                "hcho_residual_p50": float(group["hcho_residual_fraction_predicted"].quantile(0.50)),
                "hcho_residual_p95": float(group["hcho_residual_fraction_predicted"].quantile(0.95)),
                "water_load_p05": float(group["water_load_g_m2"].quantile(0.05)),
                "water_load_p50": float(group["water_load_g_m2"].quantile(0.50)),
                "water_load_p95": float(group["water_load_g_m2"].quantile(0.95)),
                "swelling_p95": float(group["peak_swelling_risk_index"].quantile(0.95)),
                "drying_p50": float(group["drying_time_h_predicted"].quantile(0.50)),
                "drying_p95": float(group["drying_time_h_predicted"].quantile(0.95)),
            }
        )
    return pd.DataFrame(rows)


def best_formula_counts(experiments: pd.DataFrame) -> pd.DataFrame:
    # For each scenario index, identify which formula had the lowest residual.
    rows = []
    if "scenario_id" not in experiments.columns:
        return pd.DataFrame(rows)
    work = experiments.copy()
    work["scenario_no"] = work["scenario_id"].astype(str).str.rsplit("-", n=1).str[-1]
    pivot = work.pivot_table(
        index="scenario_no", columns="formula", values="hcho_residual_fraction_predicted", aggfunc="first"
    )
    if pivot.empty:
        return pd.DataFrame(rows)
    lowest = pivot.idxmin(axis=1)
    counts = lowest.value_counts().to_dict()
    for fid in sorted(experiments["formula"].astype(str).unique()):
        rows.append({"formula": fid, "scenario_wins_lowest_residual": int(counts.get(fid, 0))})
    return pd.DataFrame(rows)


def target_reconciliation(properties: pd.DataFrame, experiments: pd.DataFrame) -> pd.DataFrame:
    # Historical document targets are engineering targets, not model outputs.
    water_by_formula = properties.set_index("formula")["water_load_g_m2_mean"].to_dict()
    drying_by_formula = properties.set_index("formula")["drying_time_h_mean"].to_dict()
    residual_by_formula = properties.set_index("formula")["hcho_residual_fraction_mean"].to_dict()
    wet_majority = max(water_by_formula, key=lambda k: water_by_formula[k])
    rows = [
        {
            "document_target": "Process/installation time <= 9 min",
            "document_value": "9 min",
            "computed_proxy": "predicted drying time, h (surrogate)",
            "computed_representative_range": ", ".join(f"{k}: {drying_by_formula[k]:.2f} h" for k in sorted(drying_by_formula)),
            "comparison_status": "NON-COMPARABLE",
            "reason": "Units, definition and time horizon differ; model drying surrogate is not an installation process time.",
        },
        {
            "document_target": "Total application amount <= 36 g/m2",
            "document_value": "36 g/m2",
            "computed_proxy": "predicted water load, g/m2",
            "computed_representative_range": ", ".join(f"{k}: {water_by_formula[k]:.2f} g/m2 water" for k in sorted(water_by_formula)),
            "comparison_status": "NON-COMPARABLE",
            "reason": "Water load is only part of total wet formulation mass; substrate, dose definition and application geometry differ.",
        },
        {
            "document_target": "Peak/residual swelling <= 0.060 mm",
            "document_value": "0.060 mm",
            "computed_proxy": "peak swelling risk index, dimensionless",
            "computed_representative_range": ", ".join(f"{k}: {experiments[experiments.formula == k].peak_swelling_risk_index.quantile(0.95):.4f} (p95)" for k in sorted(water_by_formula)),
            "comparison_status": "NON-COMPARABLE",
            "reason": "A dimensionless risk proxy cannot be converted to millimetres without calibrated experiments.",
        },
        {
            "document_target": "Formaldehyde reduction >= 70 over 90 days",
            "document_value": "70% over 90 days",
            "computed_proxy": "predicted residual HCHO fraction, instantaneous surrogate",
            "computed_representative_range": ", ".join(f"{k}: {residual_by_formula[k]:.3f} residual mean" for k in sorted(residual_by_formula)),
            "comparison_status": "NON-COMPARABLE",
            "reason": "Time horizon, test method and measured emission data are unavailable; surrogate residual fraction is not a 90-day reduction result.",
        },
    ]
    return pd.DataFrame(rows)


def generate_report(input_dir: Path, output_dir: Path, use_llm: bool = False, run_id: str | None = None) -> dict[str, Any]:
    artifacts = load_artifacts(input_dir)
    experiments = artifacts["experiments"]
    feas_path = input_dir / "feasible-candidates.csv"
    feasible_df = pd.read_csv(feas_path) if feas_path.is_file() else pd.DataFrame()
    properties = artifacts["properties"]
    sensitivity = artifacts["sensitivity"]
    pareto = artifacts["pareto"]
    manifest = artifacts["manifest"]
    assumptions = artifacts["assumptions"]

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "figures").mkdir(parents=True, exist_ok=True)

    # Copy existing plots if available.
    for plot in ["plots/hcho_residual_hist.png", "plots/pareto_scores.png"]:
        src = input_dir / plot
        if src.is_file():
            (output_dir / "figures" / Path(plot).name).write_bytes(src.read_bytes())

    property_agg = aggregate_from_experiments(experiments)
    wins = best_formula_counts(experiments)
    reconciliation = target_reconciliation(properties, experiments)

    water_by_formula = properties.set_index("formula")["water_load_g_m2_mean"].to_dict()
    drying_by_formula = properties.set_index("formula")["drying_time_h_mean"].to_dict()
    residual_by_formula = properties.set_index("formula")["hcho_residual_fraction_mean"].to_dict()

    # Render markdown tables.
    properties_table = properties[
        [
            "formula",
            "water_load_g_m2_mean",
            "water_load_g_m2_p05",
            "water_load_g_m2_p95",
            "hcho_residual_fraction_mean",
            "hcho_residual_fraction_p05",
            "hcho_residual_fraction_p95",
            "peak_swelling_risk_mean",
            "peak_swelling_risk_p95",
            "drying_time_h_mean",
            "drying_time_h_p95",
            "active_mass_consumption_g_m2_mean",
            "robustness_residual_cv",
        ]
    ].round(4).to_markdown(index=False)
    pareto_table = pareto.round(4).to_markdown(index=False)
    sensitivity_head = sensitivity.head(12).round(4).to_markdown(index=False)
    wins_table = wins.to_markdown(index=False) if not wins.empty else "No win-count data."
    if not feasible_df.empty:
        funnel_rows = []
        for field, values in [
            ("mass_balance_status", feasible_df.get("mass_balance_status")),
            ("functional_status", feasible_df.get("functional_status")),
            ("compatibility_status", feasible_df.get("compatibility_status")),
            ("model_support_status", feasible_df.get("model_support_status")),
            ("selection_status", feasible_df.get("selection_status")),
        ]:
            if values is None:
                continue
            for status, count in values.value_counts().sort_index().items():
                funnel_rows.append({"gate": field, "status": status, "count": int(count)})
        funnel_table = pd.DataFrame(funnel_rows).to_markdown(index=False)
    else:
        funnel_table = "No candidate screening data."
    candidates = artifacts.get("candidates", [])
    if candidates:
        candidate_lines = ["| Candidate (stable ID) | Display | Functional | Compatibility | Model | Residual surrogate | Water g/m2 |", "|---|---|---|---|---|---:|---:|"]
        for c in candidates:
            candidate_lines.append(
                "| {sid} | {cid} | {func} | {comp} | {model} | {res:.3f} | {water:.2f} |".format(
                    sid=c.get("stable_formula_id", c["candidate_id"]),
                    cid=c.get("display_label", c["candidate_id"]),
                    func=c.get("functional_status", "UNKNOWN"),
                    comp=c.get("compatibility_status", "UNKNOWN"),
                    model=c.get("model_support_status", "UNKNOWN"),
                    res=c["hcho_residual_fraction_mid"],
                    water=c["water_load_g_m2"],
                )
            )
        candidate_table = "\n".join(candidate_lines)
    else:
        candidate_table = "No new discovered candidates passed the feasibility screen in this run."
    property_agg_table = property_agg.round(4).to_markdown(index=False)

    llm_note = "Optional LLM interpretation is disabled in this offline run."
    if use_llm:
        llm_note = "LLM interpretation was requested, but this implementation keeps it disabled by default and has no paid-service path."

    report = f"""# BMF formulation research report

## 1. Provenance
- Model version: `{MODEL_VERSION}`
- Source commit: `{manifest.get('source_commit', 'unknown')}`
- Simulation run ID: `{run_id or manifest.get('run_id', 'local/unknown')}`
- Input artifact directory: `{input_dir}`
- Source artifact model manifest: `model_manifest.json`
- Random seed: `{manifest.get('seed', 'unknown')}`
- Scenario count per formula: `{manifest.get('n_scenarios_executed_per_formula', 'unknown')}`
- Formulas: {", ".join(manifest.get("formulas", []))}
- All values are virtual model predictions, not laboratory measurements.

## 2. Formulas and material balance
Material-balance rows are in `mass_balance.csv`; derived purchasable solution masses are in `assumptions.json`.

Mass fractions sum to 100 on the stated ready-to-use basis. Water includes water in purchased dispersions and PEI solutions.

## Candidate status funnel
{funnel_table}

## Discovered candidates
{candidate_table}

## 3. Methods, equations and assumptions
See `assumptions.json`. Main equations:
- PEI nitrogen mass = PEI active mass x `{assumptions.get('supplier_and_material_assumptions', {}).get('pei_nitrogen_mass_fraction', 0.3252)}`.
- Theoretical formaldehyde capacity uses nitrogen moles times an uncertain stoichiometry bound of 1-2 HCHO per nitrogen, adjusted by group availability and irreversibility.
- Drying and transport outputs are parametric surrogates with uncalibrated coefficients.
Data gaps are listed under missing inputs and in `limitations.md` from the simulation artifact.

## 4. Scope
This is a computational screen for prioritizing laboratory tests. It does not prove efficacy, safety, compatibility, stability or regulatory compliance.

## 5. Formula aggregates (p05/p50/p95)
{property_agg_table}

Detailed aggregate statistics:
{properties_table}

Scenario wins by lowest predicted residual HCHO:
{wins_table}

## 6. Sensitivity
Representative parameter perturbations (one factor at a time):
{sensitivity_head}

This is an OAT screen, not a global sensitivity or uncertainty decomposition.

## 7. Rank stability and Pareto
{pareto_table}

Pareto membership is computed from normalized characteristic scores and is a scenario ranking device. A, B and C may all remain non-dominated because they optimize different characteristics; this does not make any formula validated.

## 8. Scenario reversal analysis
Across virtual scenarios, each formula can be the best by lowest predicted residual HCHO. Reversals are driven by PEI availability, barrier factor, dose, water load, board density and evaporation assumptions. Where the lowest-residual scenario winner changes, ranking is not robust.

## 9. Limitations
- No measured HCHO emissions, swelling, drying times or toxicology are available.
- Theoretical capacities are upper bounds, not yields.
- Surrogate coefficients are uncalibrated.
- PEI/acrylic compatibility, pH, VOC and shelf life were not modelled.
- Ranking may change under different plausible parameter ranges.

## 10. Falsification plan
Before any design adoption: manufacture B and C, run carrier-only and untreated controls, measure peak and residual swelling on LDSP, emission time courses, VOC/odor, adhesion, pH stability and shelf life. Retain A as a higher-reactivity reserve.

## 11. Questions for BMF
- Can C (25% acrylic solids, 3% PEI) be manufactured without coagulation using a different binder?
- Can B be stored and applied at practical viscosity?
- What water-mass limit is consistent with the swelling acceptance criterion?
- Which application method gives repeatable dose per linear metre on site?
- Are pH and anionic acrylic compatibility acceptable for each candidate?

{llm_note}
"""
    (output_dir / RESEARCH_REPORT_NAME).write_text(report, encoding="utf-8")

    expert_brief = f"""# Expert feedback brief — BMF formulations

Purpose: engineering review, not experimental evidence.

Key model-supported screening observations:
- A, B and C all remain active candidates.
- Predicted mean water loads: {', '.join(f'{k} {water_by_formula[k]:.2f} g/m2' for k in sorted(water_by_formula))}.
- Predicted mean residual HCHO surrogates: {', '.join(f'{k} {residual_by_formula[k]:.3f}' for k in sorted(residual_by_formula))}.
- Predicted mean drying-time surrogates: {', '.join(f'{k} {drying_by_formula[k]:.2f} h' for k in sorted(drying_by_formula))}.

Questions for review:
- Is the water-load range acceptable for LDSP edge swelling?
- Which candidate should be manufactured first despite imperfect model scores?
- Are the proposed controls and test methods sufficient to discriminate A, B and C?
- What compatibility and stability data must be produced before B or C can be approved?

All values are virtual model predictions from `{MODEL_VERSION}`.
"""
    (output_dir / EXPERT_BRIEF_NAME).write_text(expert_brief, encoding="utf-8")

    reconciliation.to_csv(output_dir / TARGET_RECONCILIATION_NAME, index=False)

    manifest_files = [RESEARCH_REPORT_NAME, EXPERT_BRIEF_NAME, TARGET_RECONCILIATION_NAME]
    if (input_dir / "plots" / "hcho_residual_hist.png").is_file():
        manifest_files.append("figures/hcho_residual_hist.png")
    if (input_dir / "plots" / "pareto_scores.png").is_file():
        manifest_files.append("figures/pareto_scores.png")
    report_manifest = {
        "report_type": "BMF formulation research report",
        "report_version": "v0.2",
        "model_version": MODEL_VERSION,
        "source_simulation_manifest": manifest,
        "input_dir": str(input_dir),
        "run_id": run_id or manifest.get("run_id", "local/unknown"),
        "output_dir": str(output_dir),
        "artifacts": manifest_files,
        "sha256": {name: sha256_file(output_dir / name) for name in manifest_files},
        "generated_artifact_is_virtual": True,
    }
    (output_dir / REPORT_MANIFEST_NAME).write_text(
        json.dumps(report_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    sum_lines = []
    for path in sorted(output_dir.rglob("*")):
        if path.is_file() and path.name != "sha256sums.txt":
            rel = path.relative_to(output_dir).as_posix()
            sum_lines.append(f"{sha256_file(path)}  {rel}")
    (output_dir / "sha256sums.txt").write_text("\n".join(sum_lines) + "\n", encoding="utf-8")

    return {
        "output_dir": str(output_dir),
        "files": manifest_files + [REPORT_MANIFEST_NAME],
    }

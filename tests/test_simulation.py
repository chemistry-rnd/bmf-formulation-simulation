from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from simulation.bmf.experiments import run_virtual_experiments
from simulation.bmf.formulations import ALL_FORMULATIONS, FORMULATIONS
from simulation.bmf.mass_balance import mass_balance_all, mass_balance_for
from simulation.bmf.pipeline import run_pipeline
from simulation.bmf.transport import drying_time_h, hcho_residual_fraction, peak_swelling_risk_index


def test_mass_fractions_sum_to_100():
    rows, derived = mass_balance_all(ALL_FORMULATIONS)
    for fid in ALL_FORMULATIONS:
        assert abs(derived[fid]["mass_fraction_sum_pct"] - 100.0) < 1e-9


def test_component_mass_conservation():
    rows, derived = mass_balance_all(ALL_FORMULATIONS)
    mass_df = pd.DataFrame(rows)
    for fid in ALL_FORMULATIONS:
        subtotal = mass_df.loc[mass_df["formula"] == fid, "mass_g_per_m2"].sum()
        assert subtotal == pytest.approx(derived[fid]["wet_application_g_m2"], rel=1e-12)


def test_water_in_dispersions_is_accounted():
    _, derived = mass_balance_all(ALL_FORMULATIONS)
    for fid in ALL_FORMULATIONS:
        d = derived[fid]
        assert d["water_from_pei_solution_g_m2"] > 0 or d["pei_active_g_m2"] == 0
        assert d["total_water_g_m2"] == pytest.approx(
            d["water_from_pei_solution_g_m2"]
            + d["water_from_acrylic_dispersion_g_m2"]
            + d["free_water_g_m2"],
            rel=1e-12,
        )
        if d["acrylic_dry_g_m2"] > 0:
            assert d["acrylic_dispersion_purchased_g_m2"] > d["acrylic_dry_g_m2"]


def test_impossible_mixture_rejected():
    with pytest.raises(ValueError):
        mass_balance_for("A", -1.0)
    with pytest.raises(ValueError):
        mass_balance_for("Z", 10.0)


def test_zero_dose_boundary():
    rows, derived = mass_balance_for("A", 0.0)
    assert derived["wet_application_g_m2"] == 0.0
    assert derived["total_water_g_m2"] == 0.0
    assert hcho_residual_fraction(0.0, 10.0, 0.0, 1.0, 23.0) == 1.0
    assert drying_time_h(0.0, 1.0, 23.0, 0.5) >= 0
    assert peak_swelling_risk_index(0.0, 650.0, 16.0, 0.0) == 0.0


def test_reproducible_seed():
    a = run_virtual_experiments(["A", "B"], 20, 42, mode="mock")
    b = run_virtual_experiments(["A", "B"], 20, 42, mode="mock")
    assert a == b


def test_extreme_parameters_finite(tmp_path: Path):
    run_pipeline(tmp_path / "extreme", ["C"], n_scenarios=5, seed=999, mode="mock")
    exp = pd.read_csv(tmp_path / "extreme" / "virtual_experiments.csv")
    numeric = exp.select_dtypes(include=[np.number])
    assert np.isfinite(numeric.to_numpy()).all()


def test_missing_kinetics_not_invented(tmp_path: Path):
    run_pipeline(tmp_path / "kinetics", ["A"], n_scenarios=5, seed=1, mode="mock")
    assumptions = json.loads((tmp_path / "kinetics" / "assumptions.json").read_text())
    missing = " ".join(assumptions["missing_inputs_not_invented"]).lower()
    assert "kinetics" in missing
    assert "rate constants" in missing or "kinetic" in missing


def test_virtual_results_are_not_measured(tmp_path: Path):
    run_pipeline(tmp_path / "labels", ["A", "B"], n_scenarios=5, seed=7, mode="mock")
    exp = pd.read_csv(tmp_path / "labels" / "virtual_experiments.csv")
    assert (exp["result_status"].astype(str).str.startswith("virtual")).all()
    limitations = (tmp_path / "labels" / "limitations.md").read_text()
    assert "not experimental confirmation" in limitations
    assumptions = json.loads((tmp_path / "labels" / "assumptions.json").read_text())
    assert assumptions["result_type"].startswith("virtual")


def test_scenario_limits_enforced():
    with pytest.raises(ValueError):
        run_virtual_experiments(["A"], 0, 1, mode="mock")
    with pytest.raises(ValueError):
        run_virtual_experiments(["A"], 10001, 1, mode="mock")


def test_pipeline_artifacts_and_hashes(tmp_path: Path):
    result = run_pipeline(tmp_path / "full", ["A", "B", "C"], n_scenarios=20, seed=123, mode="mock")
    out = Path(result["output_dir"])
    expected = {
        "mass_balance.csv",
        "virtual_experiments.csv",
        "property_predictions.csv",
        "sensitivity.csv",
        "pareto.csv",
        "assumptions.json",
        "model_manifest.json",
        "limitations.md",
        "sha256sums.txt",
    }
    for name in expected:
        assert (out / name).is_file(), name
    assert (out / "plots" / "hcho_residual_hist.png").is_file()
    assert (out / "plots" / "pareto_scores.png").is_file()
    manifest = json.loads((out / "model_manifest.json").read_text())
    assert manifest["seed"] == 123
    assert set(manifest["formulas"]) == {"A", "B", "C"}
    assert manifest["generated_artifact_is_virtual"] is True


def test_dose_changes_hcho_residual_absolutely():
    from simulation.bmf.chemistry import theoretical_formaldehyde_capacity
    from simulation.bmf.transport import hcho_residual_fraction

    cap10 = theoretical_formaldehyde_capacity(10.0 * 0.2)["accessible_reversible_adjusted_capacity_g_m2"]
    cap20 = theoretical_formaldehyde_capacity(20.0 * 0.2)["accessible_reversible_adjusted_capacity_g_m2"]
    r10 = hcho_residual_fraction(cap10, 10.0, 0.5, 1.0, 23.0, available_hcho_g_m2=5.0)
    r20 = hcho_residual_fraction(cap20, 20.0, 0.5, 1.0, 23.0, available_hcho_g_m2=5.0)
    assert r10 != r20
    assert cap20 > cap10

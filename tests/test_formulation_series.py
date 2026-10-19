"""Six-recipe screening series A-F and collision-free discovery labels.

The program series (A Reactive, B Balanced, C Barrier, D Low Dose, E Conc Combo,
F Bal Conc) is fixed by the testing program of the formaldehyde-scavenger
project. D/E/F compositions come from that document and are evaluated here by
the same virtual screening as A/B/C.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from simulation.bmf.discovery import discovery_labels
from simulation.bmf.formulations import ALL_FORMULATIONS, FORMULATIONS
from simulation.bmf.pipeline import run_pipeline

# Compositions fixed by the testing program (Приложение 1), mass fractions in %.
PROGRAM_SERIES = {
    "D": {"pei_active": 0.17, "acrylic_dry_solids": 0.0, "nonionic_wetter": 0.1, "wet_application_g_m2": 11.35},
    "E": {"pei_active": 16.51, "acrylic_dry_solids": 28.51, "nonionic_wetter": 0.1, "wet_application_g_m2": 10.24},
    "F": {"pei_active": 13.04, "acrylic_dry_solids": 26.23, "nonionic_wetter": 0.1, "wet_application_g_m2": 10.01},
}


def test_all_formulations_cover_the_six_recipe_series():
    assert ALL_FORMULATIONS == ["A", "B", "C", "D", "E", "F"]


@pytest.mark.parametrize("fid", sorted(PROGRAM_SERIES))
def test_program_series_compositions_are_preserved(fid: str):
    formulation = FORMULATIONS[fid]
    expected = PROGRAM_SERIES[fid]
    assert formulation.wet_application_g_m2 == pytest.approx(expected["wet_application_g_m2"])
    for component, value in expected.items():
        if component == "wet_application_g_m2":
            continue
        assert formulation.mass_fractions[component] == pytest.approx(value)


@pytest.mark.parametrize("fid", sorted(PROGRAM_SERIES))
def test_program_series_mass_fractions_sum_to_100(fid: str):
    total = sum(FORMULATIONS[fid].mass_fractions.values())
    assert total == pytest.approx(100.0)


def test_discovery_labels_never_collide_with_formulation_ids():
    labels = discovery_labels(set(ALL_FORMULATIONS), 5)
    assert labels == ["G", "H", "I", "J", "K"]
    assert not set(labels) & set(ALL_FORMULATIONS)


def test_pipeline_evaluates_every_series_and_labels_candidates(tmp_path: Path):
    result = run_pipeline(tmp_path / "series", ALL_FORMULATIONS, n_scenarios=20, seed=7, mode="mock")
    out = Path(result["output_dir"])

    manifest = json.loads((out / "model_manifest.json").read_text())
    assert manifest["formulas"] == ALL_FORMULATIONS

    props = pd.read_csv(out / "property_predictions.csv")
    assert set(props["formula"]) == set(ALL_FORMULATIONS)

    mass = pd.read_csv(out / "mass_balance.csv")
    names = dict(zip(mass["formula"], mass["formula_name"]))
    for fid in ALL_FORMULATIONS:
        assert names[fid] == FORMULATIONS[fid].name

    candidates = json.loads((out / "discovered_candidates.json").read_text())
    for candidate in candidates:
        assert candidate["candidate_id"] not in ALL_FORMULATIONS


def test_low_dose_series_shows_no_calculated_effect(tmp_path: Path):
    """Series D carries 0.17% PEI: the calculated residual must stay near the untreated level."""
    result = run_pipeline(tmp_path / "d-series", ["D"], n_scenarios=50, seed=11, mode="mock")
    props = pd.read_csv(Path(result["output_dir"]) / "property_predictions.csv")
    residual = float(props.loc[props["formula"] == "D", "hcho_residual_fraction_mean"].iloc[0])
    assert residual > 0.5

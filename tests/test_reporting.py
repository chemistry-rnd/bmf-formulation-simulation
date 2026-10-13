from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pandas as pd
import pytest

from simulation.bmf.pipeline import run_pipeline
from simulation.bmf.reporting import generate_report


def test_report_generates_expected_artifacts(tmp_path: Path):
    inp = tmp_path / "inp"
    run_pipeline(inp, ["A", "B"], n_scenarios=15, seed=11, mode="mock")
    out = tmp_path / "rep"
    result = generate_report(inp, out, use_llm=False)
    expected = {
        "BMF-Research-Report.md",
        "expert-feedback-brief.md",
        "target-reconciliation.csv",
        "report-manifest.json",
    }
    assert expected.issubset({Path(p).name for p in result["files"]})
    for name in expected:
        assert (out / name).is_file()
    assert (out / "figures" / "hcho_residual_hist.png").is_file()
    assert (out / "figures" / "pareto_scores.png").is_file()


def test_report_matches_csv_values(tmp_path: Path):
    inp = tmp_path / "inp"
    run_pipeline(inp, ["A", "B", "C"], n_scenarios=20, seed=7, mode="mock")
    out = tmp_path / "rep"
    generate_report(inp, out, use_llm=False)
    report = (out / "BMF-Research-Report.md").read_text(encoding="utf-8")
    properties = pd.read_csv(inp / "property_predictions.csv")
    assert "virtual model predictions" in report
    assert "NON-COMPARABLE" in (out / "target-reconciliation.csv").read_text(encoding="utf-8")
    for fid in properties["formula"]:
        assert fid in report
    manifest = json.loads((out / "report-manifest.json").read_text(encoding="utf-8"))
    assert manifest["generated_artifact_is_virtual"] is True
    assert (out / "sha256sums.txt").is_file()
    subprocess.run(["sha256sum", "-c", "sha256sums.txt"], cwd=out, check=True)


def test_target_reconciliation_does_not_claim_mm_or_90_day(tmp_path: Path):
    inp = tmp_path / "inp"
    run_pipeline(inp, ["A"], n_scenarios=5, seed=1, mode="mock")
    out = tmp_path / "rep"
    generate_report(inp, out, use_llm=False)
    text = (out / "target-reconciliation.csv").read_text(encoding="utf-8")
    assert "NON-COMPARABLE" in text
    assert "0.060" in text
    assert "70" in text
    lowered = ((out / "BMF-Research-Report.md").read_text(encoding="utf-8") + "\n" + (out / "target-reconciliation.csv").read_text(encoding="utf-8")).lower()
    assert "90" in lowered

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

RESULT_FILES = [
    "mass_balance.csv",
    "formula-search.csv",
    "feasible-candidates.csv",
    "virtual_experiments.csv",
    "property_predictions.csv",
    "pareto.csv",
    "sensitivity.csv",
    "target-feasibility.csv",
]
INPUT_FILES = ["configs/bmf-default.json"]
VALIDATION_FILES = [
    "model_manifest.json",
    "assumptions.json",
    "model-assumptions.json",
    "limitations.md",
    "report-manifest.json",
    "sha256sums.txt",
]
FEEDBACK_FILES = ["expert-feedback-brief.md", "experiment-plan.md", "discovered_candidates.json"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stage_file(src: Path, dst: Path) -> None:
    if not src.is_file():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def package(input_dir: Path, output_dir: Path) -> int:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    (output_dir / "01-inputs" / "configs").mkdir(parents=True, exist_ok=True)
    (output_dir / "01-inputs" / "formulations").mkdir(parents=True, exist_ok=True)
    (output_dir / "02-results").mkdir(parents=True, exist_ok=True)
    (output_dir / "03-visualizations").mkdir(parents=True, exist_ok=True)
    (output_dir / "04-validation").mkdir(parents=True, exist_ok=True)
    (output_dir / "05-expert-feedback").mkdir(parents=True, exist_ok=True)

    for rel in INPUT_FILES:
        stage_file(Path(rel) if not Path(rel).is_absolute() else Path(rel), output_dir / "01-inputs" / "configs" / Path(rel).name)
    stage_file(input_dir / "discovered_candidates.json", output_dir / "01-inputs" / "formulations" / "discovered-candidates.json")
    for rel in RESULT_FILES:
        stage_file(input_dir / rel, output_dir / "02-results" / rel)
    for plot_name in ["plots/hcho_residual_hist.png", "plots/pareto_scores.png", "figures/hcho_residual_hist.png", "figures/pareto_scores.png"]:
        src = input_dir / plot_name
        if src.is_file():
            stage_file(src, output_dir / "03-visualizations" / Path(plot_name).name)
    for rel in VALIDATION_FILES:
        stage_file(input_dir / rel, output_dir / "04-validation" / rel)
    for rel in FEEDBACK_FILES:
        stage_file(input_dir / rel, output_dir / "05-expert-feedback" / rel)

    sum_lines = []
    for path in sorted(output_dir.rglob("*")):
        if path.is_file() and path.name != "sha256sums.txt":
            sum_lines.append(f"{sha256_file(path)}  {path.relative_to(output_dir).as_posix()}")
    (output_dir / "sha256sums.txt").write_text("\n".join(sum_lines) + "\n", encoding="utf-8")

    readme = """# BMF Research Data package

## Contents
- `01-inputs/` — configurations, formula definitions and assumptions.
- `02-results/` — mass balance, formula search, virtual experiments, predictions, Pareto, sensitivity and target feasibility.
- `03-visualizations/` — named model figures.
- `04-validation/` — manifest, limitations, model assumptions, checksums.
- `05-expert-feedback/` — concise expert brief, experiment plan and discovered candidate metadata.

## Reproduction
```bash
python scripts/run_simulation.py --config configs/bmf-default.json --output-dir simulation-output
python scripts/generate_research_report.py --input-dir simulation-output --output-dir simulation-output
python scripts/package_research_data.py --input-dir simulation-output --output-dir bmf-research-data
```

All numerical outputs are virtual model predictions. They are not laboratory measurements, safety approval or regulatory evidence.
"""
    (output_dir / "README.md").write_text(readme, encoding="utf-8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage BMF research data artifact directory")
    parser.add_argument("--input-dir", default="simulation-output")
    parser.add_argument("--output-dir", default="bmf-research-data")
    args = parser.parse_args()
    return package(Path(args.input_dir), Path(args.output_dir))


if __name__ == "__main__":
    raise SystemExit(main())

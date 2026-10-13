# BMF CPU Formulation Simulation

CPU-only research pipeline for theoretical screening of LDSP cut-edge treatment formulations.

## Run locally

```bash
python scripts/run_simulation.py --config configs/bmf-default.json --output-dir simulation-output
python scripts/generate_research_report.py --input-dir simulation-output --output-dir simulation-output
python scripts/package_research_data.py --input-dir simulation-output --output-dir bmf-research-data
```

## Outputs
- standalone `BMF-Research-Report.md`
- structured `BMF-Research-Data` archive
- deterministic CSV, plots, assumptions and SHA256 checks

All numerical results are virtual model predictions, not laboratory measurements.

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation.bmf.formulations import ALL_FORMULATIONS
from simulation.bmf.pipeline import run_pipeline


def parse_formulas(value: str) -> list[str]:
    if value.lower() == "all":
        return list(ALL_FORMULATIONS)
    if value.lower() == "a,b,c":
        return ["A", "B", "C"]
    return [item.strip().upper() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BMF CPU formulation simulation")
    parser.add_argument("--config", help="JSON configuration file for simulation inputs")
    parser.add_argument("--formulas", help="A, B, C, or all")
    parser.add_argument("--scenarios", type=int, help="Virtual scenarios per formula")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--mode", choices=["mock", "pilot", "full"], help="Execution mode")
    parser.add_argument("--formula-count", type=int, help="Number of distinct formulations to screen")
    parser.add_argument("--output-dir", help="Output directory")
    args = parser.parse_args()

    config = {}
    if args.config:
        with open(args.config, encoding="utf-8") as f:
            config = json.load(f)

    formulas = args.formulas if args.formulas is not None else config.get("formulas", "all")
    scenarios = args.scenarios if args.scenarios is not None else config.get("scenarios", 1000)
    seed = args.seed if args.seed is not None else config.get("seed", 20261013)
    mode = args.mode if args.mode is not None else config.get("mode", "pilot")
    output_dir = args.output_dir if args.output_dir is not None else config.get("output_dir", "simulation-output")

    if scenarios < 1 or scenarios > 10000:
        raise SystemExit("--scenarios must be between 1 and 10000")
    default_formula_count = {"mock": 50, "pilot": 1000, "full": 10000}.get(mode, 1000)
    formula_count = args.formula_count if args.formula_count is not None else config.get("formula_count", default_formula_count)
    if formula_count < 1 or formula_count > 50000:
        raise SystemExit("--formula-count must be between 1 and 50000")

    result = run_pipeline(
        output_dir=Path(output_dir),
        formula_ids=parse_formulas(formulas),
        n_scenarios=scenarios,
        formula_count=formula_count,
        seed=seed,
        mode=mode,
    )
    print(f"WROTE {result['output_dir']}")
    print(f"FORMULAS {','.join(result['formulas'])}")
    print(f"SCENARIOS {result['n_scenarios']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

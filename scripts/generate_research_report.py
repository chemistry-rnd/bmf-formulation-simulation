from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation.bmf.reporting import generate_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate BMF research report from simulation artifacts")
    parser.add_argument("--input-dir", default="simulation-output")
    parser.add_argument("--output-dir", default="simulation-report")
    args = parser.parse_args()
    result = generate_report(Path(args.input_dir), Path(args.output_dir), use_llm=False)
    print(f"WROTE {result['output_dir']}")
    for name in result["files"]:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

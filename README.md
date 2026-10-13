# R&D Forge

Workspace and playbook for turning incomplete project inputs into a coherent, expert-facing Technology Description.

## Repository model

```text
rules/                         global requirements for every project
playbook/                      generation/research workflow
projects/
  <project>/
    input/                     everything supplied by the client/project owner
    requirements.md            current project-specific requirements
    requirements-log.md        append-only requirement/decision history
    output/research/           LLM-produced intermediate research and evidence
      competitors.md
      patents.md
      standards.md
      sources.md
    output/
      current.md               latest accepted/review version
      versions/                immutable snapshots
      review-notes.md          issues that should not leak into main document
```

## Core rule

The main Technology Description is written as a complete technology for expert review. Internal uncertainty and work planning belong in research/review files, not in the main document.

Generation can be started through the **Generate Technology Description** GitHub Actions workflow, which runs the standard OpenCode agent over the same playbook and rules. The manual workflow remains authoritative when the action is unavailable or when artifacts must be reviewed before publication.

Start with `playbook/technology-description.md`.

## BMF formulation simulation

Run locally:
```bash
python scripts/run_simulation.py --config configs/bmf-default.json --output-dir simulation-output
python scripts/generate_research_report.py --input-dir simulation-output --output-dir simulation-output
```

Manual second-seed convergence comparison:
```bash
python scripts/run_simulation.py --formulas all --scenarios 10000 --seed 20261013 --mode full --output-dir run-seed-a
python scripts/run_simulation.py --formulas all --scenarios 10000 --seed 20261107 --mode full --output-dir run-seed-b
```
Compare aggregate medians and quantiles, Pareto membership and sensitivity; larger N improves sampling precision only, not model validity.

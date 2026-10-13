# BMF v0.5 — Open Formula Discovery implementation handoff

Full contract: [issue #16](https://github.com/kobzevvv/rnd-forge/issues/16).

## First fix
Current `simulation/bmf/discovery.py` searches only PEI/acrylic/dose using LHS and chooses candidates if they improve any single normalized objective. Replace this with scientifically constrained, diversified Pareto selection.

## Build in order
1. Unit tests for false winners, mass-balance, supplier water, compatibility status and Pareto.
2. Separate number of formulations from number of environment scenarios. CPU bounded 1k pilot, 10k full, optional 50k benchmark; report actual counts.
3. Component registry with CAS, provenance, hazard and evidence completeness. Curated offline seed entries only initially.
4. Open family discovery with explicit unsupported/unknown status, no invented HCHO model for unfamiliar chemistry.
5. Adaptive search and uncertainty analysis; source-grounded final candidates and laboratory measurement priorities.
6. Two artifact report packaging, deterministic CI, GHA runs and performance measurements.

## Non-goals
No GPU, no automated chemical safety approval, no fabricated patents or experiments, no changes to accepted expert document, no paid external LLM calls by default. Keep PR draft until review.

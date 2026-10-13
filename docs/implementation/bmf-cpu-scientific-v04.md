# BMF CPU Scientific Model v0.4 — implementation handoff

Implement [issue #12](https://github.com/kobzevvv/rnd-forge/issues/12). This is an engineering task, not a claim of completed scientific simulation.

## Gates
P0: audit existing chemical assumptions and model validity; especially PEI nitrogen fraction 0.232558 vs theoretical ~0.325 for ideal C2H5N repeat.
P1: chemistry reaction/capacity and 1D moisture with conservation and convergence.
P2: HCHO reaction-diffusion and coating/barrier boundary conditions, clearly parameterized.
P3: separate physical uncertainties, use paired external conditions, sensitivity, rank reversal.
P4: constrained formula search and robust Pareto only after prior gates.
P5: deterministic standalone MD report and structured data archive, provenance and lab tests.
P6: CI and CPU-only GHA pilot, benchmark actual elapsed time.

## Hard constraints
No GPU, no paid APIs, no invented chemical kinetics, no extrapolation to measured 90-day HCHO, no converting swelling risk index into millimetres without calibration, no unsupported process-ready time prediction. Keep the current expert technology description unchanged. Two GHA artifacts and artifact-first delivery remain mandatory. Open PR draft early and do not merge.

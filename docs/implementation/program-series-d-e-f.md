# Program series D/E/F — screening of the six-recipe series

## Context

The testing program of the formaldehyde-scavenger project fixes a six-recipe series
plus a control: **A Reactive, B Balanced, C Barrier** (screening formulations) and
**D Low Dose, E Conc Combo, F Bal Conc** (research candidates, program Приложение 1).

Until now the model evaluated only A/B/C, so the program series D/E/F had no virtual
screening results of their own, and the run artifacts of the program and the model
were not comparable recipe by recipe.

## Change

- `simulation/bmf/formulations.py`: D/E/F added as full screening formulations with the
  compositions and doses fixed by the program (PEI 0.17/16.51/13.04%, acrylic
  0/28.51/26.23%, doses 11.35/10.24/10.01 g/m²). `ALL_FORMULATIONS` is now A–F.
- `simulation/bmf/discovery.py`: `discovery_labels()` allocates discovery labels from the
  first free letter, so discovered candidates can never collide with a formulation id.
  Before this change the labels were hard-coded as D…H and would have collided with the
  new formulations in `mass_balance.csv` and `property_predictions.csv`.
- `scripts/run_simulation.py`: `--formulas all` follows `ALL_FORMULATIONS`; the explicit
  `a,b,c` alias keeps its meaning.
- `simulation/bmf/pipeline.py`: the experiment plan names the evaluated series.

## Why the series compositions are not re-derived here

D/E/F are fixed by the program document, not by the search. The discovery stage
(`bmf-cpu-v0.5.0`) produces its own candidate letters; those are research outputs, not
the program series, and are reported separately.

The v0.5.1 audit already showed that a low-active candidate selected by an earlier run
was a false selection. Series D is evaluated here as the **negative control** the program
defines it to be, not as a promising candidate.

## Result of the pilot run

`pilot`, seed 20261013, 1000 scenarios per recipe, model `bmf-cpu-v0.4.0`
(experiments) / `bmf-cpu-v0.5.0` (discovery):

| Series | Water load, g/m² | Residual HCHO surrogate, mean | p05 | p95 | Model drying time, min | Swelling risk index p95 | Cost index | CV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 16.00 | 0.544 | 0.296 | 0.818 | 55.6 | 0.00167 | 4.90 | 0.290 |
| B | 19.97 | 0.615 | 0.380 | 0.866 | 69.3 | 0.00213 | 6.12 | 0.243 |
| C | 14.38 | 0.675 | 0.438 | 0.923 | 49.7 | 0.00151 | 6.46 | 0.224 |
| D | 11.32 | 0.701 | 0.436 | 0.964 | 39.2 | 0.00120 | 0.59 | 0.229 |
| E | 5.62 | 0.629 | 0.381 | 0.885 | 19.5 | 0.00060 | 5.00 | 0.246 |
| F | 6.07 | 0.642 | 0.407 | 0.893 | 21.1 | 0.00065 | 4.33 | 0.237 |

All values are virtual model predictions, not laboratory measurements.

Cross-checks against the technology description v018 (run 38430591444, model v0.3.0):
water load, model drying time and swelling risk index are unchanged; the residual HCHO
surrogate changed for A/B/C because of the v0.5.2 correction of the absolute PEI dose
dependence. The ranking A < B < C is preserved.

Reading against the three numerical targets: no series reaches the 70% reduction target
on the mean surrogate (best: A, 45.6%), the model drying time exceeds the 9-minute
readiness target by a factor of 4–8, and the swelling index has no validated conversion
to millimetres. Series D behaves as the negative control the program intends.

## Tests

`tests/test_formulation_series.py`: composition preservation against the program,
mass balance, label collision, pipeline coverage of all six series, negative-control
behaviour of D. Full suite: 39 passed.

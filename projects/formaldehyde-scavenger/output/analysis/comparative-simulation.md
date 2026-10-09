# Comparative Simulation — edge treatment application

Version 001 · scenario engineering model

## Purpose

Calculate falsifiable numerical scenarios for applying treatment to a 16-mm particleboard cut. **Scenario coefficients describe hypothetical application methods, not measured properties of named competitor products.** A numeric scenario cannot count as a verified competitor measurement.

## Geometry and equations

- Edge length L = 1 m; board thickness h = 0.016 m; exposed area A = L×h = 0.016 m².
- Target wet loading q = 36 g/m²; useful deposited mass m = q×A = **0.576 g**.
- Transfer efficiency η = useful mass / dispensed mass.
- Dispensed mass M = m/η; loss = M−m; cost = M×price per gram.
- Complete cycle time = setup + application + cleanup + process-ready waiting time. Define whether waiting overlaps with other work before comparing.

## Three application scenarios

These are generic process scenarios, **not** claims about Speco, BASF or Asta.

| Parameter | Contact applicator | Spray, central | Spray, favorable |
|---|---:|---:|---:|
| Useful mass on edge | 0.576 g | 0.576 g | 0.576 g |
| Transfer efficiency η | 0.90 | 0.45 | 0.75 |
| Dispensed mass | 0.640 g | 1.280 g | 0.768 g |
| Loss mass | 0.064 g | 0.704 g | 0.192 g |
| Loss fraction | 10% | 55% | 25% |
| Ratio spray/contact dispensed mass | 1.00 | 2.00 | 1.20 |

## Sensitivity

At fixed required deposited mass, dispensed mass is inversely proportional to η. If contact efficiency drops to 0.65 and spray efficiency reaches 0.75, the spray becomes more economical by mass. Thus a real experiment can disprove the claimed advantage.

## Seven quantitative comparisons to investigate

1. Transfer efficiency (%).
2. Dispensed wet mass (g/m).
3. Material lost (g/m).
4. Loss fraction (%).
5. Cost per metre at equal price (currency/m).
6. Cleanup mass (g/m).
7. Total cycle time (s/m).

Metrics 1–4 are mathematically dependent on the same transfer-efficiency assumption; they are **not seven independent evidence points**. Cost and cleanup require separate assumptions or measurements. Total cycle time requires operator study.

## Validation protocol

- Use the same 16-mm particleboard batch, cut geometry, coverage endpoint and ambient conditions.
- Compare at least two application methods; weigh reservoir/applicator before and after, treated sample and protective catch surfaces.
- Measure deposition uniformity, cleanup time and damage to adjacent lamination.
- Repeat across operators and report confidence intervals.
- Test whether differences survive a fair adjustment for formulation viscosity and target coverage.

## Compliance interpretation

The model yields numeric **process-scenario** cells. It does not yet establish 7/15 product-specific competitor cells. For a valid product comparison, collect manufacturer data or test actual products using the same protocol. The scenario matrix may be shown as an engineering appendix, explicitly labelled as modelled.

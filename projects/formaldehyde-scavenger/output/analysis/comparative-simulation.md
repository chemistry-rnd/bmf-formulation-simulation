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


## Market reference benchmarks — iteration 002

Use market-reference data to replace empty cells **only when the comparator is explicitly a market class**, not a specific product whose value is unknown.

### Published paint benchmarks

- Tikkurila Optiva Colour (interior waterborne acrylic paint): 8.4–12 m²/L per coat; non-stick ~1 h; repaintable ~4 h. Manufacturer: https://tikkurila.com/for-everyone/products/optiva-colour
- Tikkurila Everal Aqua Matt (waterborne enamel intended also for wood/chipboard): 9.8–14 m²/L; non-stick ~1 h; repaintable ~4 h. Manufacturer: https://production-tk-tikkurila.cms.tikkurila.com/products/everal-aqua-matt
- Silkcoat Acrylic (exterior paint, less comparable use case): 100–170 g/m²; touch-dry 15–20 min. Manufacturer: https://silkcoat.com/en/products/exterior-paints/acrylic/

**Unit conversion:** 8.4–12 m²/L = 83.3–119.0 mL/m². On a 16-mm edge of length 1 m (0.016 m²), this corresponds to 1.33–1.90 mL of paint, **assuming the flat-surface coverage rate transfers to an exposed edge**. That assumption is unvalidated; this is not the published edge application rate. For our design, 36 g/m² = 0.576 g/m edge. A mass comparison requires paint density and identical functional coverage criteria.

### Formaldehyde reference — not a market mean

EU REACH regulation 2023/1464 specifies 0.062 mg/m³ for furniture and wood-based articles under prescribed emission test conditions. This is a regulatory concentration limit, **not an average measured competitor emission and not equivalent to an edge-specific flux in µg/(m²·h)**. Source: https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=celex%3A32023R1464

Do not compare a proposed 70% reduction against the 0.062 mg/m³ concentration without a matched control and consistent chamber protocol.

### Comparison taxonomy

1. Product value: documented exact competitor TDS number.
2. Market benchmark: a clearly named representative product/class, with conditions.
3. Derived scenario: mathematical conversion with assumptions and uncertainty.

Never relabel (2) or (3) as a measured property of another named competitor. For quantitative coverage, only count cells where the compared quantity, units, substrate and test endpoint are sufficiently aligned.


## Iteration 003 — two complementary numerical strategies

**Strategy A: representative published market products.** Tikkurila Everal Aqua Matt (waterborne furniture/chipboard enamel): 9.8–14 m²/L, dust-dry 60 min, recoat 240 min, base density 1.04–1.30 kg/L. Optiva Colour (interior wall paint, less direct): 8.4–12 m²/L, dry ~60 min, recoat 240 min. BASF Loxanol MI 6311 ingredient: ~75% active content, density ~1.31 g/cm³, pH ~10. These are product-specific numbers, but they describe different endpoints; never silently transfer them to Speco or Asta.

**Strategy B: common-geometry model.** For L=1 m, h=0.016 m, area=0.016 m². Our wet applied mass=36×0.016=0.576 g. Everal Aqua Matt's published flat-surface coverage translates to 0.0714–0.1020 L/m²; at 1.04–1.30 kg/L, the implied mass range is ~74.3–132.7 g/m², or ~1.19–2.12 g/m of 16-mm edge **if flat-surface coverage transfers**. Optiva Colour corresponds to ~1.33–1.90 mL/m edge, but mass is not computable without verified density. For Everal, our mass is ~2.1–3.7× lower than that modeled flat-surface paint loading. This is a **scenario comparison**, not evidence of equivalent HCHO suppression or edge coverage.

Published references:
- https://tikkurila.com/pro/products/everal-aqua-matt
- https://tikkurila.com/pro/products/optiva-colour
- https://download.basf.com/p1/8a8081e18721a79301872315dfa20b42/en/Loxanol_MI_6311_TDS_30756558_EN_Technical_Data_Sheet_English.pdf?view=

**Coverage audit:** two independent published quantitative Everal metrics (coverage, drying) and one derived edge mass metric can be compared to our engineering targets under explicit caveats. The derived mass shares the same coverage input, so it is not independent evidence. These do not establish 51% coverage for the original three named competitors. Maintain separate scoring for (1) original named products and (2) representative market-reference products. Do not inflate the denominator with qualitative entries or reclassify a paint as an HCHO scavenger.

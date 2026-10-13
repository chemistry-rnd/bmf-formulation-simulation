# BMF simulation v0.2 model audit

Scope: CPU screen for candidate formulations A/B/C. Not experimental evidence.

## Verified from artifacts
- Pilot run 38424655095 hashes should be rechecked before reuse.
- Aggregate residual HCHO: A about 0.664, B about 0.684, C about 0.692.
- Water loads: A 16.00 g/m2, B 19.97 g/m2, C 14.38 g/m2.
- Predicted drying times: A about 0.89 h, B about 1.11 h, C about 0.80 h.
- Mass fractions sum to 100% and water includes purchased solution/dispersion water.

## Fixed in v0.2
- Independent Latin Hypercube samples are now generated per formula, not derived from one shared base sample.
- Report rendering moved to CSV-driven deterministic generator.
- Swelling index is reported only as a dimensionless risk proxy.

## High-risk limitations and blocked claims
- Formaldehyde capacities are theoretical nitrogen-based upper bounds, adjusted by uncertain group availability and irreversibility. They are not reaction yields.
- Drying, evaporation, swelling and residual HCHO models are parametric surrogates with uncalibrated coefficients. The evaporation time constant is not a validated transport coefficient.
- The swelling index is not and must not be converted to millimetres of swelling.
- No 90-day HCHO percentage can be inferred from the current surrogate.
- Compatibility, pH, VOC, odor, toxicology, shelf stability and coagulation risk for B/C are not modelled.
- Sensitivity output is one-factor perturbation, not a global sensitivity or uncertainty decomposition.
- No formula is safe or production-ready.

## Target reconciliation
Prior document targets remain historical engineering targets: 9 min process time, 36 g/m2, <=0.060 mm swelling, >=70% 90-day HCHO reduction. These are marked NON-COMPARABLE against current proxies when units, time horizons, substrates or metrics differ.

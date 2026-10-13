# BMF — Three candidate formulations and document-generation input

Date: 2026-10-13. Research design input for issue #3; **not laboratory results**.

## Three distinct uses

All percentages below refer to finished ready-to-use formulation and sum to 100% **on a specified active/dry basis**. Water includes the water in any purchased polymer dispersions and PEI solutions. Commercial grade selection and colloidal compatibility are prerequisites; these are theoretical target balances, not mixing instructions.

| Formula | Intended optimization | PEI active | Urea | Acrylic dry solids | Nonionic wetter | Other nonvolatile functional binder | Total water/carrier | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A Reactive | formaldehyde binding, no polymer film | 20% | 0% | 0% | 0% | 0% | 80% | 100% |
| B Balanced | reactive + barrier, one-step installation | 8% | 0% | 12% | 0.1% | 0% | 79.9% | 100% |
| C Barrier | high solids, lowest water among candidates | 3% | 0% | 25% | 0.1% | 0% | 71.9% | 100% |

**Caution:** Formula C may be impractical with standard waterborne acrylic dispersions; 25% dry polymer solids and 3% PEI may coagulate or require a different binder. Formula B has the same compatibility risk. The listed 71.9–80% water is not necessarily low enough to prevent swelling. The three candidates are screening hypotheses, not safe or validated production formulations. Actual water and mass balance must be recomputed from exact commercial grades. Non-water co-solvents, if introduced, require a new mass balance and VOC/safety assessment.

## Nominal application scenarios — design numbers only

| Formula | Wet application g/m² | PEI active g/m² | Acrylic solids g/m² | Water/carrier g/m² |
|---|---:|---:|---:|---:|
| A | 20 | 4.00 | 0 | 16.00 |
| B | 25 | 2.00 | 3.00 | 19.975 |
| C | 20 | 0.60 | 5.00 | 14.38 |

The lower active dose in C can fail formaldehyde-binding targets; barrier-only action must be measured. These numbers are NOT proven efficacy or swelling results.

## Mandatory generator instructions

1. Keep three candidate formulas with separate intended uses in the expert-facing Technology Description, preferably a single comparison table with named ingredients, mass balance, application dose, water load and process assumptions. Do not present them as experimentally optimized, approved or tested.
2. Retain existing document numerical design targets for expert feedback, but distinguish engineering specification from empirical outcomes internally. Do not silently modify competitive data.
3. Main application is fresh open LDSP cuts. MDF remains a separate applicability question. Alternative controlled application methods are permitted.
4. Explicitly address peak and residual swelling, dose control, water in acrylic dispersion, pH, compatibility of PEI with anionic acrylic emulsions, coating adhesion, VOC and storage stability.
5. Preserve full original patent/research trail and prior versions; update requirements-log append-only and generate a new immutable final-result version only after running full QA.
6. Re-run the existing playbook from Pass 0 through research, patent evidence, falsifiability, AI research spec, market comparison, compliance checks and final-result. If no executable workflow exists, record the missing automation rather than claiming a GitHub Actions run.
7. Do not confuse the separate document-numbers track with formulation optimization: numerical design targets support expert feedback, not scientific proof.

## Validation priorities

First verify manufacturability and shelf stability of B/C; next screen water uptake and peak/residual swelling on LDSP with untreated, carrier-only and binder-free controls; then emission time course and odor/VOC. A may prove preferable to B if binder hurts reactivity or stability.

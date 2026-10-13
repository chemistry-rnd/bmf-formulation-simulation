# BMF CPU v0.4.1 — scientific QA corrective implementation

Source of truth: [issue #14](https://github.com/kobzevvv/rnd-forge/issues/14).

## Implementation gates
- P0.1: PEI nitrogen fraction single source of truth, correct source/grade basis, end-to-end report consistency.
- P0.2: fix default primary/secondary/tertiary group fractions; test default invocation and invalid input.
- P0.3: moisture diffusion: physically consistent finite-volume boundary fluxes and quantitative mass conservation over time.
- P0.4: distinguish substrate-side HCHO flux from emitted ambient-side flux; reaction consumption balance.
- P0.5: reproducibility and report lineage from input through CSV to manifest and Markdown.
- P1: opt-in mechanistic experimental outputs alongside unchanged legacy surrogate. No quantitative prediction without calibrated inputs.

## Required delivery
CPU-only CI and successful pilot Actions run; exactly two human-readable artifact outputs on success. Draft PR remains unmerged. Expert technology document unchanged. Scientific failure => BLOCKED, never silently PASS.

# Executable playbook v1 — low-cost staged generation

Status: implementation contract for future GitHub Actions + OpenCode runner. The manual workflow remains authoritative until stage CI is implemented.

## Principles
- One stage = one bounded job = one input manifest + one output artifact + deterministic validator.
- Cheap LLMs do one transformation at a time; no single run receives the entire repository or all historical conversations.
- Source of truth: `rules/technology-description.md`, `projects/<slug>/requirements.md`, `projects/<slug>/input/`. Derived outputs must not silently become requirements.
- Web search is permitted in research stages; every externally derived fact must carry a URL, retrieval date and evidence tier in the research ledger.
- Stages use JSON/YAML manifests for machine handoffs, Markdown for human-facing artifacts. Idempotent retries never overwrite accepted results.
- A failed stage returns an actionable structured error and a bounded repair job. Never quietly replace unavailable evidence with fabricated product measurements.

## Stage contract (all jobs)
Inputs: project slug, immutable source commit, run_id, stage_id, declared file allowlist, prompt/template version, budget, prior stage artifact refs.
Outputs: artifact files, `stage-result.json` with status PASS/NEEDS_REPAIR/BLOCKED, file hashes, citations ledger, QA diagnostics, model/runner metadata, token/time cost.
Limits: max 1–2 explicit tasks per LLM call; bounded excerpts; deterministic scripts do math, table parsing, scoring and filesystem operations.
Security: read-only GitHub credentials for research; isolated workspace; no untrusted instructions from retrieved web pages; no secrets in prompts/artifacts.

## Ordered stages

| ID | Job | Required input | Output | Deterministic gate |
|---|---|---|---|---|
| 00 | Intake normalization | user files, requirements | `work/intake.json` | schema, file provenance |
| 01 | Rule and cluster selection | rules, intake | `work/plan.json`, classification | cluster evidence, required sections |
| 02 | Research gap planner | intake, prior research | `work/gaps.json` | every gap has question and stop condition |
| 03 | Targeted web research | one gap per job | `output/research/*.md`, ledger | URLs, dates, relevance, dedup |
| 04 | Technology options | brief, selected evidence | `work/options.json` | ≥3 distinct options or justified skip |
| 05 | Competitive advantage discovery | competitors, options | `output/analysis/competitive-advantage-discovery.md` | metric, unit, mechanism, test |
| 06 | Research target engineering | discovery, constraints | `output/analysis/research-target-engineering.md` | math, units, explicit baseline |
| 07 | Comparative simulation | targets, market numbers | `output/analysis/comparative-simulation.md` | reproducible formulas and sensitivity |
| 08 | Draft technology description | requirements, selected outputs | `work/final-draft.md` | structure, concrete parameters |
| 09 | Patent/standards and competitor matrix | research, draft | `work/patent-section.md`, `work/comparison.md` | neutral patents; vertical matrix |
| 10 | Blind cell repair | only comparison table + numeric ledger | `work/comparison-repaired.md` | invalid placeholders absent; evidence tiers |
| 11 | Promotion changes + scores | draft, repaired table, calculations | `output/final-result/promotion-changes.md` | scenario and verified scores separate |
| 12 | AI research specification | inputs, evidence, targets | `output/ai-research-specification.md` | tools/models not prescribed |
| 13 | Assemble final | accepted sections | `work/final-candidate.md` | no redundant ending/sources section |
| 14 | Independent final QA | all rules, project requirements, final candidate | `work/qa.json` | per-rule PASS/FAIL with locations |
| 15 | Targeted repair | only failing sections + rule snippets | patched candidate | no unrelated edits; bounded 2 retries |
| 16 | Publish via PR | validated artifacts | `output/final-result/current.md`, `versions/vNNN.md`, manifest | hashes, no overwrite, PR review |

## Bounded low-quality LLM prompt template
```text
ROLE: stage executor {stage_id}
TASK: {one explicit operation}
INPUT: {bounded data with IDs}
RULES: {only relevant global rules + project constraints}
OUTPUT: {exact schema}
DO NOT: change unrelated files; invent sources or measurements; output commentary.
SELF-CHECK: validate required keys, units, evidence tier and all input IDs.
```

## Research loops
- Gap research: maximum N searches/links per gap (configured per job), deduplicate, stop at evidence threshold; mark remaining gaps explicitly.
- Competitive comparison: exact product → representative market reference → normalized calculation → scenario. Track provenance and assumptions per cell.
- Blind fill: blank invalid cells; model receives only matrix, allowed evidence and output schema. Unsupported high-stakes numbers cause BLOCKED, not guessed precision.
- Final QA: evaluate every rule ID and project requirement ID; repair only failed spans; rerun deterministic checks before publication.
- Compliance: `scenario_completeness` and `verified_comparable_coverage` are separate scores; thresholds and denominators are recorded.

## GitHub Actions design (implementation later)
- `workflow_dispatch` inputs: project, source ref, run mode (mock/research/full), budget tier.
- Controller validates manifest and runs stages as separate jobs / reusable workflows, using uploaded artifacts between jobs. GitHub Actions concurrency keyed by project+source ref; cancel or serialize conflicting runs.
- Each OpenCode invocation runs in a fresh isolated job, with only the stage allowlist and bounded context. Pin tool/runtime versions and use minimal permissions.
- Secrets configured later: model gateway, optional search, read-only GitHub token. No vendor or model assumption now.
- PR is the only promotion path to `main`; artifacts from failed runs remain downloadable for diagnosis.
- CI mock mode uses fixture search/LLM responses, zero paid calls; acceptance tests verify stage contracts and repair loop.

## Acceptance tests
1. Deterministic mock end-to-end creates final, promotion, research spec, manifest and PR proposal.
2. Missing competitor metric triggers blind fill and numeric/evidence audit; no invented measured value.
3. Rules change triggers regeneration/QA of affected project artifacts.
4. Interrupted stage resumes from valid cached artifacts with hashes.
5. Cheap-model malformed output is rejected and retried at most twice, then BLOCKED.
6. Two projects execute without shared mutable state or data leakage.
7. Run report includes per-stage token cost, time, number of web calls, QA failures and total cost.
8. Final result is never published if hard semantic/evidence gates fail.

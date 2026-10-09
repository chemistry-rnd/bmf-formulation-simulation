# Executable playbook v1 — low-cost staged generation

## Run modes — create and revise

There is **one pipeline with two entry modes**, not two independent playbooks.

| Mode | Input | Entry stages | Execution scope | Output |
|---|---|---|---|---|
| `create` | Project brief, input files, active requirements | 00 intake → normal DAG | All required stages | New run artifact package |
| `revise` | Existing result package or run reference, reviewed document and/or explicit change request | Review diff → requirements reconciliation → dependency restart planner | Only affected stages and descendants | Updated run artifact package + change report |

Both modes use the same global/project rules, validation gates and artifact schema. A revise run must resolve its exact base version/hash, retain previously accepted requirements, and never silently supersede them. Reviewer diffs are proposals until reconciled; explicit user instruction is required to reverse an active decision.

`revise` reuses unaffected research and calculations from the referenced run where artifacts are available and hashes match. If the prior Actions artifact has expired, request or retrieve an explicitly persisted baseline; do not guess it. Both modes publish generated outputs as Actions artifacts, not source commits. Accepted requirements/history remain in Git.


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


## Output delivery decision — Actions artifact first

Normal generation produces **no repository write, branch, commit or PR**. All generated research, analyses, Final Result, Promotion Changes, AI Research Specification, QA reports and manifests are stored in run-scoped GitHub Actions artifacts. Stage jobs pass artifacts by unique run/stage identifiers and verify hashes. The final packaging stage publishes one downloadable artifact only after all mandatory QA gates pass; failed runs publish diagnostics separately.

Repository state consists of inputs, rules, playbooks and accepted requirements only. Legacy checked-in outputs are historical fixtures and are not the default persistence mechanism.

GitHub Actions artifact retention is finite, not durable. Set explicit retention and expose expiry. An accepted result can be saved long-term only through a separate explicit promotion flow (Release, object storage, or user-chosen destination), never automatically on each run.

Replace stage 16 PR publication with artifact packaging and upload. Remove PR creation from default acceptance tests; instead assert no source-branch mutations and verify artifact manifest and checksum integrity.


## Mandatory QA gates by stage (cheap-model resilient)

Each gate emits a machine-readable `check_id`, PASS/FAIL, location, evidence, suggested repair and severity. Deterministic checks run first. LLM semantic review is only for judgments that code cannot make. Failed sections are repaired in isolation and rechecked. Never count a rewritten placeholder as a successful numerical cell.

| Gate | Stage | Type | Requirement | Failure action |
|---|---|---|---|---|
| Q01 | 01 | Deterministic | Explicit Skolkovo cluster + direction/code at top; official source in research ledger | Research/rewrite classification |
| Q02 | 03/09 | Deterministic + source check | At least 1 verified Russian and preferably 3 verified international patent records; IDs, URLs, descriptions; neutral wording | Targeted patent search |
| Q03 | 09/13 | Deterministic | Comparison is vertical: rows are parameters, columns are named products/technology; numeric units per metric | Transpose/regenerate table |
| Q04 | 09/11 | Deterministic | At least 51% numeric scenario cells filled per competitor and overall; count denominators, reject nonnumeric placeholders | Research/model missing cells |
| Q05 | 09/11 | Deterministic + evidence | Separate verified competitor numeric coverage from modelled scenario coverage; provenance for every number | Reject unsupported cells |
| Q06 | 11/14 | Semantic LLM | Advantages are specific, buyer-relevant, falsifiable; no invented competitor weakness or cherry-picked misleading comparison | Repair only comparison |
| Q07 | 06/07 | Deterministic | Mixture fractions sum to 100%, units consistent, mass/area/time conversions reproducible | Recompute |
| Q08 | 07/11 | Statistical / simulation | Scenario ranges plausible, assumptions declared, sensitivity/boundary tests; no unjustified narrow median | Refit or widen/flag |
| Q09 | 08/14 | Deterministic + semantic | Named components, concrete process steps, temperatures, dose, acceptance values, and falsification criteria | Targeted specificity rewrite |
| Q10 | 13/14 | Deterministic | No TBD, provisional wording, duplicate sources/conclusion sections, redundant process tables or blank cells disguised as prose | Remove/rewrite |
| Q11 | 12/14 | Semantic LLM | AI Research Spec has multiple variants, objective metrics, validation tasks, uncertainty and no hardcoded agent/model | Repair research spec |
| Q12 | 14/15 | Deterministic | Every active global/project requirement has a traceable location or explicit applicability decision | Block and repair |
| Q13 | 16 | Deterministic | Final package contains all required files, manifest, hashes and QA; no branch mutation; no secrets | Block artifact publication |

### Numeric and competitive advantage scoring

Define `scenario_numeric_coverage = valid_modelled_or_verified_numeric_cells / applicable_numeric_cells`. Require ≥0.51 per competitor and overall. Separately report `verified_numeric_coverage`; it is not interchangeable with scenario coverage. Each scenario cell must link to its method/assumption ID in the internal ledger. Count a value only when its metric, unit and comparator are applicable.

Define `advantage_rate = number_of_comparable_metrics_where_our_value_is_better / number_of_comparable_metrics_with_direction_defined`. Report it as a **design/scenario** result when based on modelling. Target >0.50 for the selected customer-relevant metrics, but do not change baselines, omit material disadvantages, or fabricate observations to force a pass. If the target fails, launch advantage discovery or target-engineering iteration; never silently publish a misleading win.

### Statistical checks

For actual repeated experiments: check sample size, paired/control design, confidence intervals, variability and appropriate effect-size comparisons. Do not run significance tests on made-up scenario numbers or claim p-values for deterministic calculations. For simulations: parameter sweeps, sensitivity, boundary conditions, uncertainty propagation and rank-reversal tests. A scenario advantage must show conditions under which it disappears.

### Low-cost LLM semantic QA contract

Supply only: check ID, rule excerpt, relevant document section, short evidence ledger excerpt and exact output schema. Require `{check_id, verdict, location, reason, patch}`. A second cheap-model reviewer may verify ambiguous cases; deterministic gates remain authoritative for arithmetic/structure. Retry only failed sections (max 2), then BLOCKED with diagnostics. Never give the cheap model the entire 26k-character rules document if only one rule is relevant.

### Regression fixtures based on past failures

Tests must catch: missing patent countries; missing Skolkovo classification; two horizontal tables instead of one vertical matrix; 0/15 competitor coverage; replacing “нет сопоставимого протокола” with “требуется отдельная модель”; unsupported medians; invented competitor values; unbalanced mixture percentages; “Предлагаемая спецификация” in table header; duplicate patent section; generic final summary; standalone Sources; version gaps; incorrect artifact packaging; rule changes not reflected in saved output. Each regression fixture includes a bad input and expected failing check ID.


## Dependency-aware restart after QA failure

A failed check does **not** restart the entire workflow. Each stage has immutable inputs and content hashes. The controller maps a failed gate to the earliest stage that can correct the root cause, invalidates only its affected descendants, and reuses other cached stage artifacts.

| Failure | Restart at | Recompute | Preserve |
|---|---|---|---|
| Q04 numeric coverage | 03 targeted research for missing metrics, or 07 modelling if data exists | 07, 09–11, 13–15 | intake, cluster, unrelated research, patents |
| Q06 advantage rate ≤50% | 05 advantage discovery | 05–07, 08–11, 12 if research goals changed, 13–15 | 00–04 and unaffected research |
| Q03 matrix orientation | 09 comparison generation | 09–11, 13–15 | research, technology synthesis, target engineering |
| Q02 patents | 03 patent research | patent section in 09, 13–15 | all non-patent stages |
| Q01 cluster | 01 classification | dependent outline/sections, 13–15 | unrelated raw research |
| Q07 arithmetic | 06 or 07 depending on source | affected numeric outputs and downstream tables | unrelated documents |
| Q09 vague technology description | 08 draft section | affected sections, 13–15 | research and simulation |
| Q10 forbidden wording | 15 local repair | QA and packaging | all upstream stages |

### Advantage-rate repair strategy

1. Identify losing metrics and evidence tiers; preserve winning metrics and constraints.
2. Retry stage 05 with only losing metrics, competitor context and prior scenario assumptions. Require two candidate improvements: one existing metric and one new relevant metric.
3. Stage 06 changes only selected target parameters; stage 07 reruns sensitivity/feasibility and detects rank reversals.
4. Stage 09 updates affected matrix rows; stage 11 updates Promotion Changes and scores; stage 13 reassembles Final Result.
5. Stage 14 reruns all final gates against saved output. Stage 12 AI Research Specification reruns only if selected research objectives/constraints changed.
6. Limit repair cycles (default 3) and total budget. If still failing, emit BLOCKED diagnostic artifact with remaining losing metrics; never force a winning score by distorting evidence.

### Cache invalidation

Use a dependency graph at artifact/section granularity, not just numeric stage order. Cache key = source commit + input artifact hashes + relevant rule IDs/versions + prompt version + model/config. Changing a comparison row must not invalidate unrelated patents or Skolkovo research. The controller emits `restart-plan.json` listing failed checks, restart nodes, invalidated artifacts, reused artifacts and estimated incremental cost before execution.


### Q14 — Prompt leakage / solution-only document

At stage 08 and final stage 14, perform semantic QA: final text must describe the implemented technical design, materials, operations and verifiable properties, not restate the user assignment, editorial instructions, or generation constraints. Return exact offending spans and local replacements. Recheck saved final artifact after repair.


## Reviewer document import — requirement diff/merge (mandatory)

When a user uploads a reviewed version of a generated document, **do not overwrite the accepted Final Result directly**. Treat the upload as a reviewer candidate and run a separate requirement reconciliation workflow before regeneration.

### Workflow
1. Resolve the base version from explicit metadata or document ID; verify the current accepted version/hash. If ambiguous, stop rather than guessing a diff base.
2. Parse both Markdown documents into section IDs, headings, paragraphs, lists and table cells. Normalize whitespace and formatting separately from semantic content. Align sections by stable IDs/meaning, not only section number.
3. Produce a structured diff with old/new text, section locator, change type (`technical_value`, `terminology`, `structure`, `comparison`, `style`, `cosmetic`, `possible_error`) and source file/hash.
4. For each meaningful edit, propose one atomic project requirement with stable `REV-<version>-NN` ID, exact scope, positive/negative examples, and an acceptance check. Cosmetic changes need not become permanent requirements unless the reviewer explicitly requests a formatting convention.
5. Reconcile against **all active global/project requirements and earlier reviewer decisions**. Mark `accepted`, `conflict_needs_approval`, `duplicate`, `cosmetic` or `rejected_error`. A later uploaded file does **not** implicitly cancel a prior user decision.
6. Append every decision to `projects/<slug>/requirements-log.md`; update `requirements.md` with accepted active rules only. Record explicit `supersedes` links for reversals. Never delete old history.
7. Generate a review report with each edit, decision, conflict, evidence/provenance and affected sections. Ask the user only about genuine contradictions that cannot be resolved from explicit instructions.
8. Recompute affected downstream stages by dependency graph; retain unaffected research and calculations. Apply accepted changes to a new candidate, then run global/project QA and check that all accepted reviewer changes are represented.
9. Save the accepted requirement ledger in Git; generated review report and Final Result are run artifacts by default.

### Immutable requirement status

Each requirement has `id`, `scope`, `source`, `introduced_at`, `status`, `supersedes`, `acceptance_check`. Allowed states: `active`, `superseded_explicitly`, `pending_conflict`, `rejected`. Only an explicit user instruction can transition `active` to `superseded_explicitly`. A reviewer edit may propose the transition but cannot apply it silently.

### Cheap-LLM division

Deterministic code: Markdown parsing, text/table diff, IDs, hashes, duplicate heading detection, history append, requirement coverage checks. Bounded LLM calls: interpret one changed section or table-row group, classify semantic intent, draft atomic requirements, identify possible conflicts. Another bounded QA call checks only disputed items. Never give the full repository and all historical revisions to one low-cost model.

### Regression cases

- Reviewer reintroduces a previously removed heading: flag conflict, do not silently reinstate.
- Reviewer duplicates section number: formatting error, not a new requirement.
- Reviewer changes a numeric competitor estimate: capture value and evidence tier, do not relabel scenario as measured fact.
- Reviewer changes only Markdown spacing: cosmetic, no permanent requirement.
- Reviewer reverses a rule with explicit user approval: append `supersedes` and regenerate affected sections.
- Two reviewer versions share a base but diverge: detect merge conflict, preserve both, do not last-write-wins.

# Playbook — Generate Technology Description

## Input

A project directory under `projects/<project>/`.

Read in this order:
1. `rules/technology-description.md`;
2. all files under `input/`;
3. `requirements.md`;
4. `requirements-log.md`;
5. existing research and latest output, if present.

## Pass 1 — Understand the project

Extract:
- goal and user problem;
- what is already known/designed;
- physical/technical constraints;
- claimed advantages;
- supplied competitors/analogues;
- supplied standards/patents/tests;
- project-specific document requirements.

Do not draft the final document yet.

## Pass 2 — Requirements gate

Apply global + project requirements before research.

Decide:
- which common sections are relevant;
- which sections should be omitted;
- which technology-specific sections are required;
- which statements/wording are fixed by project requirements.

## Pass 3 — Research gap analysis

For each evidence family mark `enough` or `research`:
- competitors/analogues;
- technology/scientific approaches;
- patents;
- standards/regulation;
- test/measurement methods.

If supplied information is already sufficient, skip that research branch.

## Pass 4 — Targeted research

Fill only gaps needed to create a credible technology.

Store generated research in `output/research/` (competitors, patents, standards, sources). `input/` contains only user-supplied material.

For patent-heavy technology, review world and Russia separately when useful.

## Pass 5 — Technology synthesis

If the technology is incomplete:
1. brainstorm 3–4 plausible technical architectures/approaches;
2. compare them against project constraints and research;
3. select the strongest coherent architecture or combination;
4. record reasoning in research/review notes.

If the supplied technology is already sufficiently detailed, do not redesign it gratuitously.

## Pass 6 — Build document outline

Start from the common sections, then adapt.

Add dedicated sections for technically important subsystems/mechanisms.

Remove sections explicitly irrelevant to this project.

## Pass 7 — Draft complete Technology Description

Write the technology in final expert-facing form.

The document must explain how the system works and how critical characteristics are verified.

Keep research/planning uncertainty out of the main document.

## Pass 7a — Mandatory comparison tables

Produce two separate tables:
1. Comparison with market analogues (real products/companies, countries, links, comparable parameters).
2. Advantages over analogues (differentiator, analogue behavior, practical benefit, evidence/verification).

Run a first content/evidence pass and a second dedicated readability pass: compact headings, short cells, balanced orientation, split overwide tables and verify clickable links.

## Pass 8 — Requirements QA

Reread global and project requirements from scratch.

Check each one against the draft. Fix the document rather than merely reporting violations.

## Pass 9 — Evidence QA

Ensure the final document has no standalone Sources/References/Bibliography section. Retain source links inline and the complete ledger under `output/research/sources.md`.


Verify:
- named competitors;
- standards;
- patent identifiers;
- numerical factual claims;
- test methods.

Unsupported material is corrected, removed, or moved to review notes.

## Pass 9a — Generate AI Research Specification

Create `output/ai-research-specification.md` as a separate deliverable. Define a multi-option deep research brief with real-world scenario modelling, objective functions, uncertainty, constraints, evidence and expected outputs. Do not prescribe a specific LLM, agent framework, software stack or simulation tool. The future research executor selects and justifies its tools. Keep virtual results distinct from laboratory evidence.

## Pass 9b — Closing-section QA

Remove redundant concluding recaps (including “Практический результат технологии”). End the expert-facing description with its last substantive section; no summary-of-summary.

## Pass 10 — Save iteration

- save immutable `output/final-result/versions/vNNN.md`;
- update `output/final-result/current.md`;
- append requirement changes to `requirements-log.md`;
- put unresolved generator/editor questions in `output/review-notes.md`, never in the main document.

Then wait for human feedback and repeat.


## Pass 0 — Cluster and vocabulary alignment

Review the official Skolkovo clusters and priority directions. Determine the primary cluster and exact supported direction; record alternatives and the official source in output/research/skolkovo-classification.md. Read the domain input and prepare a glossary of verified specific names, material grades, methods, models, standards and identifiers. This happens before the outline and first draft. Do not invent identifiers.

## Final precision check

Review every section for generic/abstract formulations. Replace them with the most concrete verified technical language available, including named materials, classes, procedures and standards. Verify the classification block is at the top and reflects the actual technical subject, not just its AI research tooling.


## Pass 5a — Falsifiability engineering pass

Convert vague functions into concrete candidate embodiments and numeric **design targets**: composition, manufacturing, application, consumption, layers, drying, environment, test and failure thresholds. Label unmeasured target parameters internally as hypotheses/design values, not measured results. Verify units and mass balance. Prepare a separate evidence ledger for all factual performance claims.

## Pass 7b — Vertical competitor matrix

Generate one primary comparison matrix: rows are detailed parameters, columns are our technology and a small number of named analogues. Link only the analogue's official site/technology in the heading; put patent links in the patent section. Avoid separate generic advantages table; articulate advantages adjacent to the matrix. Review for numeric comparability, unit consistency and narrow-column readability.

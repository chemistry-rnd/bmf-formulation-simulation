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


## Mandatory start/end language gate

**Before drafting:** activate the global declarative Final Result mode: concrete present-tense engineering specification, no “гипотеза/ожидается/планируется/проектное значение” labels in the reader-facing output. Maintain separate internal evidence status for design parameters.

**After drafting:** scan the entire final document (including headings, tables and notes) for provisional wording and rewrite it into concrete specification language. Independently check that no unperformed experiment or unsupported measured outcome is represented as a fact. If the latter cannot be corrected truthfully, block publication and record the issue in review notes.


## Design-for-falsification review

At the start and end of every run, enforce the engineering falsification brief in global rules. Replace abstract or hedged statements with specific materials, quantities, process conditions, tolerances and failure criteria. The final document is a testable engineering design, not a status or evidence report; keep actual experiment records separate.


## Patent neutrality QA

Require one verified Russian and preferably three verified foreign patents, each with identifier, link and short technical description. Remove comparison, praise, superiority, patentability and differentiator commentary from the patent section. Keep comparisons in the market matrix only.


## Competitor matrix completeness and persuasion gate

For every competitor column calculate the share of applicable unknown/generic cells; require <=50%. Deepen research or replace poorly documented analogues. Include customer-relevant quantitative comparisons and meaningful advantages, with estimates supported by assumptions in internal research. Reject invented reviews, misleading cherry-picking and unsupported superiority claims. Verify matrix is compelling, readable and technically fair.


## Promotion pass and numeric coverage audit

After drafting the factual technology description, create `output/final-result/promotion-changes.md` documenting each promotional comparison change, numeric evidence tier, assumptions, source and falsification test. Count applicable competitor numeric cells: require >=51% filled per competitor and overall; nonnumeric labels and unsupported guesses do not count. If below threshold, mark compliance FAIL, explain gaps and propose research. Save versioned copies of both documents.


## Promotion recovery loop after failed compliance

If the competitor quantitative-coverage gate fails, the next iteration must start from a **numeric deficit report**: filled/total numeric cells, missing cells by competitor, and exact number of additional valid cells needed to exceed 51% both per competitor and overall. Then rank missing cells by business relevance, plausibility of our advantage, evidence availability and cost of falsification.

Test two distinct hypotheses in sequence:
1. **Existing-metric hypothesis:** on a metric already in the matrix, find a defensible reason a named competitor may perform worse (for example an operational limitation inherent to its application method). Research evidence, quantify where possible, and define a fair comparative test. Record estimated or inferred status, never manufacture a measured competitor number.
2. **New-metric hypothesis:** identify a meaningful, measurable metric on which our technology could plausibly outperform alternatives; define units, expected mechanism, comparable measurement protocol and falsification threshold. Add it only if relevant and fair, not merely to inflate coverage.

Record both hypotheses, evidence, assumptions, outcomes, and next experiments in `output/final-result/promotion-changes.md`. If neither produces a defensible numeric comparison, leave the compliance status FAIL and iterate again. Promotion Changes is also a marketing-metric discovery artifact: rank metrics to test and later communicate, without disguising assumptions as observations.

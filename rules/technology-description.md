# Global Technology Description Requirements

These rules apply to every project unless a project requirement explicitly overrides an optional rule.

## 1. Document purpose

Write a coherent technical description suitable for expert review. It describes the technology as an integrated, working system — not as a backlog or status report.

Do not put TBDs, implementation status, missing-data lists, CI/model status, or “we will later determine” language into the main document.

## 2. Evidence and research behavior

Use supplied project inputs first.

If essential context is absent, research it during the generation process: competitors, relevant technologies, standards, patents, scientific/engineering approaches and market analogues.

Do not research merely to add volume. Stop when there is enough evidence to design and explain the technology credibly.

Keep research evidence and source links in the project's `research/` files.

## 3. Technology synthesis

The generator is allowed to brainstorm several technically plausible architectures/approaches when the input contains a goal but not a complete technology.

Compare alternatives and select a coherent preferred architecture.

The main document presents the selected technology as the project technology. Alternative reasoning may remain in research/review notes when useful.

Do not invent citations, patent numbers, standards, companies or measured facts.

## 4. Results language

The document should read as a final technology description, but this does not authorize fabricated evidence.

Never invent an experiment count, measured percentage, certification or “best variant achieved X” statement unless the project inputs/evidence explicitly support it.

Where exact measured values are unavailable, describe the completed technical mechanism, control logic, test protocol and acceptance logic without false numerical claims.

## 5. Common sections

Use these when relevant:
- purpose / problem;
- technology and operating principle;
- process / architecture;
- key technical subsystems or technology-specific sections;
- controlled parameters and measurable characteristics;
- testing / validation protocol;
- safety / reliability / compatibility as relevant;
- competitors and differentiation;
- normative / standards basis;
- related patents / patent landscape for technology-heavy projects;
- implementation/use scenario.

Do **not** force irrelevant sections into every project.

## 6. Project-specific depth

The document structure is adaptive.

If one subsystem/mechanism is the technical core, give it its own detailed section rather than squeezing it into a generic template.

Technology-heavy projects should normally include a patent landscape. Split Russia/world when that distinction is useful. Prefer a short list of the most relevant patents (roughly 3–4 per relevant geography when enough strong examples exist), each with a concise explanation of what it covers and why it matters.

## 7. Testing protocol

A credible technology description must explain how its key claims/characteristics are verified.

For each critical characteristic define, where applicable:
- what is measured;
- comparison/control;
- method/equipment or standard;
- conditions;
- unit/scale;
- acceptance logic.

The protocol must correspond to the technology actually described.

## 8. Final QA

Before returning the document:
1. reread global rules;
2. reread project requirements;
3. verify every explicit project requirement is reflected;
4. remove irrelevant template sections;
5. check internal consistency;
6. check that standards/patents/competitors are real and relevant;
7. check that no internal TODO/status language leaked into the main document;
8. check that no unsupported factual result was invented.


## 9. Mandatory market comparison tables

Every expert-facing Technology Description must contain **two distinct, well-designed tables**:

1. **Comparison with market analogues** — factual comparison of real, identified market offerings or technologies.
2. **Advantages of the proposed technology over analogues** — a clear synthesis of meaningful differentiators, their practical consequences and evidence/measurement basis.

These tables are mandatory across projects; project-specific requirements may adapt the comparison criteria, but must not silently omit either table.

### Table A — market analogues
- Identify actual product/technology, company or developer, country, and a working source link.
- Compare against the proposed technology using only relevant, comparable dimensions.
- Make it explicit whether an entry is a commercial product, patent, publication or research prototype; do not pass off scientific papers as market products.
- Use evidence-backed characteristics and consistent units. Mark unverified comparisons in the research notes; do not invent specifications.
- Prefer a layout with **rows = products/analogues** and **columns = a small number of concise criteria**. If many criteria exist, split by theme instead of creating a very wide table.

### Table B — advantages over analogues
- Each row should express one distinct advantage: comparison dimension, what the proposed technology does differently, what the analogue does, practical user benefit, and verification/evidence.
- Avoid generic claims such as “more innovative”, “better”, “more efficient” without measurable or technically meaningful explanation.
- Keep cells short, headings compact and comprehensible, and comparisons grounded in source evidence or explicitly identified design characteristics.
- Do not claim experimentally proven superiority without measurements.

### Two-pass table quality workflow

**Pass 1 — substantive comparison:** gather and verify analogues, countries, source URLs, relevant parameters, and differentiation.

**Pass 2 — readability review:** inspect both tables as rendered Markdown, shorten column headers, trim dense cells, balance vertical/horizontal layout, split overloaded tables, ensure links are usable, and confirm they remain understandable without surrounding paragraphs.

Acceptance: both tables present, readable on a normal document width, no oversized text columns, no invented companies/countries/links/results, and clear practical advantages.


## 10. No standalone Sources section

The expert-facing Technology Description must **not** contain a standalone `Источники`, `Sources`, `References`, or `Библиография` section. This rule applies to all projects.

Preserve source links where they are useful: directly in market-comparison tables, patent entries, and adjacent to claims when necessary. Keep the complete source ledger in `output/research/sources.md`, not in the final document. Never remove provenance or fabricate citations merely to satisfy this formatting rule.


## 11. Mandatory AI Research Specification artifact

For each technical project, generate a separate `output/ai-research-specification.md` in addition to the expert-facing Technology Description. It is a model/agent/tool-agnostic task specification for deep virtual R&D, not an implementation architecture.

The specification must: define multiple candidate approaches, research questions, realistic use conditions and scenarios, constraints, evidence provenance, modelling and uncertainty requirements, comparison criteria, validation plan, stopping criteria, and required deliverables. The executor may select appropriate tools and models and must report their suitability and limitations. Distinguish virtual predictions from physical measurements; never fabricate experiments or imply simulations certify safety or performance.

Generate it from the project's inputs, current requirements, research (including patent/competitor landscape), and current technology description. Save intermediate research separately. Verify consistency with global and project requirements.


## 12. No concluding summary section

Do not append a concluding recap or generic closing section to the expert-facing Technology Description. In particular, omit sections titled “Практический результат технологии”, “Итоги”, “Заключение”, “Выводы”, “Резюме”, “Summary”, “Conclusion”, or equivalent when their function is merely to repeat earlier content. The document ends at its last substantive required section (such as comparison/advantages), without AI-style summary-of-summary. This is a global requirement for all projects. Distinct required documents, such as executive memos or research recommendations, are unaffected.


## 13. Subject-specific precision (all projects)

Prefer concrete domain-specific terms over generic abstractions. Where reliably known, name exact material classes, chemical identities, product/model names, technical standards with identifiers, equipment types, dimensions, methods, patents and company/country identifiers. Slightly longer accurate text is preferable to vague short text. Do not invent precision: if an exact model, grade or identifier is unverified, use the verified class and record the missing detail in review notes. During final QA, search for vague terms (“system”, “solution”, “special component”, “innovative method”) and replace them where supported.

## 14. Skolkovo cluster classification (all projects)

Before drafting, review the current official Skolkovo cluster and priority-direction descriptions, choose the best-fitting cluster and **specific priority/subpriority** by the core commercialized technology (not merely by the use of AI in R&D). Record alternative clusters and reasoning in project research. Place a compact classification block at the very beginning of the expert-facing Technology Description: cluster, priority direction/code, and a one-sentence fit rationale. Verify codes against the current official source; do not invent them or claim formal approval by Skolkovo. Write the main description in terminology consistent with the selected priority without changing the underlying technical facts.


## 15. Falsifiable technical specificity and engineering embodiment

Every technology description must be **operationally falsifiable** (Popper-style): state the most plausible concrete engineering embodiment, named component classes and, where justified, specific candidate substances/grades, formulation ranges, preparation operations, process settings, application rates, layers, drying time, test conditions, numerical target values and tolerances. Distinguish design specifications and hypotheses from verified test outcomes in the internal evidence ledger. A proposed quantitative design value may be stated as a **design parameter**, never falsely as a measured achievement. Do not hide behind functional abstractions (“special additive”, “applied in a thin layer”). Explain exactly what is made, how it is made, how it is used and how failure is detected. Prefer testable ranges and units over unmeasurable adjectives.

For material/chemical projects include: composition table (substance or specific candidate class, role, mass-% range), manufacturing process card (equipment, sequence, conditions, controls), application card (preparation, number of layers, application method, g/m², temperature, humidity, drying), and property/acceptance matrix. Place sensitive IP-level detail in an explicitly referenced appendix only when the main document still has enough detail to be falsifiable.

The expert-facing description is a complete target design, **not a fabricated lab report**. If measurements have not been performed, no claim that a company tested a number of variants or achieved particular measured values is allowed.

## 16. Comparison matrix orientation

Use **one main vertically parameterized comparison matrix**, with **rows = many qualitative/quantitative parameters** and **columns = our technology and named competitors/analogues**. Prefer numeric metrics with units and consistent measurement basis. Include a source link in each competitor's column heading (official product/technology site); do not add citation/source columns or link to general review papers inside the matrix. Keep the number of competitor columns small enough to remain readable; split into thematic matrices only when necessary. A separate prose section may interpret advantages without repeating a second broad table. Do not invent competitor performance figures; where unavailable, indicate that a comparable public value is not disclosed.

Patent references belong in a separate patent landscape section, with Russian and international documents distinguished and links to actual patent records. Do not put general literature citations into the comparison matrix.


## 17. Final-result declarative language gate

The expert-facing Final Result is written as a concrete technical embodiment in the **declarative present tense**. Do not use labels or disclaimers such as “гипотеза”, “проектная гипотеза”, “предполагается”, “ожидается”, “планируется”, “проектное значение”, “TBD”, “target”, “expected”, or equivalent provisional language in the final document. Give precise falsifiable specifications: component identity, concentration, processing conditions, application dose, drying time, and measurable acceptance criteria. The generated Final Result is a technology specification, not an R&D diary.

**Evidence integrity remains mandatory:** do not invent completed tests, measured outcomes, certifications or comparative performance. Keep the provenance and verification status of each unmeasured numeric design specification in the internal research/QA ledger. Declarative design specifications are allowed; fabricated measured results are not.

This gate is applied both **before drafting** (system-level generation contract) and **after drafting** (scan headings, tables, body and footnotes; rewrite or block offending passages). The QA pass must also reject invented evidence and misleading claims of completed validation.


## 18. Engineering falsification brief — writing philosophy

The intended reader is an engineer or experimentalist who knows the document is a theoretical technical design. The purpose is to give them a **concrete configuration to challenge and falsify**, not to hedge every sentence. Write in assertive present tense and make claims precise enough that the engineer can immediately construct a test, discover a failure and improve the technology.

Prefer “Состав содержит 7% карбамида”, “Нанесение выполняется одним проходом при расходе 30–60 г/м²”, “Время готовности — 15 минут” to “предположительно”, “возможный вариант”, “предлагаемая спецификация” or generic functions. No apology, disclaimers or epistemic qualifiers in the main text. Do not replace specificity with vague confidence statements.

This is a **design-for-falsification document**, not a laboratory evidence report. The numbers and mechanisms are concrete design assertions to be tested. Evidence status, actual measurements and failed tests live separately in internal research and experiment records. The main document must not falsely attribute a test to a named laboratory, claim a certificate exists or misquote external results; otherwise its role is to be direct and testable.

The same style gate applies to every section, table heading, parameter cell and process step. Final QA asks: “Can an engineer take this exact statement and try to disprove it with a measurable test?” If not, rewrite it.


## 19. Neutral patent landscape (all projects)

The patent section is a factual catalogue, **not a competitive argument**. Include at least one verified Russian patent and preferably three verified international patents when relevant examples exist. For each: jurisdiction, exact publication identifier, linked patent record, title, and 1–2 concise sentences explaining the claimed technical subject or method. No commentary that a patent is “similar”, “different”, “inferior”, “better”, “not identical”, or how our technology compares. No self-promotion or patentability conclusions. Separate Russian and international subsections. If the requested number of relevant patents cannot be verified, record the gap internally instead of inventing entries.


## 20. Persuasive, research-rich competitor matrix (all projects)

The vertical competitor matrix is a startup/expert-engagement artifact: it must highlight **real, technically relevant and testable advantages** of the project. Research each named competitor deeply, including manufacturer documentation, prices, use conditions, independent reviews and known limitations. Choose comparison dimensions relevant to the actual customer use case, including cost, application time, consumption, compatibility, performance and operational constraints.

**Completeness gate:** for each competitor, at most 50% of applicable metric cells may be unfilled or contain generic answers such as “not disclosed”, “depends on formulation”, “no comparable data”, or “unknown”. If the threshold fails, research further, replace the competitor with a more documentable relevant one, or reduce to a defensible set of comparable metrics. Do not game the metric by deleting meaningful dimensions or using irrelevant comparisons.

Where primary data is unavailable, a defensible calculation or explicit estimate may be used, with assumptions and provenance in `output/research/`. Do not present guessed competitor performance as verified fact, invent negative reviews, cherry-pick misleading baselines, or guarantee superiority. Use clear, concise cells in the final table; preserve detailed evidence in research files. Select useful differentiators where the proposed technology genuinely has a design advantage, while retaining material trade-offs and disadvantages. Aim for a compelling **fair** comparison, not a fabricated win.

Final QA: check completeness percentage per competitor, metric comparability, sources/assumptions, numeric units, relevance to the buyer, and whether every claimed advantage is defensible and falsifiable.


## 21. Two-document final compliance package

Every final iteration produces exactly two companion documents under `output/final-result/`:
- `current.md`: substantive expert-facing technology description, with vertical comparison matrix and concrete falsifiable parameters.
- `promotion-changes.md`: transparent promotional/comparison revision record, stating which matrix cells changed, evidence level (measured / manufacturer-stated / calculated / estimated), numerical assumptions, source provenance, confidence and test needed to disprove the estimate.

**Numeric coverage gate:** at least 51% of applicable competitor numeric cells must contain actual numerical values, with units and a meaningful comparison basis. A non-numeric description does not count. Do not count our own column toward competitor coverage. Calculate both overall coverage and per-competitor coverage; both must reach 51%. Unsupported invented values do not count. If this is impossible after research, record failure in `promotion-changes.md` and do not falsely label the pair compliant. Improve research, choose better-documented competitors, or use defensible calculations with stated assumptions. Preserve meaningful comparison metrics, including unfavorable ones.

The pair forms the review/compliance package. The promotional document is allowed to discuss estimates and uncertainty; the main document remains a concise engineering specification. Keep versioned snapshots of both.


## 22. Research target engineering artifact

For every project, create `output/analysis/research-target-engineering.md` between competitor research and AI Research Specification. Establish a plausible baseline per measurable metric, assess improvement mechanisms, and set an ambitious but physically testable target (default illustrative improvement +30% where justified, not a universal rule). For lower-is-better metrics use baseline ×0.70; for higher-is-better use baseline ×1.30, while checking feasibility and units. Keep baseline, proposed improvement, target, method, uncertainty and evidence status distinct. A target is a design specification, not evidence that performance has been achieved. Feed the target and validation/falsification criteria into AI Research Specification. Never count targets as measured competitor data for compliance.


## 23. Competitive Advantage Discovery precedes target setting

Improvement percentages are **not fixed** (30% or 40% are examples, not global rules). First generate `output/analysis/competitive-advantage-discovery.md`: examine competitors, product-use constraints, mechanisms and market needs to identify metrics with credible potential for improvement. For each opportunity state the competitor baseline or estimate, physical/operational mechanism, likely improvement range, uncertainty, test cost and a falsification experiment. Rank opportunities by meaningful buyer benefit, attainable advantage and speed of learning. Only then derive metric-specific numeric goals in Research Target Engineering. Optimize a small number of high-leverage metrics while keeping other properties as hard constraints. An aggressive target may deliberately fail and redirect research; never silently reduce it to obtain a pass.


## 24. Final comparison matrix completion policy (all projects)

The final vertical comparison matrix is populated in the following order: (1) exact manufacturer/product measurements under stated conditions; (2) representative market benchmark values from named comparable products; (3) reproducible engineering calculations normalized to the same geometry, dose and operating conditions; (4) explicitly modelled scenarios with documented assumptions and sensitivity. Do not leave generic “not published / no comparable protocol / depends on formulation” entries when a meaningful normalized engineering scenario can be calculated.

For modelled cells, use the central scenario and a plausible range only if its bounds are supported by a defined sensitivity model or reference evidence; never invent a narrow statistical median or uncertainty interval. If a competitor product lacks data, label the estimate as a **method/class scenario**, not its verified product property. Do not manufacture measured efficacy, safety, emissions, or certification claims. Maintain all inputs, equations, unit conversions, assumptions, evidence tiers, and uncertainty in `output/analysis/comparative-simulation.md` and `output/final-result/promotion-changes.md`.

The final matrix keeps rows as measurable parameters and columns as products or explicitly identified reference classes. Use consistent units and conditions; do not mix liquid volume and mass without a density conversion. A modelled value may count toward scenario-completeness only if it is meaningful and reproducible; it never counts as verified competitor-measurement coverage. Run two separate QA scores: scenario-completeness and verified comparable-data coverage. Preserve material disadvantages and do not manipulate assumptions merely to meet a target score.


## 25. Blind table-cell completion gate

After normal drafting, run a **blind table-only pass** over every competitor-comparison cell. Treat the following as INVALID content, not as an answer: “нет сопоставимого протокола”, “не опубликовано”, “зависит от покрытия/рецептуры”, “требуется отдельная модель”, “сценарий измеряется отдельно”, “требуется контроль зоны распыления”, “производственная стадия”, “не относится к монтажу”, and equivalent vague/process-only text when the row requests a measurable value.

1. Scan all rows; mark each invalid cell as missing and pass the table, row name, units, product/class and allowed evidence context to a **separate blind completion step**.
2. The completion step returns **only a replacement table**: numeric central estimates and reasonable sensitivity ranges for numeric metrics, and concrete operational values for categorical metrics. Use a disclosed generic method/class model when no product measurements exist; never invent a product-specific measured median.
3. All inferred values receive provenance and assumption records in Promotion Changes; the final table must distinguish modelled class scenarios from actual product specifications.
4. Rerun a semantic QA after filling: reject placeholders disguised as prose, unsupported precision, incompatible units and any claim that a modelled estimate is measured product performance.
5. If no defensible numerical model exists for a high-stakes metric (e.g. 90-day HCHO emissions), do not fabricate a median: use a scenario explicitly parameterized by an assumed baseline and place the corresponding calculation and sensitivity in analysis. A compliance failure remains a failure rather than a manufactured pass.

The blind step has a strict output contract: **table only, no commentary, no generic unknown placeholders**. It may fail with a structured missing-model flag, which is recorded outside the final table.


## 25. Blind competitor-table completion

After generating the final document, run an isolated table-only review. Mark generic cells as invalid, including: “Нет сопоставимого протокола”, “Не опубликовано”, “Зависит от покрытия”, “Требуется отдельная модель”, “Сценарий измеряется отдельно”, “Требуется контроль зоны распыления”. Equivalent evasive process descriptions are also invalid when the row calls for a measurable parameter.

Pass the table with invalid cells blanked to a separate completion step. Its output is only the completed table, with numerical central scenario values and ranges for quantitative metrics and concrete operational descriptions for qualitative metrics. Every estimate must have a stated model, units, assumptions and source category in the internal Promotion Changes record. Never mislabel a scenario value as a measured median for a named product.

Perform independent semantic QA after completion: verify that no placeholder survives in paraphrase, numbers are physically plausible, units and test conditions are comparable, and source status is preserved. A cell without a defensible estimation method cannot be assigned an invented precise value; flag it for further modelling outside the table. Do not declare numeric compliance merely because every cell contains a number.


## 26. Describe the solution, never retell the prompt

The final document describes the technology itself and the concrete solution, not the assignment, generation instructions, constraints as meta-commentary, or how the author followed the prompt. Avoid sentences such as “для обработки не требуется специальное оборудование”, “мы решаем задачу”, “документ должен показать”, “в соответствии с требованиями” when they merely echo the brief rather than specifying how the technology works. Translate requirements into concrete product properties, operations, technical parameters and verifiable outcomes. A genuinely informative operational limitation may remain only when expressed as an intrinsic characteristic, not an aside about the task. Apply this check at initial drafting and again during final semantic QA, including headings, tables and concluding remarks. Flag prompt leakage and repair the affected sentences without rewriting unrelated sections.

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

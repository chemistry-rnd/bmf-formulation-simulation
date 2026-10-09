# Requirements Log — Formaldehyde Scavenger

Append-only log. Current accepted state is `requirements.md`.

## R001 — baseline
- Fresh on-site cuts are primary; holes secondary.
- Composition must be practical for installer use.
- Discovery compares many formulations and key ratios/interactions.
- Odor requires instrumental + sensory treatment.
- Device is a later optional direction.

## R002 — document/research structure
- Add patent landscape for deep technology projects.
- Review world and Russian patents separately where useful; select a small set of the most relevant examples with concise explanations.
- Competitors should be researched when missing from inputs.
- The final document must include a testing/validation protocol corresponding to the technology.

## R003 — Concrete technology card and patent draft appendix
- Add materials/functions and installer operations as a technological card inside the main description.
- Reserve Appendix No. 7 for a separate draft patent application with exact chemistry, variants, parameters and proposed claims.
- Avoid suggesting a patent filing or completed appendix already exists.


## R004 — 2026-10-09 — Reviewer version 016 import (append-only)
Source: user-uploaded `Версия 16.md`, compared with `output/final-result/current.md` (version 015). The source is a review candidate, not an automatic replacement for the accepted Final Result.

| ID | Reviewer delta | Decision | Scope |
|---|---|---|---|
| REV-016-01 | Added “Инструкция монтажника:” above the seven steps | CONFLICT: earlier user explicitly removed the checklist heading; hold pending user approval | Section 5 |
| REV-016-02 | Repeated heading “## 6. Контролируемые характеристики” instead of sequential 7 | FORMAT ERROR: reject duplicate numbering | Section headings |
| REV-016-03 | Speco application time simplified to 20 min; BASF 60 min; Asta factory application | ACCEPT as reviewer-requested display; maintain scenario provenance | Competitor matrix |
| REV-016-04 | Swelling values 0.10–0.13, 0.09–0.12, 0.11–0.14 mm without scenario qualifiers | ACCEPT numeric values, NOT removal of scenario status | Competitor matrix |
| REV-016-05 | HCHO 90-day competitor cells changed from uniform 35% scenario to 35% / “Нет данных” / 50% | ACCEPT as reviewer scenario inputs; BASF missing value conflicts with numeric-fill goal, requires further modelling | Competitor matrix |
| REV-016-06 | Several scenario labels and source qualifiers shortened or removed | ACCEPT editorial brevity only; evidence tier stays in Promotion Changes | Competitor matrix |
| REV-016-07 | Patent markdown emphasis and table spacing reformatted | COSMETIC: no new technical requirement | Patent/table formatting |
| REV-016-08 | Composition, material quantities, 9-minute process, and main technology principle largely retained | NO NEW REQUIREMENT; verify no regression | Sections 1–6 |

### Historical requirements reconciliation
- R003 (technology-card table and Appendix 7) is superseded by the user's later explicit instructions to remove both; **must not be resurrected**.
- Later explicit user decisions: “Состав” is section 4; installation steps are section 5; no “Чеклист монтажника” label; no prompt-leakage/meta sentence; no redundant ending.
- Global rules remain active: neutral patent catalogue, cluster classification, vertical competitor matrix, no sources appendix, numeric evidence provenance.

A reviewer file never automatically cancels these decisions. Any reversal requires explicit user authorization, recorded with `supersedes` and a reason.

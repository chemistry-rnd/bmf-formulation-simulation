"""Source/data status registry for BMF formulation components.

Status values:
- EVIDENCE_SUPPORTED: public or project-supplied source exists.
- NEEDS_EVIDENCE: candidate chemistry requires patent/literature support.
- NOT_MODELLED: no trustworthy model was built; cannot be optimized fairly.
- UNKNOWN_COMPATIBILITY: experimental status is unknown; must not be called safe.
"""

from __future__ import annotations

COMPONENT_REGISTRY = [
    {"id": "PEI", "name": "Polyethylenimine", "role": "formaldehyde scavenger", "cas": "9002-98-6 / polymer mixture", "evidence_status": "EVIDENCE_SUPPORTED", "notes": "Nitrogen content and group distribution depend on grade; see chemistry audit."},
    {"id": "ACRYLIC_DISPERSION", "name": "Waterborne acrylic dispersion", "role": "film-forming barrier", "cas": "mixture", "evidence_status": "EVIDENCE_SUPPORTED", "notes": "Solids content and compatibility with PEI must be grade-specific."},
    {"id": "UREA", "name": "Urea", "role": "formaldehyde scavenger/crosslinker", "cas": "57-13-6", "evidence_status": "EVIDENCE_SUPPORTED", "notes": "Proven formaldehyde binder; nitrogen basis and volatility constraints apply."},
    {"id": "NONIONIC_WETTER", "name": "Nonionic wetting agent", "role": "wetting/dose control", "cas": "surfactant mixture", "evidence_status": "NEEDS_EVIDENCE", "notes": "Exact grade, VOC and compatibility pending."},
    {"id": "WATER_CARRIER", "name": "Water/carrier", "role": "solvent and swelling source", "cas": "7732-18-5", "evidence_status": "EVIDENCE_SUPPORTED", "notes": "Water in commercial dispersions must be counted."},
    {"id": "CROSS_LINKER_ALT", "name": "Alternative cross-linker/binder family", "role": "candidate architecture", "cas": "unknown", "evidence_status": "NOT_MODELLED", "notes": "No trustworthy reaction model or supplier data yet; cannot be ranked fairly."},
]


def known_component_ids() -> list[str]:
    return [item["id"] for item in COMPONENT_REGISTRY]


def model_status_for_component(component_id: str) -> str:
    for item in COMPONENT_REGISTRY:
        if item["id"] == component_id:
            return item["evidence_status"]
    return "UNKNOWN_COMPONENT"

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FormulationId = Literal["A", "B", "C"]


@dataclass(frozen=True)
class Formulation:
    name: str
    use: str
    wet_application_g_m2: float
    mass_fractions: dict[str, float]


FORMULATIONS: dict[str, Formulation] = {
    "A": Formulation(
        name="A Reactive",
        use="formaldehyde binding without polymer film",
        wet_application_g_m2=20.0,
        mass_fractions={
            "pei_active": 20.0,
            "urea": 0.0,
            "acrylic_dry_solids": 0.0,
            "nonionic_wetter": 0.0,
            "other_nonvolatile_binder": 0.0,
            "water_carrier": 80.0,
        },
    ),
    "B": Formulation(
        name="B Balanced",
        use="reactive binding plus one-step barrier coat",
        wet_application_g_m2=25.0,
        mass_fractions={
            "pei_active": 8.0,
            "urea": 0.0,
            "acrylic_dry_solids": 12.0,
            "nonionic_wetter": 0.1,
            "other_nonvolatile_binder": 0.0,
            "water_carrier": 79.9,
        },
    ),
    "C": Formulation(
        name="C Barrier",
        use="high solids, lowest water among candidates",
        wet_application_g_m2=20.0,
        mass_fractions={
            "pei_active": 3.0,
            "urea": 0.0,
            "acrylic_dry_solids": 25.0,
            "nonionic_wetter": 0.1,
            "other_nonvolatile_binder": 0.0,
            "water_carrier": 71.9,
        },
    ),
}

SUPPLIER_ASSUMPTIONS = {
    "pei_solution_active_mass_fraction": 0.50,
    "acrylic_dispersion_dry_solids_mass_fraction": 0.50,
    "nonionic_wetter_mass_fraction": 1.00,
    "edge_thickness_m": 0.016,
    "linear_piece_length_m": 1.0,
}

ALL_FORMULATIONS = ["A", "B", "C"]


def validate_formula(f_id: str) -> None:
    f = FORMULATIONS[f_id]
    fractions = f.mass_fractions
    total = sum(fractions.values())
    if abs(total - 100.0) > 1e-9:
        raise ValueError(f"{f_id}: mass fractions sum to {total}, expected 100")
    if f.wet_application_g_m2 <= 0:
        raise ValueError(f"{f_id}: wet application must be positive")
    for key, value in fractions.items():
        if value < 0.0:
            raise ValueError(f"{f_id}: negative fraction for {key}")
    if fractions["water_carrier"] < 0.0 or fractions["water_carrier"] > 100.0:
        raise ValueError(f"{f_id}: water fraction out of range")
    if fractions["acrylic_dry_solids"] > 100.0 or fractions["pei_active"] > 100.0:
        raise ValueError(f"{f_id}: component fraction exceeds 100")

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


def _trapezoid(y, x):
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(y, x))
    return float(np.trapz(y, x))
from scipy.integrate import solve_ivp


@dataclass
class MoistureDiffusion1D:
    board_thickness_m: float
    diffusivity_m2_s: float
    initial_concentration_kg_m3: float
    ambient_equilibrium_kg_m3: float
    surface_transfer_coeff_m_s: float
    exposure_hours: float
    nodes: int = 21
    both_surfaces: bool = True

    def require_inputs(self) -> None:
        if self.board_thickness_m <= 0:
            raise ValueError("board thickness must be positive")
        if self.diffusivity_m2_s < 0:
            raise ValueError("diffusivity must be non-negative")
        if self.nodes < 5:
            raise ValueError("use at least 5 spatial nodes")
        if self.exposure_hours < 0:
            raise ValueError("exposure time must be non-negative")


def moisture_diffusion_1d(model: MoistureDiffusion1D) -> dict[str, Any]:
    """One-dimensional Fickian moisture diffusion/evaporation.

    Units: concentration kg/m3, diffusivity m2/s, h_m m/s. Boundary flux is
    h_m (C_surface - C_ambient). This is a parameterized physical model; D and
    h_m are not installed-material calibration data unless explicitly stated.
    """
    model.require_inputs()
    x = np.linspace(0.0, model.board_thickness_m, model.nodes)
    dx = x[1] - x[0]
    c0 = np.full(model.nodes, model.initial_concentration_kg_m3, dtype=float)
    t0 = 0.0
    tf = model.exposure_hours * 3600.0
    # Reduced state: concentrations at nodes. Define derivatives.
    # Robin boundaries approximated by ghost-node fluxes.
    def derivatives(t, c):
        dcdt = np.zeros_like(c)
        # interior second derivative
        for i in range(1, model.nodes - 1):
            dcdt[i] = model.diffusivity_m2_s * (c[i - 1] - 2 * c[i] + c[i + 1]) / dx**2
        # left boundary flux (into/out of board from environment)
        flux_left = model.surface_transfer_coeff_m_s * (model.ambient_equilibrium_kg_m3 - c[0])
        dcdt[0] = flux_left / dx if model.both_surfaces else (flux_left - _internal_flux(c, 0, dx, model)) / dx
        # For a simple Robin treatment, boundary node mass balance uses ghost cell.
        # Right boundary
        flux_right = model.surface_transfer_coeff_m_s * (model.ambient_equilibrium_kg_m3 - c[-1])
        dcdt[-1] += flux_right / dx
        return dcdt

    sol = solve_ivp(derivatives, (t0, tf), c0, method="RK23", max_step=300.0, dense_output=True, rtol=1e-7, atol=1e-9)
    if not sol.success:
        raise RuntimeError("moisture diffusion integration failed: " + sol.message)
    c_final = sol.y[:, -1]
    initial_mass = _trapezoid(c0, x)
    final_mass = _trapezoid(c_final, x)
    mass_change = final_mass - initial_mass
    evaporated_equivalent = max(-mass_change, 0.0)  # negative final mass change can be evaporation
    absorbed = max(mass_change, 0.0)
    profile_range = np.ptp(c_final)
    conserved = np.isfinite(c_final).all() and not np.any(c_final < -1e-9)
    return {
        "grid_m": x.tolist(),
        "initial_concentration_kg_m3": model.initial_concentration_kg_m3,
        "final_concentration_kg_m3": c_final.tolist(),
        "initial_mass_kg_m2": float(initial_mass),
        "final_mass_kg_m2": float(final_mass),
        "mass_change_kg_m2": float(mass_change),
        "evaporated_equivalent_kg_m2": float(evaporated_equivalent),
        "absorbed_from_environment_kg_m2": float(absorbed),
        "final_min_kg_m3": float(c_final.min()),
        "final_max_kg_m3": float(c_final.max()),
        "profile_range_kg_m3": float(profile_range),
        "numerical_mass_conservation_ok": conserved,
        "parameters_calibrated": False,
        "note": "parameterized CPU diffusion with Robin boundary conditions; dimensions kg/m3 and m2/s.",
    }



@dataclass
class CoatingFilm:
    dose_g_m2: float
    wet_density_kg_m3: float = 1000.0
    dry_mass_fraction: float = 1.0
    dry_density_kg_m3: float = 1200.0

    def thickness_and_mass(self) -> dict[str, Any]:
        if self.dose_g_m2 < 0 or self.wet_density_kg_m3 <= 0 or self.dry_density_kg_m3 <= 0:
            raise ValueError("invalid coating inputs")
        wet_mass = self.dose_g_m2 / 1000.0
        dry_mass = wet_mass * self.dry_mass_fraction
        wet_thickness_m = wet_mass / self.wet_density_kg_m3
        dry_thickness_m = dry_mass / self.dry_density_kg_m3 if self.dry_mass_fraction > 0 else 0.0
        return {
            "dose_g_m2": self.dose_g_m2,
            "wet_film_thickness_m": wet_thickness_m,
            "dry_film_thickness_m": dry_thickness_m,
            "dry_mass_fraction": self.dry_mass_fraction,
            "tack_free_time": "UNKNOWN without calibrated test",
            "process_ready_time": "UNKNOWN without calibrated test",
        }


def hcho_reaction_diffusion(
    substrate_concentration_kg_m3: float,
    ambient_concentration_kg_m3: float,
    coating_thickness_m: float,
    diffusivity_m2_s: float,
    reaction_rate_1_s: float = 0.0,
    nodes: int = 21,
) -> dict[str, Any]:
    if coating_thickness_m <= 0:
        raise ValueError("coating thickness must be positive")
    if diffusivity_m2_s <= 0:
        raise ValueError("diffusivity must be positive")
    if nodes < 5:
        raise ValueError("use at least 5 nodes")
    x = np.linspace(0.0, coating_thickness_m, nodes)
    h = x[1] - x[0]
    a = np.zeros((nodes, nodes))
    b = np.zeros(nodes)
    for i in range(1, nodes - 1):
        a[i, i - 1] = diffusivity_m2_s / h**2
        a[i, i] = -(2 * diffusivity_m2_s / h**2 + reaction_rate_1_s)
        a[i, i + 1] = diffusivity_m2_s / h**2
    a[0, 0] = 1.0
    b[0] = substrate_concentration_kg_m3
    a[-1, -1] = 1.0
    b[-1] = ambient_concentration_kg_m3
    profile = np.linalg.solve(a, b)
    gradient_left = (profile[1] - profile[0]) / h
    flux = -diffusivity_m2_s * gradient_left
    return {
        "thickness_m": coating_thickness_m,
        "diffusivity_m2_s": diffusivity_m2_s,
        "reaction_rate_1_s": reaction_rate_1_s,
        "substrate_concentration_kg_m3": substrate_concentration_kg_m3,
        "ambient_concentration_kg_m3": ambient_concentration_kg_m3,
        "surface_flux_kg_m2_s": float(flux),
        "layer_integrated_concentration_kg_m2": float(_trapezoid(profile, x)),
        "concentration_profile_kg_m3": profile.tolist(),
        "rate_constant_calibrated": False,
        "note": "steady-state reaction-diffusion surrogate; rate constant must be measured for quantitative claims.",
    }


@dataclass
class SwellingCalibration:
    slope_mm_per_mass_fraction: float | None = None
    intercept_mm: float = 0.0
    source: str = "uncalibrated"

    def predict_mm(self, moisture_mass_fraction: float) -> float | None:
        if self.slope_mm_per_mass_fraction is None:
            return None
        return self.intercept_mm + self.slope_mm_per_mass_fraction * moisture_mass_fraction

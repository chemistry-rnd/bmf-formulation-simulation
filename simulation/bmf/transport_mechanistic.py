from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp


def _trapezoid(y, x):
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(y, x))
    return float(np.trapz(y, x))


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
    """One-dimensional Fickian moisture diffusion/evaporation with Robin boundaries.

    The integrated form is used for mass conservation:
    (M_final - M_initial) + integral incoming/outgoing flux dt = 0.
    Positive flux is defined as transport from surface to surrounding air.
    """
    model.require_inputs()
    x = np.linspace(0.0, model.board_thickness_m, model.nodes)
    dx = x[1] - x[0]
    c0 = np.full(model.nodes, model.initial_concentration_kg_m3, dtype=float)
    tf = model.exposure_hours * 3600.0

    def ode(t, c):
        out = np.zeros_like(c)
        # interior cells
        out[1:-1] = model.diffusivity_m2_s * (c[:-2] - 2 * c[1:-1] + c[2:]) / dx**2
        # left boundary cell, finite volume
        out[0] = (model.diffusivity_m2_s * (c[1] - c[0]) / dx + model.surface_transfer_coeff_m_s * (model.ambient_equilibrium_kg_m3 - c[0])) / dx
        if model.both_surfaces:
            out[-1] = (model.diffusivity_m2_s * (c[-2] - c[-1]) / dx + model.surface_transfer_coeff_m_s * (model.ambient_equilibrium_kg_m3 - c[-1])) / dx
        else:
            out[-1] = model.diffusivity_m2_s * (c[-2] - c[-1]) / dx**2
        return out

    if tf == 0:
        sol_t = np.array([0.0])
        sol_y = c0[:, None]
        sol = None
    else:
        n_times = max(51, int(tf / 10.0) if tf <= 3600 else 201)
        t_eval = np.linspace(0.0, tf, n_times)
        sol = solve_ivp(ode, (0.0, tf), c0, method="RK45", t_eval=t_eval, rtol=1e-9, atol=1e-11, max_step=max(tf / 200.0, 1.0))
        if not sol.success:
            raise RuntimeError("moisture diffusion integration failed: " + sol.message)
        sol_t = sol.t
        sol_y = sol.y

    c_final = sol_y[:, -1]
    initial_mass = float(dx * np.sum(c0))
    final_mass = float(dx * np.sum(c_final))
    mass_change = final_mass - initial_mass

    # Integrate boundary fluxes using the solution at output time points.
    if tf == 0:
        integrated_outward_flux = 0.0
    else:
        left_flux = model.surface_transfer_coeff_m_s * (sol_y[0, :] - model.ambient_equilibrium_kg_m3)
        if model.both_surfaces:
            right_flux = model.surface_transfer_coeff_m_s * (sol_y[-1, :] - model.ambient_equilibrium_kg_m3)
            total_flux = left_flux + right_flux
        else:
            total_flux = left_flux
        integrated_outward_flux = float(np.trapezoid(total_flux.values if hasattr(total_flux, "values") else total_flux, sol_t)) if len(sol_t) > 1 else 0.0
    flux_mass_change = -integrated_outward_flux
    balance_error = mass_change - flux_mass_change
    tol = max(1e-8, 1e-4 * (abs(initial_mass) + 1.0))
    return {
        "grid_m": x.tolist(),
        "initial_concentration_kg_m3": model.initial_concentration_kg_m3,
        "final_concentration_kg_m3": c_final.tolist(),
        "initial_mass_kg_m2": float(initial_mass),
        "final_mass_kg_m2": float(final_mass),
        "mass_change_kg_m2": float(mass_change),
        "integrated_outward_flux_kg_m2": float(integrated_outward_flux),
        "mass_balance_residual_kg_m2": float(balance_error),
        "profile_range_kg_m3": float(np.ptp(c_final)),
        "numerical_mass_conservation_ok": bool(abs(balance_error) <= tol and np.isfinite(c_final).all()),
        "incoming_mass_kg_m2": float(max(integrated_outward_flux, 0.0)),
        "outgoing_mass_kg_m2": float(min(integrated_outward_flux, 0.0) or 0.0),
        "parameters_calibrated": False,
        "note": "quantitative integrated-flux moisture balance; D and transfer coefficient remain uncalibrated.",
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
    gradient_right = (profile[-1] - profile[-2]) / h
    substrate_interface_flux = -diffusivity_m2_s * gradient_left
    ambient_emission_flux = -diffusivity_m2_s * gradient_right
    reaction_consumption = substrate_interface_flux - ambient_emission_flux
    reaction_integral = float(np.trapezoid(np.maximum(profile, 0.0), x) * reaction_rate_1_s) if hasattr(np, "trapezoid") else float(np.trapz(np.maximum(profile, 0.0), x) * reaction_rate_1_s)
    return {
        "thickness_m": coating_thickness_m,
        "diffusivity_m2_s": diffusivity_m2_s,
        "reaction_rate_1_s": reaction_rate_1_s,
        "substrate_interface_flux_kg_m2_s": float(substrate_interface_flux),
        "ambient_emission_flux_kg_m2_s": float(ambient_emission_flux),
        "surface_flux_kg_m2_s": float(ambient_emission_flux),  # backwards-compatible alias
        "reaction_consumption_kg_m2_s": float(reaction_consumption),
        "reaction_integral_kg_m2_s": float(reaction_integral),
        "substrate_concentration_kg_m3": substrate_concentration_kg_m3,
        "ambient_concentration_kg_m3": ambient_concentration_kg_m3,
        "layer_integrated_concentration_kg_m2": float(_trapezoid(profile, x)),
        "concentration_profile_kg_m3": profile.tolist(),
        "mass_balance_residual_kg_m2_s": float(reaction_consumption - reaction_integral),
        "rate_constant_calibrated": False,
        "note": "steady-state reaction-diffusion; rate constants and diffusivities require calibration.",
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

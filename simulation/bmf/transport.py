from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp


def moisture_evaporation(
    water_load_g_m2: float,
    area_m2: float = 1.0,
    duration_h: float = 24.0,
    evaporation_coeff_m_s: float = 1.0e-4,
    air_humidity_fraction: float = 0.5,
    temperature_c: float = 23.0,
) -> dict[str, float]:
    """Parametric surface evaporation model using SciPy integration.

    Returns evaporated and residual water after the observation period. This is a
    modelled transport quantity, not a measured drying outcome.
    """
    if water_load_g_m2 < 0:
        raise ValueError("water load must be non-negative")
    if area_m2 <= 0 or duration_h <= 0 or evaporation_coeff_m_s < 0:
        raise ValueError("area, duration and coefficient must be positive/non-negative where applicable")

    temperature_k = temperature_c + 273.15
    water_mass_kg = water_load_g_m2 / 1000.0 * area_m2
    eq_water_kg = water_mass_kg * air_humidity_fraction * 0.35
    rate = evaporation_coeff_m_s * area_m2 * max(0.0, temperature_k - 273.15 + 20.0) / 1000.0

    def ode(t, y):
        w = y[0]
        dw = -rate * (w - eq_water_kg)
        return [dw]

    sol = solve_ivp(ode, (0.0, duration_h * 3600.0), [water_mass_kg], method="RK45", dense_output=True)
    if not sol.success:
        raise RuntimeError(f"moisture ODE failed: {sol.message}")
    final_water_kg = max(float(sol.y[0, -1]), 0.0)
    evaporated_kg = max(water_mass_kg - final_water_kg, 0.0)
    return {
        "initial_water_g_m2": water_load_g_m2,
        "residual_water_after_duration_g_m2": final_water_kg * 1000.0 / area_m2,
        "evaporated_water_g_m2": evaporated_kg * 1000.0 / area_m2,
        "duration_h": duration_h,
        "equilibrium_water_g_m2": eq_water_kg * 1000.0 / area_m2,
        "note": "parametric evaporation estimate; not a measured drying result",
    }


def hcho_residual_fraction(
    capacity_g_m2: float,
    wet_application_g_m2: float,
    barrier_factor: float,
    diffusion_factor: float = 1.0,
    temperature_c: float = 23.0,
) -> float:
    """Dimensionless residual HCHO fraction after treated layer.

    Lower is better. This is a bounded parametric surrogate, not measured
    emission reduction.
    """
    if wet_application_g_m2 <= 0:
        return 1.0
    if capacity_g_m2 < 0 or barrier_factor < 0:
        raise ValueError("capacity and barrier factor must be non-negative")
    temperature_term = 1.0 + 0.02 * (temperature_c - 20.0)
    exponent = capacity_g_m2 / max(wet_application_g_m2, 1e-9) + 0.8 * barrier_factor
    reduction = 1.0 - math.exp(-max(exponent, 0.0) / max(diffusion_factor, 1e-9) * temperature_term)
    reduction = min(max(reduction, 0.0), 0.995)
    return 1.0 - reduction


def peak_swelling_risk_index(
    water_load_g_m2: float,
    board_density_kg_m3: float = 650.0,
    thickness_mm: float = 16.0,
    barrier_factor: float = 0.0,
) -> float:
    """Dimensionless swelling risk proxy. Explicitly a surrogate, not measured."""
    if board_density_kg_m3 <= 0 or thickness_mm <= 0:
        raise ValueError("board density and thickness must be positive")
    water_volume_fraction = (water_load_g_m2 / 1000.0) / (board_density_kg_m3 * thickness_mm / 1000.0 * 1.0)
    return max(0.0, min(1.0, water_volume_fraction * (1.0 - 0.4 * barrier_factor)))


def drying_time_h(
    water_load_g_m2: float,
    evaporation_rate_factor: float = 1.0,
    temperature_c: float = 23.0,
    humidity_fraction: float = 0.5,
) -> float:
    if water_load_g_m2 < 0:
        raise ValueError("water load must be non-negative")
    base = water_load_g_m2 / 20.0
    factor = max(evaporation_rate_factor, 1e-9) * (1.0 + 0.03 * (temperature_c - 20.0)) * (1.0 - 0.3 * humidity_fraction)
    return max(base / factor, 0.01)

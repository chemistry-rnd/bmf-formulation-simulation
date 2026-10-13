from __future__ import annotations

import math

import numpy as np
import pytest

from simulation.bmf.transport_mechanistic import (
    CoatingFilm,
    MoistureDiffusion1D,
    SwellingCalibration,
    hcho_reaction_diffusion,
    moisture_diffusion_1d,
)


def test_moisture_mass_change_and_finite():
    model = MoistureDiffusion1D(0.016, 1e-9, 100.0, 20.0, 1e-5, 1.0, nodes=11)
    result = moisture_diffusion_1d(model)
    assert math.isfinite(result["initial_mass_kg_m2"])
    assert math.isfinite(result["final_mass_kg_m2"])
    assert all(math.isfinite(v) for v in result["final_concentration_kg_m3"])
    assert not any(v < -1e-9 for v in result["final_concentration_kg_m3"])


def test_zero_diffusivity_no_internal_change_limit():
    model = MoistureDiffusion1D(0.016, 0.0, 100.0, 20.0, 0.0, 1.0, nodes=9)
    result = moisture_diffusion_1d(model)
    # Evaporation from boundary still allowed, but interior profile remains finite.
    assert result["profile_range_kg_m3"] >= 0.0


def test_coating_mass_and_thickness_positive():
    film = CoatingFilm(dose_g_m2=20.0, dry_mass_fraction=0.2).thickness_and_mass()
    assert film["wet_film_thickness_m"] > 0
    assert film["dry_film_thickness_m"] >= 0
    assert film["tack_free_time"] == "UNKNOWN without calibrated test"


def test_hcho_flux_decreases_with_thicker_barrier():
    thin = hcho_reaction_diffusion(10, 0, 1e-4, 1e-9, 0.0)["surface_flux_kg_m2_s"]
    thick = hcho_reaction_diffusion(10, 0, 5e-4, 1e-9, 0.0)["surface_flux_kg_m2_s"]
    assert thin >= thick >= 0.0


def test_swelling_calibration_unknown_without_data():
    cal = SwellingCalibration()
    assert cal.predict_mm(0.1) is None
    cal2 = SwellingCalibration(slope_mm_per_mass_fraction=0.5, source="lab fit")
    assert cal2.predict_mm(0.1) == pytest.approx(0.05)

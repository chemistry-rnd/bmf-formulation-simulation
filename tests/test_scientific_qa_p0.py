from __future__ import annotations

import math

import numpy as np
import pytest

from simulation.bmf.chemistry import (
    PEI_GROUP_DISTRIBUTION_ASSUMPTIONS,
    PEI_NITROGEN_MASS_FRACTION,
    pei_group_capacity_g_m2,
)
from simulation.bmf.pipeline import _assumptions
from simulation.bmf.transport_mechanistic import (
    MoistureDiffusion1D,
    hcho_reaction_diffusion,
    moisture_diffusion_1d,
)


def test_pei_nitrogen_single_source():
    assert abs(PEI_NITROGEN_MASS_FRACTION - 0.3252) < 1e-12
    assumptions = _assumptions()
    stored = assumptions["supplier_and_material_assumptions"]["pei_nitrogen_mass_fraction"]
    assert abs(stored - PEI_NITROGEN_MASS_FRACTION) < 1e-12


def test_pei_group_defaults_sum_to_one():
    result = pei_group_capacity_g_m2(1.0)
    fractions = PEI_GROUP_DISTRIBUTION_ASSUMPTIONS
    assert abs(fractions["primary_amine_fraction_of_n"] + fractions["secondary_amine_fraction_of_n"] + fractions["tertiary_amine_fraction_of_n"] - 1.0) < 1e-12
    assert result["primary_amine_mmol_m2"] >= 0
    assert result["secondary_amine_mmol_m2"] >= 0
    assert result["tertiary_amine_mmol_m2"] >= 0


def test_pei_group_invalid_inputs_rejected():
    with pytest.raises(ValueError):
        pei_group_capacity_g_m2(1.0, primary_fraction=0.6, secondary_fraction=0.3, tertiary_fraction=0.2)
    with pytest.raises(ValueError):
        pei_group_capacity_g_m2(1.0, primary_fraction=-0.1, secondary_fraction=0.5, tertiary_fraction=0.6)


def test_moisture_mass_balance_quantitative():
    model = MoistureDiffusion1D(0.016, 1e-9, 100.0, 20.0, 1e-5, 0.5, nodes=13)
    result = moisture_diffusion_1d(model)
    assert abs(result["mass_balance_residual_kg_m2"]) <= 1e-2
    assert result["numerical_mass_conservation_ok"] is True
    assert abs(result["incoming_mass_kg_m2"]) >= 0.0


def test_hcho_flux_balance_and_zero_reaction():
    result = hcho_reaction_diffusion(10.0, 0.0, 1e-4, 1e-9, 0.0, 21)
    assert result["substrate_interface_flux_kg_m2_s"] >= 0.0
    assert result["ambient_emission_flux_kg_m2_s"] >= 0.0
    assert abs(result["mass_balance_residual_kg_m2_s"]) <= 1e-12
    assert abs(result["substrate_interface_flux_kg_m2_s"] - result["ambient_emission_flux_kg_m2_s"]) <= 1e-12

    reacted = hcho_reaction_diffusion(10.0, 0.0, 1e-4, 1e-9, 0.5, 21)
    assert reacted["substrate_interface_flux_kg_m2_s"] >= reacted["ambient_emission_flux_kg_m2_s"]
    assert abs(reacted["mass_balance_residual_kg_m2_s"]) <= 1e-2

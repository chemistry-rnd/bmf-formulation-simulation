from __future__ import annotations

from simulation.bmf.discovery import FunctionalStatus, build_candidate, stable_formula_id


def test_low_activity_candidate_rejected():
    low_pei = build_candidate("D-test", 0.4, 0.4, 13.9)
    assert low_pei["mass_balance_status"] == "VALID"
    assert low_pei["functional_status"] != "SCREEN_PASS"
    assert "residual HCHO" in low_pei["functional_reason"] or "threshold" in low_pei["functional_reason"] or "barrier" in low_pei["functional_reason"]


def test_e_candidates_pass_functional_screen():
    strong = build_candidate("E-test", 16.7, 29.6, 10.2)
    assert strong["mass_balance_status"] == "VALID"
    assert strong["functional_status"] == "SCREEN_PASS"


def test_functional_statuses_are_independent_of_mass_balance():
    invalid = build_candidate("invalid", 20.0, 30.0, 10.0)
    assert invalid["mass_balance_status"] == "INVALID"
    assert invalid["functional_status"] in {"SCREEN_FAIL", "UNKNOWN"}


def test_stable_formula_id_deterministic():
    a = build_candidate("a", 8.0, 12.0, 25.0)
    b = build_candidate("b", 8.0, 12.0, 25.0)
    assert stable_formula_id(a) == stable_formula_id(b)

"""通年エネルギー消費効率のテスト (ドキュメント 3 章「概要」)。"""

import pytest

from jis_c9612 import CoolingInput, compute_apf, compute_cooling, compute_heating


def test_apf(cooling_input, heating_input):
    r = compute_apf(cooling_input, heating_input)
    c, h = compute_cooling(cooling_input), compute_heating(heating_input)
    assert r.f_ap == pytest.approx((c.l_cst + h.l_hst) / (c.c_cse + h.c_hse))
    assert r.annual_energy == pytest.approx(c.c_cse + h.c_hse)


def test_rated_capacity_must_match(heating_input):
    other = CoolingInput(phi_c_ful_t100=2500.0, phi_c_ful_35=2500.0, p_c_ful_35=600.0, phi_c_haf_35=1250.0, p_c_haf_35=250.0)
    with pytest.raises(ValueError):
        compute_apf(other, heating_input)

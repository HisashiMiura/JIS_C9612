"""冷房期間の計算のテスト (ドキュメント 3 章「冷房期間」)。"""

import pytest

from conftest import PHI_C_FUL_T100, bisect_root
from jis_c9612 import CoolingInput, compute_cooling
from jis_c9612.climate import TOKYO_COOLING_HOURS
from jis_c9612.cooling import CoolingCharacteristics, CoolingState, _cooling_load, _crossing_temperature


def test_tokyo_hours_total():
    assert sum(TOKYO_COOLING_HOURS.values()) == 1569


def test_coefficients_at_29(cooling_input):
    ch = CoolingCharacteristics._from_input(cooling_input)
    assert ch.phi_c_ful(29) == pytest.approx(1.077 * 2800)
    assert ch.p_c_ful(29) == pytest.approx(0.914 * 700)
    assert ch.phi_c_haf(29) == pytest.approx(1.077 * 1400)
    assert ch.p_c_haf(29) == pytest.approx(0.914 * 280)


def test_load_line():
    assert _cooling_load(PHI_C_FUL_T100, 23) == 0
    assert _cooling_load(PHI_C_FUL_T100, 35) == pytest.approx(PHI_C_FUL_T100)


def test_crossing_temperature_matches_root(cooling_input):
    """閉じた式 [eq-c-tb] [eq-c-tc] が、負荷線と能力線の交点と一致する。"""
    ch = CoolingCharacteristics._from_input(cooling_input)
    for cap in (ch.phi_c_ful, ch.phi_c_haf):
        t = _crossing_temperature(PHI_C_FUL_T100, cap)
        root = bisect_root(lambda x: _cooling_load(PHI_C_FUL_T100, x) - cap(x), 20, 45)
        assert t == pytest.approx(root, abs=1e-9)


def test_crossing_temperature_example(cooling_input):
    r = compute_cooling(cooling_input)
    assert r.t_c == pytest.approx(29.43, abs=0.005)
    assert r.t_b == pytest.approx(35.00, abs=0.005)
    assert r.eer_haf_t_c == pytest.approx(5.822, abs=0.0005)
    assert r.eer_ful_t_b == pytest.approx(4.000, abs=0.0005)


# 図 2 (外気温度と消費電力の関係) の各温度区分の値 (W)
EXPECTED_POWER = {
    24: 43.8, 25: 86.0, 26: 126.8, 27: 166.3, 28: 204.7, 29: 241.9, 30: 289.8, 31: 351.6,
    32: 421.6, 33: 501.3, 34: 593.2, 35: 700.0, 36: 710.0, 37: 720.1, 38: 730.1,
}


def test_power_per_bin(cooling_input):
    r = compute_cooling(cooling_input)
    for b in r.bins:
        assert b.p_c == pytest.approx(EXPECTED_POWER[b.t_j], abs=0.05), b.t_j


def test_states(cooling_input):
    r = compute_cooling(cooling_input)
    states = {b.t_j: b.state for b in r.bins}
    assert all(states[t] is CoolingState.INTERMITTENT for t in range(24, 30))
    assert all(states[t] is CoolingState.VARIABLE for t in range(30, 36))
    assert all(states[t] is CoolingState.RATED for t in range(36, 39))


def test_intermittent_example_26c(cooling_input):
    """3 章「断続運転」の数値例 (外気 26 ℃)。"""
    b = next(b for b in compute_cooling(cooling_input).bins if b.t_j == 26)
    assert b.l_c == pytest.approx(700.0)
    assert b.x_c == pytest.approx(0.448, abs=0.0005)
    assert b.f_c_pl == pytest.approx(0.862, abs=0.0005)
    assert b.p_c == pytest.approx(126.8, abs=0.05)


def test_processed_load_is_capped_by_rated_capacity(cooling_input):
    """定格運転では処理する空調負荷が定格運転能力になる [eq-c-l]。"""
    r = compute_cooling(cooling_input)
    ch = CoolingCharacteristics._from_input(cooling_input)
    for b in r.bins:
        assert b.q_c == pytest.approx(min(b.l_c, ch.phi_c_ful(b.t_j)))


def test_power_continuous_at_crossings(cooling_input):
    """消費電力は交点温度で連続になる (断続 ↔ 可変、可変 ↔ 定格)。"""
    hours = {29.43: 1.0, 29.4301: 1.0, 34.9999: 1.0, 35.0001: 1.0}
    r = compute_cooling(cooling_input, hours)
    p = [b.p_c for b in r.bins]
    assert p[0] == pytest.approx(p[1], rel=1e-3)
    assert p[2] == pytest.approx(p[3], rel=1e-3)


def test_totals(cooling_input):
    r = compute_cooling(cooling_input)
    ch = CoolingCharacteristics._from_input(cooling_input)
    l_cst = sum(min(_cooling_load(PHI_C_FUL_T100, t), ch.phi_c_ful(t)) * n for t, n in TOKYO_COOLING_HOURS.items())
    c_cse = sum(EXPECTED_POWER[t] * n for t, n in TOKYO_COOLING_HOURS.items())
    assert r.l_cst == pytest.approx(l_cst)
    assert r.c_cse == pytest.approx(c_cse, abs=0.05 * 1569)
    assert r.f_csp == pytest.approx(r.l_cst / r.c_cse)


@pytest.mark.parametrize("field", ["phi_c_ful_t100", "phi_c_ful_35", "p_c_ful_35", "phi_c_haf_35", "p_c_haf_35"])
def test_input_must_be_positive(field):
    values = dict(phi_c_ful_t100=2800.0, phi_c_ful_35=2800.0, p_c_ful_35=700.0, phi_c_haf_35=1400.0, p_c_haf_35=280.0)
    values[field] = 0.0
    with pytest.raises(ValueError):
        CoolingInput(**values)

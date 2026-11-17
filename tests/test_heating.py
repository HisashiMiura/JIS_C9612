"""暖房期間の計算のテスト (ドキュメント 3 章「暖房期間」)。"""

import pytest

from conftest import PHI_C_FUL_T100, bisect_root
from jis_c9612 import HeatingInput, compute_heating
from jis_c9612.climate import TOKYO_HEATING_HOURS
from jis_c9612.heating import (
    HeatingCharacteristics,
    HeatingState,
    _crossing_temperature,
    _heating_load,
    _is_frost,
)


def test_tokyo_hours_total():
    assert sum(TOKYO_HEATING_HOURS.values()) == 2707


def test_frost_region():
    assert not _is_frost(-7)
    assert _is_frost(-6)
    assert _is_frost(5)
    assert not _is_frost(5.5)
    assert not _is_frost(6)


def test_load_line():
    assert _heating_load(PHI_C_FUL_T100, 17) == 0
    assert _heating_load(PHI_C_FUL_T100, 0) == pytest.approx(0.82 * 1.25 * PHI_C_FUL_T100)


def test_test_value_completion(heating_input):
    """3 章「試験値の補完」の係数。"""
    ch = HeatingCharacteristics._from_input(heating_input)
    nf, fr = ch.nonfrost, ch.frost
    assert nf.ful.phi(-7) == pytest.approx(0.64 * 3600)
    assert nf.ful.p(-7) == pytest.approx(0.82 * 900)
    assert nf.haf.phi(-7) == pytest.approx(0.64 * 1800)
    assert nf.ext.phi(2) == pytest.approx(1.12 * 4200)
    assert nf.ext.p(2) == pytest.approx(1.06 * 1500)
    assert nf.ext.phi(-7) == pytest.approx(0.734 * 1.12 * 4200)
    assert nf.ext.p(-7) == pytest.approx(0.877 * 1.06 * 1500)
    # 着霜時: 2 ℃の無着霜時の値を 1.12 / 1.06 で割る
    assert fr.ful.phi(2) == pytest.approx(nf.ful.phi(2) / 1.12)
    assert fr.ful.p(2) == pytest.approx(nf.ful.p(2) / 1.06)
    assert fr.haf.phi(2) == pytest.approx(nf.haf.phi(2) / 1.12)
    assert fr.ext.phi(2) == pytest.approx(4200)
    # −7 ℃では着霜時の線も無着霜時の値を通る
    for op in ("ful", "haf", "ext"):
        assert getattr(fr, op).phi(-7) == pytest.approx(getattr(nf, op).phi(-7))


def test_crossing_temperatures_match_root(heating_input):
    """閉じた式 [eq-h-a] など が、負荷線と能力線の交点と一致する。"""
    ch = HeatingCharacteristics._from_input(heating_input)
    for rc in (ch.nonfrost, ch.frost):
        for op in (rc.ful, rc.haf, rc.ext):
            t = _crossing_temperature(PHI_C_FUL_T100, op.phi)
            root = bisect_root(lambda x: _heating_load(PHI_C_FUL_T100, x) - op.phi(x), -30, 30)
            assert t == pytest.approx(root, abs=1e-9)


def test_crossing_temperatures_example(heating_input):
    r = compute_heating(heating_input)
    assert r.nonfrost.t_haf == pytest.approx(6.48, abs=0.005)  # t_d
    assert r.nonfrost.t_ful == pytest.approx(-0.31, abs=0.005)  # t_a
    assert r.nonfrost.t_ext == pytest.approx(-5.05, abs=0.005)  # t_h
    assert r.frost.t_haf == pytest.approx(7.76, abs=0.005)  # t_e
    assert r.frost.t_ful == pytest.approx(0.80, abs=0.005)  # t_g
    assert r.frost.t_ext == pytest.approx(-4.62, abs=0.005)  # t_f


# 暖房の試算 (図 6 の値) の各温度区分の値: (運転状態, 消費電力 W)
EXPECTED = {
    -7: (HeatingState.MAX, 1993.5), -6: (HeatingState.MAX, 1753.3), -5: (HeatingState.MAX, 1513.2),
    -4: (HeatingState.FUL_EXT, 1327.6), -3: (HeatingState.FUL_EXT, 1189.7), -2: (HeatingState.FUL_EXT, 1067.2),
    -1: (HeatingState.FUL_EXT, 957.6), 0: (HeatingState.FUL_EXT, 859.0),
    1: (HeatingState.HAF_FUL, 769.6), 2: (HeatingState.HAF_FUL, 687.2), 3: (HeatingState.HAF_FUL, 612.3),
    4: (HeatingState.HAF_FUL, 543.9), 5: (HeatingState.HAF_FUL, 481.2), 6: (HeatingState.HAF_FUL, 381.4),
    7: (HeatingState.INTERMITTENT, 343.0), 8: (HeatingState.INTERMITTENT, 314.0), 9: (HeatingState.INTERMITTENT, 283.8),
    10: (HeatingState.INTERMITTENT, 252.5), 11: (HeatingState.INTERMITTENT, 220.1), 12: (HeatingState.INTERMITTENT, 186.5),
    13: (HeatingState.INTERMITTENT, 151.6), 14: (HeatingState.INTERMITTENT, 115.6), 15: (HeatingState.INTERMITTENT, 78.3),
    16: (HeatingState.INTERMITTENT, 39.8),
}


def test_states_and_power_per_bin(heating_input):
    hours = {t: 1.0 for t in EXPECTED}
    r = compute_heating(heating_input, hours)
    for b in r.bins:
        state, power = EXPECTED[b.t_j]
        assert b.state is state, b.t_j
        assert b.p_h == pytest.approx(power, abs=0.05), b.t_j


def test_auxiliary_heater(heating_input):
    """最大運転では不足分を補助電熱装置で補い、負荷は全量処理される [eq-h-q] [eq-h-prh]。"""
    ch = HeatingCharacteristics._from_input(heating_input)
    r = compute_heating(heating_input, {-7: 1.0, -6: 1.0, 10: 1.0})
    for b in r.bins:
        assert b.q_h == b.l_h
        if b.state is HeatingState.MAX:
            rc = ch.frost if b.frost else ch.nonfrost
            assert b.p_h_rh == pytest.approx(b.l_h - rc.ext.phi(b.t_j))
            assert b.p_h == pytest.approx(rc.ext.p(b.t_j) + b.p_h_rh)
        else:
            assert b.p_h_rh == 0.0


def test_totals_tokyo(heating_input):
    """東京の発生時間での期間合計 (暖房の試算の値)。"""
    r = compute_heating(heating_input)
    assert r.l_hst == pytest.approx(3_547_320, abs=1)
    assert r.c_hse == pytest.approx(782_045, abs=1)
    assert r.f_hsp == pytest.approx(4.54, abs=0.005)
    # 東京の発生時間では補助電熱装置の電力は加わらない
    assert sum(b.p_h_rh * b.n_h_j for b in r.bins) == 0


def test_no_max_mode_uses_rated_as_max(heating_input):
    """最大モードをもたない機種: 最大運転 = 定格運転 (4 章「最大モードをもたない機種 (暫定)」)。"""
    inp = HeatingInput(
        phi_c_ful_t100=PHI_C_FUL_T100, phi_h_ful_7=3600.0, p_h_ful_7=900.0, phi_h_haf_7=1800.0, p_h_haf_7=360.0,
        phi_h_ful_f_2=2700.0, p_h_ful_f_2=800.0,
    )
    ch = HeatingCharacteristics._from_input(inp)
    assert ch.nonfrost.ext is ch.nonfrost.ful
    assert ch.frost.ext is ch.frost.ful
    assert ch.frost.ful.phi(2) == pytest.approx(2700.0)
    r = compute_heating(inp, {t: 1.0 for t in range(-14, 17)})
    assert all(b.state is not HeatingState.FUL_EXT for b in r.bins)


@pytest.mark.parametrize(
    "extra",
    [
        {},  # どちらもない
        {"phi_h_ext_f_2": 4200.0, "p_h_ext_f_2": 1500.0, "phi_h_ful_f_2": 2700.0, "p_h_ful_f_2": 800.0},  # 両方ある
        {"phi_h_ext_f_2": 4200.0},  # 片方だけ
    ],
)
def test_input_requires_exactly_one_2c_test(extra):
    with pytest.raises(ValueError):
        HeatingInput(phi_c_ful_t100=PHI_C_FUL_T100, phi_h_ful_7=3600.0, p_h_ful_7=900.0, phi_h_haf_7=1800.0, p_h_haf_7=360.0, **extra)

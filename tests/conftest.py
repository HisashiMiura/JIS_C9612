"""テストで共通に使う入力値。

ドキュメント 3 章の図の例と同じ値である (docs/figures/make_figures.py)。
"""

import pytest

from jis_c9612 import CoolingInput, HeatingInput

PHI_C_FUL_T100 = 2800.0


@pytest.fixture
def cooling_input() -> CoolingInput:
    return CoolingInput(phi_c_ful_t100=PHI_C_FUL_T100, phi_c_ful_35=2800.0, p_c_ful_35=700.0, phi_c_haf_35=1400.0, p_c_haf_35=280.0)


@pytest.fixture
def heating_input() -> HeatingInput:
    return HeatingInput(
        phi_c_ful_t100=PHI_C_FUL_T100, phi_h_ful_7=3600.0, p_h_ful_7=900.0, phi_h_haf_7=1800.0, p_h_haf_7=360.0,
        phi_h_ext_f_2=4200.0, p_h_ext_f_2=1500.0,
    )


def bisect_root(f, lo: float, hi: float) -> float:
    """f(t) = 0 の根を二分法で求める (閉じた式の検算用)。"""
    flo = f(lo)
    for _ in range(200):
        mid = (lo + hi) / 2
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2

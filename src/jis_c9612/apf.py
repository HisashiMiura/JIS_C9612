"""通年エネルギー消費効率 (ドキュメント 3 章「概要」、附属書 B の B.3)。"""

from dataclasses import dataclass

from .cooling import CoolingResult, compute_cooling
from .heating import HeatingResult, compute_heating
from .inputs import CoolingInput, HeatingInput


@dataclass(frozen=True)
class AnnualResult:
    """通年の計算結果。

    Attributes:
        f_ap: 通年エネルギー消費効率 F_AP (−)
        cooling: 冷房期間の計算結果
        heating: 暖房期間の計算結果
    """

    f_ap: float
    cooling: CoolingResult
    heating: HeatingResult

    @property
    def annual_energy(self) -> float:
        """期間消費電力量 (AEC)。

        Returns:
            冷房期間消費電力量と暖房期間消費電力量の和 C_CSE + C_HSE (Wh)

        Note:
            附属書 B の B.3.3.5 の定義による。
        """
        # 冷房期間消費電力量と暖房期間消費電力量を足す
        return self.cooling.c_cse + self.heating.c_hse


def compute_apf(
    cooling: CoolingInput,
    heating: HeatingInput,
    n_c_j: dict[float, float] | None = None,
    n_h_j: dict[float, float] | None = None,
) -> AnnualResult:
    """通年エネルギー消費効率を求める。

    Args:
        cooling: 冷房期間の入力値
        heating: 暖房期間の入力値
        n_c_j: 冷房期間の外気温度 t_j (℃)と発生時間 n_c,j (h)。省略すると東京の値
        n_h_j: 暖房期間の外気温度 t_j (℃)と発生時間 n_h,j (h)。省略すると東京の値

    Returns:
        通年の計算結果

    Raises:
        ValueError: 冷房と暖房で定格冷房能力 (表示値) が異なる場合。
            そのほか compute_cooling、compute_heating が出すエラー

    Note:
        3 章 式 (1)。
    """
    # 冷房と暖房で同じ機種の値であることを、定格冷房能力 (表示値) が一致するかで確かめる
    if cooling.phi_c_ful_t100 != heating.phi_c_ful_t100:

        raise ValueError("冷房と暖房で定格冷房能力 (表示値) が異なる")

    # 冷房期間と暖房期間をそれぞれ計算する
    c = compute_cooling(cooling, n_c_j)
    h = compute_heating(heating, n_h_j)

    # 両期間の空調負荷の合計を、消費電力量の合計で割る (式 (1))
    f_ap = (c.l_cst + h.l_hst) / (c.c_cse + h.c_hse)
    return AnnualResult(f_ap, c, h)

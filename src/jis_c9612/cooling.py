"""冷房期間の計算 (ドキュメント 3 章「冷房期間」、附属書 B の B.1)。

docstring とコメントの「式 (n)」は、ドキュメント 3 章「評価方法」の式番号である。
変数名は 3 章・5 章の記号に合わせている (例: n_c,j → n_c_j、F_c,PL → f_c_pl)。
"""

from dataclasses import dataclass, field
from enum import Enum

from . import coefficients as k
from .climate import TOKYO_COOLING_HOURS
from .inputs import CoolingInput
from .lines import Line


class CoolingState(Enum):
    """冷房の運転状態。

    Note:
        3 章 式 (6) の場合分けに対応する。
    """

    INTERMITTENT = "断続運転"
    VARIABLE = "可変運転"
    RATED = "定格運転"


@dataclass(frozen=True)
class CoolingCharacteristics:
    """冷房の能力・消費電力の特性線。

    Attributes:
        phi_c_ful: 定格運転能力 Φ_c,ful(t) (W)
        p_c_ful: 定格運転消費電力 P_c,ful(t) (W)
        phi_c_haf: 中間運転能力 Φ_c,haf(t) (W)
        p_c_haf: 中間運転消費電力 P_c,haf(t) (W)

    Note:
        3 章「能力・消費電力の特性」の式 (18), (19), (20), (21)。
    """

    phi_c_ful: Line
    p_c_ful: Line
    phi_c_haf: Line
    p_c_haf: Line

    @classmethod
    def _from_input(cls, inp: CoolingInput) -> "CoolingCharacteristics":
        """入力値から特性線を作る。

        外気 29 ℃の値を係数で求め、35 ℃と 29 ℃の 2 点を結ぶ。

        Args:
            inp: 冷房期間の入力値

        Returns:
            冷房の能力・消費電力の特性線

        Note:
            29 ℃の値を 3 章「試験値の補完」の式 (22), (23), (24), (25) で求め、
            3 章「能力・消費電力の特性」の式 (18), (19), (20), (21) の特性線を作る。
            特性線の値は、返した特性線に外気温度を与えて呼び出したときに求まる。
        """
        # 外気 29 ℃の定格運転能力・消費電力を、35 ℃の試験値に係数を掛けて求める (式 (22), (23))
        phi_c_ful_29 = k.COOLING_CAP_29 * inp.phi_c_ful_35
        p_c_ful_29 = k.COOLING_POW_29 * inp.p_c_ful_35

        # 外気 29 ℃の中間運転能力・消費電力を、35 ℃の試験値に係数を掛けて求める (式 (24), (25))
        phi_c_haf_29 = k.COOLING_CAP_29 * inp.phi_c_haf_35
        p_c_haf_29 = k.COOLING_POW_29 * inp.p_c_haf_35

        # 35 ℃と 29 ℃の 2 点を結んで、定格運転・中間運転の特性線を作る (式 (18), (19), (20), (21))
        return cls(
            phi_c_ful=Line(35.0, inp.phi_c_ful_35, 29.0, phi_c_ful_29),
            p_c_ful=Line(35.0, inp.p_c_ful_35, 29.0, p_c_ful_29),
            phi_c_haf=Line(35.0, inp.phi_c_haf_35, 29.0, phi_c_haf_29),
            p_c_haf=Line(35.0, inp.p_c_haf_35, 29.0, p_c_haf_29),
        )


def _cooling_load(phi_c_ful_t100: float, t: float) -> float:
    """想定冷房空調負荷 L_c(t) を求める。

    Args:
        phi_c_ful_t100: 定格冷房能力 (表示値) Φ_c,ful,t100 (W)
        t: 外気温度 (℃)

    Returns:
        外気温度 t における想定冷房空調負荷 L_c(t) (W)

    Note:
        3 章 式 (17)。
    """
    # 23 ℃で 0、35 ℃で定格冷房能力となる直線の値を求める (式 (17))
    return phi_c_ful_t100 * (t - k.T_C_0) / (k.T_C_100 - k.T_C_0)


def _crossing_temperature(phi_c_ful_t100: float, phi: Line) -> float:
    """想定冷房空調負荷と能力線が等しくなる外気温度を求める。

    Args:
        phi_c_ful_t100: 定格冷房能力 (表示値) Φ_c,ful,t100 (W)
        phi: 外気 35 ℃と 29 ℃の 2 点で定めた能力線 Φ_c,ful(t) または Φ_c,haf(t)

    Returns:
        交点温度 (℃)。phi が定格運転能力なら t_b、中間運転能力なら t_c

    Raises:
        ValueError: 負荷線と能力線が平行で、交点温度が求まらない場合

    Note:
        3 章 式 (15), (16)。式 (13), (14) の関係を外気温度について解いたもの。
    """
    # 能力線の 35 ℃と 29 ℃の値、負荷線の両端の温度 t_c,0、t_c,100 を取り出す
    phi_35, phi_29 = phi(35.0), phi(29.0)
    t_c_0, t_c_100 = k.T_C_0, k.T_C_100

    # 分母を求める。0 なら負荷線と能力線が平行で、交点がない
    d = (phi_29 - phi_35) * (t_c_100 - t_c_0)
    den = 6 * phi_c_ful_t100 + d
    if den == 0:

        raise ValueError("想定冷房空調負荷と能力線が平行で、交点温度が求まらない")

    # 交点温度を求める (式 (15), (16))
    return (6 * phi_c_ful_t100 * t_c_0 + 6 * phi_35 * (t_c_100 - t_c_0) + 35 * d) / den


@dataclass(frozen=True)
class CoolingBin:
    """冷房の温度区分ごとの計算結果。

    Attributes:
        t_j: 外気温度 t_j (℃)
        n_c_j: 発生時間 n_c,j (h)
        state: 運転状態
        l_c: 想定冷房空調負荷 L_c(t_j) (W)
        q_c: 処理する空調負荷 Q_c(t_j) (W)
        p_c: 消費電力 P_c(t_j) (W)
        x_c: 運転率 X_c(t_j) (−)。断続運転のときだけ値をもつ。
        f_c_pl: 部分負荷率 F_c,PL(t_j) (−)。断続運転のときだけ値をもつ。
        eer_hf: 可変運転のエネルギー消費効率 EER_hf(t_j) (−)。可変運転のときだけ値をもつ。

    Note:
        3 章 式 (5), (6) の 1 つの温度区分の値である。
    """

    t_j: float
    n_c_j: float
    state: CoolingState
    l_c: float
    q_c: float
    p_c: float
    x_c: float | None = None
    f_c_pl: float | None = None
    eer_hf: float | None = None


@dataclass(frozen=True)
class CoolingResult:
    """冷房期間の計算結果。

    Attributes:
        l_cst: 冷房期間総合空調負荷 L_CST (Wh)
        c_cse: 冷房期間消費電力量 C_CSE (Wh)
        f_csp: 冷房期間エネルギー消費効率 F_CSP (−)
        t_b: 想定冷房空調負荷と定格運転能力が等しくなる外気温度 t_b (℃)
        t_c: 想定冷房空調負荷と中間運転能力が等しくなる外気温度 t_c (℃)
        eer_ful_t_b: 交点温度 t_b における定格運転のエネルギー消費効率 EER_ful(t_b) (−)
        eer_haf_t_c: 交点温度 t_c における中間運転のエネルギー消費効率 EER_haf(t_c) (−)
        bins: 温度区分ごとの計算結果。外気温度の低い順
    """

    l_cst: float
    c_cse: float
    f_csp: float
    t_b: float
    t_c: float
    eer_ful_t_b: float
    eer_haf_t_c: float
    bins: list[CoolingBin] = field(default_factory=list)


def compute_cooling(inp: CoolingInput, n_c_j: dict[float, float] | None = None) -> CoolingResult:
    """冷房期間エネルギー消費効率などを求める。

    Args:
        inp: 冷房期間の入力値
        n_c_j: 外気温度 t_j (℃)をキー、発生時間 n_c,j (h)を値とする辞書。
            省略すると東京の値 (附属書 B の表 B.3) を用いる。

    Returns:
        冷房期間の計算結果

    Raises:
        ValueError: 交点温度が求まらない場合、または t_c < t_b を満たさない場合

    Note:
        3 章「冷房期間」の式 (2), (3), (4), (5), (6), (7), (8), (9), (10), (11), (12) による。
        負荷 0 %の外気温度 (23 ℃)以下の温度区分は、負荷も消費電力も 0 とする
        (東京の表 B.3 にはない。DESIGN.md「設計方針」)。
    """
    # 発生時間が与えられなければ、東京の値を用いる
    n_c_j = TOKYO_COOLING_HOURS if n_c_j is None else n_c_j

    # 試験値を補完し、能力・消費電力の特性線を作る (式 (18)〜(25))
    ch = CoolingCharacteristics._from_input(inp)

    # 想定冷房空調負荷が定格運転能力・中間運転能力と等しくなる交点温度を求める (式 (15), (16))
    t_b = _crossing_temperature(inp.phi_c_ful_t100, ch.phi_c_ful)
    t_c = _crossing_temperature(inp.phi_c_ful_t100, ch.phi_c_haf)

    # 可変運転の範囲 (t_c から t_b まで) が成り立つことを確かめる
    if not t_c < t_b:

        raise ValueError(f"交点温度が t_c < t_b を満たさない (t_c = {t_c}, t_b = {t_b})")

    # 交点温度でのエネルギー消費効率を求める。可変運転の EER の補間の両端になる (式 (11), (12))
    eer_haf_t_c = ch.phi_c_haf(t_c) / ch.p_c_haf(t_c)
    eer_ful_t_b = ch.phi_c_ful(t_b) / ch.p_c_ful(t_b)

    # 温度区分ごとに、運転状態を判定して空調負荷と消費電力を求める (式 (5), (6))
    bins: list[CoolingBin] = []
    for t_j in sorted(n_c_j):

        # この温度区分の想定冷房空調負荷を求める (式 (17))
        l_c = _cooling_load(inp.phi_c_ful_t100, t_j)

        # 負荷 0 %の外気温度以下では、負荷も消費電力も 0 とする (東京の発生時間にはない)
        if l_c <= 0:

            bins.append(CoolingBin(t_j, n_c_j[t_j], CoolingState.INTERMITTENT, l_c, 0.0, 0.0, x_c=0.0))
            continue

        # この温度区分の中間運転能力と定格運転能力を求める (式 (18), (20))
        phi_c_haf, phi_c_ful = ch.phi_c_haf(t_j), ch.phi_c_ful(t_j)

        if l_c <= phi_c_haf:

            # 断続運転: 運転率と部分負荷率を求める (式 (8), (7))
            x_c = l_c / phi_c_haf
            f_c_pl = 1 - k.C_C_D * (1 - x_c)

            # 断続運転: 運転率の分だけ中間運転し、部分負荷率で効率の低下を補正する (式 (6))
            p_c = x_c * ch.p_c_haf(t_j) / f_c_pl
            bins.append(
                CoolingBin(t_j, n_c_j[t_j], CoolingState.INTERMITTENT, l_c, l_c, p_c, x_c=x_c, f_c_pl=f_c_pl)
            )

        elif l_c <= phi_c_ful:

            # 可変運転: 交点温度の間で EER を直線補間する (式 (10))
            eer_hf = eer_haf_t_c + (eer_ful_t_b - eer_haf_t_c) / (t_b - t_c) * (t_j - t_c)

            # 可変運転: 想定冷房空調負荷を EER で割って消費電力を求める (式 (9))
            p_c = l_c / eer_hf
            bins.append(CoolingBin(t_j, n_c_j[t_j], CoolingState.VARIABLE, l_c, l_c, p_c, eer_hf=eer_hf))

        else:

            # 定格運転: 処理する空調負荷は定格運転能力、消費電力は定格運転消費電力とする (式 (5), (6))
            bins.append(CoolingBin(t_j, n_c_j[t_j], CoolingState.RATED, l_c, phi_c_ful, ch.p_c_ful(t_j)))

    # 温度区分ごとの値に発生時間を掛けて合計する (式 (3), (4))
    l_cst = sum(b.q_c * b.n_c_j for b in bins)
    c_cse = sum(b.p_c * b.n_c_j for b in bins)

    # 冷房期間エネルギー消費効率を求めて、結果をまとめる (式 (2))
    return CoolingResult(l_cst, c_cse, l_cst / c_cse, t_b, t_c, eer_ful_t_b, eer_haf_t_c, bins)

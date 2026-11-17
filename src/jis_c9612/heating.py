"""暖房期間の計算 (ドキュメント 3 章「暖房期間」、附属書 B の B.2)。

docstring とコメントの「式 (n)」は、ドキュメント 3 章「評価方法」の式番号である。
変数名は 3 章・5 章の記号に合わせている (例: n_h,j → n_h_j、P_h,RH → p_h_rh)。着霜時の値は添字 f (変数名の _f) で表す。
"""

from dataclasses import dataclass, field
from enum import Enum

from . import coefficients as k
from .climate import TOKYO_HEATING_HOURS
from .inputs import HeatingInput
from .lines import Line


class HeatingState(Enum):
    """暖房の運転状態。

    Note:
        3 章 式 (30), (31) の場合分けに対応する。
    """

    INTERMITTENT = "断続運転"
    HAF_FUL = "中間〜定格の可変運転"
    FUL_EXT = "定格〜最大の可変運転"
    MAX = "最大運転"


@dataclass(frozen=True)
class OperationLines:
    """1 つの運転 (定格・中間・最大) の能力線と消費電力線。

    Attributes:
        phi: 運転能力の特性線 Φ_h,x(t) または Φ_h,x,f(t) (W)
        p: 運転消費電力の特性線 P_h,x(t) または P_h,x,f(t) (W)
    """

    phi: Line
    p: Line


@dataclass(frozen=True)
class RegionCharacteristics:
    """無着霜時または着霜時の特性線。

    Attributes:
        ful: 定格運転の特性線
        haf: 中間運転の特性線
        ext: 最大運転の特性線
    """

    ful: OperationLines
    haf: OperationLines
    ext: OperationLines


@dataclass(frozen=True)
class HeatingCharacteristics:
    """暖房の能力・消費電力の特性線。

    Attributes:
        nonfrost: 無着霜時の特性線
        frost: 着霜時の特性線

    Note:
        3 章「能力・消費電力の特性」の式 (65)〜(76)。
    """

    nonfrost: RegionCharacteristics
    frost: RegionCharacteristics

    @classmethod
    def _from_input(cls, inp: HeatingInput) -> "HeatingCharacteristics":
        """入力値から特性線を作る。

        試験を行わない外気 −7 ℃、2 ℃の値を係数で求め、2 点を結ぶ。
        最大モードをもたない機種では、最大運転の特性線に定格運転の特性線を用いる。

        Args:
            inp: 暖房期間の入力値

        Returns:
            暖房の能力・消費電力の特性線

        Note:
            試験を行わない値を 3 章「試験値の補完」の式 (77)〜(92) で求め、
            3 章「能力・消費電力の特性」の式 (65)〜(76) の特性線を作る。
            式 (77), (78) は最大モードをもつ機種だけに用いる。
            特性線の値は、返した特性線に外気温度を与えて呼び出したときに求まる。
            最大モードをもたない機種の扱いは 4 章「最大モードをもたない機種 (暫定)」による。
        """
        # 外気 −7 ℃の定格運転・中間運転の能力と消費電力を、7 ℃の試験値に係数を掛けて求める (式 (85)〜(88))
        phi_h_ful_m7 = k.HEATING_CAP_M7 * inp.phi_h_ful_7
        p_h_ful_m7 = k.HEATING_POW_M7 * inp.p_h_ful_7
        phi_h_haf_m7 = k.HEATING_CAP_M7 * inp.phi_h_haf_7
        p_h_haf_m7 = k.HEATING_POW_M7 * inp.p_h_haf_7

        def at_2(v_m7: float, v_7: float) -> float:
            # 外気 2 ℃の無着霜時の値を、−7 ℃と 7 ℃の値の直線補間で求める (式 (81)〜(84))
            return v_m7 + (v_7 - v_m7) / (7 - (-7)) * (2 - (-7))

        # 無着霜時の定格運転・中間運転の特性線を、−7 ℃と 7 ℃の 2 点を結んで作る (式 (65)〜(68))
        ful = OperationLines(Line(-7.0, phi_h_ful_m7, 7.0, inp.phi_h_ful_7), Line(-7.0, p_h_ful_m7, 7.0, inp.p_h_ful_7))
        haf = OperationLines(Line(-7.0, phi_h_haf_m7, 7.0, inp.phi_h_haf_7), Line(-7.0, p_h_haf_m7, 7.0, inp.p_h_haf_7))

        # 外気 2 ℃の着霜時の中間運転の値を、無着霜時の値を係数で割って求める (式 (79), (80))
        phi_h_haf_f_2 = at_2(phi_h_haf_m7, inp.phi_h_haf_7) / k.HEATING_CAP_FROST
        p_h_haf_f_2 = at_2(p_h_haf_m7, inp.p_h_haf_7) / k.HEATING_POW_FROST

        # 着霜時の中間運転の特性線を、−7 ℃と 2 ℃の 2 点を結んで作る (式 (73), (74))
        haf_f = OperationLines(Line(-7.0, phi_h_haf_m7, 2.0, phi_h_haf_f_2), Line(-7.0, p_h_haf_m7, 2.0, p_h_haf_f_2))

        # 外気 2 ℃の着霜時の定格運転の値を決める
        if inp.has_max_mode:

            # 最大モードをもつ機種: 無着霜時の値を係数で割って求める (式 (77), (78))
            phi_h_ful_f_2 = at_2(phi_h_ful_m7, inp.phi_h_ful_7) / k.HEATING_CAP_FROST
            p_h_ful_f_2 = at_2(p_h_ful_m7, inp.p_h_ful_7) / k.HEATING_POW_FROST

        else:

            # 最大モードをもたない機種: 試験値 (入力値) をそのまま用いる
            phi_h_ful_f_2, p_h_ful_f_2 = inp.phi_h_ful_f_2, inp.p_h_ful_f_2

        # 着霜時の定格運転の特性線を、−7 ℃と 2 ℃の 2 点を結んで作る (式 (71), (72))
        ful_f = OperationLines(Line(-7.0, phi_h_ful_m7, 2.0, phi_h_ful_f_2), Line(-7.0, p_h_ful_m7, 2.0, p_h_ful_f_2))

        # 最大運転の特性線を作る
        if inp.has_max_mode:

            # 外気 2 ℃の無着霜時の最大運転の値を、着霜時の試験値に係数を掛けて求める (式 (91), (92))
            phi_h_ext_2 = k.HEATING_CAP_FROST * inp.phi_h_ext_f_2
            p_h_ext_2 = k.HEATING_POW_FROST * inp.p_h_ext_f_2

            # 外気 −7 ℃の最大運転の値を、2 ℃の無着霜時の値に係数を掛けて求める (式 (89), (90))
            phi_h_ext_m7 = k.HEATING_CAP_M7_EXT * phi_h_ext_2
            p_h_ext_m7 = k.HEATING_POW_M7_EXT * p_h_ext_2

            # 無着霜時・着霜時の最大運転の特性線を、−7 ℃と 2 ℃の 2 点を結んで作る (式 (69), (70), (75), (76))
            ext = OperationLines(Line(-7.0, phi_h_ext_m7, 2.0, phi_h_ext_2), Line(-7.0, p_h_ext_m7, 2.0, p_h_ext_2))
            ext_f = OperationLines(
                Line(-7.0, phi_h_ext_m7, 2.0, inp.phi_h_ext_f_2), Line(-7.0, p_h_ext_m7, 2.0, inp.p_h_ext_f_2)
            )

        else:

            # 最大モードをもたない機種: 最大運転の特性線に定格運転の特性線を用いる (4 章、暫定)
            ext, ext_f = ful, ful_f

        # 無着霜時・着霜時の特性線をまとめる
        return cls(
            nonfrost=RegionCharacteristics(ful=ful, haf=haf, ext=ext),
            frost=RegionCharacteristics(ful=ful_f, haf=haf_f, ext=ext_f),
        )


def _heating_load(phi_c_ful_t100: float, t: float) -> float:
    """想定暖房空調負荷 L_h(t) を求める。

    Args:
        phi_c_ful_t100: 定格冷房能力 (表示値) Φ_c,ful,t100 (W)
        t: 外気温度 (℃)

    Returns:
        外気温度 t における想定暖房空調負荷 L_h(t) (W)

    Note:
        3 章 式 (64)。
    """
    # 17 ℃で 0、0 ℃で 0.82 × 1.25 × 定格冷房能力となる直線の値を求める (式 (64))
    return k.HEATING_LOAD_FACTOR * phi_c_ful_t100 * (k.T_H_0 - t) / (k.T_H_0 - k.T_H_100)


def _crossing_temperature(phi_c_ful_t100: float, phi: Line) -> float:
    """想定暖房空調負荷と能力線が等しくなる外気温度を求める。

    Args:
        phi_c_ful_t100: 定格冷房能力 (表示値) Φ_c,ful,t100 (W)
        phi: 外気 −7 ℃と、7 ℃または 2 ℃の 2 点で定めた能力線。1 点目は −7 ℃とする。

    Returns:
        交点温度 (℃)

    Raises:
        ValueError: 能力線の 1 点目が −7 ℃でない場合。負荷線と能力線が平行で、交点温度が求まらない場合

    Note:
        3 章「交点温度」の式 (58)〜(63)。無着霜時は式 (58), (59), (60)、着霜時は式 (61), (62), (63) である。
        満たす関係は式 (52)〜(57)。
    """
    # 能力線が −7 ℃の点から始まることを確かめる (交点温度の式はこの形を前提とする)
    if phi.t1 != -7.0:

        raise ValueError("能力線の 1 点目は外気 −7 ℃でなければならない")

    # 能力線の 2 点 (−7 ℃と、7 ℃または 2 ℃)の値と、負荷線の両端の温度 t_h,0、t_h,100 を取り出す
    t2 = phi.t2
    phi_m7, phi_t2 = phi.y1, phi.y2
    t_h_0, t_h_100 = k.T_H_0, k.T_H_100

    # 外気 t_h,100 (0 ℃)の想定暖房空調負荷 (1.025 × 定格冷房能力)と、能力線の 2 点の温度差を求める
    l_h_100 = k.HEATING_LOAD_FACTOR * phi_c_ful_t100
    w = t2 + 7

    # 分母を求める。0 なら負荷線と能力線が平行で、交点がない
    den = l_h_100 * w + (phi_t2 - phi_m7) * (t_h_0 - t_h_100)
    if den == 0:

        raise ValueError("想定暖房空調負荷と能力線が平行で、交点温度が求まらない")

    # 交点温度を求める (式 (58)〜(63))
    return (l_h_100 * t_h_0 * w - (t2 * phi_m7 + 7 * phi_t2) * (t_h_0 - t_h_100)) / den


def _is_frost(t: float) -> bool:
    """着霜領域かどうかを判定する。

    Args:
        t: 外気温度 (℃)

    Returns:
        −7 ℃ < t < 5.5 ℃ なら True

    Note:
        3 章「着霜領域と無着霜領域」による。
    """
    # −7 ℃を超え 5.5 ℃未満なら着霜領域とする
    return k.FROST_LOW < t < k.FROST_HIGH


@dataclass(frozen=True)
class HeatingCrossings:
    """無着霜時または着霜時の交点温度と、そこでのエネルギー消費効率。

    Attributes:
        t_ful: 定格運転能力との交点温度。無着霜時 t_a、着霜時 t_g (℃)
        t_haf: 中間運転能力との交点温度。無着霜時 t_d、着霜時 t_e (℃)
        t_ext: 最大運転能力との交点温度。無着霜時 t_h、着霜時 t_f (℃)
        cop_ful: 交点温度での定格運転の COP。COP_ful(t_a) または COP_ful,f(t_g) (−)
        cop_haf: 交点温度での中間運転の COP。COP_haf(t_d) または COP_haf,f(t_e) (−)
        cop_ext: 交点温度での最大運転の COP。COP_ext(t_h) または COP_ext,f(t_f) (−)

    Note:
        COP は 3 章「交点温度でのエネルギー消費効率」の式 (46)〜(51) による。
        無着霜時は式 (46), (47), (48)、着霜時は式 (49), (50), (51) である。
    """

    t_ful: float
    t_haf: float
    t_ext: float
    cop_ful: float
    cop_haf: float
    cop_ext: float

    @classmethod
    def _from_characteristics(cls, phi_c_ful_t100: float, rc: RegionCharacteristics) -> "HeatingCrossings":
        """特性線から交点温度と、そこでの COP を求める。

        Args:
            phi_c_ful_t100: 定格冷房能力 (表示値) Φ_c,ful,t100 (W)
            rc: 無着霜時または着霜時の特性線

        Returns:
            交点温度と COP

        Note:
            交点温度は _crossing_temperature、COP は能力を消費電力で割って求める (3 章 式 (46)〜(51))。
        """

        def at(op: OperationLines) -> tuple[float, float]:
            # 想定暖房空調負荷と能力線の交点温度を求める
            t = _crossing_temperature(phi_c_ful_t100, op.phi)
            # 交点温度での能力を消費電力で割って COP を求める (式 (46)〜(51))
            return t, op.phi(t) / op.p(t)

        # 定格運転・中間運転・最大運転のそれぞれについて、交点温度と COP を求める
        (t_ful, c_ful), (t_haf, c_haf), (t_ext, c_ext) = at(rc.ful), at(rc.haf), at(rc.ext)
        return cls(t_ful, t_haf, t_ext, c_ful, c_haf, c_ext)

    def _cop_hf(self, t: float) -> float:
        """中間運転能力と定格運転能力の間で可変運転したときの COP を求める。

        定格運転の交点温度と中間運転の交点温度の間を、外気温度で直線補間する (範囲外は延長する)。

        Args:
            t: 外気温度 (℃)

        Returns:
            COP_hf(t) または COP_hf,f(t) (−)

        Raises:
            ValueError: 2 つの交点温度が等しく、補間できない場合

        Note:
            3 章 式 (38), (39)。範囲外の扱いは 4 章「交点温度が着霜領域・無着霜領域の外にある場合」による。
        """
        # 補間の両端の温度が同じでは補間できない
        if self.t_haf == self.t_ful:

            raise ValueError("中間運転と定格運転の交点温度が同じで、COP を補間できない")

        # 定格運転の交点温度での COP から、中間運転の交点温度での COP へ直線補間する (式 (38), (39))
        return self.cop_ful + (self.cop_haf - self.cop_ful) / (self.t_haf - self.t_ful) * (t - self.t_ful)

    def _cop_fe(self, t: float) -> float:
        """定格運転能力と最大運転能力の間で可変運転したときの COP を求める。

        最大運転の交点温度と定格運転の交点温度の間を、外気温度で直線補間する (範囲外は延長する)。

        Args:
            t: 外気温度 (℃)

        Returns:
            COP_fe(t) または COP_fe,f(t) (−)

        Raises:
            ValueError: 2 つの交点温度が等しく、補間できない場合

        Note:
            3 章 式 (42), (43)。
        """
        # 補間の両端の温度が同じでは補間できない
        if self.t_ful == self.t_ext:

            raise ValueError("定格運転と最大運転の交点温度が同じで、COP を補間できない")

        # 最大運転の交点温度での COP から、定格運転の交点温度での COP へ直線補間する (式 (42), (43))
        return self.cop_ext + (self.cop_ful - self.cop_ext) / (self.t_ful - self.t_ext) * (t - self.t_ext)


@dataclass(frozen=True)
class HeatingBin:
    """暖房の温度区分ごとの計算結果。

    Attributes:
        t_j: 外気温度 t_j (℃)
        n_h_j: 発生時間 n_h,j (h)
        frost: 着霜領域なら True
        state: 運転状態
        l_h: 想定暖房空調負荷 L_h(t_j) (W)
        p_h: 消費電力 P_h(t_j)。補助電熱装置の消費電力を含む (W)
        p_h_rh: 補助電熱装置の消費電力 P_h,RH(t_j) または P_h,RH,f(t_j) (W)。最大運転以外は 0
        x_h: 運転率 X_h(t_j) または X_h,f(t_j) (−)。断続運転のときだけ値をもつ。
        f_h_pl: 部分負荷率 F_h,PL(t_j) または F_h,PL,f(t_j) (−)。断続運転のときだけ値をもつ。
        cop: 可変運転のときの COP (−)。可変運転のときだけ値をもつ。

    Note:
        3 章 式 (30), (31) の 1 つの温度区分の値である。
    """

    t_j: float
    n_h_j: float
    frost: bool
    state: HeatingState
    l_h: float
    p_h: float
    p_h_rh: float = 0.0
    x_h: float | None = None
    f_h_pl: float | None = None
    cop: float | None = None

    @property
    def q_h(self) -> float:
        """処理する空調負荷 Q_h(t_j)。

        Returns:
            想定暖房空調負荷に等しい値 (W)

        Note:
            3 章 式 (29)。
        """
        # 暖房では能力の不足分を補助電熱装置で補うので、想定暖房空調負荷を全量処理する (式 (29))
        return self.l_h


@dataclass(frozen=True)
class HeatingResult:
    """暖房期間の計算結果。

    Attributes:
        l_hst: 暖房期間総合空調負荷 L_HST (Wh)
        c_hse: 暖房期間消費電力量 C_HSE (Wh)
        f_hsp: 暖房期間エネルギー消費効率 F_HSP (−)
        nonfrost: 無着霜時の交点温度と COP
        frost: 着霜時の交点温度と COP
        bins: 温度区分ごとの計算結果。外気温度の低い順
    """

    l_hst: float
    c_hse: float
    f_hsp: float
    nonfrost: HeatingCrossings
    frost: HeatingCrossings
    bins: list[HeatingBin] = field(default_factory=list)


def compute_heating(inp: HeatingInput, n_h_j: dict[float, float] | None = None) -> HeatingResult:
    """暖房期間エネルギー消費効率などを求める。

    Args:
        inp: 暖房期間の入力値
        n_h_j: 外気温度 t_j (℃)をキー、発生時間 n_h,j (h)を値とする辞書。
            省略すると東京の値 (附属書 B の表 B.6) を用いる。

    Returns:
        暖房期間の計算結果

    Raises:
        ValueError: 交点温度が求まらない場合、または COP を補間できない場合

    Note:
        3 章「暖房期間」の式 (26), (27), (28), (29), (30), (31), (32), (33), (34), (35), (36), (37),
        (40), (41), (44), (45) による。
        負荷 0 %の外気温度 (17 ℃)以上の温度区分は、消費電力を 0 とする
        (東京の表 B.6 にはない。DESIGN.md「設計方針」)。
    """
    # 発生時間が与えられなければ、東京の値を用いる
    n_h_j = TOKYO_HEATING_HOURS if n_h_j is None else n_h_j

    # 試験値を補完し、無着霜時・着霜時の能力・消費電力の特性線を作る (式 (65)〜(92))
    ch = HeatingCharacteristics._from_input(inp)

    # 無着霜時・着霜時のそれぞれについて、交点温度とそこでの COP を求める (式 (46)〜(63))
    cross_nf = HeatingCrossings._from_characteristics(inp.phi_c_ful_t100, ch.nonfrost)
    cross_f = HeatingCrossings._from_characteristics(inp.phi_c_ful_t100, ch.frost)

    # 温度区分ごとに、運転状態を判定して消費電力を求める (式 (30), (31))
    bins: list[HeatingBin] = []
    for t_j in sorted(n_h_j):

        # 着霜領域かどうかで、使う特性線と交点温度を選ぶ
        frost = _is_frost(t_j)
        rc, cr = (ch.frost, cross_f) if frost else (ch.nonfrost, cross_nf)

        # この温度区分の想定暖房空調負荷を求める (式 (64))
        l_h = _heating_load(inp.phi_c_ful_t100, t_j)

        # 負荷 0 %の外気温度以上では、消費電力を 0 とする (東京の発生時間にはない)
        if l_h <= 0:

            bins.append(HeatingBin(t_j, n_h_j[t_j], frost, HeatingState.INTERMITTENT, l_h, 0.0, x_h=0.0))
            continue

        # この温度区分の中間運転・定格運転・最大運転の能力を求める
        phi_h_haf, phi_h_ful, phi_h_ext = rc.haf.phi(t_j), rc.ful.phi(t_j), rc.ext.phi(t_j)

        if l_h <= phi_h_haf:

            # 断続運転: 運転率と部分負荷率を求める (式 (34), (35), (32), (33))
            x_h = l_h / phi_h_haf
            f_h_pl = 1 - k.C_H_D * (1 - x_h)

            # 断続運転: 運転率の分だけ中間運転し、部分負荷率で効率の低下を補正する (式 (30), (31))
            p_h = x_h * rc.haf.p(t_j) / f_h_pl
            bins.append(HeatingBin(t_j, n_h_j[t_j], frost, HeatingState.INTERMITTENT, l_h, p_h, x_h=x_h, f_h_pl=f_h_pl))

        elif l_h <= phi_h_ful:

            # 中間〜定格の可変運転: 交点温度の間で COP を補間し、負荷を COP で割る (式 (36), (37))
            cop = cr._cop_hf(t_j)
            bins.append(HeatingBin(t_j, n_h_j[t_j], frost, HeatingState.HAF_FUL, l_h, l_h / cop, cop=cop))

        elif l_h <= phi_h_ext:

            # 定格〜最大の可変運転: 交点温度の間で COP を補間し、負荷を COP で割る (式 (40), (41))
            cop = cr._cop_fe(t_j)
            bins.append(HeatingBin(t_j, n_h_j[t_j], frost, HeatingState.FUL_EXT, l_h, l_h / cop, cop=cop))

        else:

            # 最大運転: 能力の不足分を補助電熱装置で補う (式 (44), (45))
            p_h_rh = l_h - phi_h_ext

            # 最大運転: 最大運転消費電力に補助電熱装置の消費電力を加える (式 (30), (31))
            bins.append(HeatingBin(t_j, n_h_j[t_j], frost, HeatingState.MAX, l_h, rc.ext.p(t_j) + p_h_rh, p_h_rh=p_h_rh))

    # 温度区分ごとの値に発生時間を掛けて合計する (式 (27), (28))
    l_hst = sum(b.q_h * b.n_h_j for b in bins)
    c_hse = sum(b.p_h * b.n_h_j for b in bins)

    # 暖房期間エネルギー消費効率を求めて、結果をまとめる (式 (26))
    return HeatingResult(l_hst, c_hse, l_hst / c_hse, cross_nf, cross_f, bins)

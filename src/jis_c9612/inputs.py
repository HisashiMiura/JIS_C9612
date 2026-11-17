"""入力値 (ドキュメント 3 章の冷房期間・暖房期間の「入力値」)。

単位は W。フィールド名は 3 章・5 章の記号に合わせている (例: Φ_c,ful(35) → phi_c_ful_35)。係数で求める値 (外気 29 ℃、−7 ℃などの値) は入力として受け付けない
(ドキュメント 4 章「回転数制御形の外気 29 ℃の値」「係数で求める値」)。
"""

from dataclasses import dataclass


def _positive(name: str, value: float) -> None:
    """値が正であることを確かめる。

    Args:
        name: 入力値の名前。エラーメッセージに用いる。
        value: 確かめる値

    Raises:
        ValueError: value が 0 以下の場合
    """
    # 0 以下 (と NaN)を誤りとする
    if not value > 0:

        raise ValueError(f"{name} は正の値でなければならない (値: {value})")


@dataclass(frozen=True)
class CoolingInput:
    """冷房期間の入力値。

    Attributes:
        phi_c_ful_t100: 定格冷房能力 (表示値) Φ_c,ful,t100 (W)
        phi_c_ful_35: 冷房能力試験 (外気 35 ℃)での定格運転能力 Φ_c,ful(35) (W)
        p_c_ful_35: 冷房能力試験 (外気 35 ℃)での定格運転消費電力 P_c,ful(35) (W)
        phi_c_haf_35: 冷房能力試験 (外気 35 ℃)での中間運転能力 Φ_c,haf(35) (W)
        p_c_haf_35: 冷房能力試験 (外気 35 ℃)での中間運転消費電力 P_c,haf(35) (W)

    Note:
        3 章「冷房期間」の「入力値」に対応する。
    """

    phi_c_ful_t100: float
    phi_c_ful_35: float
    p_c_ful_35: float
    phi_c_haf_35: float
    p_c_haf_35: float

    def __post_init__(self) -> None:
        """入力値を確かめる。

        Raises:
            ValueError: いずれかの入力値が 0 以下の場合
        """
        # すべての入力値が正であることを確かめる
        for name in ("phi_c_ful_t100", "phi_c_ful_35", "p_c_ful_35", "phi_c_haf_35", "p_c_haf_35"):

            _positive(name, getattr(self, name))


@dataclass(frozen=True)
class HeatingInput:
    """暖房期間の入力値。

    最大モードをもつ機種は phi_h_ext_f_2 と p_h_ext_f_2 を、
    最大モードをもたない機種は phi_h_ful_f_2 と p_h_ful_f_2 を与える。

    Attributes:
        phi_c_ful_t100: 定格冷房能力 (表示値) Φ_c,ful,t100 (W)。想定暖房空調負荷に用いる。
        phi_h_ful_7: 暖房標準能力試験 (外気 7 ℃)での定格運転能力 Φ_h,ful(7) (W)
        p_h_ful_7: 暖房標準能力試験 (外気 7 ℃)での定格運転消費電力 P_h,ful(7) (W)
        phi_h_haf_7: 暖房標準能力試験 (外気 7 ℃)での中間運転能力 Φ_h,haf(7) (W)
        p_h_haf_7: 暖房標準能力試験 (外気 7 ℃)での中間運転消費電力 P_h,haf(7) (W)
        phi_h_ext_f_2: 暖房低温能力試験 (外気 2 ℃)での最大運転能力 Φ_h,ext,f(2) (W)。
            最大モードをもつ機種だけ与える。
        p_h_ext_f_2: 暖房低温能力試験 (外気 2 ℃)での最大運転消費電力 P_h,ext,f(2) (W)。
            最大モードをもつ機種だけ与える。
        phi_h_ful_f_2: 暖房低温能力試験 (外気 2 ℃)での定格運転能力 Φ_h,ful,f(2) (W)。
            最大モードをもたない機種だけ与える。
        p_h_ful_f_2: 暖房低温能力試験 (外気 2 ℃)での定格運転消費電力 P_h,ful,f(2) (W)。
            最大モードをもたない機種だけ与える。

    Note:
        3 章「暖房期間」の「入力値」に対応する。
        最大モードの有無による入力の違いは、4 章「最大モードをもたない機種 (暫定)」による。
    """

    phi_c_ful_t100: float
    phi_h_ful_7: float
    p_h_ful_7: float
    phi_h_haf_7: float
    p_h_haf_7: float
    phi_h_ext_f_2: float | None = None
    p_h_ext_f_2: float | None = None
    phi_h_ful_f_2: float | None = None
    p_h_ful_f_2: float | None = None

    def __post_init__(self) -> None:
        """入力値と、外気 2 ℃の試験値の組み合わせを確かめる。

        Raises:
            ValueError: 入力値が 0 以下の場合。外気 2 ℃の能力と消費電力の片方だけを与えた場合。
                最大運転と定格運転の 2 ℃の試験値を両方与えた場合、またはどちらも与えない場合
        """
        # 必ず与える入力値が正であることを確かめる
        for name in ("phi_c_ful_t100", "phi_h_ful_7", "p_h_ful_7", "phi_h_haf_7", "p_h_haf_7"):

            _positive(name, getattr(self, name))

        # 外気 2 ℃の試験値が、最大運転・定格運転のそれぞれで能力と消費電力の組でそろっているかを調べる
        ext = (self.phi_h_ext_f_2, self.p_h_ext_f_2)
        ful = (self.phi_h_ful_f_2, self.p_h_ful_f_2)
        has_ext = all(v is not None for v in ext)
        has_ful = all(v is not None for v in ful)

        # 能力と消費電力の片方だけが与えられていたら誤りとする
        if any(v is not None for v in ext) and not has_ext:

            raise ValueError("phi_h_ext_f_2 と p_h_ext_f_2 は両方を与える")
        if any(v is not None for v in ful) and not has_ful:

            raise ValueError("phi_h_ful_f_2 と p_h_ful_f_2 は両方を与える")

        # 最大運転と定格運転の試験値は、どちらか一方だけを与える (最大モードの有無が決まるように)
        if has_ext == has_ful:

            raise ValueError(
                "最大モードをもつ機種は phi_h_ext_f_2, p_h_ext_f_2 を、"
                "もたない機種は phi_h_ful_f_2, p_h_ful_f_2 を、どちらか一方だけ与える"
            )

        # 与えた外気 2 ℃の試験値が正であることを確かめる
        for name in ("phi_h_ext_f_2", "p_h_ext_f_2", "phi_h_ful_f_2", "p_h_ful_f_2"):

            v = getattr(self, name)
            if v is not None:

                _positive(name, v)

    @property
    def has_max_mode(self) -> bool:
        """最大モードをもつ機種か。

        Returns:
            最大運転の 2 ℃の試験値 (phi_h_ext_f_2) を与えた場合に True
        """
        # 最大運転の 2 ℃の試験値があれば最大モードをもつ機種とする (__post_init__ で組み合わせは確認済み)
        return self.phi_h_ext_f_2 is not None

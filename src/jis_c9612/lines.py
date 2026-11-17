"""外気温度の 1 次式で表す特性線。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Line:
    """2 点 (t1, y1)、(t2, y2) を通る直線 y(t)。

    能力・消費電力の特性線を表す。

    Attributes:
        t1: 1 点目の外気温度 (℃)
        y1: 1 点目の値 (W)
        t2: 2 点目の外気温度 (℃)
        y2: 2 点目の値 (W)

    Note:
        3 章「能力・消費電力の特性」の各式の形の直線である (冷房は式 (18)〜(21)、暖房は式 (65)〜(76))。
    """

    t1: float
    y1: float
    t2: float
    y2: float

    def __post_init__(self) -> None:
        """2 点の外気温度が異なることを確かめる。

        Raises:
            ValueError: t1 と t2 が等しく、直線が定まらない場合
        """
        # 2 点の外気温度が同じだと傾きが定まらないので、誤りとする
        if self.t1 == self.t2:

            raise ValueError("直線を決める 2 点の外気温度が同じである")

    @property
    def _slope(self) -> float:
        """直線の傾き。

        Returns:
            外気温度 1 ℃あたりの変化量 (W/℃)
        """
        # 2 点の値の差を、外気温度の差で割る
        return (self.y2 - self.y1) / (self.t2 - self.t1)

    def __call__(self, t: float) -> float:
        """外気温度 t における値を返す。

        Args:
            t: 外気温度 (℃)

        Returns:
            外気温度 t における値 (W)。2 点の範囲外では直線を延長した値
        """
        # 1 点目の値に、1 点目からの外気温度の差と傾きの積を足す
        return self.y1 + self._slope * (t - self.t1)

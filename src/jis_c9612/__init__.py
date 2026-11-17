"""JIS C 9612:2013 附属書 B による回転数制御形ルームエアコンの APF 計算。

計算方法はドキュメント (docs/) の 3 章「評価方法」、その根拠は 4 章による。
"""

from .apf import AnnualResult, compute_apf
from .cooling import CoolingResult, compute_cooling
from .heating import HeatingResult, compute_heating
from .inputs import CoolingInput, HeatingInput

__all__ = [
    "AnnualResult",
    "CoolingInput",
    "CoolingResult",
    "HeatingInput",
    "HeatingResult",
    "compute_apf",
    "compute_cooling",
    "compute_heating",
]

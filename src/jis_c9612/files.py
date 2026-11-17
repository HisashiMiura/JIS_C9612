"""入力ファイルの読み込みと、計算結果の出力 (ドキュメント 2 章「プログラムの使い方」)。"""

import csv
import tomllib
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from .apf import AnnualResult
from .inputs import CoolingInput, HeatingInput

#: [cooling] に書けるキー
_COOLING_KEYS = ("phi_c_ful_35", "p_c_ful_35", "phi_c_haf_35", "p_c_haf_35")
#: [heating] に必ず書くキー
_HEATING_KEYS = ("phi_h_ful_7", "p_h_ful_7", "phi_h_haf_7", "p_h_haf_7")
#: [heating] に、最大モードの有無に応じて書くキー
_HEATING_OPTIONAL_KEYS = ("phi_h_ext_f_2", "p_h_ext_f_2", "phi_h_ful_f_2", "p_h_ful_f_2")
#: 最上位に書けるキー
_TOP_KEYS = ("name", "phi_c_ful_t100", "cooling", "heating", "n_c_j", "n_h_j")


@dataclass(frozen=True)
class ModelInput:
    """入力ファイルから読み込んだ 1 つの機種の値。

    Attributes:
        name: 機種の名前。入力ファイルに書かれていなければ入力ファイルの名前
        cooling: 冷房期間の入力値
        heating: 暖房期間の入力値
        n_c_j: 冷房期間の外気温度 t_j (℃)と発生時間 n_c,j (h)。書かれていなければ None (東京の値を用いる)
        n_h_j: 暖房期間の外気温度 t_j (℃)と発生時間 n_h,j (h)。書かれていなければ None (東京の値を用いる)
    """

    name: str
    cooling: CoolingInput
    heating: HeatingInput
    n_c_j: dict[float, float] | None = None
    n_h_j: dict[float, float] | None = None


def _number(where: str, value: object) -> float:
    """入力ファイルの値を数値として取り出す。

    Args:
        where: 値の場所 (エラーメッセージに用いる)。例: "[cooling] の phi_c_ful_35"
        value: 入力ファイルから読み込んだ値

    Returns:
        数値

    Raises:
        ValueError: 値が数値でない場合 (真偽値も数値とみなさない)
    """
    # TOML の true / false は Python では int の仲間になるので、先に除く
    if isinstance(value, bool) or not isinstance(value, (int, float)):

        raise ValueError(f"{where} は数値でなければならない (値: {value!r})")

    return float(value)


def _check_keys(where: str, table: dict, allowed: tuple[str, ...]) -> None:
    """表に、書けないキーが含まれていないかを確かめる。

    Args:
        where: 表の場所 (エラーメッセージに用いる)。例: "[cooling]"
        table: 入力ファイルから読み込んだ表
        allowed: 書けるキー

    Raises:
        ValueError: 書けないキーが含まれている場合
    """
    # 書けるキー以外のキーを集めて、あれば誤りとする (キーの書き間違いを見つけるため)
    unknown = sorted(set(table) - set(allowed))
    if unknown:

        raise ValueError(f"{where} に書けないキーがある: {', '.join(unknown)}")


def _table(data: dict, key: str) -> dict:
    """入力ファイルから表を取り出す。

    Args:
        data: 入力ファイル全体
        key: 表の名前

    Returns:
        表の中身

    Raises:
        ValueError: 表がない場合、または表でない場合
    """
    # 表があり、かつ表 (TOML のテーブル)であることを確かめる
    table = data.get(key)
    if not isinstance(table, dict):

        raise ValueError(f"[{key}] がない、または表ではない")

    return table


def _hours(data: dict, key: str) -> dict[float, float] | None:
    """外気温度の発生時間の表を読み込む。

    Args:
        data: 入力ファイル全体
        key: 表の名前 ("n_c_j" または "n_h_j")

    Returns:
        外気温度 t_j (℃)をキー、発生時間 (h)を値とする辞書。表がなければ None

    Raises:
        ValueError: 外気温度が数値として読めない場合、発生時間が数値でないか負の場合、表が空の場合
    """
    # 表がなければ、東京の値を用いるので None を返す
    if key not in data:

        return None

    table = _table(data, key)
    if not table:

        raise ValueError(f"[{key}] が空である")

    # キー (外気温度の文字列)を数値に、値を発生時間に変換する
    hours: dict[float, float] = {}
    for t_text, n in table.items():

        try:

            t_j = float(t_text)

        except ValueError:

            raise ValueError(f"[{key}] のキー {t_text!r} を外気温度として読めない") from None

        n_j = _number(f"[{key}] の {t_text!r}", n)
        if n_j < 0:

            raise ValueError(f"[{key}] の {t_text!r} の発生時間が負である (値: {n_j})")

        hours[t_j] = n_j

    return hours


def load_input(path: str | Path) -> ModelInput:
    """入力ファイル (TOML)を読み込む。

    Args:
        path: 入力ファイルのパス

    Returns:
        入力ファイルから読み込んだ機種の値

    Raises:
        OSError: ファイルを開けない場合
        tomllib.TOMLDecodeError: TOML として読めない場合
        ValueError: キーが足りない、書けないキーがある、値が数値でない、または正でない場合

    Note:
        入力ファイルの書き方は 2 章「入力ファイル」による。
    """
    # ファイルを TOML として読み込む
    path = Path(path)
    with path.open("rb") as f:

        data = tomllib.load(f)

    # 最上位・[cooling]・[heating] に、書けないキーがないことを確かめる
    _check_keys("最上位", data, _TOP_KEYS)
    cooling_table = _table(data, "cooling")
    heating_table = _table(data, "heating")
    _check_keys("[cooling]", cooling_table, _COOLING_KEYS)
    _check_keys("[heating]", heating_table, _HEATING_KEYS + _HEATING_OPTIONAL_KEYS)

    # 冷房・暖房に共通の定格冷房能力 (表示値)を読み込む
    if "phi_c_ful_t100" not in data:

        raise ValueError("phi_c_ful_t100 (定格冷房能力 (表示値))がない")

    phi_c_ful_t100 = _number("phi_c_ful_t100", data["phi_c_ful_t100"])

    # [cooling] の値を読み込む。キーが足りなければ誤りとする
    missing = [key for key in _COOLING_KEYS if key not in cooling_table]
    if missing:

        raise ValueError(f"[cooling] に {', '.join(missing)} がない")

    cooling_values = {key: _number(f"[cooling] の {key}", cooling_table[key]) for key in _COOLING_KEYS}

    # [heating] の値を読み込む。必ず書くキーが足りなければ誤りとする
    missing = [key for key in _HEATING_KEYS if key not in heating_table]
    if missing:

        raise ValueError(f"[heating] に {', '.join(missing)} がない")

    heating_values = {
        key: _number(f"[heating] の {key}", heating_table[key])
        for key in _HEATING_KEYS + _HEATING_OPTIONAL_KEYS
        if key in heating_table
    }

    # 機種の名前を決める。書かれていなければ入力ファイルの名前とする
    name = data.get("name", path.stem)
    if not isinstance(name, str):

        raise ValueError(f"name は文字列でなければならない (値: {name!r})")

    # 入力値を作る。値の範囲と最大モードの組み合わせは CoolingInput / HeatingInput で確かめる
    return ModelInput(
        name=name,
        cooling=CoolingInput(phi_c_ful_t100=phi_c_ful_t100, **cooling_values),
        heating=HeatingInput(phi_c_ful_t100=phi_c_ful_t100, **heating_values),
        n_c_j=_hours(data, "n_c_j"),
        n_h_j=_hours(data, "n_h_j"),
    )


def round_efficiency(value: float) -> str:
    """効率を、小数第 2 位を四捨五入して小数第 1 位までの文字列にする。

    Args:
        value: 効率 (APF、CSPF、HSPF など)

    Returns:
        小数第 1 位までの文字列。例: 4.798 → "4.8"

    Note:
        2 章「出力」による。Python の round() は偶数への丸めなので用いず、四捨五入する。
    """
    # 10 進数として四捨五入する (2 進数の誤差で 4.85 が 4.8 になるのを避けるため、文字列から変換する)
    return str(Decimal(repr(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def format_summary(name: str, result: AnnualResult) -> str:
    """計算結果の要約を、画面に表示する文字列にする。

    Args:
        name: 機種の名前
        result: 計算結果

    Returns:
        画面に表示する文字列 (複数行)

    Note:
        2 章「出力」の「画面」による。
    """
    c, h = result.cooling, result.heating

    # 効率は小数第 1 位まで、電力量は kWh で小数第 1 位まで表示する
    rows = [
        ("通年エネルギー消費効率 (APF)", round_efficiency(result.f_ap), ""),
        ("冷房期間エネルギー消費効率 (CSPF)", round_efficiency(c.f_csp), ""),
        ("暖房期間エネルギー消費効率 (HSPF)", round_efficiency(h.f_hsp), ""),
        ("冷房期間総合空調負荷 (CSTL)", f"{c.l_cst / 1000:,.1f}", "kWh"),
        ("冷房期間消費電力量 (CSEC)", f"{c.c_cse / 1000:,.1f}", "kWh"),
        ("暖房期間総合空調負荷 (HSTL)", f"{h.l_hst / 1000:,.1f}", "kWh"),
        ("暖房期間消費電力量 (HSEC)", f"{h.c_hse / 1000:,.1f}", "kWh"),
        ("期間消費電力量", f"{result.annual_energy / 1000:,.1f}", "kWh"),
    ]

    # 項目名の幅をそろえて、1 行ずつ並べる (全角文字は 2 文字分の幅とする)
    def width(text: str) -> int:
        return sum(2 if ord(ch) > 0x7F else 1 for ch in text)

    label_w = max(width(label) for label, _, _ in rows)
    value_w = max(len(value) for _, value, _ in rows)
    lines = [name]
    for label, value, unit in rows:

        pad = " " * (label_w - width(label))
        lines.append(f"  {label}{pad}  {value:>{value_w}} {unit}".rstrip())

    return "\n".join(lines)


def _cell(value: object) -> object:
    """CSV の 1 つのセルの値にする。

    Args:
        value: 値

    Returns:
        None なら空文字列、それ以外はそのままの値
    """
    # 値をもたない項目 (断続運転以外の運転率など)は空欄にする
    return "" if value is None else value


def write_csv(result: AnnualResult, name: str, output_dir: str | Path, stem: str) -> list[Path]:
    """計算結果を CSV ファイルに保存する。

    Args:
        result: 計算結果
        name: 機種の名前
        output_dir: CSV ファイルを保存するディレクトリ。なければ作る
        stem: CSV ファイルの名前の先頭に付ける文字列 (入力ファイルの名前から拡張子を除いたもの)

    Returns:
        保存した CSV ファイルのパス (要約、冷房期間、暖房期間の順)

    Note:
        2 章「出力」の「CSV ファイル」による。値は丸めない。文字コードは BOM 付きの UTF-8 とする。
    """
    c, h = result.cooling, result.heating

    # 保存先のディレクトリを用意する
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = [output_dir / f"{stem}_summary.csv", output_dir / f"{stem}_cooling.csv", output_dir / f"{stem}_heating.csv"]

    # 要約: 項目、記号、値、単位を 1 行ずつ書く
    summary = [
        ("項目", "記号", "値", "単位"),
        ("機種の名前", "", name, ""),
        ("通年エネルギー消費効率 (APF)", "F_AP", result.f_ap, "−"),
        ("冷房期間エネルギー消費効率 (CSPF)", "F_CSP", c.f_csp, "−"),
        ("暖房期間エネルギー消費効率 (HSPF)", "F_HSP", h.f_hsp, "−"),
        ("冷房期間総合空調負荷 (CSTL)", "L_CST", c.l_cst, "Wh"),
        ("冷房期間消費電力量 (CSEC)", "C_CSE", c.c_cse, "Wh"),
        ("暖房期間総合空調負荷 (HSTL)", "L_HST", h.l_hst, "Wh"),
        ("暖房期間消費電力量 (HSEC)", "C_HSE", h.c_hse, "Wh"),
        ("期間消費電力量", "C_CSE + C_HSE", result.annual_energy, "Wh"),
        ("冷房: 定格運転能力との交点温度", "t_b", c.t_b, "℃"),
        ("冷房: 中間運転能力との交点温度", "t_c", c.t_c, "℃"),
        ("暖房: 無着霜時の定格運転能力との交点温度", "t_a", h.nonfrost.t_ful, "℃"),
        ("暖房: 無着霜時の中間運転能力との交点温度", "t_d", h.nonfrost.t_haf, "℃"),
        ("暖房: 無着霜時の最大運転能力との交点温度", "t_h", h.nonfrost.t_ext, "℃"),
        ("暖房: 着霜時の定格運転能力との交点温度", "t_g", h.frost.t_ful, "℃"),
        ("暖房: 着霜時の中間運転能力との交点温度", "t_e", h.frost.t_haf, "℃"),
        ("暖房: 着霜時の最大運転能力との交点温度", "t_f", h.frost.t_ext, "℃"),
    ]

    # 冷房期間: 温度区分ごとの値を 1 行ずつ書く
    cooling = [("t_j (℃)", "n_c,j (h)", "運転状態", "L_c(t_j) (W)", "Q_c(t_j) (W)", "P_c(t_j) (W)",
                "X_c(t_j) (−)", "F_c,PL(t_j) (−)", "EER_hf(t_j) (−)")]
    for b in c.bins:

        cooling.append((b.t_j, b.n_c_j, b.state.value, b.l_c, b.q_c, b.p_c,
                        _cell(b.x_c), _cell(b.f_c_pl), _cell(b.eer_hf)))

    # 暖房期間: 温度区分ごとの値を 1 行ずつ書く (着霜時の値は添字 f の記号の値)
    heating = [("t_j (℃)", "n_h,j (h)", "着霜領域", "運転状態", "L_h(t_j) (W)", "P_h(t_j) (W)",
                "P_h,RH(t_j) / P_h,RH,f(t_j) (W)", "X_h(t_j) / X_h,f(t_j) (−)",
                "F_h,PL(t_j) / F_h,PL,f(t_j) (−)", "COP (−)")]
    for b in h.bins:

        heating.append((b.t_j, b.n_h_j, "着霜" if b.frost else "無着霜", b.state.value, b.l_h, b.p_h,
                        b.p_h_rh, _cell(b.x_h), _cell(b.f_h_pl), _cell(b.cop)))

    # 3 つの表を、BOM 付きの UTF-8 で保存する (表計算ソフトで文字化けしないように)
    for path, rows in zip(paths, (summary, cooling, heating)):

        with path.open("w", encoding="utf-8-sig", newline="") as f:

            csv.writer(f).writerows(rows)

    return paths

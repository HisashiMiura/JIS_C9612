"""入力ファイルの読み込み、出力、コマンドラインのテスト (ドキュメント 2 章「プログラムの使い方」)。"""

import csv
import pathlib

import pytest

from jis_c9612 import compute_apf
from jis_c9612.cli import main
from jis_c9612.files import format_summary, load_input, round_efficiency, write_csv

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "example_tokyo.toml"

BASE = """
name = "テスト機"
phi_c_ful_t100 = 2800

[cooling]
phi_c_ful_35 = 2800
p_c_ful_35 = 700
phi_c_haf_35 = 1400
p_c_haf_35 = 280

[heating]
phi_h_ful_7 = 3600
p_h_ful_7 = 900
phi_h_haf_7 = 1800
p_h_haf_7 = 360
phi_h_ext_f_2 = 4200
p_h_ext_f_2 = 1500
"""


def _write(tmp_path: pathlib.Path, text: str, name: str = "model.toml") -> pathlib.Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_load_example():
    m = load_input(EXAMPLE)
    assert m.name == "例: 2.8 kW 機"
    assert m.cooling.phi_c_ful_35 == 2800
    assert m.heating.has_max_mode
    assert m.n_c_j is None and m.n_h_j is None


def test_example_gives_same_apf_as_python_api(cooling_input, heating_input):
    m = load_input(EXAMPLE)
    r = compute_apf(m.cooling, m.heating)
    assert r.f_ap == pytest.approx(compute_apf(cooling_input, heating_input).f_ap)


def test_name_defaults_to_file_stem(tmp_path):
    path = _write(tmp_path, BASE.replace('name = "テスト機"\n', ""), "my_model.toml")
    assert load_input(path).name == "my_model"


def test_no_max_mode(tmp_path):
    text = BASE.replace("phi_h_ext_f_2 = 4200\np_h_ext_f_2 = 1500", "phi_h_ful_f_2 = 2700\np_h_ful_f_2 = 800")
    assert not load_input(_write(tmp_path, text)).heating.has_max_mode


def test_custom_hours(tmp_path):
    text = BASE + '\n[n_c_j]\n"30" = 100\n"34.5" = 10\n\n[n_h_j]\n"-1" = 5\n"10" = 200\n'
    m = load_input(_write(tmp_path, text))
    assert m.n_c_j == {30.0: 100.0, 34.5: 10.0}
    assert m.n_h_j == {-1.0: 5.0, 10.0: 200.0}


@pytest.mark.parametrize(
    "old, new, message",
    [
        ("phi_c_ful_35 = 2800", "phi_c_ful35 = 2800", "書けないキー"),  # 書き間違い
        ("p_c_haf_35 = 280\n", "", "p_c_haf_35 がない"),  # 不足
        ("phi_c_ful_t100 = 2800\n", "", "phi_c_ful_t100"),  # 不足
        ("p_h_ful_7 = 900", 'p_h_ful_7 = "900"', "数値でなければならない"),  # 文字列
        ("p_h_ful_7 = 900", "p_h_ful_7 = true", "数値でなければならない"),  # 真偽値
        ("p_h_ful_7 = 900", "p_h_ful_7 = -900", "正の値"),  # 負
        ("p_h_ext_f_2 = 1500\n", "", "両方を与える"),  # 組の片方だけ
    ],
)
def test_input_errors(tmp_path, old, new, message):
    assert old in BASE
    with pytest.raises(ValueError, match=message):
        load_input(_write(tmp_path, BASE.replace(old, new, 1)))


@pytest.mark.parametrize(
    "hours, message",
    [('"abc" = 1', "外気温度として読めない"), ('"30" = -1', "負"), ('"30" = "x"', "数値でなければならない")],
)
def test_hours_errors(tmp_path, hours, message):
    with pytest.raises(ValueError, match=message):
        load_input(_write(tmp_path, BASE + f"\n[n_c_j]\n{hours}\n"))


@pytest.mark.parametrize("value, text", [(4.798, "4.8"), (4.85, "4.9"), (4.849, "4.8"), (4.75, "4.8"), (5.0, "5.0")])
def test_round_efficiency_half_up(value, text):
    """小数第 2 位を四捨五入する (偶数への丸めではない)。"""
    assert round_efficiency(value) == text


def test_summary_shows_rounded_efficiency(cooling_input, heating_input):
    text = format_summary("テスト機", compute_apf(cooling_input, heating_input))
    assert text.splitlines()[0] == "テスト機"
    assert "4.8" in text and "5.4" in text and "4.5" in text
    assert "1,103.9 kWh" in text


def _read(path: pathlib.Path) -> list[list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def test_csv_files(tmp_path, cooling_input, heating_input):
    r = compute_apf(cooling_input, heating_input)
    paths = write_csv(r, "テスト機", tmp_path / "out", "model")
    assert [p.name for p in paths] == ["model_summary.csv", "model_cooling.csv", "model_heating.csv"]
    # BOM 付きの UTF-8
    assert paths[0].read_bytes().startswith(b"\xef\xbb\xbf")

    summary = {row[1]: row[2] for row in _read(paths[0])[1:]}
    assert float(summary["F_AP"]) == pytest.approx(r.f_ap)  # 丸めない値

    # 温度区分ごとの値に発生時間を掛けて合計すると、期間の合計に一致する (2 章「CSV ファイル」)
    cooling = _read(paths[1])[1:]
    assert sum(float(row[1]) * float(row[4]) for row in cooling) == pytest.approx(r.cooling.l_cst)
    assert sum(float(row[1]) * float(row[5]) for row in cooling) == pytest.approx(r.cooling.c_cse)
    heating = _read(paths[2])[1:]
    assert sum(float(row[1]) * float(row[4]) for row in heating) == pytest.approx(r.heating.l_hst)
    assert sum(float(row[1]) * float(row[5]) for row in heating) == pytest.approx(r.heating.c_hse)


def test_cli(tmp_path, capsys):
    path = _write(tmp_path, BASE)
    assert main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "テスト機" in out and "4.8" in out
    assert (tmp_path / "model_summary.csv").exists()


def test_cli_output_dir_and_no_csv(tmp_path, capsys):
    path = _write(tmp_path, BASE)
    assert main([str(path), "-o", str(tmp_path / "res")]) == 0
    assert (tmp_path / "res" / "model_heating.csv").exists()
    assert main([str(path), "--no-csv"]) == 0
    assert not (tmp_path / "model_summary.csv").exists()


def test_cli_reports_errors(tmp_path, capsys):
    path = _write(tmp_path, BASE.replace("p_c_haf_35 = 280\n", ""))
    assert main([str(path)]) == 1
    assert "p_c_haf_35 がない" in capsys.readouterr().err
    assert main([str(tmp_path / "missing.toml")]) == 1
    assert main([str(_write(tmp_path, "phi = [", "broken.toml"))]) == 1

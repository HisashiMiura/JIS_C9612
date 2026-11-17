# JIS C 9612 APF 計算プログラム

[![tests](https://github.com/HisashiMiura/JIS_C9612/actions/workflows/tests.yml/badge.svg)](https://github.com/HisashiMiura/JIS_C9612/actions/workflows/tests.yml)
[![docs](https://app.readthedocs.org/projects/jis-c9612/badge/?version=latest)](https://jis-c9612.readthedocs.io/)

JIS C 9612:2013 (ルームエアコンディショナ) 附属書 B に基づいて、回転数制御形ルームエアコンの通年エネルギー消費効率 (APF) を計算する Python プログラムと、その計算方法を説明するドキュメントである。

- 冷房能力試験・暖房能力試験の値から、冷房期間エネルギー消費効率 (CSPF)、暖房期間エネルギー消費効率 (HSPF)、APF を計算する。
- 計算手順はドキュメント (`docs/`) の「3. 評価方法」に式で示し、プログラムは各式と 1 対 1 に対応させている。
- 規格の記述に解釈が必要な箇所は、採った方法と理由を「4. 評価方法の根拠」に記録している。

## 対象範囲

- 対象は回転数制御形 (インバータ) ルームエアコンだけである。定速単圧縮機形、マルチ形 (附属書 E、F) は扱わない。
- 外気温度の発生時間は、附属書 B の東京の値を用いる。特定地域の値を入力して計算することもできる。
- 試験の方法は扱わない。試験で得た値から APF を計算する部分だけを扱う。

詳しくはドキュメントの「1. はじめに」を参照のこと。

## 必要なもの

- Python 3.12 以上 (計算には標準ライブラリだけを用いる)
- ドキュメントをビルドする場合は Sphinx など (`docs/requirements.txt`)

## インストール

conda を用いる場合は、リポジトリのルートで次を実行する。計算プログラム、テスト、ドキュメントのビルドに必要なものがまとめて入る。

```sh
conda env create -f environment.yml
conda activate JIS_C9612
```

conda を用いない場合は、リポジトリのルートで次を実行する。

```sh
pip install -e .
```

## 使い方

機種の試験値を TOML 形式の入力ファイルに書く。例は [`examples/example_tokyo.toml`](examples/example_tokyo.toml) にある。

```toml
name = "例: 2.8 kW 機"
phi_c_ful_t100 = 2800   # 定格冷房能力 (表示値) (W)

[cooling]               # 冷房能力試験 (外気 35 ℃) の値 (W)
phi_c_ful_35 = 2800
p_c_ful_35 = 700
phi_c_haf_35 = 1400
p_c_haf_35 = 280

[heating]               # 暖房能力試験の値 (W)
phi_h_ful_7 = 3600
p_h_ful_7 = 900
phi_h_haf_7 = 1800
p_h_haf_7 = 360
phi_h_ext_f_2 = 4200    # 最大モードをもつ機種
p_h_ext_f_2 = 1500
```

コマンド `jis-c9612` に入力ファイルを指定して実行する。

```sh
jis-c9612 examples/example_tokyo.toml
```

計算結果の要約を画面に表示し、温度区分ごとの内訳などを CSV ファイルに保存する。

```text
例: 2.8 kW 機
  通年エネルギー消費効率 (APF)           4.8
  冷房期間エネルギー消費効率 (CSPF)      5.4
  暖房期間エネルギー消費効率 (HSPF)      4.5
  冷房期間総合空調負荷 (CSTL)        1,748.8 kWh
  冷房期間消費電力量 (CSEC)            321.8 kWh
  暖房期間総合空調負荷 (HSTL)        3,547.3 kWh
  暖房期間消費電力量 (HSEC)            782.0 kWh
  期間消費電力量                     1,103.9 kWh
```

入力ファイルのすべての項目、オプション、CSV ファイルの中身は、ドキュメントの「2. プログラムの使い方」に示している。

Python のプログラムから直接呼び出すこともできる (例: [`examples/example_tokyo.py`](examples/example_tokyo.py))。

```python
from jis_c9612 import CoolingInput, HeatingInput, compute_apf

cooling = CoolingInput(phi_c_ful_t100=2800, phi_c_ful_35=2800, p_c_ful_35=700,
                       phi_c_haf_35=1400, p_c_haf_35=280)
heating = HeatingInput(phi_c_ful_t100=2800, phi_h_ful_7=3600, p_h_ful_7=900,
                       phi_h_haf_7=1800, p_h_haf_7=360,
                       phi_h_ext_f_2=4200, p_h_ext_f_2=1500)
r = compute_apf(cooling, heating)
print(r.f_ap, r.cooling.f_csp, r.heating.f_hsp)
```

例の値は説明用であり、特定の機種の値ではない。

## ドキュメント

計算方法とプログラムの説明は `docs/` にある (Sphinx + MyST)。Read the Docs で公開している: <https://jis-c9612.readthedocs.io/>

手元でビルドする場合は次のようにする。`docs/_build/html/index.html` ができる。

```sh
cd docs
make html
```

| 章 | 内容 |
|---|---|
| 1. はじめに | 目的、準拠する規格、対象範囲、用語、記号と表記 |
| 2. プログラムの使い方 | 入力ファイル、実行方法、出力 |
| 3. 評価方法 | 冷房期間、暖房期間、APF の計算式 |
| 4. 評価方法の根拠 | 規格の記述から解釈を要した事項と、その理由 |
| 5. 記号の対応 | 本書の記号と附属書 B の記号の対応 |

## 規格の解釈についての注意

附属書 B には、誤記とみられる記述や、明記がない事項がある。本プログラムはそれらを次のように扱っている。詳細と理由はドキュメントの「4. 評価方法の根拠」にある。

- 誤記とみられる 3 か所 (暖房の可変運転・最大運転の消費電力) は、前後の規定と整合するように読んでいる。
- 最大モードをもたない機種は、最大運転を定格運転と同じとみなしている。附属書 B に規定がないため、本書で定めた**暫定**の扱いである。
- 係数で求めると定められた値 (外気 29 ℃、−7 ℃の値など) は、常に係数で求め、実測値は入力として受け付けない。

本プログラムの計算結果は、規格に基づく公式の値を保証するものではない。

## テスト

```sh
python -m pytest
```

各計算段階のテストのほか、プログラムに書いた式番号がドキュメントの式番号と一致するかを確かめるテストがある。

VS Code では、Python 拡張機能を入れ、コマンドパレットの「Python: Select Interpreter」で conda 環境 `JIS_C9612` を選ぶと、テストエクスプローラーからテストを実行できる (設定は `.vscode/settings.json`)。

## リポジトリの構成

| パス | 内容 |
|---|---|
| `src/jis_c9612/` | 計算プログラム |
| `tests/` | テスト (pytest) |
| `examples/` | 入力ファイルの例と、Python から使う例 |
| `docs/` | ドキュメント (Sphinx + MyST)。図は `docs/figures/make_figures.py` で作る |
| `docs/reference/` | JIS 規格の原本を置く場所 (リポジトリには含めない) |
| `DESIGN.md` | 計算プログラムの設計メモ |
| `HANDOFF.md` | 作業の引き継ぎメモ (現在の状況、決定事項、次の作業) |

## JIS 規格の原本について

JIS 規格の原本は著作物であるため、このリポジトリには含めていない。計算方法を確認する場合は、各自で入手した規格を参照すること。開発で用いる場合は `docs/reference/` に置く (`.gitignore` で除外している)。

## 開発に参加する場合

作業を始める前に [`HANDOFF.md`](HANDOFF.md) を読むこと。決定事項 (ドキュメントの書き方、記号と変数名の付け方、docstring とコメントの書き方など) と、現在の状況・次の作業をまとめている。

## ライセンス

[MIT License](LICENSE)

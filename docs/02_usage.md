# プログラムの使い方

本章では、計算プログラム (Python パッケージ `jis_c9612`)の使い方を示す。
計算方法は {doc}`03_method` による。

## 動作環境

Python 3.12 以上で動作する。計算には標準ライブラリだけを用い、外部のライブラリは不要である。

リポジトリのルートで次のように実行すると、conda 環境 `JIS_C9612` が作られ、本プログラムがインストールされる。

```sh
conda env create -f environment.yml
conda activate JIS_C9612
```

conda を用いない場合は、リポジトリのルートで `pip install -e .` を実行する。

## 実行方法

入力ファイルを指定して、コマンド `jis-c9612` を実行する。

```sh
jis-c9612 examples/example_tokyo.toml
```

`python -m jis_c9612 examples/example_tokyo.toml` としても同じである。

計算結果の要約を画面に表示し、温度区分ごとの内訳などを CSV ファイルに保存する ({ref}`usage-output`)。

次のオプションを指定できる。

:::{container} symbols
`-o`, `--output-dir`
: CSV ファイルを保存するディレクトリ。省略すると、入力ファイルと同じディレクトリに保存する

`--no-csv`
: CSV ファイルを保存せず、画面に表示するだけにする
:::

(usage-input)=
## 入力ファイル

入力ファイルは TOML 形式で書く。1 つのファイルに 1 つの機種の値を書く。
例を {numref}`code-usage-input` に示す (`examples/example_tokyo.toml`)。

```{code-block} toml
:name: code-usage-input
:caption: 入力ファイルの例

# 機種の名前 (省略可)。画面と CSV ファイルに表示する
name = "例: 2.8 kW 機"

# 定格冷房能力 (表示値) Φ_c,ful,t100 (W)。冷房・暖房の想定空調負荷に用いる
phi_c_ful_t100 = 2800

[cooling]
# 冷房能力試験 (外気 35 ℃)の値 (W)
phi_c_ful_35 = 2800   # 定格運転能力
p_c_ful_35 = 700      # 定格運転消費電力
phi_c_haf_35 = 1400   # 中間運転能力
p_c_haf_35 = 280      # 中間運転消費電力

[heating]
# 暖房標準能力試験 (外気 7 ℃)の値 (W)
phi_h_ful_7 = 3600    # 定格運転能力
p_h_ful_7 = 900       # 定格運転消費電力
phi_h_haf_7 = 1800    # 中間運転能力
p_h_haf_7 = 360       # 中間運転消費電力

# 暖房低温能力試験 (外気 2 ℃)の値 (W)。最大モードをもつ機種
phi_h_ext_f_2 = 4200  # 最大運転能力
p_h_ext_f_2 = 1500    # 最大運転消費電力
```

各項目は次のとおりである。キーは {doc}`05_symbols` の記号に合わせている。
値の単位は W であり、正の数を書く。

:::{container} symbols
`name`
: 機種の名前 (省略可)

`phi_c_ful_t100`
: 定格冷房能力 (表示値) $\Phi_{\mathrm{c,ful},t100}$

`[cooling]` の `phi_c_ful_35`、`p_c_ful_35`
: 冷房能力試験 (外気 35 ℃)での定格運転能力 $\Phi_\mathrm{c,ful}(35)$、定格運転消費電力 $P_\mathrm{c,ful}(35)$

`[cooling]` の `phi_c_haf_35`、`p_c_haf_35`
: 冷房能力試験 (外気 35 ℃)での中間運転能力 $\Phi_\mathrm{c,haf}(35)$、中間運転消費電力 $P_\mathrm{c,haf}(35)$

`[heating]` の `phi_h_ful_7`、`p_h_ful_7`
: 暖房標準能力試験 (外気 7 ℃)での定格運転能力 $\Phi_\mathrm{h,ful}(7)$、定格運転消費電力 $P_\mathrm{h,ful}(7)$

`[heating]` の `phi_h_haf_7`、`p_h_haf_7`
: 暖房標準能力試験 (外気 7 ℃)での中間運転能力 $\Phi_\mathrm{h,haf}(7)$、中間運転消費電力 $P_\mathrm{h,haf}(7)$

`[heating]` の `phi_h_ext_f_2`、`p_h_ext_f_2`
: 暖房低温能力試験 (外気 2 ℃)での最大運転能力 $\Phi_\mathrm{h,ext,f}(2)$、最大運転消費電力 $P_\mathrm{h,ext,f}(2)$。最大モードをもつ機種だけ書く

`[heating]` の `phi_h_ful_f_2`、`p_h_ful_f_2`
: 暖房低温能力試験 (外気 2 ℃)での定格運転能力 $\Phi_\mathrm{h,ful,f}(2)$、定格運転消費電力 $P_\mathrm{h,ful,f}(2)$。最大モードをもたない機種だけ書く ({ref}`r-h-nomax`)
:::

`[heating]` には、`phi_h_ext_f_2` と `p_h_ext_f_2` の組、または `phi_h_ful_f_2` と `p_h_ful_f_2` の組の、どちらか一方だけを書く。
どちらを書いたかによって、最大モードをもつ機種かどうかを判定する。

上記にないキーを書いた場合、必要なキーがない場合、値が正の数でない場合は、エラーとして計算を止める。
外気 29 ℃や −7 ℃の値など、係数で求める値は入力できない ({ref}`r-c-coef`、{ref}`r-h-coef`)。

### 外気温度の発生時間

外気温度の発生時間は、省略すると東京の値 (附属書 B の表 B.3、表 B.6)を用いる。
特定地域の値を用いる場合は、`[n_c_j]` (冷房期間)と `[n_h_j]` (暖房期間)に、外気温度 $t_j$ (℃)をキー、発生時間 (h)を値として書く。
TOML のキーは文字列なので、外気温度は引用符で囲む。

```{code-block} toml
:caption: 発生時間の書き方の例 (一部)

[n_c_j]
"24" = 161
"25" = 201
"26" = 197

[n_h_j]
"0" = 2
"1" = 5
"-1" = 0
```

`[n_c_j]` と `[n_h_j]` は、それぞれ独立に省略できる。書いた場合は、計算に用いるすべての温度区分を書く。

(usage-output)=
## 出力

### 画面

計算結果の要約を画面に表示する。
通年エネルギー消費効率、冷房期間エネルギー消費効率、暖房期間エネルギー消費効率は、小数第 2 位を四捨五入して小数第 1 位まで表示する。
CSV ファイルには丸めない値を保存する。

```{code-block} text
:caption: 画面の表示の例

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

### CSV ファイル

入力ファイルの名前 (拡張子を除く)を先頭に付けた、次の 3 つの CSV ファイルを保存する。
文字コードは BOM 付きの UTF-8 とし、表計算ソフトでそのまま開けるようにしている。
各列の見出しには、{doc}`05_symbols` の記号と単位を書く。

:::{container} symbols
`<名前>_summary.csv`
: 要約。APF、CSPF、HSPF、期間の合計、交点温度など

`<名前>_cooling.csv`
: 冷房期間の温度区分ごとの値。外気温度、発生時間、運転状態、想定冷房空調負荷、処理する空調負荷、消費電力、運転率、部分負荷率、可変運転のエネルギー消費効率

`<名前>_heating.csv`
: 暖房期間の温度区分ごとの値。外気温度、発生時間、着霜領域かどうか、運転状態、想定暖房空調負荷、消費電力、補助電熱装置の消費電力、運転率、部分負荷率、可変運転のエネルギー消費効率
:::

温度区分ごとの CSV ファイルの値に発生時間を掛けて合計すると、要約の期間の合計 (CSTL、CSEC、HSTL、HSEC)に一致する。

## Python から使う

計算は、Python のプログラムから直接呼び出すこともできる。

```{code-block} python
:caption: Python から使う例

from jis_c9612 import CoolingInput, HeatingInput, compute_apf

cooling = CoolingInput(phi_c_ful_t100=2800, phi_c_ful_35=2800, p_c_ful_35=700,
                       phi_c_haf_35=1400, p_c_haf_35=280)
heating = HeatingInput(phi_c_ful_t100=2800, phi_h_ful_7=3600, p_h_ful_7=900,
                       phi_h_haf_7=1800, p_h_haf_7=360,
                       phi_h_ext_f_2=4200, p_h_ext_f_2=1500)
r = compute_apf(cooling, heating)
print(r.f_ap, r.cooling.f_csp, r.heating.f_hsp)
```

`compute_apf` の結果は、APF (`f_ap`)、冷房期間の結果 (`cooling`)、暖房期間の結果 (`heating`)をもつ。
それぞれの項目は、関数とクラスの docstring に記述している。

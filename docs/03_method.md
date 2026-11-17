# 評価方法

本章では、本プログラムが実装する計算方法を示す。
計算方法は JIS C 9612:2013 附属書 B (以下、附属書 B)による。
各式の上の説明文には、対応する附属書 B の式番号を示す。
附属書 B と異なる解釈をとった箇所、附属書 B に明記がない事項は、{doc}`04_rationale` に記録した。
本書では、冷房期間と暖房期間で意味が変わる記号に、冷房は添字 c、暖房は添字 h を付けて書き分ける (例: 定格運転能力 $\Phi_\mathrm{c,ful}(t)$、$\Phi_\mathrm{h,ful}(t)$)。附属書 B の記号には c、h は付いていない。

## 概要

### 通年エネルギー消費効率

通年エネルギー消費効率 (APF)$F_\mathrm{AP}$ は、冷房期間と暖房期間を通じた空調負荷の合計を、消費電力量の合計で割って求める (附属書 B の式 (B.76))。

$$
F_\mathrm{AP} = \frac{L_\mathrm{CST} + L_\mathrm{HST}}{C_\mathrm{CSE} + C_\mathrm{HSE}}
$$ (eq-apf)

:::{container} where
ここに、

$F_\mathrm{AP}$
: 通年エネルギー消費効率 (APF) (−)

$L_\mathrm{CST}$
: 冷房期間総合空調負荷 (CSTL) (Wh)

$C_\mathrm{CSE}$
: 冷房期間消費電力量 (CSEC) (Wh)

$L_\mathrm{HST}$
: 暖房期間総合空調負荷 (HSTL) (Wh)

$C_\mathrm{HSE}$
: 暖房期間消費電力量 (HSEC) (Wh)

である。
:::

### 計算の流れ

冷房期間・暖房期間とも、次の順に計算する。

1. **試験値の補完**:附属書 B で試験を行わないと定められた値を、試験値に係数を掛けて求める。
2. **能力・消費電力の特性**:2 つの外気温度での値を結ぶ直線で、各外気温度での能力と消費電力を表す。
3. **想定空調負荷**:外気温度に比例する負荷線で、各外気温度での空調負荷を表す。
4. **交点温度**:空調負荷と能力が等しくなる外気温度を求める。可変運転域の効率の補間に使う。
5. **温度区分ごとの計算**:外気温度の温度区分 $j$ ごとに運転状態を判定し、空調負荷と消費電力を求める。
6. **期間合計**:各温度区分の値に発生時間 $n_j$ を掛けて合計する。

本章の記述は、計算の順とは逆に、求める値の式を先に示し、その式で用いる値を後の式で定義する順とする。

### 対象とする機種

本プログラムは、回転数制御形ルームエアコンだけを対象とする。
回転数制御形は、負荷に応じて圧縮機の回転数を一定の範囲で 3 段階以上または連続的に変えられる機種である (JIS C 9612:2013 の 3.12)。
附属書 B のうち、回転数制御形の計算方法 (B.1.6.5、B.2.6.5)を実装し、定速単圧縮機形の計算方法 (B.1.6.4、B.2.6.4)は実装しない ({ref}`scope`)。

## 冷房期間

### 入力値

冷房期間の計算に用いる入力値を次に示す。

:::{container} symbols
$\Phi_{\mathrm{c,ful},t100}$
: 定格冷房能力 (表示値) (W)

$\Phi_\mathrm{c,ful}(35)$
: 冷房能力試験 (外気 35 ℃)での定格運転能力 (W)

$P_\mathrm{c,ful}(35)$
: 冷房能力試験 (外気 35 ℃)での定格運転消費電力 (W)

$\Phi_\mathrm{c,haf}(35)$
: 冷房能力試験 (外気 35 ℃)での中間運転能力 (W)

$P_\mathrm{c,haf}(35)$
: 冷房能力試験 (外気 35 ℃)での中間運転消費電力 (W)
:::

中間運転能力は、定格冷房能力 (表示値)の 50 % (許容範囲 45 %〜55 %)で測定した値とする (附属書 B の B.1.5.3.1)。
最小運転能力・消費電力は、冷房期間の計算に用いない ({ref}`r-c-min`)。

### 冷房期間エネルギー消費効率

冷房期間エネルギー消費効率 (CSPF)$F_\mathrm{CSP}$ は、次式による (附属書 B の式 (B.1))。

$$
F_\mathrm{CSP} = \frac{L_\mathrm{CST}}{C_\mathrm{CSE}}
$$ (eq-cspf)

:::{container} where
ここに、

$F_\mathrm{CSP}$
: 冷房期間エネルギー消費効率 (CSPF) (−)

$L_\mathrm{CST}$
: 冷房期間総合空調負荷 (CSTL) (Wh)

$C_\mathrm{CSE}$
: 冷房期間消費電力量 (CSEC) (Wh)

である。
:::

### 冷房期間総合空調負荷と冷房期間消費電力量

冷房期間総合空調負荷 $L_\mathrm{CST}$ と冷房期間消費電力量 $C_\mathrm{CSE}$ は、温度区分ごとの値に発生時間を掛けて合計する (附属書 B の式 (B.5)、(B.11)、{ref}`r-c-cstl`)。

$$
L_\mathrm{CST} = \sum_j Q_\mathrm{c}(t_j)\,n_{\mathrm{c},j}
$$ (eq-cstl)

:::{container} where
ここに、

$L_\mathrm{CST}$
: 冷房期間総合空調負荷 (CSTL) (Wh)

$Q_\mathrm{c}(t_j)$
: 温度区分 $j$ において処理する空調負荷 (W)

$n_{\mathrm{c},j}$
: 温度区分 $j$ の発生時間 (h)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

$$
C_\mathrm{CSE} = \sum_j P_\mathrm{c}(t_j)\,n_{\mathrm{c},j}
$$ (eq-csec)

:::{container} where
ここに、

$C_\mathrm{CSE}$
: 冷房期間消費電力量 (CSEC) (Wh)

$P_\mathrm{c}(t_j)$
: 温度区分 $j$ における消費電力 (W)

$n_{\mathrm{c},j}$
: 温度区分 $j$ の発生時間 (h)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

### 外気温度の発生時間

外気温度 $t_j$ とその発生時間 $n_{\mathrm{c},j}$ は、附属書 B の表 B.3 (東京)による ({numref}`tbl-c-bins`)。
特定地域の値を用いる場合は、附属書 B の B.1.9 による。

```{list-table} 冷房期間の外気温度の発生時間 (東京)
:name: tbl-c-bins
:header-rows: 1
:stub-columns: 1

* - $t_j$ (℃)
  - 24
  - 25
  - 26
  - 27
  - 28
  - 29
  - 30
  - 31
  - 32
  - 33
  - 34
  - 35
  - 36
  - 37
  - 38
* - $n_{\mathrm{c},j}$ (h)
  - 161
  - 201
  - 197
  - 191
  - 213
  - 182
  - 166
  - 123
  - 86
  - 39
  - 10
  - 0
  - 0
  - 0
  - 0
```

発生時間の合計は 1 569 h である。

### 温度区分ごとの空調負荷と消費電力

温度区分 $j$ ごとに、想定冷房空調負荷 $L_\mathrm{c}(t_j)$ を中間運転能力 $\Phi_\mathrm{c,haf}(t_j)$ と定格運転能力 $\Phi_\mathrm{c,ful}(t_j)$ に比べて、運転状態を断続運転、可変運転、定格運転のいずれかに判定する ({numref}`fig-c-regions`、{ref}`r-region`)。

```{figure} figures/cooling_regions.svg
:name: fig-c-regions
:width: 100%

想定冷房空調負荷、運転能力、交点温度と運転状態の関係 (冷房)

数値は説明用の例である (定格冷房能力 (表示値) 2 800 W、中間運転能力 (35 ℃) 1 400 W)。
```

処理する空調負荷 $Q_\mathrm{c}(t_j)$ は、負荷が定格運転能力以下なら想定冷房空調負荷そのものとし、定格運転能力を超えるときは定格運転能力とする (附属書 B の式 (B.5))。

$$
Q_\mathrm{c}(t_j) =
\begin{cases}
L_\mathrm{c}(t_j) & \text{($L_\mathrm{c}(t_j) \le \Phi_\mathrm{c,ful}(t_j)$ のとき)} \\
\Phi_\mathrm{c,ful}(t_j) & \text{($L_\mathrm{c}(t_j) > \Phi_\mathrm{c,ful}(t_j)$ のとき)}
\end{cases}
$$ (eq-c-l)

:::{container} where
ここに、

$Q_\mathrm{c}(t_j)$
: 温度区分 $j$ において処理する空調負荷 (W)

$L_\mathrm{c}(t_j)$
: 外気温度 $t_j$ における想定冷房空調負荷 (W)

$\Phi_\mathrm{c,ful}(t_j)$
: 外気温度 $t_j$ における定格運転能力 (W)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

消費電力 $P_\mathrm{c}(t_j)$ は、運転状態ごとに次式による (附属書 B の式 (B.11))。

$$
P_\mathrm{c}(t_j) =
\begin{cases}
\dfrac{X_\mathrm{c}(t_j)\,P_\mathrm{c,haf}(t_j)}{F_\mathrm{c,PL}(t_j)} & \text{(断続運転: $L_\mathrm{c}(t_j) \le \Phi_\mathrm{c,haf}(t_j)$ のとき)} \\[2ex]
P_\mathrm{c,hf}(t_j) & \text{(可変運転: $\Phi_\mathrm{c,haf}(t_j) < L_\mathrm{c}(t_j) \le \Phi_\mathrm{c,ful}(t_j)$ のとき)} \\[1ex]
P_\mathrm{c,ful}(t_j) & \text{(定格運転: $L_\mathrm{c}(t_j) > \Phi_\mathrm{c,ful}(t_j)$ のとき)}
\end{cases}
$$ (eq-c-p)

:::{container} where
ここに、

$P_\mathrm{c}(t_j)$
: 温度区分 $j$ における消費電力 (W)

$X_\mathrm{c}(t_j)$
: 外気温度 $t_j$ における運転率 (−)

$P_\mathrm{c,haf}(t_j)$
: 外気温度 $t_j$ における中間運転消費電力 (W)

$F_\mathrm{c,PL}(t_j)$
: 外気温度 $t_j$ における部分負荷率 (−)

$P_\mathrm{c,hf}(t_j)$
: 外気温度 $t_j$ で可変運転したときの消費電力 (W)

$P_\mathrm{c,ful}(t_j)$
: 外気温度 $t_j$ における定格運転消費電力 (W)

$L_\mathrm{c}(t_j)$
: 外気温度 $t_j$ における想定冷房空調負荷 (W)

$\Phi_\mathrm{c,haf}(t_j)$
: 外気温度 $t_j$ における中間運転能力 (W)

$\Phi_\mathrm{c,ful}(t_j)$
: 外気温度 $t_j$ における定格運転能力 (W)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

外気温度と消費電力の関係の例を {numref}`fig-c-power` に示す。

```{figure} figures/cooling_power.svg
:name: fig-c-power
:width: 100%

外気温度と消費電力の関係 (冷房)

数値は説明用の例である ({numref}`fig-c-regions` の例に、定格運転消費電力 (35 ℃) 700 W、中間運転消費電力 (35 ℃) 280 W を加えた)。点は温度区分ごとの値、破線は定格運転・中間運転の消費電力特性を示す。
```

#### 断続運転

想定冷房空調負荷が中間運転能力以下のときは、中間運転能力で運転と停止を繰り返して負荷に合わせる。JIS C 9612:2013 の附属書 B は、中間運転能力より小さい負荷では、中間運転能力で断続運転すると仮定している (B.1.6.5.5 a))。

断続運転のときの消費電力は、次の考え方で求める。

1. 運転している時間の割合を運転率 $X_\mathrm{c}(t_j)$ とする。運転率は、想定冷房空調負荷と中間運転能力の比である。たとえば負荷が中間運転能力の半分なら、運転率は 0.5 であり、時間の半分だけ運転すれば負荷を処理できる。
2. 運転している間の消費電力は中間運転消費電力 $P_\mathrm{c,haf}(t_j)$ なので、効率が変わらなければ、平均の消費電力は $X_\mathrm{c}(t_j)\,P_\mathrm{c,haf}(t_j)$ となる。
3. 実際には、起動のたびに損失が生じ、運転と停止を繰り返すと効率が下がる。この効率の低下を部分負荷率 $F_\mathrm{c,PL}(t_j)$ (1 以下の値)で表し、$X_\mathrm{c}(t_j)\,P_\mathrm{c,haf}(t_j)$ を $F_\mathrm{c,PL}(t_j)$ で割って消費電力を大きくする。停止している時間が長い (運転率が小さい)ほど、効率の低下は大きい。

例として、{numref}`fig-c-power` の外気温度 26 ℃では、想定冷房空調負荷 700 W、中間運転能力 1 561.7 W、中間運転消費電力 243.9 W である。運転率は 700 / 1 561.7 = 0.448、効率が変わらない場合の消費電力は 0.448 × 243.9 = 109.3 W、部分負荷率は 1 − 0.25 × (1 − 0.448) = 0.862 であり、消費電力は 109.3 / 0.862 = 126.8 W となる。

部分負荷率と運転率は、次式による (附属書 B の式 (B.8)、(B.7))。

部分負荷率 $F_\mathrm{c,PL}(t_j)$ は、効率低下係数 $C_\mathrm{c,D}$ を用いて次式で求める。効率低下係数は、断続運転によって生じる効率の低下を表す係数であり、試験を行わず 0.25 とする (附属書 B の表 B.1、B.1.5.3.3)。

$$
F_\mathrm{c,PL}(t_j) = 1 - C_\mathrm{c,D}\,[1 - X_\mathrm{c}(t_j)]
$$ (eq-c-plf)

:::{container} where
ここに、

$F_\mathrm{c,PL}(t_j)$
: 外気温度 $t_j$ における部分負荷率 (−)

$C_\mathrm{c,D}$
: 効率低下係数。0.25 とする (−)

$X_\mathrm{c}(t_j)$
: 外気温度 $t_j$ における運転率 (−)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

部分負荷率と運転率の関係を {numref}`fig-c-plf` に示す。運転率が小さい (停止している時間が長い)ほど、部分負荷率は小さくなる。運転率が 0 に近づくと、部分負荷率は $1 - C_\mathrm{c,D} = 0.75$ に近づく。

```{figure} figures/cooling_plf.svg
:name: fig-c-plf
:width: 80%

運転率と部分負荷率の関係 ($C_\mathrm{c,D} = 0.25$)

点は {numref}`fig-c-power` の例の外気温度 26 ℃における値を示す。
```

運転率 $X_\mathrm{c}(t_j)$ は、想定冷房空調負荷と中間運転能力の比であり、次式による (附属書 B の式 (B.7))。

$$
X_\mathrm{c}(t_j) = \frac{L_\mathrm{c}(t_j)}{\Phi_\mathrm{c,haf}(t_j)}
$$ (eq-c-x)

:::{container} where
ここに、

$X_\mathrm{c}(t_j)$
: 外気温度 $t_j$ における運転率 (−)

$L_\mathrm{c}(t_j)$
: 外気温度 $t_j$ における想定冷房空調負荷 (W)

$\Phi_\mathrm{c,haf}(t_j)$
: 外気温度 $t_j$ における中間運転能力 (W)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

#### 可変運転

想定冷房空調負荷が中間運転能力を超え、定格運転能力以下のときは、能力を連続的に変えて、負荷とつり合う能力で運転する。

可変運転での消費電力 $P_\mathrm{c,hf}(t_j)$ は、想定冷房空調負荷を可変運転のエネルギー消費効率で割って求める (附属書 B の式 (B.15))。

$$
P_\mathrm{c,hf}(t_j) = \frac{L_\mathrm{c}(t_j)}{E_\mathrm{ER,hf}(t_j)}
$$ (eq-c-phf)

:::{container} where
ここに、

$P_\mathrm{c,hf}(t_j)$
: 外気温度 $t_j$ で可変運転したときの消費電力 (W)

$L_\mathrm{c}(t_j)$
: 外気温度 $t_j$ における想定冷房空調負荷 (W)

$E_\mathrm{ER,hf}(t_j)$
: 外気温度 $t_j$ で可変運転したときのエネルギー消費効率 (−)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

可変運転のエネルギー消費効率 $E_\mathrm{ER,hf}(t_j)$ は、交点温度 $t_\mathrm{c}$ での中間運転のエネルギー消費効率と、交点温度 $t_\mathrm{b}$ での定格運転のエネルギー消費効率の間を、外気温度で直線補間して求める (附属書 B の式 (B.14))。

$$
E_\mathrm{ER,hf}(t_j) = E_\mathrm{ER,haf}(t_\mathrm{c})
+ \frac{E_\mathrm{ER,ful}(t_\mathrm{b}) - E_\mathrm{ER,haf}(t_\mathrm{c})}{t_\mathrm{b} - t_\mathrm{c}}\,(t_j - t_\mathrm{c})
$$ (eq-c-eer-hf)

:::{container} where
ここに、

$E_\mathrm{ER,hf}(t_j)$
: 外気温度 $t_j$ で可変運転したときのエネルギー消費効率 (−)

$E_\mathrm{ER,haf}(t_\mathrm{c})$
: 外気温度 $t_\mathrm{c}$ における中間運転のエネルギー消費効率 (−)

$E_\mathrm{ER,ful}(t_\mathrm{b})$
: 外気温度 $t_\mathrm{b}$ における定格運転のエネルギー消費効率 (−)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

$t_\mathrm{b}$
: 想定冷房空調負荷と定格運転能力が等しくなる外気温度 (℃)

$t_\mathrm{c}$
: 想定冷房空調負荷と中間運転能力が等しくなる外気温度 (℃)

である。
:::

可変運転のエネルギー消費効率の例を {numref}`fig-c-eer` に示す。$t_\mathrm{c}$ では中間運転のエネルギー消費効率に、$t_\mathrm{b}$ では定格運転のエネルギー消費効率に一致し、その間を直線で結ぶ。

```{figure} figures/cooling_eer.svg
:name: fig-c-eer
:width: 100%

可変運転のエネルギー消費効率の補間 (冷房)

数値は {numref}`fig-c-power` と同じ例である。破線は、中間運転・定格運転で連続運転したときのエネルギー消費効率を参考として示す。
```

交点温度でのエネルギー消費効率は、次式による (附属書 B の式 (B.12)、(B.13))。

$$
E_\mathrm{ER,haf}(t_\mathrm{c}) = \frac{\Phi_\mathrm{c,haf}(t_\mathrm{c})}{P_\mathrm{c,haf}(t_\mathrm{c})}
$$ (eq-c-eer-haf)

:::{container} where
ここに、

$E_\mathrm{ER,haf}(t_\mathrm{c})$
: 外気温度 $t_\mathrm{c}$ における中間運転のエネルギー消費効率 (−)

$\Phi_\mathrm{c,haf}(t_\mathrm{c})$
: 外気温度 $t_\mathrm{c}$ における中間運転能力 (W)

$P_\mathrm{c,haf}(t_\mathrm{c})$
: 外気温度 $t_\mathrm{c}$ における中間運転消費電力 (W)

$t_\mathrm{c}$
: 想定冷房空調負荷と中間運転能力が等しくなる外気温度 (℃)

である。
:::

$$
E_\mathrm{ER,ful}(t_\mathrm{b}) = \frac{\Phi_\mathrm{c,ful}(t_\mathrm{b})}{P_\mathrm{c,ful}(t_\mathrm{b})}
$$ (eq-c-eer-ful)

:::{container} where
ここに、

$E_\mathrm{ER,ful}(t_\mathrm{b})$
: 外気温度 $t_\mathrm{b}$ における定格運転のエネルギー消費効率 (−)

$\Phi_\mathrm{c,ful}(t_\mathrm{b})$
: 外気温度 $t_\mathrm{b}$ における定格運転能力 (W)

$P_\mathrm{c,ful}(t_\mathrm{b})$
: 外気温度 $t_\mathrm{b}$ における定格運転消費電力 (W)

$t_\mathrm{b}$
: 想定冷房空調負荷と定格運転能力が等しくなる外気温度 (℃)

である。
:::

#### 定格運転

想定冷房空調負荷が定格運転能力を超えるときは、定格運転能力で連続運転する。空調負荷は定格運転能力までしか処理されず、消費電力は定格運転消費電力 $P_\mathrm{c,ful}(t_j)$ となる ({ref}`r-c-cstl`)。$\Phi_\mathrm{c,ful}(t_j)$ と $P_\mathrm{c,ful}(t_j)$ は、{eq}`eq-c-cap-ful` と {eq}`eq-c-pow-ful` による。

### 交点温度

外気温度が高くなるほど、想定冷房空調負荷 $L_\mathrm{c}(t)$ は大きくなり、運転能力は小さくなる。このため、ある外気温度で負荷と能力が等しくなる ({numref}`fig-c-regions`)。この外気温度を交点温度と呼び、次の 2 つを用いる。

:::{container} symbols
$t_\mathrm{c}$
: 想定冷房空調負荷と中間運転能力が等しくなる外気温度

$t_\mathrm{b}$
: 想定冷房空調負荷と定格運転能力が等しくなる外気温度
:::

外気温度が $t_\mathrm{c}$ より低いと、負荷が中間運転能力より小さいので断続運転になる。$t_\mathrm{c}$ から $t_\mathrm{b}$ までは、負荷に合わせて中間運転能力と定格運転能力の間で可変運転する。$t_\mathrm{b}$ より高いと、負荷が定格運転能力を超える。交点温度は、可変運転のエネルギー消費効率を補間する {eq}`eq-c-eer-hf` で、補間の両端として用いる。

交点温度 $t_\mathrm{b}$ と $t_\mathrm{c}$ は、それぞれ次の関係を満たす。

$$
L_\mathrm{c}(t_\mathrm{b}) = \Phi_\mathrm{c,ful}(t_\mathrm{b})
$$ (eq-c-tb-def)

:::{container} where
ここに、

$L_\mathrm{c}(t_\mathrm{b})$
: 外気温度 $t_\mathrm{b}$ における想定冷房空調負荷。{eq}`eq-c-load` による (W)

$\Phi_\mathrm{c,ful}(t_\mathrm{b})$
: 外気温度 $t_\mathrm{b}$ における定格運転能力。{eq}`eq-c-cap-ful` による (W)

$t_\mathrm{b}$
: 想定冷房空調負荷と定格運転能力が等しくなる外気温度 (℃)

である。
:::

$$
L_\mathrm{c}(t_\mathrm{c}) = \Phi_\mathrm{c,haf}(t_\mathrm{c})
$$ (eq-c-tc-def)

:::{container} where
ここに、

$L_\mathrm{c}(t_\mathrm{c})$
: 外気温度 $t_\mathrm{c}$ における想定冷房空調負荷。{eq}`eq-c-load` による (W)

$\Phi_\mathrm{c,haf}(t_\mathrm{c})$
: 外気温度 $t_\mathrm{c}$ における中間運転能力。{eq}`eq-c-cap-haf` による (W)

$t_\mathrm{c}$
: 想定冷房空調負荷と中間運転能力が等しくなる外気温度 (℃)

である。
:::

負荷も能力も外気温度の 1 次式なので、上の関係を外気温度について解くと、交点温度は次式で求まる (附属書 B の式 (B.20)、(B.22)、{ref}`r-intersection`)。式中の 6 は、能力の 2 つの試験温度 35 ℃と 29 ℃の差である。

$$
t_\mathrm{b} = \frac{6\,\Phi_{\mathrm{c,ful},t100}\,t_{\mathrm{c},0} + 6\,\Phi_\mathrm{c,ful}(35)\,(t_{\mathrm{c},100} - t_{\mathrm{c},0}) + 35\,[\Phi_\mathrm{c,ful}(29) - \Phi_\mathrm{c,ful}(35)]\,(t_{\mathrm{c},100} - t_{\mathrm{c},0})}{6\,\Phi_{\mathrm{c,ful},t100} + [\Phi_\mathrm{c,ful}(29) - \Phi_\mathrm{c,ful}(35)]\,(t_{\mathrm{c},100} - t_{\mathrm{c},0})}
$$ (eq-c-tb)

:::{container} where
ここに、

$t_\mathrm{b}$
: 想定冷房空調負荷と定格運転能力が等しくなる外気温度 (℃)

$\Phi_{\mathrm{c,ful},t100}$
: 定格冷房能力 (表示値) (W)

$\Phi_\mathrm{c,ful}(35)$
: 外気温度 35 ℃における定格運転能力 (W)

$\Phi_\mathrm{c,ful}(29)$
: 外気温度 29 ℃における定格運転能力 (W)

$t_{\mathrm{c},0}$
: 想定冷房空調負荷が 0 となる外気温度。23 ℃とする (℃)

$t_{\mathrm{c},100}$
: 想定冷房空調負荷が定格冷房能力と等しくなる外気温度。35 ℃とする (℃)

である。
:::

$$
t_\mathrm{c} = \frac{6\,\Phi_{\mathrm{c,ful},t100}\,t_{\mathrm{c},0} + 6\,\Phi_\mathrm{c,haf}(35)\,(t_{\mathrm{c},100} - t_{\mathrm{c},0}) + 35\,[\Phi_\mathrm{c,haf}(29) - \Phi_\mathrm{c,haf}(35)]\,(t_{\mathrm{c},100} - t_{\mathrm{c},0})}{6\,\Phi_{\mathrm{c,ful},t100} + [\Phi_\mathrm{c,haf}(29) - \Phi_\mathrm{c,haf}(35)]\,(t_{\mathrm{c},100} - t_{\mathrm{c},0})}
$$ (eq-c-tc)

:::{container} where
ここに、

$t_\mathrm{c}$
: 想定冷房空調負荷と中間運転能力が等しくなる外気温度 (℃)

$\Phi_{\mathrm{c,ful},t100}$
: 定格冷房能力 (表示値) (W)

$\Phi_\mathrm{c,haf}(35)$
: 外気温度 35 ℃における中間運転能力 (W)

$\Phi_\mathrm{c,haf}(29)$
: 外気温度 29 ℃における中間運転能力 (W)

$t_{\mathrm{c},0}$
: 想定冷房空調負荷が 0 となる外気温度。23 ℃とする (℃)

$t_{\mathrm{c},100}$
: 想定冷房空調負荷が定格冷房能力と等しくなる外気温度。35 ℃とする (℃)

である。
:::

### 想定冷房空調負荷

外気温度 $t$ における想定冷房空調負荷 $L_\mathrm{c}(t)$ は、外気温度 $t_{\mathrm{c},0}$ で 0、$t_{\mathrm{c},100}$ で定格冷房能力 (表示値)となる直線とする (附属書 B の式 (B.2)、(B.16))。

$$
L_\mathrm{c}(t) = \Phi_{\mathrm{c,ful},t100} \times \frac{t - t_{\mathrm{c},0}}{t_{\mathrm{c},100} - t_{\mathrm{c},0}}
$$ (eq-c-load)

:::{container} where
ここに、

$L_\mathrm{c}(t)$
: 外気温度 $t$ における想定冷房空調負荷 (W)

$\Phi_{\mathrm{c,ful},t100}$
: 定格冷房能力 (表示値) (W)

$t$
: 外気温度 (℃)

$t_{\mathrm{c},0}$
: 想定冷房空調負荷が 0 となる外気温度 (℃)

$t_{\mathrm{c},100}$
: 想定冷房空調負荷が定格冷房能力と等しくなる外気温度 (℃)

である。
:::

なお、$t_{\mathrm{c},0} = 23$ ℃、$t_{\mathrm{c},100} = 35$ ℃ とする。

### 能力・消費電力の特性

外気温度 $t$ における能力と消費電力は、外気 35 ℃と 29 ℃の値を結ぶ直線とする。特性線は、定格運転と中間運転の 2 本を用いる。

定格運転能力 $\Phi_\mathrm{c,ful}(t)$ と定格運転消費電力 $P_\mathrm{c,ful}(t)$ は、次式による (附属書 B の式 (B.3)、(B.4))。

$$
\Phi_\mathrm{c,ful}(t) = \Phi_\mathrm{c,ful}(35) + \frac{\Phi_\mathrm{c,ful}(29) - \Phi_\mathrm{c,ful}(35)}{29 - 35}\,(t - 35)
$$ (eq-c-cap-ful)

:::{container} where
ここに、

$\Phi_\mathrm{c,ful}(t)$
: 外気温度 $t$ における定格運転能力 (W)

$\Phi_\mathrm{c,ful}(35)$
: 外気温度 35 ℃における定格運転能力 (W)

$\Phi_\mathrm{c,ful}(29)$
: 外気温度 29 ℃における定格運転能力 (W)

$t$
: 外気温度 (℃)

である。
:::

$$
P_\mathrm{c,ful}(t) = P_\mathrm{c,ful}(35) + \frac{P_\mathrm{c,ful}(29) - P_\mathrm{c,ful}(35)}{29 - 35}\,(t - 35)
$$ (eq-c-pow-ful)

:::{container} where
ここに、

$P_\mathrm{c,ful}(t)$
: 外気温度 $t$ における定格運転消費電力 (W)

$P_\mathrm{c,ful}(35)$
: 外気温度 35 ℃における定格運転消費電力 (W)

$P_\mathrm{c,ful}(29)$
: 外気温度 29 ℃における定格運転消費電力 (W)

$t$
: 外気温度 (℃)

である。
:::

中間運転能力 $\Phi_\mathrm{c,haf}(t)$ と中間運転消費電力 $P_\mathrm{c,haf}(t)$ は、次式による (附属書 B の式 (B.9)、(B.10))。

$$
\Phi_\mathrm{c,haf}(t) = \Phi_\mathrm{c,haf}(35) + \frac{\Phi_\mathrm{c,haf}(29) - \Phi_\mathrm{c,haf}(35)}{29 - 35}\,(t - 35)
$$ (eq-c-cap-haf)

:::{container} where
ここに、

$\Phi_\mathrm{c,haf}(t)$
: 外気温度 $t$ における中間運転能力 (W)

$\Phi_\mathrm{c,haf}(35)$
: 外気温度 35 ℃における中間運転能力 (W)

$\Phi_\mathrm{c,haf}(29)$
: 外気温度 29 ℃における中間運転能力 (W)

$t$
: 外気温度 (℃)

である。
:::

$$
P_\mathrm{c,haf}(t) = P_\mathrm{c,haf}(35) + \frac{P_\mathrm{c,haf}(29) - P_\mathrm{c,haf}(35)}{29 - 35}\,(t - 35)
$$ (eq-c-pow-haf)

:::{container} where
ここに、

$P_\mathrm{c,haf}(t)$
: 外気温度 $t$ における中間運転消費電力 (W)

$P_\mathrm{c,haf}(35)$
: 外気温度 35 ℃における中間運転消費電力 (W)

$P_\mathrm{c,haf}(29)$
: 外気温度 29 ℃における中間運転消費電力 (W)

$t$
: 外気温度 (℃)

である。
:::

### 試験値の補完

外気 29 ℃での値は、外気 35 ℃の試験値に係数を掛けて求める (附属書 B の表 B.1、{ref}`r-c-coef`)。

定格運転能力 $\Phi_\mathrm{c,ful}(29)$ と定格運転消費電力 $P_\mathrm{c,ful}(29)$ は、次式による。

$$
\Phi_\mathrm{c,ful}(29) = 1.077 \times \Phi_\mathrm{c,ful}(35)
$$ (eq-c-cap29-ful)

:::{container} where
ここに、

$\Phi_\mathrm{c,ful}(29)$
: 外気温度 29 ℃における定格運転能力 (W)

$\Phi_\mathrm{c,ful}(35)$
: 外気温度 35 ℃における定格運転能力 (W)

である。
:::

$$
P_\mathrm{c,ful}(29) = 0.914 \times P_\mathrm{c,ful}(35)
$$ (eq-c-pow29-ful)

:::{container} where
ここに、

$P_\mathrm{c,ful}(29)$
: 外気温度 29 ℃における定格運転消費電力 (W)

$P_\mathrm{c,ful}(35)$
: 外気温度 35 ℃における定格運転消費電力 (W)

である。
:::

中間運転能力 $\Phi_\mathrm{c,haf}(29)$ と中間運転消費電力 $P_\mathrm{c,haf}(29)$ は、次式による。

$$
\Phi_\mathrm{c,haf}(29) = 1.077 \times \Phi_\mathrm{c,haf}(35)
$$ (eq-c-cap29-haf)

:::{container} where
ここに、

$\Phi_\mathrm{c,haf}(29)$
: 外気温度 29 ℃における中間運転能力 (W)

$\Phi_\mathrm{c,haf}(35)$
: 外気温度 35 ℃における中間運転能力 (W)

である。
:::

$$
P_\mathrm{c,haf}(29) = 0.914 \times P_\mathrm{c,haf}(35)
$$ (eq-c-pow29-haf)

:::{container} where
ここに、

$P_\mathrm{c,haf}(29)$
: 外気温度 29 ℃における中間運転消費電力 (W)

$P_\mathrm{c,haf}(35)$
: 外気温度 35 ℃における中間運転消費電力 (W)

である。
:::

## 暖房期間

### 入力値

暖房期間の計算に用いる入力値を次に示す。

:::{container} symbols
$\Phi_{\mathrm{c,ful},t100}$
: 定格冷房能力 (表示値) (W)

$\Phi_\mathrm{h,ful}(7)$
: 暖房標準能力試験 (外気 7 ℃)での定格運転能力 (W)

$P_\mathrm{h,ful}(7)$
: 暖房標準能力試験 (外気 7 ℃)での定格運転消費電力 (W)

$\Phi_\mathrm{h,haf}(7)$
: 暖房標準能力試験 (外気 7 ℃)での中間運転能力 (W)

$P_\mathrm{h,haf}(7)$
: 暖房標準能力試験 (外気 7 ℃)での中間運転消費電力 (W)

$\Phi_\mathrm{h,ext,f}(2)$
: 暖房低温能力試験 (外気 2 ℃)での最大運転能力 (W)

$P_\mathrm{h,ext,f}(2)$
: 暖房低温能力試験 (外気 2 ℃)での最大運転消費電力 (W)
:::

想定暖房空調負荷は、定格暖房能力ではなく、定格冷房能力 (表示値)から求める (附属書 B の表 B.5)。

中間運転能力は、定格暖房能力 (表示値)の 50 % (許容範囲 45 %〜55 %)で測定した値とする (附属書 B の B.2.5.3.1)。最小運転能力・消費電力は、暖房期間の計算に用いない。

最大モードをもたない機種では、$\Phi_\mathrm{h,ext,f}(2)$ と $P_\mathrm{h,ext,f}(2)$ の代わりに、暖房低温能力試験 (外気 2 ℃)での定格運転能力 $\Phi_\mathrm{h,ful,f}(2)$ と定格運転消費電力 $P_\mathrm{h,ful,f}(2)$ を入力する (附属書 B の表 B.4 注 a)、{ref}`r-h-nomax`)。

### 暖房期間エネルギー消費効率

暖房期間エネルギー消費効率 (HSPF)$F_\mathrm{HSP}$ は、次式による (附属書 B の式 (B.27))。

$$
F_\mathrm{HSP} = \frac{L_\mathrm{HST}}{C_\mathrm{HSE}}
$$ (eq-hspf)

:::{container} where
ここに、

$F_\mathrm{HSP}$
: 暖房期間エネルギー消費効率 (HSPF) (−)

$L_\mathrm{HST}$
: 暖房期間総合空調負荷 (HSTL) (Wh)

$C_\mathrm{HSE}$
: 暖房期間消費電力量 (HSEC) (Wh)

である。
:::

### 暖房期間総合空調負荷と暖房期間消費電力量

暖房期間総合空調負荷 $L_\mathrm{HST}$ は、温度区分ごとに処理する空調負荷に発生時間を掛けて合計する (附属書 B の式 (B.33))。

$$
L_\mathrm{HST} = \sum_j Q_\mathrm{h}(t_j)\,n_{\mathrm{h},j}
$$ (eq-hstl)

:::{container} where
ここに、

$L_\mathrm{HST}$
: 暖房期間総合空調負荷 (HSTL) (Wh)

$Q_\mathrm{h}(t_j)$
: 温度区分 $j$ において処理する空調負荷 (W)

$n_{\mathrm{h},j}$
: 温度区分 $j$ の発生時間 (h)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

暖房期間消費電力量 $C_\mathrm{HSE}$ は、温度区分ごとの消費電力に発生時間を掛けて合計する (附属書 B の式 (B.46))。消費電力には、補助電熱装置の消費電力を含む。

$$
C_\mathrm{HSE} = \sum_j P_\mathrm{h}(t_j)\,n_{\mathrm{h},j}
$$ (eq-hsec)

:::{container} where
ここに、

$C_\mathrm{HSE}$
: 暖房期間消費電力量 (HSEC) (Wh)

$P_\mathrm{h}(t_j)$
: 温度区分 $j$ における消費電力。補助電熱装置の消費電力を含む (W)

$n_{\mathrm{h},j}$
: 温度区分 $j$ の発生時間 (h)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

### 外気温度の発生時間

外気温度 $t_j$ とその発生時間 $n_{\mathrm{h},j}$ は、附属書 B の表 B.6 (東京)による ({numref}`tbl-h-bins`)。表 B.6 は −14 ℃から 16 ℃までの温度区分を示しているが、−14 ℃から −1 ℃までの発生時間はすべて 0 h なので、表では省略した。特定地域の値を用いる場合は、附属書 B の B.2.9 による。

```{list-table} 暖房期間の外気温度の発生時間 (東京)
:name: tbl-h-bins
:header-rows: 1
:stub-columns: 1

* - $t_j$ (℃)
  - 0
  - 1
  - 2
  - 3
  - 4
  - 5
  - 6
  - 7
  - 8
  - 9
  - 10
  - 11
  - 12
  - 13
  - 14
  - 15
  - 16
* - $n_{\mathrm{h},j}$ (h)
  - 2
  - 5
  - 25
  - 75
  - 121
  - 176
  - 207
  - 257
  - 281
  - 315
  - 271
  - 225
  - 234
  - 197
  - 130
  - 111
  - 75
```

発生時間の合計は 2 707 h である。

### 着霜領域と無着霜領域

外気温度が −7 ℃を超え 5.5 ℃未満の範囲では、室外側の熱交換器に霜が付き、除霜運転を行う。JIS C 9612:2013 の附属書 B は、除霜による能力と消費電力の低下が 5.5 ℃で最も大きく、外気温度が下がるにつれて小さくなり、−7 ℃でなくなると仮定している (附属書 B の B.2.6.4.2)。

そこで、この範囲を着霜領域とし、着霜時の能力・消費電力の特性を用いる。それ以外の範囲 ($t_j \le -7$ ℃または $5.5$ ℃$\le t_j$)を無着霜領域とし、無着霜時の特性を用いる。本書では、着霜時の値を添字 f で表す (例: $\Phi_\mathrm{h,ful,f}(t_j)$)。

### 温度区分ごとの空調負荷と消費電力

温度区分 $j$ ごとに、想定暖房空調負荷 $L_\mathrm{h}(t_j)$ を中間運転能力、定格運転能力、最大運転能力と比べて、運転状態を次の 4 つのいずれかに判定する ({numref}`fig-h-regions`、{ref}`r-region`)。比べる能力は、無着霜領域では無着霜時の能力、着霜領域では着霜時の能力とする。
以下の式では、運転状態の名前で場合を分ける。

:::{container} symbols
断続運転
: 負荷が中間運転能力以下

中間〜定格の可変運転
: 負荷が中間運転能力を超え、定格運転能力以下

定格〜最大の可変運転
: 負荷が定格運転能力を超え、最大運転能力以下

最大運転
: 負荷が最大運転能力を超える。不足分は補助電熱装置で補う
:::

```{figure} figures/heating_regions.svg
:name: fig-h-regions
:width: 100%

想定暖房空調負荷と運転能力の関係 (暖房)

数値は説明用の例である (定格冷房能力 (表示値) 2 800 W、外気 7 ℃の定格運転能力 3 600 W・中間運転能力 1 800 W、外気 2 ℃の着霜時の最大運転能力 4 200 W)。灰色の範囲が着霜領域であり、着霜領域では能力が着霜時の特性 (実線)に切り替わる。
```

処理する空調負荷 $Q_\mathrm{h}(t_j)$ は、運転状態によらず想定暖房空調負荷に等しい (附属書 B の式 (B.33))。冷房と異なり、暖房では能力が足りない分を補助電熱装置で補うので、負荷は必ず全量処理される。

$$
Q_\mathrm{h}(t_j) = L_\mathrm{h}(t_j)
$$ (eq-h-q)

:::{container} where
ここに、

$Q_\mathrm{h}(t_j)$
: 温度区分 $j$ において処理する空調負荷 (W)

$L_\mathrm{h}(t_j)$
: 外気温度 $t_j$ における想定暖房空調負荷 (W)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

消費電力 $P_\mathrm{h}(t_j)$ は、無着霜領域 ($t_j \le -7$ ℃または $5.5$ ℃$\le t_j$)では次式による (附属書 B の式 (B.46))。

$$
P_\mathrm{h}(t_j) =
\begin{cases}
\dfrac{X_\mathrm{h}(t_j)\,P_\mathrm{h,haf}(t_j)}{F_\mathrm{h,PL}(t_j)} & \text{(断続運転)} \\[2ex]
P_\mathrm{h,hf}(t_j) & \text{(中間〜定格の可変運転)} \\[1ex]
P_\mathrm{h,fe}(t_j) & \text{(定格〜最大の可変運転)} \\[1ex]
P_\mathrm{h,ext}(t_j) + P_\mathrm{h,RH}(t_j) & \text{(最大運転)}
\end{cases}
$$ (eq-h-p)

:::{container} where
ここに、

$P_\mathrm{h}(t_j)$
: 温度区分 $j$ における消費電力。補助電熱装置の消費電力を含む (W)

$X_\mathrm{h}(t_j)$
: 外気温度 $t_j$ における無着霜時の運転率 (−)

$P_\mathrm{h,haf}(t_j)$
: 外気温度 $t_j$ における無着霜時の中間運転消費電力 (W)

$F_\mathrm{h,PL}(t_j)$
: 外気温度 $t_j$ における無着霜時の部分負荷率 (−)

$P_\mathrm{h,hf}(t_j)$
: 外気温度 $t_j$ において、無着霜時に中間運転能力と定格運転能力の間で可変運転したときの消費電力 (W)

$P_\mathrm{h,fe}(t_j)$
: 外気温度 $t_j$ において、無着霜時に定格運転能力と最大運転能力の間で可変運転したときの消費電力 (W)

$P_\mathrm{h,ext}(t_j)$
: 外気温度 $t_j$ における無着霜時の最大運転消費電力 (W)

$P_\mathrm{h,RH}(t_j)$
: 外気温度 $t_j$ における無着霜時の補助電熱装置の消費電力 (W)

$L_\mathrm{h}(t_j)$
: 外気温度 $t_j$ における想定暖房空調負荷 (W)

$\Phi_\mathrm{h,haf}(t_j)$
: 外気温度 $t_j$ における無着霜時の中間運転能力 (W)

$\Phi_\mathrm{h,ful}(t_j)$
: 外気温度 $t_j$ における無着霜時の定格運転能力 (W)

$\Phi_\mathrm{h,ext}(t_j)$
: 外気温度 $t_j$ における無着霜時の最大運転能力 (W)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

着霜領域 ($-7$ ℃$< t_j < 5.5$ ℃)では、無着霜時の能力・消費電力を着霜時の値に置き換えた次式による (附属書 B の式 (B.46))。

$$
P_\mathrm{h}(t_j) =
\begin{cases}
\dfrac{X_\mathrm{h,f}(t_j)\,P_\mathrm{h,haf,f}(t_j)}{F_\mathrm{h,PL,f}(t_j)} & \text{(断続運転)} \\[2ex]
P_\mathrm{h,hf,f}(t_j) & \text{(中間〜定格の可変運転)} \\[1ex]
P_\mathrm{h,fe,f}(t_j) & \text{(定格〜最大の可変運転)} \\[1ex]
P_\mathrm{h,ext,f}(t_j) + P_\mathrm{h,RH,f}(t_j) & \text{(最大運転)}
\end{cases}
$$ (eq-h-p-f)

:::{container} where
ここに、

$P_\mathrm{h}(t_j)$
: 温度区分 $j$ における消費電力。補助電熱装置の消費電力を含む (W)

$X_\mathrm{h,f}(t_j)$
: 外気温度 $t_j$ における着霜時の運転率 (−)

$P_\mathrm{h,haf,f}(t_j)$
: 外気温度 $t_j$ における着霜時の中間運転消費電力 (W)

$F_\mathrm{h,PL,f}(t_j)$
: 外気温度 $t_j$ における着霜時の部分負荷率 (−)

$P_\mathrm{h,hf,f}(t_j)$
: 外気温度 $t_j$ において、着霜時に中間運転能力と定格運転能力の間で可変運転したときの消費電力 (W)

$P_\mathrm{h,fe,f}(t_j)$
: 外気温度 $t_j$ において、着霜時に定格運転能力と最大運転能力の間で可変運転したときの消費電力 (W)

$P_\mathrm{h,ext,f}(t_j)$
: 外気温度 $t_j$ における着霜時の最大運転消費電力 (W)

$P_\mathrm{h,RH,f}(t_j)$
: 外気温度 $t_j$ における着霜時の補助電熱装置の消費電力 (W)

$L_\mathrm{h}(t_j)$
: 外気温度 $t_j$ における想定暖房空調負荷 (W)

$\Phi_\mathrm{h,haf,f}(t_j)$
: 外気温度 $t_j$ における着霜時の中間運転能力 (W)

$\Phi_\mathrm{h,ful,f}(t_j)$
: 外気温度 $t_j$ における着霜時の定格運転能力 (W)

$\Phi_\mathrm{h,ext,f}(t_j)$
: 外気温度 $t_j$ における着霜時の最大運転能力 (W)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

外気温度と消費電力の関係の例を {numref}`fig-h-power` に示す。

```{figure} figures/heating_power.svg
:name: fig-h-power
:width: 100%

外気温度と消費電力の関係 (暖房)

数値は説明用の例である ({numref}`fig-h-regions` の例に、外気 7 ℃の定格運転消費電力 900 W・中間運転消費電力 360 W、外気 2 ℃の着霜時の最大運転消費電力 1 500 W を加えた)。点は温度区分ごとの値、棒はそのうちの補助電熱装置の消費電力、灰色の範囲は着霜領域を示す。
```

#### 断続運転

想定暖房空調負荷が中間運転能力以下のときは、中間運転能力で運転と停止を繰り返して負荷に合わせる。消費電力の考え方は冷房と同じである (冷房期間の「断続運転」)。

無着霜時の部分負荷率 $F_\mathrm{h,PL}(t_j)$ と着霜時の部分負荷率 $F_\mathrm{h,PL,f}(t_j)$ は、効率低下係数 $C_\mathrm{h,D}$ を用いて次式で求める (附属書 B の式 (B.36))。効率低下係数は、試験を行わず 0.25 とする (附属書 B の表 B.4、B.2.5.3.4)。

$$
F_\mathrm{h,PL}(t_j) = 1 - C_\mathrm{h,D}\,[1 - X_\mathrm{h}(t_j)]
$$ (eq-h-plf)

:::{container} where
ここに、

$F_\mathrm{h,PL}(t_j)$
: 外気温度 $t_j$ における無着霜時の部分負荷率 (−)

$C_\mathrm{h,D}$
: 効率低下係数。0.25 とする (−)

$X_\mathrm{h}(t_j)$
: 外気温度 $t_j$ における無着霜時の運転率 (−)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

$$
F_\mathrm{h,PL,f}(t_j) = 1 - C_\mathrm{h,D}\,[1 - X_\mathrm{h,f}(t_j)]
$$ (eq-h-plf-f)

:::{container} where
ここに、

$F_\mathrm{h,PL,f}(t_j)$
: 外気温度 $t_j$ における着霜時の部分負荷率 (−)

$C_\mathrm{h,D}$
: 効率低下係数。0.25 とする (−)

$X_\mathrm{h,f}(t_j)$
: 外気温度 $t_j$ における着霜時の運転率 (−)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

無着霜時の運転率 $X_\mathrm{h}(t_j)$ と着霜時の運転率 $X_\mathrm{h,f}(t_j)$ は、想定暖房空調負荷と中間運転能力の比であり、次式による (附属書 B の式 (B.35))。

$$
X_\mathrm{h}(t_j) = \frac{L_\mathrm{h}(t_j)}{\Phi_\mathrm{h,haf}(t_j)}
$$ (eq-h-x)

:::{container} where
ここに、

$X_\mathrm{h}(t_j)$
: 外気温度 $t_j$ における無着霜時の運転率 (−)

$L_\mathrm{h}(t_j)$
: 外気温度 $t_j$ における想定暖房空調負荷 (W)

$\Phi_\mathrm{h,haf}(t_j)$
: 外気温度 $t_j$ における無着霜時の中間運転能力 (W)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

$$
X_\mathrm{h,f}(t_j) = \frac{L_\mathrm{h}(t_j)}{\Phi_\mathrm{h,haf,f}(t_j)}
$$ (eq-h-x-f)

:::{container} where
ここに、

$X_\mathrm{h,f}(t_j)$
: 外気温度 $t_j$ における着霜時の運転率 (−)

$L_\mathrm{h}(t_j)$
: 外気温度 $t_j$ における想定暖房空調負荷 (W)

$\Phi_\mathrm{h,haf,f}(t_j)$
: 外気温度 $t_j$ における着霜時の中間運転能力 (W)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

#### 中間運転能力と定格運転能力の間の可変運転

想定暖房空調負荷が中間運転能力を超え、定格運転能力以下のときは、能力を連続的に変えて、負荷とつり合う能力で運転する。無着霜時の消費電力 $P_\mathrm{h,hf}(t_j)$ と着霜時の消費電力 $P_\mathrm{h,hf,f}(t_j)$ は、想定暖房空調負荷をエネルギー消費効率 (COP)で割って求める (附属書 B の式 (B.48))。

$$
P_\mathrm{h,hf}(t_j) = \frac{L_\mathrm{h}(t_j)}{C_\mathrm{OP,hf}(t_j)}
$$ (eq-h-phf)

:::{container} where
ここに、

$P_\mathrm{h,hf}(t_j)$
: 外気温度 $t_j$ において、無着霜時に中間運転能力と定格運転能力の間で可変運転したときの消費電力 (W)

$L_\mathrm{h}(t_j)$
: 外気温度 $t_j$ における想定暖房空調負荷 (W)

$C_\mathrm{OP,hf}(t_j)$
: 外気温度 $t_j$ において、無着霜時に中間運転能力と定格運転能力の間で可変運転したときのエネルギー消費効率 (−)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

$$
P_\mathrm{h,hf,f}(t_j) = \frac{L_\mathrm{h}(t_j)}{C_\mathrm{OP,hf,f}(t_j)}
$$ (eq-h-phf-f)

:::{container} where
ここに、

$P_\mathrm{h,hf,f}(t_j)$
: 外気温度 $t_j$ において、着霜時に中間運転能力と定格運転能力の間で可変運転したときの消費電力 (W)

$L_\mathrm{h}(t_j)$
: 外気温度 $t_j$ における想定暖房空調負荷 (W)

$C_\mathrm{OP,hf,f}(t_j)$
: 外気温度 $t_j$ において、着霜時に中間運転能力と定格運転能力の間で可変運転したときのエネルギー消費効率 (−)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

無着霜時のエネルギー消費効率 $C_\mathrm{OP,hf}(t_j)$ は、交点温度 $t_\mathrm{a}$ での定格運転のエネルギー消費効率と、交点温度 $t_\mathrm{d}$ での中間運転のエネルギー消費効率の間を、外気温度で直線補間して求める (附属書 B の式 (B.49)、{ref}`r-h-cop`)。

$$
C_\mathrm{OP,hf}(t_j) = C_\mathrm{OP,ful}(t_\mathrm{a}) + \frac{C_\mathrm{OP,haf}(t_\mathrm{d}) - C_\mathrm{OP,ful}(t_\mathrm{a})}{t_\mathrm{d} - t_\mathrm{a}}\,(t_j - t_\mathrm{a})
$$ (eq-h-cop-hf)

:::{container} where
ここに、

$C_\mathrm{OP,hf}(t_j)$
: 外気温度 $t_j$ において、無着霜時に中間運転能力と定格運転能力の間で可変運転したときのエネルギー消費効率 (−)

$C_\mathrm{OP,ful}(t_\mathrm{a})$
: 外気温度 $t_\mathrm{a}$ における無着霜時の定格運転のエネルギー消費効率 (−)

$C_\mathrm{OP,haf}(t_\mathrm{d})$
: 外気温度 $t_\mathrm{d}$ における無着霜時の中間運転のエネルギー消費効率 (−)

$t_\mathrm{a}$
: 想定暖房空調負荷と無着霜時の定格運転能力が等しくなる外気温度 (℃)

$t_\mathrm{d}$
: 想定暖房空調負荷と無着霜時の中間運転能力が等しくなる外気温度 (℃)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

着霜時のエネルギー消費効率 $C_\mathrm{OP,hf,f}(t_j)$ は、交点温度 $t_\mathrm{g}$ での着霜時の定格運転のエネルギー消費効率と、交点温度 $t_\mathrm{e}$ での着霜時の中間運転のエネルギー消費効率の間を、外気温度で直線補間して求める (附属書 B の式 (B.51))。

$$
C_\mathrm{OP,hf,f}(t_j) = C_\mathrm{OP,ful,f}(t_\mathrm{g}) + \frac{C_\mathrm{OP,haf,f}(t_\mathrm{e}) - C_\mathrm{OP,ful,f}(t_\mathrm{g})}{t_\mathrm{e} - t_\mathrm{g}}\,(t_j - t_\mathrm{g})
$$ (eq-h-cop-hf-f)

:::{container} where
ここに、

$C_\mathrm{OP,hf,f}(t_j)$
: 外気温度 $t_j$ において、着霜時に中間運転能力と定格運転能力の間で可変運転したときのエネルギー消費効率 (−)

$C_\mathrm{OP,ful,f}(t_\mathrm{g})$
: 外気温度 $t_\mathrm{g}$ における着霜時の定格運転のエネルギー消費効率 (−)

$C_\mathrm{OP,haf,f}(t_\mathrm{e})$
: 外気温度 $t_\mathrm{e}$ における着霜時の中間運転のエネルギー消費効率 (−)

$t_\mathrm{g}$
: 想定暖房空調負荷と着霜時の定格運転能力が等しくなる外気温度 (℃)

$t_\mathrm{e}$
: 想定暖房空調負荷と着霜時の中間運転能力が等しくなる外気温度 (℃)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

#### 定格運転能力と最大運転能力の間の可変運転

想定暖房空調負荷が定格運転能力を超え、最大運転能力以下のときは、定格運転能力より高い能力で、負荷とつり合うように運転する。無着霜時の消費電力 $P_\mathrm{h,fe}(t_j)$ と着霜時の消費電力 $P_\mathrm{h,fe,f}(t_j)$ は、想定暖房空調負荷をエネルギー消費効率で割って求める (附属書 B の式 (B.48))。

$$
P_\mathrm{h,fe}(t_j) = \frac{L_\mathrm{h}(t_j)}{C_\mathrm{OP,fe}(t_j)}
$$ (eq-h-pfe)

:::{container} where
ここに、

$P_\mathrm{h,fe}(t_j)$
: 外気温度 $t_j$ において、無着霜時に定格運転能力と最大運転能力の間で可変運転したときの消費電力 (W)

$L_\mathrm{h}(t_j)$
: 外気温度 $t_j$ における想定暖房空調負荷 (W)

$C_\mathrm{OP,fe}(t_j)$
: 外気温度 $t_j$ において、無着霜時に定格運転能力と最大運転能力の間で可変運転したときのエネルギー消費効率 (−)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

$$
P_\mathrm{h,fe,f}(t_j) = \frac{L_\mathrm{h}(t_j)}{C_\mathrm{OP,fe,f}(t_j)}
$$ (eq-h-pfe-f)

:::{container} where
ここに、

$P_\mathrm{h,fe,f}(t_j)$
: 外気温度 $t_j$ において、着霜時に定格運転能力と最大運転能力の間で可変運転したときの消費電力 (W)

$L_\mathrm{h}(t_j)$
: 外気温度 $t_j$ における想定暖房空調負荷 (W)

$C_\mathrm{OP,fe,f}(t_j)$
: 外気温度 $t_j$ において、着霜時に定格運転能力と最大運転能力の間で可変運転したときのエネルギー消費効率 (−)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

無着霜時のエネルギー消費効率 $C_\mathrm{OP,fe}(t_j)$ は、交点温度 $t_\mathrm{h}$ での最大運転のエネルギー消費効率と、交点温度 $t_\mathrm{a}$ での定格運転のエネルギー消費効率の間を、外気温度で直線補間して求める (附属書 B の式 (B.50)、{ref}`r-h-cop`)。

$$
C_\mathrm{OP,fe}(t_j) = C_\mathrm{OP,ext}(t_\mathrm{h}) + \frac{C_\mathrm{OP,ful}(t_\mathrm{a}) - C_\mathrm{OP,ext}(t_\mathrm{h})}{t_\mathrm{a} - t_\mathrm{h}}\,(t_j - t_\mathrm{h})
$$ (eq-h-cop-fe)

:::{container} where
ここに、

$C_\mathrm{OP,fe}(t_j)$
: 外気温度 $t_j$ において、無着霜時に定格運転能力と最大運転能力の間で可変運転したときのエネルギー消費効率 (−)

$C_\mathrm{OP,ext}(t_\mathrm{h})$
: 外気温度 $t_\mathrm{h}$ における無着霜時の最大運転のエネルギー消費効率 (−)

$C_\mathrm{OP,ful}(t_\mathrm{a})$
: 外気温度 $t_\mathrm{a}$ における無着霜時の定格運転のエネルギー消費効率 (−)

$t_\mathrm{h}$
: 想定暖房空調負荷と無着霜時の最大運転能力が等しくなる外気温度 (℃)

$t_\mathrm{a}$
: 想定暖房空調負荷と無着霜時の定格運転能力が等しくなる外気温度 (℃)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

着霜時のエネルギー消費効率 $C_\mathrm{OP,fe,f}(t_j)$ は、交点温度 $t_\mathrm{f}$ での着霜時の最大運転のエネルギー消費効率と、交点温度 $t_\mathrm{g}$ での着霜時の定格運転のエネルギー消費効率の間を、外気温度で直線補間して求める (附属書 B の式 (B.52))。

$$
C_\mathrm{OP,fe,f}(t_j) = C_\mathrm{OP,ext,f}(t_\mathrm{f}) + \frac{C_\mathrm{OP,ful,f}(t_\mathrm{g}) - C_\mathrm{OP,ext,f}(t_\mathrm{f})}{t_\mathrm{g} - t_\mathrm{f}}\,(t_j - t_\mathrm{f})
$$ (eq-h-cop-fe-f)

:::{container} where
ここに、

$C_\mathrm{OP,fe,f}(t_j)$
: 外気温度 $t_j$ において、着霜時に定格運転能力と最大運転能力の間で可変運転したときのエネルギー消費効率 (−)

$C_\mathrm{OP,ext,f}(t_\mathrm{f})$
: 外気温度 $t_\mathrm{f}$ における着霜時の最大運転のエネルギー消費効率 (−)

$C_\mathrm{OP,ful,f}(t_\mathrm{g})$
: 外気温度 $t_\mathrm{g}$ における着霜時の定格運転のエネルギー消費効率 (−)

$t_\mathrm{f}$
: 想定暖房空調負荷と着霜時の最大運転能力が等しくなる外気温度 (℃)

$t_\mathrm{g}$
: 想定暖房空調負荷と着霜時の定格運転能力が等しくなる外気温度 (℃)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

#### 最大運転

想定暖房空調負荷が最大運転能力を超えるときは、最大運転能力で連続運転し、足りない熱量を補助電熱装置で補う。最大運転の消費電力は、無着霜領域では $P_\mathrm{h,ext}(t_j)$、着霜領域では $P_\mathrm{h,ext,f}(t_j)$ とする ({eq}`eq-h-p`、{eq}`eq-h-p-f`、{ref}`r-h-pext`)。

無着霜時の補助電熱装置の消費電力 $P_\mathrm{h,RH}(t_j)$ と着霜時の補助電熱装置の消費電力 $P_\mathrm{h,RH,f}(t_j)$ は、不足する熱量に等しいとし、次式による (附属書 B の式 (B.37))。

$$
P_\mathrm{h,RH}(t_j) = L_\mathrm{h}(t_j) - \Phi_\mathrm{h,ext}(t_j)
$$ (eq-h-prh)

:::{container} where
ここに、

$P_\mathrm{h,RH}(t_j)$
: 外気温度 $t_j$ における無着霜時の補助電熱装置の消費電力 (W)

$L_\mathrm{h}(t_j)$
: 外気温度 $t_j$ における想定暖房空調負荷 (W)

$\Phi_\mathrm{h,ext}(t_j)$
: 外気温度 $t_j$ における無着霜時の最大運転能力 (W)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

$$
P_\mathrm{h,RH,f}(t_j) = L_\mathrm{h}(t_j) - \Phi_\mathrm{h,ext,f}(t_j)
$$ (eq-h-prh-f)

:::{container} where
ここに、

$P_\mathrm{h,RH,f}(t_j)$
: 外気温度 $t_j$ における着霜時の補助電熱装置の消費電力 (W)

$L_\mathrm{h}(t_j)$
: 外気温度 $t_j$ における想定暖房空調負荷 (W)

$\Phi_\mathrm{h,ext,f}(t_j)$
: 外気温度 $t_j$ における着霜時の最大運転能力 (W)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

#### 交点温度でのエネルギー消費効率

交点温度でのエネルギー消費効率は、その温度での能力を消費電力で割って求める (附属書 B の式 (B.47))。

$$
C_\mathrm{OP,ful}(t_\mathrm{a}) = \frac{\Phi_\mathrm{h,ful}(t_\mathrm{a})}{P_\mathrm{h,ful}(t_\mathrm{a})}
$$ (eq-h-cop-ful)

:::{container} where
ここに、

$C_\mathrm{OP,ful}(t_\mathrm{a})$
: 外気温度 $t_\mathrm{a}$ における無着霜時の定格運転のエネルギー消費効率 (−)

$\Phi_\mathrm{h,ful}(t_\mathrm{a})$
: 外気温度 $t_\mathrm{a}$ における無着霜時の定格運転能力 (W)

$P_\mathrm{h,ful}(t_\mathrm{a})$
: 外気温度 $t_\mathrm{a}$ における無着霜時の定格運転消費電力 (W)

$t_\mathrm{a}$
: 想定暖房空調負荷と無着霜時の定格運転能力が等しくなる外気温度 (℃)

である。
:::

$$
C_\mathrm{OP,haf}(t_\mathrm{d}) = \frac{\Phi_\mathrm{h,haf}(t_\mathrm{d})}{P_\mathrm{h,haf}(t_\mathrm{d})}
$$ (eq-h-cop-haf)

:::{container} where
ここに、

$C_\mathrm{OP,haf}(t_\mathrm{d})$
: 外気温度 $t_\mathrm{d}$ における無着霜時の中間運転のエネルギー消費効率 (−)

$\Phi_\mathrm{h,haf}(t_\mathrm{d})$
: 外気温度 $t_\mathrm{d}$ における無着霜時の中間運転能力 (W)

$P_\mathrm{h,haf}(t_\mathrm{d})$
: 外気温度 $t_\mathrm{d}$ における無着霜時の中間運転消費電力 (W)

$t_\mathrm{d}$
: 想定暖房空調負荷と無着霜時の中間運転能力が等しくなる外気温度 (℃)

である。
:::

$$
C_\mathrm{OP,ext}(t_\mathrm{h}) = \frac{\Phi_\mathrm{h,ext}(t_\mathrm{h})}{P_\mathrm{h,ext}(t_\mathrm{h})}
$$ (eq-h-cop-ext)

:::{container} where
ここに、

$C_\mathrm{OP,ext}(t_\mathrm{h})$
: 外気温度 $t_\mathrm{h}$ における無着霜時の最大運転のエネルギー消費効率 (−)

$\Phi_\mathrm{h,ext}(t_\mathrm{h})$
: 外気温度 $t_\mathrm{h}$ における無着霜時の最大運転能力 (W)

$P_\mathrm{h,ext}(t_\mathrm{h})$
: 外気温度 $t_\mathrm{h}$ における無着霜時の最大運転消費電力 (W)

$t_\mathrm{h}$
: 想定暖房空調負荷と無着霜時の最大運転能力が等しくなる外気温度 (℃)

である。
:::

$$
C_\mathrm{OP,ful,f}(t_\mathrm{g}) = \frac{\Phi_\mathrm{h,ful,f}(t_\mathrm{g})}{P_\mathrm{h,ful,f}(t_\mathrm{g})}
$$ (eq-h-cop-ful-f)

:::{container} where
ここに、

$C_\mathrm{OP,ful,f}(t_\mathrm{g})$
: 外気温度 $t_\mathrm{g}$ における着霜時の定格運転のエネルギー消費効率 (−)

$\Phi_\mathrm{h,ful,f}(t_\mathrm{g})$
: 外気温度 $t_\mathrm{g}$ における着霜時の定格運転能力 (W)

$P_\mathrm{h,ful,f}(t_\mathrm{g})$
: 外気温度 $t_\mathrm{g}$ における着霜時の定格運転消費電力 (W)

$t_\mathrm{g}$
: 想定暖房空調負荷と着霜時の定格運転能力が等しくなる外気温度 (℃)

である。
:::

$$
C_\mathrm{OP,haf,f}(t_\mathrm{e}) = \frac{\Phi_\mathrm{h,haf,f}(t_\mathrm{e})}{P_\mathrm{h,haf,f}(t_\mathrm{e})}
$$ (eq-h-cop-haf-f)

:::{container} where
ここに、

$C_\mathrm{OP,haf,f}(t_\mathrm{e})$
: 外気温度 $t_\mathrm{e}$ における着霜時の中間運転のエネルギー消費効率 (−)

$\Phi_\mathrm{h,haf,f}(t_\mathrm{e})$
: 外気温度 $t_\mathrm{e}$ における着霜時の中間運転能力 (W)

$P_\mathrm{h,haf,f}(t_\mathrm{e})$
: 外気温度 $t_\mathrm{e}$ における着霜時の中間運転消費電力 (W)

$t_\mathrm{e}$
: 想定暖房空調負荷と着霜時の中間運転能力が等しくなる外気温度 (℃)

である。
:::

$$
C_\mathrm{OP,ext,f}(t_\mathrm{f}) = \frac{\Phi_\mathrm{h,ext,f}(t_\mathrm{f})}{P_\mathrm{h,ext,f}(t_\mathrm{f})}
$$ (eq-h-cop-ext-f)

:::{container} where
ここに、

$C_\mathrm{OP,ext,f}(t_\mathrm{f})$
: 外気温度 $t_\mathrm{f}$ における着霜時の最大運転のエネルギー消費効率 (−)

$\Phi_\mathrm{h,ext,f}(t_\mathrm{f})$
: 外気温度 $t_\mathrm{f}$ における着霜時の最大運転能力 (W)

$P_\mathrm{h,ext,f}(t_\mathrm{f})$
: 外気温度 $t_\mathrm{f}$ における着霜時の最大運転消費電力 (W)

$t_\mathrm{f}$
: 想定暖房空調負荷と着霜時の最大運転能力が等しくなる外気温度 (℃)

である。
:::

### 交点温度

暖房では、外気温度が低くなるほど想定暖房空調負荷は大きくなり、運転能力は小さくなる。このため、ある外気温度で負荷と能力が等しくなる ({numref}`fig-h-regions`)。この外気温度を交点温度と呼び、次の 6 つを用いる。

:::{container} symbols
$t_\mathrm{d}$
: 想定暖房空調負荷と無着霜時の中間運転能力が等しくなる外気温度

$t_\mathrm{a}$
: 想定暖房空調負荷と無着霜時の定格運転能力が等しくなる外気温度

$t_\mathrm{h}$
: 想定暖房空調負荷と無着霜時の最大運転能力が等しくなる外気温度

$t_\mathrm{e}$
: 想定暖房空調負荷と着霜時の中間運転能力が等しくなる外気温度

$t_\mathrm{g}$
: 想定暖房空調負荷と着霜時の定格運転能力が等しくなる外気温度

$t_\mathrm{f}$
: 想定暖房空調負荷と着霜時の最大運転能力が等しくなる外気温度
:::

交点温度は、可変運転のエネルギー消費効率を補間する {eq}`eq-h-cop-hf`〜{eq}`eq-h-cop-fe-f` で、補間の両端として用いる。着霜時の交点温度が着霜領域の外になる場合も、そのまま補間に用いる ({ref}`r-h-extrap`)。

交点温度は、それぞれ次の関係を満たす。

$$
L_\mathrm{h}(t_\mathrm{d}) = \Phi_\mathrm{h,haf}(t_\mathrm{d})
$$ (eq-h-d-def)

:::{container} where
ここに、

$L_\mathrm{h}(t_\mathrm{d})$
: 外気温度 $t_\mathrm{d}$ における想定暖房空調負荷。{eq}`eq-h-load` による (W)

$\Phi_\mathrm{h,haf}(t_\mathrm{d})$
: 外気温度 $t_\mathrm{d}$ における無着霜時の中間運転能力。{eq}`eq-h-cap-haf` による (W)

$t_\mathrm{d}$
: 想定暖房空調負荷と無着霜時の中間運転能力が等しくなる外気温度 (℃)

である。
:::

$$
L_\mathrm{h}(t_\mathrm{a}) = \Phi_\mathrm{h,ful}(t_\mathrm{a})
$$ (eq-h-a-def)

:::{container} where
ここに、

$L_\mathrm{h}(t_\mathrm{a})$
: 外気温度 $t_\mathrm{a}$ における想定暖房空調負荷。{eq}`eq-h-load` による (W)

$\Phi_\mathrm{h,ful}(t_\mathrm{a})$
: 外気温度 $t_\mathrm{a}$ における無着霜時の定格運転能力。{eq}`eq-h-cap-ful` による (W)

$t_\mathrm{a}$
: 想定暖房空調負荷と無着霜時の定格運転能力が等しくなる外気温度 (℃)

である。
:::

$$
L_\mathrm{h}(t_\mathrm{h}) = \Phi_\mathrm{h,ext}(t_\mathrm{h})
$$ (eq-h-h-def)

:::{container} where
ここに、

$L_\mathrm{h}(t_\mathrm{h})$
: 外気温度 $t_\mathrm{h}$ における想定暖房空調負荷。{eq}`eq-h-load` による (W)

$\Phi_\mathrm{h,ext}(t_\mathrm{h})$
: 外気温度 $t_\mathrm{h}$ における無着霜時の最大運転能力。{eq}`eq-h-cap-ext` による (W)

$t_\mathrm{h}$
: 想定暖房空調負荷と無着霜時の最大運転能力が等しくなる外気温度 (℃)

である。
:::

$$
L_\mathrm{h}(t_\mathrm{e}) = \Phi_\mathrm{h,haf,f}(t_\mathrm{e})
$$ (eq-h-e-def)

:::{container} where
ここに、

$L_\mathrm{h}(t_\mathrm{e})$
: 外気温度 $t_\mathrm{e}$ における想定暖房空調負荷。{eq}`eq-h-load` による (W)

$\Phi_\mathrm{h,haf,f}(t_\mathrm{e})$
: 外気温度 $t_\mathrm{e}$ における着霜時の中間運転能力。{eq}`eq-h-cap-haf-f` による (W)

$t_\mathrm{e}$
: 想定暖房空調負荷と着霜時の中間運転能力が等しくなる外気温度 (℃)

である。
:::

$$
L_\mathrm{h}(t_\mathrm{g}) = \Phi_\mathrm{h,ful,f}(t_\mathrm{g})
$$ (eq-h-g-def)

:::{container} where
ここに、

$L_\mathrm{h}(t_\mathrm{g})$
: 外気温度 $t_\mathrm{g}$ における想定暖房空調負荷。{eq}`eq-h-load` による (W)

$\Phi_\mathrm{h,ful,f}(t_\mathrm{g})$
: 外気温度 $t_\mathrm{g}$ における着霜時の定格運転能力。{eq}`eq-h-cap-ful-f` による (W)

$t_\mathrm{g}$
: 想定暖房空調負荷と着霜時の定格運転能力が等しくなる外気温度 (℃)

である。
:::

$$
L_\mathrm{h}(t_\mathrm{f}) = \Phi_\mathrm{h,ext,f}(t_\mathrm{f})
$$ (eq-h-f-def)

:::{container} where
ここに、

$L_\mathrm{h}(t_\mathrm{f})$
: 外気温度 $t_\mathrm{f}$ における想定暖房空調負荷。{eq}`eq-h-load` による (W)

$\Phi_\mathrm{h,ext,f}(t_\mathrm{f})$
: 外気温度 $t_\mathrm{f}$ における着霜時の最大運転能力。{eq}`eq-h-cap-ext-f` による (W)

$t_\mathrm{f}$
: 想定暖房空調負荷と着霜時の最大運転能力が等しくなる外気温度 (℃)

である。
:::

負荷も能力も外気温度の 1 次式なので、上の関係を外気温度について解くと、交点温度は次式で求まる (附属書 B の式 (B.60)〜(B.71)、{ref}`r-intersection`)。式中の 1.025 は想定暖房空調負荷の係数 0.82 × 1.25 であり、14 と 9 は能力特性の 2 つの外気温度の差 (7 ℃と −7 ℃、2 ℃と −7 ℃)である。

$$
t_\mathrm{d} = \frac{1.025\,\Phi_{\mathrm{c,ful},t100}\,t_{\mathrm{h},0} \times 14 - [7\,\Phi_\mathrm{h,haf}(-7) + 7\,\Phi_\mathrm{h,haf}(7)]\,(t_{\mathrm{h},0} - t_{\mathrm{h},100})}{1.025\,\Phi_{\mathrm{c,ful},t100} \times 14 + [\Phi_\mathrm{h,haf}(7) - \Phi_\mathrm{h,haf}(-7)]\,(t_{\mathrm{h},0} - t_{\mathrm{h},100})}
$$ (eq-h-d)

:::{container} where
ここに、

$t_\mathrm{d}$
: 想定暖房空調負荷と無着霜時の中間運転能力が等しくなる外気温度 (℃)

$\Phi_{\mathrm{c,ful},t100}$
: 定格冷房能力 (表示値) (W)

$\Phi_\mathrm{h,haf}(-7)$
: 外気温度 −7 ℃における無着霜時の中間運転能力 (W)

$\Phi_\mathrm{h,haf}(7)$
: 外気温度 7 ℃における無着霜時の中間運転能力 (W)

$t_{\mathrm{h},0}$
: 想定暖房空調負荷が 0 となる外気温度。17 ℃とする (℃)

$t_{\mathrm{h},100}$
: 想定暖房空調負荷が $1.025\,\Phi_{\mathrm{c,ful},t100}$ となる外気温度。0 ℃とする (℃)

である。
:::

$$
t_\mathrm{a} = \frac{1.025\,\Phi_{\mathrm{c,ful},t100}\,t_{\mathrm{h},0} \times 14 - [7\,\Phi_\mathrm{h,ful}(-7) + 7\,\Phi_\mathrm{h,ful}(7)]\,(t_{\mathrm{h},0} - t_{\mathrm{h},100})}{1.025\,\Phi_{\mathrm{c,ful},t100} \times 14 + [\Phi_\mathrm{h,ful}(7) - \Phi_\mathrm{h,ful}(-7)]\,(t_{\mathrm{h},0} - t_{\mathrm{h},100})}
$$ (eq-h-a)

:::{container} where
ここに、

$t_\mathrm{a}$
: 想定暖房空調負荷と無着霜時の定格運転能力が等しくなる外気温度 (℃)

$\Phi_{\mathrm{c,ful},t100}$
: 定格冷房能力 (表示値) (W)

$\Phi_\mathrm{h,ful}(-7)$
: 外気温度 −7 ℃における無着霜時の定格運転能力 (W)

$\Phi_\mathrm{h,ful}(7)$
: 外気温度 7 ℃における無着霜時の定格運転能力 (W)

$t_{\mathrm{h},0}$
: 想定暖房空調負荷が 0 となる外気温度。17 ℃とする (℃)

$t_{\mathrm{h},100}$
: 想定暖房空調負荷が $1.025\,\Phi_{\mathrm{c,ful},t100}$ となる外気温度。0 ℃とする (℃)

である。
:::

$$
t_\mathrm{h} = \frac{1.025\,\Phi_{\mathrm{c,ful},t100}\,t_{\mathrm{h},0} \times 9 - [2\,\Phi_\mathrm{h,ext}(-7) + 7\,\Phi_\mathrm{h,ext}(2)]\,(t_{\mathrm{h},0} - t_{\mathrm{h},100})}{1.025\,\Phi_{\mathrm{c,ful},t100} \times 9 + [\Phi_\mathrm{h,ext}(2) - \Phi_\mathrm{h,ext}(-7)]\,(t_{\mathrm{h},0} - t_{\mathrm{h},100})}
$$ (eq-h-h)

:::{container} where
ここに、

$t_\mathrm{h}$
: 想定暖房空調負荷と無着霜時の最大運転能力が等しくなる外気温度 (℃)

$\Phi_{\mathrm{c,ful},t100}$
: 定格冷房能力 (表示値) (W)

$\Phi_\mathrm{h,ext}(-7)$
: 外気温度 −7 ℃における無着霜時の最大運転能力 (W)

$\Phi_\mathrm{h,ext}(2)$
: 外気温度 2 ℃における無着霜時の最大運転能力 (W)

$t_{\mathrm{h},0}$
: 想定暖房空調負荷が 0 となる外気温度。17 ℃とする (℃)

$t_{\mathrm{h},100}$
: 想定暖房空調負荷が $1.025\,\Phi_{\mathrm{c,ful},t100}$ となる外気温度。0 ℃とする (℃)

である。
:::

$$
t_\mathrm{e} = \frac{1.025\,\Phi_{\mathrm{c,ful},t100}\,t_{\mathrm{h},0} \times 9 - [2\,\Phi_\mathrm{h,haf}(-7) + 7\,\Phi_\mathrm{h,haf,f}(2)]\,(t_{\mathrm{h},0} - t_{\mathrm{h},100})}{1.025\,\Phi_{\mathrm{c,ful},t100} \times 9 + [\Phi_\mathrm{h,haf,f}(2) - \Phi_\mathrm{h,haf}(-7)]\,(t_{\mathrm{h},0} - t_{\mathrm{h},100})}
$$ (eq-h-e)

:::{container} where
ここに、

$t_\mathrm{e}$
: 想定暖房空調負荷と着霜時の中間運転能力が等しくなる外気温度 (℃)

$\Phi_{\mathrm{c,ful},t100}$
: 定格冷房能力 (表示値) (W)

$\Phi_\mathrm{h,haf}(-7)$
: 外気温度 −7 ℃における無着霜時の中間運転能力 (W)

$\Phi_\mathrm{h,haf,f}(2)$
: 外気温度 2 ℃における着霜時の中間運転能力 (W)

$t_{\mathrm{h},0}$
: 想定暖房空調負荷が 0 となる外気温度。17 ℃とする (℃)

$t_{\mathrm{h},100}$
: 想定暖房空調負荷が $1.025\,\Phi_{\mathrm{c,ful},t100}$ となる外気温度。0 ℃とする (℃)

である。
:::

$$
t_\mathrm{g} = \frac{1.025\,\Phi_{\mathrm{c,ful},t100}\,t_{\mathrm{h},0} \times 9 - [2\,\Phi_\mathrm{h,ful}(-7) + 7\,\Phi_\mathrm{h,ful,f}(2)]\,(t_{\mathrm{h},0} - t_{\mathrm{h},100})}{1.025\,\Phi_{\mathrm{c,ful},t100} \times 9 + [\Phi_\mathrm{h,ful,f}(2) - \Phi_\mathrm{h,ful}(-7)]\,(t_{\mathrm{h},0} - t_{\mathrm{h},100})}
$$ (eq-h-g)

:::{container} where
ここに、

$t_\mathrm{g}$
: 想定暖房空調負荷と着霜時の定格運転能力が等しくなる外気温度 (℃)

$\Phi_{\mathrm{c,ful},t100}$
: 定格冷房能力 (表示値) (W)

$\Phi_\mathrm{h,ful}(-7)$
: 外気温度 −7 ℃における無着霜時の定格運転能力 (W)

$\Phi_\mathrm{h,ful,f}(2)$
: 外気温度 2 ℃における着霜時の定格運転能力 (W)

$t_{\mathrm{h},0}$
: 想定暖房空調負荷が 0 となる外気温度。17 ℃とする (℃)

$t_{\mathrm{h},100}$
: 想定暖房空調負荷が $1.025\,\Phi_{\mathrm{c,ful},t100}$ となる外気温度。0 ℃とする (℃)

である。
:::

$$
t_\mathrm{f} = \frac{1.025\,\Phi_{\mathrm{c,ful},t100}\,t_{\mathrm{h},0} \times 9 - [2\,\Phi_\mathrm{h,ext}(-7) + 7\,\Phi_\mathrm{h,ext,f}(2)]\,(t_{\mathrm{h},0} - t_{\mathrm{h},100})}{1.025\,\Phi_{\mathrm{c,ful},t100} \times 9 + [\Phi_\mathrm{h,ext,f}(2) - \Phi_\mathrm{h,ext}(-7)]\,(t_{\mathrm{h},0} - t_{\mathrm{h},100})}
$$ (eq-h-f)

:::{container} where
ここに、

$t_\mathrm{f}$
: 想定暖房空調負荷と着霜時の最大運転能力が等しくなる外気温度 (℃)

$\Phi_{\mathrm{c,ful},t100}$
: 定格冷房能力 (表示値) (W)

$\Phi_\mathrm{h,ext}(-7)$
: 外気温度 −7 ℃における無着霜時の最大運転能力 (W)

$\Phi_\mathrm{h,ext,f}(2)$
: 外気温度 2 ℃における着霜時の最大運転能力 (W)

$t_{\mathrm{h},0}$
: 想定暖房空調負荷が 0 となる外気温度。17 ℃とする (℃)

$t_{\mathrm{h},100}$
: 想定暖房空調負荷が $1.025\,\Phi_{\mathrm{c,ful},t100}$ となる外気温度。0 ℃とする (℃)

である。
:::

### 想定暖房空調負荷

外気温度 $t$ における想定暖房空調負荷 $L_\mathrm{h}(t)$ は、外気温度 $t_{\mathrm{h},0}$ で 0、$t_{\mathrm{h},100}$ で定格冷房能力 (表示値)の 0.82 × 1.25 倍となる直線とする (附属書 B の式 (B.28)、(B.53))。

$$
L_\mathrm{h}(t) = 0.82 \times 1.25 \times \Phi_{\mathrm{c,ful},t100} \times \frac{t_{\mathrm{h},0} - t}{t_{\mathrm{h},0} - t_{\mathrm{h},100}}
$$ (eq-h-load)

:::{container} where
ここに、

$L_\mathrm{h}(t)$
: 外気温度 $t$ における想定暖房空調負荷 (W)

$\Phi_{\mathrm{c,ful},t100}$
: 定格冷房能力 (表示値) (W)

$t$
: 外気温度 (℃)

$t_{\mathrm{h},0}$
: 想定暖房空調負荷が 0 となる外気温度 (℃)

$t_{\mathrm{h},100}$
: 想定暖房空調負荷が定格冷房能力 (表示値)の 0.82 × 1.25 倍となる外気温度 (℃)

である。
:::

なお、$t_{\mathrm{h},0} = 17$ ℃、$t_{\mathrm{h},100} = 0$ ℃ とする。JIS C 9612:2013 の附属書 B は、外気 0 ℃における無着霜時の暖房能力を、外気 7 ℃の暖房標準能力の 0.82 倍としている (附属書 B の B.2.6.2)。

### 能力・消費電力の特性

外気温度 $t$ における能力と消費電力は、2 つの外気温度での値を結ぶ直線とする。結ぶ 2 点は次のとおりである。

:::{container} symbols
無着霜時の定格運転・中間運転
: −7 ℃と 7 ℃

無着霜時の最大運転
: −7 ℃と 2 ℃

着霜時 (定格・中間・最大)
: −7 ℃と 2 ℃ (2 ℃は着霜時の値)
:::

−7 ℃では着霜しないので、着霜時の特性線も −7 ℃では無着霜時の値を通る。最大モードをもたない機種では、最大運転の特性に定格運転の特性を用いる ({ref}`r-h-nomax`)。

#### 無着霜時

無着霜時の定格運転能力 $\Phi_\mathrm{h,ful}(t)$ と定格運転消費電力 $P_\mathrm{h,ful}(t)$ は、次式による (附属書 B の式 (B.29)、(B.31))。

$$
\Phi_\mathrm{h,ful}(t) = \Phi_\mathrm{h,ful}(-7) + \frac{\Phi_\mathrm{h,ful}(7) - \Phi_\mathrm{h,ful}(-7)}{7 - (-7)}\,[t - (-7)]
$$ (eq-h-cap-ful)

:::{container} where
ここに、

$\Phi_\mathrm{h,ful}(t)$
: 外気温度 $t$ における無着霜時の定格運転能力 (W)

$\Phi_\mathrm{h,ful}(-7)$
: 外気温度 −7 ℃における無着霜時の定格運転能力 (W)

$\Phi_\mathrm{h,ful}(7)$
: 外気温度 7 ℃における無着霜時の定格運転能力 (W)

$t$
: 外気温度 (℃)

である。
:::

$$
P_\mathrm{h,ful}(t) = P_\mathrm{h,ful}(-7) + \frac{P_\mathrm{h,ful}(7) - P_\mathrm{h,ful}(-7)}{7 - (-7)}\,[t - (-7)]
$$ (eq-h-pow-ful)

:::{container} where
ここに、

$P_\mathrm{h,ful}(t)$
: 外気温度 $t$ における無着霜時の定格運転消費電力 (W)

$P_\mathrm{h,ful}(-7)$
: 外気温度 −7 ℃における無着霜時の定格運転消費電力 (W)

$P_\mathrm{h,ful}(7)$
: 外気温度 7 ℃における無着霜時の定格運転消費電力 (W)

$t$
: 外気温度 (℃)

である。
:::

無着霜時の中間運転能力 $\Phi_\mathrm{h,haf}(t)$ と中間運転消費電力 $P_\mathrm{h,haf}(t)$ は、次式による (附属書 B の式 (B.39)、(B.43))。

$$
\Phi_\mathrm{h,haf}(t) = \Phi_\mathrm{h,haf}(-7) + \frac{\Phi_\mathrm{h,haf}(7) - \Phi_\mathrm{h,haf}(-7)}{7 - (-7)}\,[t - (-7)]
$$ (eq-h-cap-haf)

:::{container} where
ここに、

$\Phi_\mathrm{h,haf}(t)$
: 外気温度 $t$ における無着霜時の中間運転能力 (W)

$\Phi_\mathrm{h,haf}(-7)$
: 外気温度 −7 ℃における無着霜時の中間運転能力 (W)

$\Phi_\mathrm{h,haf}(7)$
: 外気温度 7 ℃における無着霜時の中間運転能力 (W)

$t$
: 外気温度 (℃)

である。
:::

$$
P_\mathrm{h,haf}(t) = P_\mathrm{h,haf}(-7) + \frac{P_\mathrm{h,haf}(7) - P_\mathrm{h,haf}(-7)}{7 - (-7)}\,[t - (-7)]
$$ (eq-h-pow-haf)

:::{container} where
ここに、

$P_\mathrm{h,haf}(t)$
: 外気温度 $t$ における無着霜時の中間運転消費電力 (W)

$P_\mathrm{h,haf}(-7)$
: 外気温度 −7 ℃における無着霜時の中間運転消費電力 (W)

$P_\mathrm{h,haf}(7)$
: 外気温度 7 ℃における無着霜時の中間運転消費電力 (W)

$t$
: 外気温度 (℃)

である。
:::

無着霜時の最大運転能力 $\Phi_\mathrm{h,ext}(t)$ と最大運転消費電力 $P_\mathrm{h,ext}(t)$ は、次式による (附属書 B の式 (B.38)、(B.42))。

$$
\Phi_\mathrm{h,ext}(t) = \Phi_\mathrm{h,ext}(-7) + \frac{\Phi_\mathrm{h,ext}(2) - \Phi_\mathrm{h,ext}(-7)}{2 - (-7)}\,[t - (-7)]
$$ (eq-h-cap-ext)

:::{container} where
ここに、

$\Phi_\mathrm{h,ext}(t)$
: 外気温度 $t$ における無着霜時の最大運転能力 (W)

$\Phi_\mathrm{h,ext}(-7)$
: 外気温度 −7 ℃における無着霜時の最大運転能力 (W)

$\Phi_\mathrm{h,ext}(2)$
: 外気温度 2 ℃における無着霜時の最大運転能力 (W)

$t$
: 外気温度 (℃)

である。
:::

$$
P_\mathrm{h,ext}(t) = P_\mathrm{h,ext}(-7) + \frac{P_\mathrm{h,ext}(2) - P_\mathrm{h,ext}(-7)}{2 - (-7)}\,[t - (-7)]
$$ (eq-h-pow-ext)

:::{container} where
ここに、

$P_\mathrm{h,ext}(t)$
: 外気温度 $t$ における無着霜時の最大運転消費電力 (W)

$P_\mathrm{h,ext}(-7)$
: 外気温度 −7 ℃における無着霜時の最大運転消費電力 (W)

$P_\mathrm{h,ext}(2)$
: 外気温度 2 ℃における無着霜時の最大運転消費電力 (W)

$t$
: 外気温度 (℃)

である。
:::

#### 着霜時

着霜時の定格運転能力 $\Phi_\mathrm{h,ful,f}(t)$ と定格運転消費電力 $P_\mathrm{h,ful,f}(t)$ は、次式による (附属書 B の式 (B.30)、(B.32))。

$$
\Phi_\mathrm{h,ful,f}(t) = \Phi_\mathrm{h,ful}(-7) + \frac{\Phi_\mathrm{h,ful,f}(2) - \Phi_\mathrm{h,ful}(-7)}{2 - (-7)}\,[t - (-7)]
$$ (eq-h-cap-ful-f)

:::{container} where
ここに、

$\Phi_\mathrm{h,ful,f}(t)$
: 外気温度 $t$ における着霜時の定格運転能力 (W)

$\Phi_\mathrm{h,ful}(-7)$
: 外気温度 −7 ℃における無着霜時の定格運転能力 (W)

$\Phi_\mathrm{h,ful,f}(2)$
: 外気温度 2 ℃における着霜時の定格運転能力 (W)

$t$
: 外気温度 (℃)

である。
:::

$$
P_\mathrm{h,ful,f}(t) = P_\mathrm{h,ful}(-7) + \frac{P_\mathrm{h,ful,f}(2) - P_\mathrm{h,ful}(-7)}{2 - (-7)}\,[t - (-7)]
$$ (eq-h-pow-ful-f)

:::{container} where
ここに、

$P_\mathrm{h,ful,f}(t)$
: 外気温度 $t$ における着霜時の定格運転消費電力 (W)

$P_\mathrm{h,ful}(-7)$
: 外気温度 −7 ℃における無着霜時の定格運転消費電力 (W)

$P_\mathrm{h,ful,f}(2)$
: 外気温度 2 ℃における着霜時の定格運転消費電力 (W)

$t$
: 外気温度 (℃)

である。
:::

着霜時の中間運転能力 $\Phi_\mathrm{h,haf,f}(t)$ と中間運転消費電力 $P_\mathrm{h,haf,f}(t)$ は、次式による (附属書 B の式 (B.41)、(B.45))。

$$
\Phi_\mathrm{h,haf,f}(t) = \Phi_\mathrm{h,haf}(-7) + \frac{\Phi_\mathrm{h,haf,f}(2) - \Phi_\mathrm{h,haf}(-7)}{2 - (-7)}\,[t - (-7)]
$$ (eq-h-cap-haf-f)

:::{container} where
ここに、

$\Phi_\mathrm{h,haf,f}(t)$
: 外気温度 $t$ における着霜時の中間運転能力 (W)

$\Phi_\mathrm{h,haf}(-7)$
: 外気温度 −7 ℃における無着霜時の中間運転能力 (W)

$\Phi_\mathrm{h,haf,f}(2)$
: 外気温度 2 ℃における着霜時の中間運転能力 (W)

$t$
: 外気温度 (℃)

である。
:::

$$
P_\mathrm{h,haf,f}(t) = P_\mathrm{h,haf}(-7) + \frac{P_\mathrm{h,haf,f}(2) - P_\mathrm{h,haf}(-7)}{2 - (-7)}\,[t - (-7)]
$$ (eq-h-pow-haf-f)

:::{container} where
ここに、

$P_\mathrm{h,haf,f}(t)$
: 外気温度 $t$ における着霜時の中間運転消費電力 (W)

$P_\mathrm{h,haf}(-7)$
: 外気温度 −7 ℃における無着霜時の中間運転消費電力 (W)

$P_\mathrm{h,haf,f}(2)$
: 外気温度 2 ℃における着霜時の中間運転消費電力 (W)

$t$
: 外気温度 (℃)

である。
:::

着霜時の最大運転能力 $\Phi_\mathrm{h,ext,f}(t)$ と最大運転消費電力 $P_\mathrm{h,ext,f}(t)$ は、次式による (附属書 B の式 (B.40)、(B.44))。

$$
\Phi_\mathrm{h,ext,f}(t) = \Phi_\mathrm{h,ext}(-7) + \frac{\Phi_\mathrm{h,ext,f}(2) - \Phi_\mathrm{h,ext}(-7)}{2 - (-7)}\,[t - (-7)]
$$ (eq-h-cap-ext-f)

:::{container} where
ここに、

$\Phi_\mathrm{h,ext,f}(t)$
: 外気温度 $t$ における着霜時の最大運転能力 (W)

$\Phi_\mathrm{h,ext}(-7)$
: 外気温度 −7 ℃における無着霜時の最大運転能力 (W)

$\Phi_\mathrm{h,ext,f}(2)$
: 外気温度 2 ℃における着霜時の最大運転能力 (W)

$t$
: 外気温度 (℃)

である。
:::

$$
P_\mathrm{h,ext,f}(t) = P_\mathrm{h,ext}(-7) + \frac{P_\mathrm{h,ext,f}(2) - P_\mathrm{h,ext}(-7)}{2 - (-7)}\,[t - (-7)]
$$ (eq-h-pow-ext-f)

:::{container} where
ここに、

$P_\mathrm{h,ext,f}(t)$
: 外気温度 $t$ における着霜時の最大運転消費電力 (W)

$P_\mathrm{h,ext}(-7)$
: 外気温度 −7 ℃における無着霜時の最大運転消費電力 (W)

$P_\mathrm{h,ext,f}(2)$
: 外気温度 2 ℃における着霜時の最大運転消費電力 (W)

$t$
: 外気温度 (℃)

である。
:::

### 試験値の補完

試験を行わない値は、試験値に係数を掛けて求める (附属書 B の表 B.4、{ref}`r-h-coef`)。

#### 外気 2 ℃の着霜時の値 (定格運転・中間運転)

外気 2 ℃における着霜時の定格運転・中間運転の能力と消費電力は、無着霜時の値を係数で割って求める (附属書 B の表 B.4)。ただし、最大モードをもたない機種の $\Phi_\mathrm{h,ful,f}(2)$ と $P_\mathrm{h,ful,f}(2)$ は入力値であり、{eq}`eq-h-cap2f-ful` と {eq}`eq-h-pow2f-ful` を用いない。

$$
\Phi_\mathrm{h,ful,f}(2) = \frac{\Phi_\mathrm{h,ful}(2)}{1.12}
$$ (eq-h-cap2f-ful)

:::{container} where
ここに、

$\Phi_\mathrm{h,ful,f}(2)$
: 外気温度 2 ℃における着霜時の定格運転能力 (W)

$\Phi_\mathrm{h,ful}(2)$
: 外気温度 2 ℃における無着霜時の定格運転能力 (W)

である。
:::

$$
P_\mathrm{h,ful,f}(2) = \frac{P_\mathrm{h,ful}(2)}{1.06}
$$ (eq-h-pow2f-ful)

:::{container} where
ここに、

$P_\mathrm{h,ful,f}(2)$
: 外気温度 2 ℃における着霜時の定格運転消費電力 (W)

$P_\mathrm{h,ful}(2)$
: 外気温度 2 ℃における無着霜時の定格運転消費電力 (W)

である。
:::

$$
\Phi_\mathrm{h,haf,f}(2) = \frac{\Phi_\mathrm{h,haf}(2)}{1.12}
$$ (eq-h-cap2f-haf)

:::{container} where
ここに、

$\Phi_\mathrm{h,haf,f}(2)$
: 外気温度 2 ℃における着霜時の中間運転能力 (W)

$\Phi_\mathrm{h,haf}(2)$
: 外気温度 2 ℃における無着霜時の中間運転能力 (W)

である。
:::

$$
P_\mathrm{h,haf,f}(2) = \frac{P_\mathrm{h,haf}(2)}{1.06}
$$ (eq-h-pow2f-haf)

:::{container} where
ここに、

$P_\mathrm{h,haf,f}(2)$
: 外気温度 2 ℃における着霜時の中間運転消費電力 (W)

$P_\mathrm{h,haf}(2)$
: 外気温度 2 ℃における無着霜時の中間運転消費電力 (W)

である。
:::

#### 外気 2 ℃の無着霜時の値 (定格運転・中間運転)

外気 2 ℃における無着霜時の定格運転・中間運転の能力と消費電力は、−7 ℃と 7 ℃の値を直線補間して求める (附属書 B の表 B.4 注 d))。

$$
\Phi_\mathrm{h,ful}(2) = \Phi_\mathrm{h,ful}(-7) + \frac{\Phi_\mathrm{h,ful}(7) - \Phi_\mathrm{h,ful}(-7)}{7 - (-7)}\,[2 - (-7)]
$$ (eq-h-cap2-ful)

:::{container} where
ここに、

$\Phi_\mathrm{h,ful}(2)$
: 外気温度 2 ℃における無着霜時の定格運転能力 (W)

$\Phi_\mathrm{h,ful}(-7)$
: 外気温度 −7 ℃における無着霜時の定格運転能力 (W)

$\Phi_\mathrm{h,ful}(7)$
: 外気温度 7 ℃における無着霜時の定格運転能力 (W)

である。
:::

$$
P_\mathrm{h,ful}(2) = P_\mathrm{h,ful}(-7) + \frac{P_\mathrm{h,ful}(7) - P_\mathrm{h,ful}(-7)}{7 - (-7)}\,[2 - (-7)]
$$ (eq-h-pow2-ful)

:::{container} where
ここに、

$P_\mathrm{h,ful}(2)$
: 外気温度 2 ℃における無着霜時の定格運転消費電力 (W)

$P_\mathrm{h,ful}(-7)$
: 外気温度 −7 ℃における無着霜時の定格運転消費電力 (W)

$P_\mathrm{h,ful}(7)$
: 外気温度 7 ℃における無着霜時の定格運転消費電力 (W)

である。
:::

$$
\Phi_\mathrm{h,haf}(2) = \Phi_\mathrm{h,haf}(-7) + \frac{\Phi_\mathrm{h,haf}(7) - \Phi_\mathrm{h,haf}(-7)}{7 - (-7)}\,[2 - (-7)]
$$ (eq-h-cap2-haf)

:::{container} where
ここに、

$\Phi_\mathrm{h,haf}(2)$
: 外気温度 2 ℃における無着霜時の中間運転能力 (W)

$\Phi_\mathrm{h,haf}(-7)$
: 外気温度 −7 ℃における無着霜時の中間運転能力 (W)

$\Phi_\mathrm{h,haf}(7)$
: 外気温度 7 ℃における無着霜時の中間運転能力 (W)

である。
:::

$$
P_\mathrm{h,haf}(2) = P_\mathrm{h,haf}(-7) + \frac{P_\mathrm{h,haf}(7) - P_\mathrm{h,haf}(-7)}{7 - (-7)}\,[2 - (-7)]
$$ (eq-h-pow2-haf)

:::{container} where
ここに、

$P_\mathrm{h,haf}(2)$
: 外気温度 2 ℃における無着霜時の中間運転消費電力 (W)

$P_\mathrm{h,haf}(-7)$
: 外気温度 −7 ℃における無着霜時の中間運転消費電力 (W)

$P_\mathrm{h,haf}(7)$
: 外気温度 7 ℃における無着霜時の中間運転消費電力 (W)

である。
:::

#### 外気 −7 ℃の値

外気 −7 ℃における定格運転・中間運転の能力と消費電力は、外気 7 ℃の値に係数を掛けて求める。最大運転の能力と消費電力は、外気 2 ℃の無着霜時の値に係数を掛けて求める (附属書 B の表 B.4)。

$$
\Phi_\mathrm{h,ful}(-7) = 0.64 \times \Phi_\mathrm{h,ful}(7)
$$ (eq-h-capm7-ful)

:::{container} where
ここに、

$\Phi_\mathrm{h,ful}(-7)$
: 外気温度 −7 ℃における無着霜時の定格運転能力 (W)

$\Phi_\mathrm{h,ful}(7)$
: 外気温度 7 ℃における無着霜時の定格運転能力 (W)

である。
:::

$$
P_\mathrm{h,ful}(-7) = 0.82 \times P_\mathrm{h,ful}(7)
$$ (eq-h-powm7-ful)

:::{container} where
ここに、

$P_\mathrm{h,ful}(-7)$
: 外気温度 −7 ℃における無着霜時の定格運転消費電力 (W)

$P_\mathrm{h,ful}(7)$
: 外気温度 7 ℃における無着霜時の定格運転消費電力 (W)

である。
:::

$$
\Phi_\mathrm{h,haf}(-7) = 0.64 \times \Phi_\mathrm{h,haf}(7)
$$ (eq-h-capm7-haf)

:::{container} where
ここに、

$\Phi_\mathrm{h,haf}(-7)$
: 外気温度 −7 ℃における無着霜時の中間運転能力 (W)

$\Phi_\mathrm{h,haf}(7)$
: 外気温度 7 ℃における無着霜時の中間運転能力 (W)

である。
:::

$$
P_\mathrm{h,haf}(-7) = 0.82 \times P_\mathrm{h,haf}(7)
$$ (eq-h-powm7-haf)

:::{container} where
ここに、

$P_\mathrm{h,haf}(-7)$
: 外気温度 −7 ℃における無着霜時の中間運転消費電力 (W)

$P_\mathrm{h,haf}(7)$
: 外気温度 7 ℃における無着霜時の中間運転消費電力 (W)

である。
:::

$$
\Phi_\mathrm{h,ext}(-7) = 0.734 \times \Phi_\mathrm{h,ext}(2)
$$ (eq-h-capm7-ext)

:::{container} where
ここに、

$\Phi_\mathrm{h,ext}(-7)$
: 外気温度 −7 ℃における無着霜時の最大運転能力 (W)

$\Phi_\mathrm{h,ext}(2)$
: 外気温度 2 ℃における無着霜時の最大運転能力 (W)

である。
:::

$$
P_\mathrm{h,ext}(-7) = 0.877 \times P_\mathrm{h,ext}(2)
$$ (eq-h-powm7-ext)

:::{container} where
ここに、

$P_\mathrm{h,ext}(-7)$
: 外気温度 −7 ℃における無着霜時の最大運転消費電力 (W)

$P_\mathrm{h,ext}(2)$
: 外気温度 2 ℃における無着霜時の最大運転消費電力 (W)

である。
:::

#### 外気 2 ℃の無着霜時の値 (最大運転)

外気 2 ℃における無着霜時の最大運転の能力と消費電力は、着霜時の試験値に係数を掛けて求める (附属書 B の表 B.4)。

$$
\Phi_\mathrm{h,ext}(2) = 1.12 \times \Phi_\mathrm{h,ext,f}(2)
$$ (eq-h-cap2-ext)

:::{container} where
ここに、

$\Phi_\mathrm{h,ext}(2)$
: 外気温度 2 ℃における無着霜時の最大運転能力 (W)

$\Phi_\mathrm{h,ext,f}(2)$
: 外気温度 2 ℃における着霜時の最大運転能力 (W)

である。
:::

$$
P_\mathrm{h,ext}(2) = 1.06 \times P_\mathrm{h,ext,f}(2)
$$ (eq-h-pow2-ext)

:::{container} where
ここに、

$P_\mathrm{h,ext}(2)$
: 外気温度 2 ℃における無着霜時の最大運転消費電力 (W)

$P_\mathrm{h,ext,f}(2)$
: 外気温度 2 ℃における着霜時の最大運転消費電力 (W)

である。
:::

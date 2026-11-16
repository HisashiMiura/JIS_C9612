# 評価方法

本章では、本プログラムが実装する計算方法を示す。
計算方法は JIS C 9612:2013 附属書 B (以下、附属書 B)による。
各式の上の説明文には、対応する附属書 B の式番号を示す。
附属書 B と異なる解釈をとった箇所、附属書 B に明記がない事項は、{doc}`04_rationale` に記録した。

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
$\Phi_{\mathrm{ful},t100}$
: 定格冷房能力 (表示値) (W)

$\Phi_\mathrm{ful}(35)$
: 冷房能力試験 (外気 35 ℃)での定格運転能力 (W)

$P_\mathrm{ful}(35)$
: 冷房能力試験 (外気 35 ℃)での定格運転消費電力 (W)

$\Phi_\mathrm{haf}(35)$
: 冷房能力試験 (外気 35 ℃)での中間運転能力 (W)

$P_\mathrm{haf}(35)$
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
L_\mathrm{CST} = \sum_j L(t_j)\,n_j
$$ (eq-cstl)

:::{container} where
ここに、

$L_\mathrm{CST}$
: 冷房期間総合空調負荷 (CSTL) (Wh)

$L(t_j)$
: 温度区分 $j$ における空調負荷 (W)

$n_j$
: 温度区分 $j$ の発生時間 (h)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

$$
C_\mathrm{CSE} = \sum_j P(t_j)\,n_j
$$ (eq-csec)

:::{container} where
ここに、

$C_\mathrm{CSE}$
: 冷房期間消費電力量 (CSEC) (Wh)

$P(t_j)$
: 温度区分 $j$ における消費電力 (W)

$n_j$
: 温度区分 $j$ の発生時間 (h)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

### 外気温度の発生時間

外気温度 $t_j$ とその発生時間 $n_j$ は、附属書 B の表 B.3 (東京)による ({numref}`tbl-c-bins`)。
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
* - $n_j$ (h)
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

温度区分 $j$ ごとに、想定冷房空調負荷 $L_\mathrm{c}(t_j)$ を中間運転能力 $\Phi_\mathrm{haf}(t_j)$ と定格運転能力 $\Phi_\mathrm{ful}(t_j)$ に比べて、運転状態を断続運転、可変運転、定格運転のいずれかに判定する ({numref}`fig-c-regions`、{ref}`r-region`)。

```{figure} figures/cooling_regions.svg
:name: fig-c-regions
:width: 100%

想定冷房空調負荷、運転能力、交点温度と運転状態の関係 (冷房)

数値は説明用の例である (定格冷房能力 (表示値) 2 800 W、中間運転能力 (35 ℃) 1 400 W)。
```

空調負荷 $L(t_j)$ は、負荷が定格運転能力以下なら想定冷房空調負荷そのものとし、定格運転能力を超えるときは定格運転能力とする (附属書 B の式 (B.5))。

$$
L(t_j) =
\begin{cases}
L_\mathrm{c}(t_j) & \text{($L_\mathrm{c}(t_j) \le \Phi_\mathrm{ful}(t_j)$ のとき)} \\
\Phi_\mathrm{ful}(t_j) & \text{($L_\mathrm{c}(t_j) > \Phi_\mathrm{ful}(t_j)$ のとき)}
\end{cases}
$$ (eq-c-l)

:::{container} where
ここに、

$L(t_j)$
: 温度区分 $j$ における空調負荷 (W)

$L_\mathrm{c}(t_j)$
: 外気温度 $t_j$ における想定冷房空調負荷 (W)

$\Phi_\mathrm{ful}(t_j)$
: 外気温度 $t_j$ における定格運転能力 (W)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

消費電力 $P(t_j)$ は、運転状態ごとに次式による (附属書 B の式 (B.11))。

$$
P(t_j) =
\begin{cases}
\dfrac{X(t_j)\,P_\mathrm{haf}(t_j)}{F_\mathrm{PL}(t_j)} & \text{(断続運転: $L_\mathrm{c}(t_j) \le \Phi_\mathrm{haf}(t_j)$ のとき)} \\[2ex]
P_\mathrm{hf}(t_j) & \text{(可変運転: $\Phi_\mathrm{haf}(t_j) < L_\mathrm{c}(t_j) \le \Phi_\mathrm{ful}(t_j)$ のとき)} \\[1ex]
P_\mathrm{ful}(t_j) & \text{(定格運転: $L_\mathrm{c}(t_j) > \Phi_\mathrm{ful}(t_j)$ のとき)}
\end{cases}
$$ (eq-c-p)

:::{container} where
ここに、

$P(t_j)$
: 温度区分 $j$ における消費電力 (W)

$X(t_j)$
: 外気温度 $t_j$ における運転率 (−)

$P_\mathrm{haf}(t_j)$
: 外気温度 $t_j$ における中間運転消費電力 (W)

$F_\mathrm{PL}(t_j)$
: 外気温度 $t_j$ における部分負荷率 (−)

$P_\mathrm{hf}(t_j)$
: 外気温度 $t_j$ で可変運転したときの消費電力 (W)

$P_\mathrm{ful}(t_j)$
: 外気温度 $t_j$ における定格運転消費電力 (W)

$L_\mathrm{c}(t_j)$
: 外気温度 $t_j$ における想定冷房空調負荷 (W)

$\Phi_\mathrm{haf}(t_j)$
: 外気温度 $t_j$ における中間運転能力 (W)

$\Phi_\mathrm{ful}(t_j)$
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

想定冷房空調負荷が中間運転能力以下のときは、中間運転能力で運転と停止を繰り返して負荷に合わせる。附属書 B は、中間運転能力より小さい負荷では、中間運転能力で断続運転すると仮定している (B.1.6.5.5 a))。

断続運転のときの消費電力は、次の考え方で求める。

1. 運転している時間の割合を運転率 $X(t_j)$ とする。運転率は、想定冷房空調負荷と中間運転能力の比である。たとえば負荷が中間運転能力の半分なら、運転率は 0.5 であり、時間の半分だけ運転すれば負荷を処理できる。
2. 運転している間の消費電力は中間運転消費電力 $P_\mathrm{haf}(t_j)$ なので、効率が変わらなければ、平均の消費電力は $X(t_j)\,P_\mathrm{haf}(t_j)$ となる。
3. 実際には、起動のたびに損失が生じ、運転と停止を繰り返すと効率が下がる。この効率の低下を部分負荷率 $F_\mathrm{PL}(t_j)$ (1 以下の値)で表し、$X(t_j)\,P_\mathrm{haf}(t_j)$ を $F_\mathrm{PL}(t_j)$ で割って消費電力を大きくする。停止している時間が長い (運転率が小さい)ほど、効率の低下は大きい。

例として、{numref}`fig-c-power` の外気温度 26 ℃では、想定冷房空調負荷 700 W、中間運転能力 1 561.7 W、中間運転消費電力 243.9 W である。運転率は 700 / 1 561.7 = 0.448、効率が変わらない場合の消費電力は 0.448 × 243.9 = 109.3 W、部分負荷率は 1 − 0.25 × (1 − 0.448) = 0.862 であり、消費電力は 109.3 / 0.862 = 126.8 W となる。

部分負荷率と運転率は、次式による (附属書 B の式 (B.8)、(B.7))。

部分負荷率 $F_\mathrm{PL}(t_j)$ は、効率低下係数 $C_\mathrm{D}$ を用いて次式で求める。効率低下係数は、断続運転によって生じる効率の低下を表す係数であり、試験を行わず 0.25 とする (附属書 B の表 B.1、B.1.5.3.3)。

$$
F_\mathrm{PL}(t_j) = 1 - C_\mathrm{D}\,[1 - X(t_j)]
$$ (eq-c-plf)

:::{container} where
ここに、

$F_\mathrm{PL}(t_j)$
: 外気温度 $t_j$ における部分負荷率 (−)

$C_\mathrm{D}$
: 効率低下係数。0.25 とする (−)

$X(t_j)$
: 外気温度 $t_j$ における運転率 (−)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

運転率 $X(t_j)$ は、想定冷房空調負荷と運転能力の比であり、次式による。

$$
X(t_j) = \frac{L_\mathrm{c}(t_j)}{\Phi(t_j)}
$$ (eq-c-x)

:::{container} where
ここに、

$X(t_j)$
: 外気温度 $t_j$ における運転率 (−)

$L_\mathrm{c}(t_j)$
: 外気温度 $t_j$ における想定冷房空調負荷 (W)

$\Phi(t_j)$
: 外気温度 $t_j$ において断続運転するときの運転能力 (W)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

#### 可変運転

想定冷房空調負荷が中間運転能力を超え、定格運転能力以下のときは、能力を連続的に変えて、負荷とつり合う能力で運転する。

可変運転での消費電力 $P_\mathrm{hf}(t_j)$ は、想定冷房空調負荷を可変運転のエネルギー消費効率で割って求める (附属書 B の式 (B.15))。

$$
P_\mathrm{hf}(t_j) = \frac{L_\mathrm{c}(t_j)}{E_\mathrm{ER,hf}(t_j)}
$$ (eq-c-phf)

:::{container} where
ここに、

$P_\mathrm{hf}(t_j)$
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

交点温度でのエネルギー消費効率は、次式による (附属書 B の式 (B.12)、(B.13))。

$$
E_\mathrm{ER,haf}(t_\mathrm{c}) = \frac{\Phi_\mathrm{haf}(t_\mathrm{c})}{P_\mathrm{haf}(t_\mathrm{c})}
$$ (eq-c-eer-haf)

:::{container} where
ここに、

$E_\mathrm{ER,haf}(t_\mathrm{c})$
: 外気温度 $t_\mathrm{c}$ における中間運転のエネルギー消費効率 (−)

$\Phi_\mathrm{haf}(t_\mathrm{c})$
: 外気温度 $t_\mathrm{c}$ における中間運転能力 (W)

$P_\mathrm{haf}(t_\mathrm{c})$
: 外気温度 $t_\mathrm{c}$ における中間運転消費電力 (W)

$t_\mathrm{c}$
: 想定冷房空調負荷と中間運転能力が等しくなる外気温度 (℃)

である。
:::

$$
E_\mathrm{ER,ful}(t_\mathrm{b}) = \frac{\Phi_\mathrm{ful}(t_\mathrm{b})}{P_\mathrm{ful}(t_\mathrm{b})}
$$ (eq-c-eer-ful)

:::{container} where
ここに、

$E_\mathrm{ER,ful}(t_\mathrm{b})$
: 外気温度 $t_\mathrm{b}$ における定格運転のエネルギー消費効率 (−)

$\Phi_\mathrm{ful}(t_\mathrm{b})$
: 外気温度 $t_\mathrm{b}$ における定格運転能力 (W)

$P_\mathrm{ful}(t_\mathrm{b})$
: 外気温度 $t_\mathrm{b}$ における定格運転消費電力 (W)

$t_\mathrm{b}$
: 想定冷房空調負荷と定格運転能力が等しくなる外気温度 (℃)

である。
:::

#### 定格運転

想定冷房空調負荷が定格運転能力を超えるときは、定格運転能力で連続運転する。空調負荷は定格運転能力までしか処理されず、消費電力は定格運転消費電力 $P_\mathrm{ful}(t_j)$ となる ({ref}`r-c-cstl`)。$\Phi_\mathrm{ful}(t_j)$ と $P_\mathrm{ful}(t_j)$ は、{eq}`eq-c-cap-ful` と {eq}`eq-c-pow-ful` による。

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
L_\mathrm{c}(t_\mathrm{b}) = \Phi_\mathrm{ful}(t_\mathrm{b})
$$ (eq-c-tb-def)

:::{container} where
ここに、

$L_\mathrm{c}(t_\mathrm{b})$
: 外気温度 $t_\mathrm{b}$ における想定冷房空調負荷。{eq}`eq-c-load` による (W)

$\Phi_\mathrm{ful}(t_\mathrm{b})$
: 外気温度 $t_\mathrm{b}$ における定格運転能力。{eq}`eq-c-cap-ful` による (W)

$t_\mathrm{b}$
: 想定冷房空調負荷と定格運転能力が等しくなる外気温度 (℃)

である。
:::

$$
L_\mathrm{c}(t_\mathrm{c}) = \Phi_\mathrm{haf}(t_\mathrm{c})
$$ (eq-c-tc-def)

:::{container} where
ここに、

$L_\mathrm{c}(t_\mathrm{c})$
: 外気温度 $t_\mathrm{c}$ における想定冷房空調負荷。{eq}`eq-c-load` による (W)

$\Phi_\mathrm{haf}(t_\mathrm{c})$
: 外気温度 $t_\mathrm{c}$ における中間運転能力。{eq}`eq-c-cap-haf` による (W)

$t_\mathrm{c}$
: 想定冷房空調負荷と中間運転能力が等しくなる外気温度 (℃)

である。
:::

負荷も能力も外気温度の 1 次式なので、上の関係を外気温度について解くと、交点温度は次式で求まる (附属書 B の式 (B.20)、(B.22)、{ref}`r-intersection`)。式中の 6 は、能力の 2 つの試験温度 35 ℃と 29 ℃の差である。

$$
t_\mathrm{b} = \frac{6\,\Phi_{\mathrm{ful},t100}\,t_0 + 6\,\Phi_\mathrm{ful}(35)\,(t_{100} - t_0) + 35\,[\Phi_\mathrm{ful}(29) - \Phi_\mathrm{ful}(35)]\,(t_{100} - t_0)}{6\,\Phi_{\mathrm{ful},t100} + [\Phi_\mathrm{ful}(29) - \Phi_\mathrm{ful}(35)]\,(t_{100} - t_0)}
$$ (eq-c-tb)

:::{container} where
ここに、

$t_\mathrm{b}$
: 想定冷房空調負荷と定格運転能力が等しくなる外気温度 (℃)

$\Phi_{\mathrm{ful},t100}$
: 定格冷房能力 (表示値) (W)

$\Phi_\mathrm{ful}(35)$
: 外気温度 35 ℃における定格運転能力 (W)

$\Phi_\mathrm{ful}(29)$
: 外気温度 29 ℃における定格運転能力 (W)

$t_0$
: 想定冷房空調負荷が 0 となる外気温度。23 ℃とする (℃)

$t_{100}$
: 想定冷房空調負荷が定格冷房能力と等しくなる外気温度。35 ℃とする (℃)

である。
:::

$$
t_\mathrm{c} = \frac{6\,\Phi_{\mathrm{ful},t100}\,t_0 + 6\,\Phi_\mathrm{haf}(35)\,(t_{100} - t_0) + 35\,[\Phi_\mathrm{haf}(29) - \Phi_\mathrm{haf}(35)]\,(t_{100} - t_0)}{6\,\Phi_{\mathrm{ful},t100} + [\Phi_\mathrm{haf}(29) - \Phi_\mathrm{haf}(35)]\,(t_{100} - t_0)}
$$ (eq-c-tc)

:::{container} where
ここに、

$t_\mathrm{c}$
: 想定冷房空調負荷と中間運転能力が等しくなる外気温度 (℃)

$\Phi_{\mathrm{ful},t100}$
: 定格冷房能力 (表示値) (W)

$\Phi_\mathrm{haf}(35)$
: 外気温度 35 ℃における中間運転能力 (W)

$\Phi_\mathrm{haf}(29)$
: 外気温度 29 ℃における中間運転能力 (W)

$t_0$
: 想定冷房空調負荷が 0 となる外気温度。23 ℃とする (℃)

$t_{100}$
: 想定冷房空調負荷が定格冷房能力と等しくなる外気温度。35 ℃とする (℃)

である。
:::

### 想定冷房空調負荷

外気温度 $t$ における想定冷房空調負荷 $L_\mathrm{c}(t)$ は、外気温度 $t_0$ で 0、$t_{100}$ で定格冷房能力 (表示値)となる直線とする (附属書 B の式 (B.2)、(B.16))。

$$
L_\mathrm{c}(t) = \Phi_{\mathrm{ful},t100} \times \frac{t - t_0}{t_{100} - t_0}
$$ (eq-c-load)

:::{container} where
ここに、

$L_\mathrm{c}(t)$
: 外気温度 $t$ における想定冷房空調負荷 (W)

$\Phi_{\mathrm{ful},t100}$
: 定格冷房能力 (表示値) (W)

$t$
: 外気温度 (℃)

$t_0$
: 想定冷房空調負荷が 0 となる外気温度 (℃)

$t_{100}$
: 想定冷房空調負荷が定格冷房能力と等しくなる外気温度 (℃)

である。
:::

なお、$t_0 = 23$ ℃、$t_{100} = 35$ ℃ とする。

### 能力・消費電力の特性

外気温度 $t$ における能力と消費電力は、外気 35 ℃と 29 ℃の値を結ぶ直線とする。特性線は、定格運転と中間運転の 2 本を用いる。

定格運転能力 $\Phi_\mathrm{ful}(t)$ と定格運転消費電力 $P_\mathrm{ful}(t)$ は、次式による (附属書 B の式 (B.3)、(B.4))。

$$
\Phi_\mathrm{ful}(t) = \Phi_\mathrm{ful}(35) + \frac{\Phi_\mathrm{ful}(29) - \Phi_\mathrm{ful}(35)}{29 - 35}\,(t - 35)
$$ (eq-c-cap-ful)

:::{container} where
ここに、

$\Phi_\mathrm{ful}(t)$
: 外気温度 $t$ における定格運転能力 (W)

$\Phi_\mathrm{ful}(35)$
: 外気温度 35 ℃における定格運転能力 (W)

$\Phi_\mathrm{ful}(29)$
: 外気温度 29 ℃における定格運転能力 (W)

$t$
: 外気温度 (℃)

である。
:::

$$
P_\mathrm{ful}(t) = P_\mathrm{ful}(35) + \frac{P_\mathrm{ful}(29) - P_\mathrm{ful}(35)}{29 - 35}\,(t - 35)
$$ (eq-c-pow-ful)

:::{container} where
ここに、

$P_\mathrm{ful}(t)$
: 外気温度 $t$ における定格運転消費電力 (W)

$P_\mathrm{ful}(35)$
: 外気温度 35 ℃における定格運転消費電力 (W)

$P_\mathrm{ful}(29)$
: 外気温度 29 ℃における定格運転消費電力 (W)

$t$
: 外気温度 (℃)

である。
:::

中間運転能力 $\Phi_\mathrm{haf}(t)$ と中間運転消費電力 $P_\mathrm{haf}(t)$ は、次式による (附属書 B の式 (B.9)、(B.10))。

$$
\Phi_\mathrm{haf}(t) = \Phi_\mathrm{haf}(35) + \frac{\Phi_\mathrm{haf}(29) - \Phi_\mathrm{haf}(35)}{29 - 35}\,(t - 35)
$$ (eq-c-cap-haf)

:::{container} where
ここに、

$\Phi_\mathrm{haf}(t)$
: 外気温度 $t$ における中間運転能力 (W)

$\Phi_\mathrm{haf}(35)$
: 外気温度 35 ℃における中間運転能力 (W)

$\Phi_\mathrm{haf}(29)$
: 外気温度 29 ℃における中間運転能力 (W)

$t$
: 外気温度 (℃)

である。
:::

$$
P_\mathrm{haf}(t) = P_\mathrm{haf}(35) + \frac{P_\mathrm{haf}(29) - P_\mathrm{haf}(35)}{29 - 35}\,(t - 35)
$$ (eq-c-pow-haf)

:::{container} where
ここに、

$P_\mathrm{haf}(t)$
: 外気温度 $t$ における中間運転消費電力 (W)

$P_\mathrm{haf}(35)$
: 外気温度 35 ℃における中間運転消費電力 (W)

$P_\mathrm{haf}(29)$
: 外気温度 29 ℃における中間運転消費電力 (W)

$t$
: 外気温度 (℃)

である。
:::

### 試験値の補完

外気 29 ℃での値は、外気 35 ℃の試験値に係数を掛けて求める (附属書 B の表 B.1、{ref}`r-c-coef`)。

定格運転能力 $\Phi_\mathrm{ful}(29)$ と定格運転消費電力 $P_\mathrm{ful}(29)$ は、次式による。

$$
\Phi_\mathrm{ful}(29) = 1.077 \times \Phi_\mathrm{ful}(35)
$$ (eq-c-cap29-ful)

:::{container} where
ここに、

$\Phi_\mathrm{ful}(29)$
: 外気温度 29 ℃における定格運転能力 (W)

$\Phi_\mathrm{ful}(35)$
: 外気温度 35 ℃における定格運転能力 (W)

である。
:::

$$
P_\mathrm{ful}(29) = 0.914 \times P_\mathrm{ful}(35)
$$ (eq-c-pow29-ful)

:::{container} where
ここに、

$P_\mathrm{ful}(29)$
: 外気温度 29 ℃における定格運転消費電力 (W)

$P_\mathrm{ful}(35)$
: 外気温度 35 ℃における定格運転消費電力 (W)

である。
:::

中間運転能力 $\Phi_\mathrm{haf}(29)$ と中間運転消費電力 $P_\mathrm{haf}(29)$ は、次式による。

$$
\Phi_\mathrm{haf}(29) = 1.077 \times \Phi_\mathrm{haf}(35)
$$ (eq-c-cap29-haf)

:::{container} where
ここに、

$\Phi_\mathrm{haf}(29)$
: 外気温度 29 ℃における中間運転能力 (W)

$\Phi_\mathrm{haf}(35)$
: 外気温度 35 ℃における中間運転能力 (W)

である。
:::

$$
P_\mathrm{haf}(29) = 0.914 \times P_\mathrm{haf}(35)
$$ (eq-c-pow29-haf)

:::{container} where
ここに、

$P_\mathrm{haf}(29)$
: 外気温度 29 ℃における中間運転消費電力 (W)

$P_\mathrm{haf}(35)$
: 外気温度 35 ℃における中間運転消費電力 (W)

である。
:::

## 暖房期間

<!-- 冷房期間の実装・テストが終わってから執筆する。DESIGN.md の 2.2 を参照。 -->

(執筆予定)

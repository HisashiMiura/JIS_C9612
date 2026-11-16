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

### 対象とする機種

本プログラムは、回転数制御形ルームエアコンだけを対象とする。
回転数制御形は、負荷に応じて圧縮機の回転数を一定の範囲で 3 段階以上または連続的に変えられる機種である (JIS C 9612:2013 の 3.12)。
附属書 B のうち、回転数制御形の計算方法 (B.1.6.5、B.2.6.5)を実装し、定速単圧縮機形の計算方法 (B.1.6.4、B.2.6.4)は実装しない ({ref}`scope`)。

## 冷房期間

### 入力値

冷房期間の計算に用いる入力値を {numref}`tbl-c-input` に示す。

```{list-table} 冷房期間の入力値
:name: tbl-c-input
:header-rows: 1

* - 記号
  - 内容
  - 単位
* - $\Phi_{\mathrm{ful},t100}$
  - 定格冷房能力 (表示値)
  - W
* - $\Phi_\mathrm{ful}(35)$, $P_\mathrm{ful}(35)$
  - 冷房能力試験 (外気 35 ℃)での定格運転能力・消費電力
  - W
* - $\Phi_\mathrm{haf}(35)$, $P_\mathrm{haf}(35)$
  - 冷房能力試験 (外気 35 ℃)での中間運転能力・消費電力
  - W
```

外気 29 ℃での値は入力せず、係数で求める ({ref}`r-c-coef`)。

中間運転能力は、定格冷房能力 (表示値)の 50 % (許容範囲 45 %〜55 %)で測定した値とする (附属書 B の B.1.5.3.1)。
最小運転能力・消費電力は、冷房期間の計算に用いない ({ref}`r-c-min`)。

### 試験値の補完

外気 29 ℃での値は、外気 35 ℃の試験値に係数を掛けて求める (附属書 B の表 B.1、{ref}`r-c-coef`)。

$$
\Phi_x(29) = 1.077 \times \Phi_x(35), \qquad
P_x(29) = 0.914 \times P_x(35)
$$ (eq-c-coef29)

:::{container} where
ここに、

$\Phi_x(29)$
: 外気温度 29 ℃における運転能力 (W)

$\Phi_x(35)$
: 外気温度 35 ℃における運転能力 (W)

$P_x(29)$
: 外気温度 29 ℃における運転消費電力 (W)

$P_x(35)$
: 外気温度 35 ℃における運転消費電力 (W)

$x$
: 運転の種類を表す添字。ful は定格運転、haf は中間運転を表す

である。
:::

効率低下係数 $C_\mathrm{D}$ は、試験を行わず 0.25 とする (附属書 B の表 B.1、B.1.5.3.3)。

### 能力・消費電力の特性

外気温度 $t$ における能力 $\Phi_x(t)$ と消費電力 $P_x(t)$ は、外気 35 ℃と 29 ℃の値を結ぶ直線とする (附属書 B の式 (B.3)、(B.4)、(B.9)、(B.10))。

$$
\Phi_x(t) = \Phi_x(35) + \frac{\Phi_x(29) - \Phi_x(35)}{29 - 35}\,(t - 35)
$$ (eq-c-cap)

:::{container} where
ここに、

$\Phi_x(t)$
: 外気温度 $t$ における運転能力 (W)

$\Phi_x(35)$
: 外気温度 35 ℃における運転能力 (W)

$\Phi_x(29)$
: 外気温度 29 ℃における運転能力 (W)

$t$
: 外気温度 (℃)

$x$
: 運転の種類を表す添字。ful は定格運転、haf は中間運転を表す

である。
:::

$$
P_x(t) = P_x(35) + \frac{P_x(29) - P_x(35)}{29 - 35}\,(t - 35)
$$ (eq-c-pow)

:::{container} where
ここに、

$P_x(t)$
: 外気温度 $t$ における運転消費電力 (W)

$P_x(35)$
: 外気温度 35 ℃における運転消費電力 (W)

$P_x(29)$
: 外気温度 29 ℃における運転消費電力 (W)

$t$
: 外気温度 (℃)

$x$
: 運転の種類を表す添字。ful は定格運転、haf は中間運転を表す

である。
:::

特性線は、定格運転 ($x = \mathrm{ful}$)と中間運転 ($x = \mathrm{haf}$)の 2 本を用いる。

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

### 交点温度

可変運転域の効率を補間するため、次の 2 つの交点温度を用いる。

- $t_\mathrm{b}$:想定冷房空調負荷が定格運転能力と等しくなる外気温度。$L_\mathrm{c}(t_\mathrm{b}) = \Phi_\mathrm{ful}(t_\mathrm{b})$
- $t_\mathrm{c}$:想定冷房空調負荷が中間運転能力と等しくなる外気温度。$L_\mathrm{c}(t_\mathrm{c}) = \Phi_\mathrm{haf}(t_\mathrm{c})$

負荷線と能力線はどちらも外気温度の 1 次式である。
そこで、2 直線 $y = a_1 + b_1 t$ と $y = a_2 + b_2 t$ の交点として求める ({ref}`r-intersection`)。この式は附属書 B の式 (B.20)、(B.22) と同じ値を与える。

$$
t = \frac{a_2 - a_1}{b_1 - b_2}
$$ (eq-intersection)

:::{container} where
ここに、

$t$
: 2 直線の交点の外気温度 (℃)

$a_1$
: 一方の直線の切片 (W)

$b_1$
: 一方の直線の傾き (W/℃)

$a_2$
: 他方の直線の切片 (W)

$b_2$
: 他方の直線の傾き (W/℃)

である。
:::

### 温度区分ごとの計算

温度区分 $j$ ごとに、想定冷房空調負荷 $L_\mathrm{c}(t_j)$ と能力を比べて運転状態を判定する ({ref}`r-region`)。
各運転状態での空調負荷 $L(t_j)$ と消費電力 $P(t_j)$ を、以下に示す。

断続運転では、負荷と能力の比 $X(t_j)$ (運転率)と、部分負荷率 $F_\mathrm{PL}(t_j)$ を用いる (附属書 B の式 (B.7)、(B.8))。

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

$$
F_\mathrm{PL}(t_j) = 1 - C_\mathrm{D}\,[1 - X(t_j)]
$$ (eq-c-plf)

:::{container} where
ここに、

$F_\mathrm{PL}(t_j)$
: 外気温度 $t_j$ における部分負荷率 (−)

$C_\mathrm{D}$
: 効率低下係数 (−)

$X(t_j)$
: 外気温度 $t_j$ における運転率 (−)

$t_j$
: 温度区分 $j$ の外気温度 (℃)

である。
:::

運転状態は {numref}`tbl-c-inverter` の 3 つに分かれる。

```{list-table} 運転状態ごとの空調負荷と消費電力 (冷房)
:name: tbl-c-inverter
:header-rows: 1

* - 運転状態
  - 判定条件
  - 空調負荷 $L(t_j)$
  - 消費電力 $P(t_j)$
* - 断続運転
  - $L_\mathrm{c}(t_j) \le \Phi_\mathrm{haf}(t_j)$
  - $L_\mathrm{c}(t_j)$
  - $\dfrac{X(t_j)\,P_\mathrm{haf}(t_j)}{F_\mathrm{PL}(t_j)}$、$\Phi(t_j) = \Phi_\mathrm{haf}(t_j)$
* - 可変運転
  - $\Phi_\mathrm{haf}(t_j) < L_\mathrm{c}(t_j) \le \Phi_\mathrm{ful}(t_j)$
  - $L_\mathrm{c}(t_j)$
  - $P_\mathrm{hf}(t_j)$、式 {eq}`eq-c-phf`
* - 定格運転
  - $L_\mathrm{c}(t_j) > \Phi_\mathrm{ful}(t_j)$
  - $\Phi_\mathrm{ful}(t_j)$
  - $P_\mathrm{ful}(t_j)$
```

断続運転は、中間運転能力で運転と停止を繰り返す状態である。
附属書 B は、中間運転能力より小さい負荷では、中間運転能力で断続運転すると仮定している (B.1.6.5.5 a))。

可変運転での消費電力 $P_\mathrm{hf}(t_j)$ は、交点温度 $t_\mathrm{c}$ と $t_\mathrm{b}$ でのエネルギー消費効率 (EER)を外気温度で直線補間して求める (附属書 B の式 (B.12)〜(B.15))。

$$
E_\mathrm{ER,haf}(t_\mathrm{c}) = \frac{\Phi_\mathrm{haf}(t_\mathrm{c})}{P_\mathrm{haf}(t_\mathrm{c})}, \qquad
E_\mathrm{ER,ful}(t_\mathrm{b}) = \frac{\Phi_\mathrm{ful}(t_\mathrm{b})}{P_\mathrm{ful}(t_\mathrm{b})}
$$ (eq-c-eer-ends)

:::{container} where
ここに、

$E_\mathrm{ER,haf}(t_\mathrm{c})$
: 外気温度 $t_\mathrm{c}$ における中間運転のエネルギー消費効率 (−)

$E_\mathrm{ER,ful}(t_\mathrm{b})$
: 外気温度 $t_\mathrm{b}$ における定格運転のエネルギー消費効率 (−)

$\Phi_\mathrm{haf}(t_\mathrm{c})$
: 外気温度 $t_\mathrm{c}$ における中間運転能力 (W)

$P_\mathrm{haf}(t_\mathrm{c})$
: 外気温度 $t_\mathrm{c}$ における中間運転消費電力 (W)

$\Phi_\mathrm{ful}(t_\mathrm{b})$
: 外気温度 $t_\mathrm{b}$ における定格運転能力 (W)

$P_\mathrm{ful}(t_\mathrm{b})$
: 外気温度 $t_\mathrm{b}$ における定格運転消費電力 (W)

$t_\mathrm{c}$
: 想定冷房空調負荷と中間運転能力が等しくなる外気温度 (℃)

$t_\mathrm{b}$
: 想定冷房空調負荷と定格運転能力が等しくなる外気温度 (℃)

である。
:::

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

### 冷房期間の合計と効率

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

## 暖房期間

<!-- 冷房期間の実装・テストが終わってから執筆する。DESIGN.md の 2.2 を参照。 -->

(執筆予定)

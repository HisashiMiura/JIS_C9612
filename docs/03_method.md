# 評価方法

本章では、本プログラムが実装する計算方法を示す。
計算方法は JIS C 9612:2013 附属書 B(以下、附属書 B)による。
各式の末尾には、対応する附属書 B の式番号を〔 〕で示す。
附属書 B と異なる解釈をとった箇所、附属書 B に明記がない事項は、{doc}`04_rationale` に記録した。

## 概要

### 通年エネルギー消費効率

通年エネルギー消費効率(APF)$F_\mathrm{AP}$ は、冷房期間と暖房期間を通じた空調負荷の合計を、消費電力量の合計で割って求める。

$$
F_\mathrm{AP} = \frac{L_\mathrm{CST} + L_\mathrm{HST}}{C_\mathrm{CSE} + C_\mathrm{HSE}}
\quad \text{〔B.76〕}
$$ (eq-apf)

ここに、

- $L_\mathrm{CST}$:冷房期間総合空調負荷(CSTL)[Wh]
- $C_\mathrm{CSE}$:冷房期間消費電力量(CSEC)[Wh]
- $L_\mathrm{HST}$:暖房期間総合空調負荷(HSTL)[Wh]
- $C_\mathrm{HSE}$:暖房期間消費電力量(HSEC)[Wh]

### 計算の流れ

冷房期間・暖房期間とも、次の順に計算する。

1. **試験値の補完**:附属書 B で試験を行わないと定められた値を、試験値に係数を掛けて求める。
2. **能力・消費電力の特性**:2 つの外気温度での値を結ぶ直線で、各外気温度での能力と消費電力を表す。
3. **想定空調負荷**:外気温度に比例する負荷線で、各外気温度での空調負荷を表す。
4. **交点温度**:空調負荷と能力が等しくなる外気温度を求める。可変運転域の効率の補間に使う。
5. **温度区分ごとの計算**:外気温度の温度区分 $j$ ごとに運転状態を判定し、空調負荷と消費電力を求める。
6. **期間合計**:各温度区分の値に発生時間 $n_j$ を掛けて合計する。

### 機種の種類

本プログラムは、次の 2 種類を扱う。

- **定速単圧縮機形**:能力を変えられない。負荷が能力を下回るときは、断続運転(オン・オフ)で負荷に合わせる。
- **回転数制御形**:能力を連続的に変えられる。

## 冷房期間

### 入力値

冷房期間の計算に用いる入力値を {numref}`tbl-c-input` に示す。

```{list-table} 冷房期間の入力値
:name: tbl-c-input
:header-rows: 1

* - 記号
  - 内容
  - 単位
  - 定速単圧縮機形
  - 回転数制御形
* - $\Phi_{\mathrm{ful},t100}$
  - 定格冷房能力(表示値)
  - W
  - 必須
  - 必須
* - $\Phi_\mathrm{ful}(35)$, $P_\mathrm{ful}(35)$
  - 冷房能力試験(外気 35 ℃)での定格運転能力・消費電力
  - W
  - 必須
  - 必須
* - $\Phi_\mathrm{haf}(35)$, $P_\mathrm{haf}(35)$
  - 冷房能力試験(外気 35 ℃)での中間運転能力・消費電力
  - W
  - —
  - 必須
* - $\Phi_\mathrm{ful}(29)$, $P_\mathrm{ful}(29)$
  - 冷房低温能力試験(外気 29 ℃)での定格運転能力・消費電力
  - W
  - 必須
  - —(係数で求める)
```

中間運転能力は、定格冷房能力(表示値)の 50 %(許容範囲 45 %〜55 %)で測定した値とする(附属書 B の B.1.5.3.1)。
最小運転能力・消費電力は、冷房期間の計算に用いない({ref}`r-c-min`)。

### 試験値の補完

回転数制御形では、外気 29 ℃での値を、外気 35 ℃の試験値に係数を掛けて求める(附属書 B の表 B.1、{ref}`r-c-coef`)。
添字 $x$ は、定格(ful)または中間(haf)を表す。

$$
\Phi_x(29) = 1.077 \times \Phi_x(35), \qquad
P_x(29) = 0.914 \times P_x(35)
$$ (eq-c-coef29)

効率低下係数 $C_\mathrm{D}$ は、試験を行わず 0.25 とする(附属書 B の表 B.1、B.1.5.3.3)。

### 能力・消費電力の特性

外気温度 $t$ における能力 $\Phi_x(t)$ と消費電力 $P_x(t)$ は、外気 35 ℃と 29 ℃の値を結ぶ直線とする。

$$
\Phi_x(t) = \Phi_x(35) + \frac{\Phi_x(29) - \Phi_x(35)}{29 - 35}\,(t - 35)
\quad \text{〔B.3, B.9〕}
$$ (eq-c-cap)

$$
P_x(t) = P_x(35) + \frac{P_x(29) - P_x(35)}{29 - 35}\,(t - 35)
\quad \text{〔B.4, B.10〕}
$$ (eq-c-pow)

定速単圧縮機形では $x = \mathrm{ful}$ だけを、回転数制御形では $x = \mathrm{ful}, \mathrm{haf}$ を用いる。

### 想定冷房空調負荷

外気温度 $t$ における想定冷房空調負荷 $L_\mathrm{c}(t)$ は、外気温度 $t_0$ で 0、$t_{100}$ で定格冷房能力(表示値)となる直線とする。

$$
L_\mathrm{c}(t) = \Phi_{\mathrm{ful},t100} \times \frac{t - t_0}{t_{100} - t_0}
\quad \text{〔B.2, B.16〕}
$$ (eq-c-load)

ここに、$t_0 = 23$ ℃、$t_{100} = 35$ ℃ とする。

### 外気温度の発生時間

外気温度 $t_j$ とその発生時間 $n_j$ は、附属書 B の表 B.3(東京)による({numref}`tbl-c-bins`)。
特定地域の値を用いる場合は、附属書 B の B.1.9 による。

```{list-table} 冷房期間の外気温度の発生時間(東京)
:name: tbl-c-bins
:header-rows: 1
:stub-columns: 1

* - $t_j$ [℃]
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
* - $n_j$ [h]
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

回転数制御形では、可変運転域の効率を補間するため、次の 2 つの交点温度を用いる。

- $t_\mathrm{b}$:想定冷房空調負荷が定格運転能力と等しくなる外気温度。$L_\mathrm{c}(t_\mathrm{b}) = \Phi_\mathrm{ful}(t_\mathrm{b})$
- $t_\mathrm{c}$:想定冷房空調負荷が中間運転能力と等しくなる外気温度。$L_\mathrm{c}(t_\mathrm{c}) = \Phi_\mathrm{haf}(t_\mathrm{c})$

負荷線と能力線はどちらも外気温度の 1 次式である。
そこで、2 直線 $y = a_1 + b_1 t$ と $y = a_2 + b_2 t$ の交点として求める({ref}`r-intersection`)。

$$
t = \frac{a_2 - a_1}{b_1 - b_2}
\quad \text{〔B.20, B.22 と同値〕}
$$ (eq-intersection)

### 温度区分ごとの計算

温度区分 $j$ ごとに、想定冷房空調負荷 $L_\mathrm{c}(t_j)$ と能力を比べて運転状態を判定する({ref}`r-region`)。
各運転状態での空調負荷 $L(t_j)$ と消費電力 $P(t_j)$ を、以下に示す。

断続運転では、負荷と能力の比 $X(t_j)$(運転率)と、部分負荷率 $F_\mathrm{PL}(t_j)$ を用いる。

$$
X(t_j) = \frac{L_\mathrm{c}(t_j)}{\Phi(t_j)}
\quad \text{〔B.7〕}
$$ (eq-c-x)

$$
F_\mathrm{PL}(t_j) = 1 - C_\mathrm{D}\,[1 - X(t_j)]
\quad \text{〔B.8〕}
$$ (eq-c-plf)

#### 定速単圧縮機形

```{list-table} 定速単圧縮機形の運転状態(冷房)
:name: tbl-c-fixed
:header-rows: 1

* - 運転状態
  - 判定条件
  - 空調負荷 $L(t_j)$
  - 消費電力 $P(t_j)$
* - 断続運転
  - $L_\mathrm{c}(t_j) \le \Phi_\mathrm{ful}(t_j)$
  - $L_\mathrm{c}(t_j)$
  - $\dfrac{X(t_j)\,P_\mathrm{ful}(t_j)}{F_\mathrm{PL}(t_j)}$、$\Phi(t_j) = \Phi_\mathrm{ful}(t_j)$
* - 定格運転
  - $L_\mathrm{c}(t_j) > \Phi_\mathrm{ful}(t_j)$
  - $\Phi_\mathrm{ful}(t_j)$
  - $P_\mathrm{ful}(t_j)$
```

#### 回転数制御形

```{list-table} 回転数制御形の運転状態(冷房)
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

可変運転での消費電力 $P_\mathrm{hf}(t_j)$ は、交点温度 $t_\mathrm{c}$ と $t_\mathrm{b}$ でのエネルギー消費効率(EER)を外気温度で直線補間して求める。

$$
E_\mathrm{ER,haf}(t_\mathrm{c}) = \frac{\Phi_\mathrm{haf}(t_\mathrm{c})}{P_\mathrm{haf}(t_\mathrm{c})}, \qquad
E_\mathrm{ER,ful}(t_\mathrm{b}) = \frac{\Phi_\mathrm{ful}(t_\mathrm{b})}{P_\mathrm{ful}(t_\mathrm{b})}
\quad \text{〔B.12, B.13〕}
$$ (eq-c-eer-ends)

$$
E_\mathrm{ER,hf}(t_j) = E_\mathrm{ER,haf}(t_\mathrm{c})
+ \frac{E_\mathrm{ER,ful}(t_\mathrm{b}) - E_\mathrm{ER,haf}(t_\mathrm{c})}{t_\mathrm{b} - t_\mathrm{c}}\,(t_j - t_\mathrm{c})
\quad \text{〔B.14〕}
$$ (eq-c-eer-hf)

$$
P_\mathrm{hf}(t_j) = \frac{L_\mathrm{c}(t_j)}{E_\mathrm{ER,hf}(t_j)}
\quad \text{〔B.15〕}
$$ (eq-c-phf)

### 冷房期間の合計と効率

冷房期間総合空調負荷 $L_\mathrm{CST}$ と冷房期間消費電力量 $C_\mathrm{CSE}$ は、温度区分ごとの値に発生時間を掛けて合計する({ref}`r-c-cstl`)。

$$
L_\mathrm{CST} = \sum_j L(t_j)\,n_j
\quad \text{〔B.5〕}
$$ (eq-cstl)

$$
C_\mathrm{CSE} = \sum_j P(t_j)\,n_j
\quad \text{〔B.6, B.11〕}
$$ (eq-csec)

冷房期間エネルギー消費効率(CSPF)$F_\mathrm{CSP}$ は、次式による。

$$
F_\mathrm{CSP} = \frac{L_\mathrm{CST}}{C_\mathrm{CSE}}
\quad \text{〔B.1〕}
$$ (eq-cspf)

## 暖房期間

<!-- 冷房期間の実装・テストが終わってから執筆する。DESIGN.md の 2.2 を参照。 -->

(執筆予定)

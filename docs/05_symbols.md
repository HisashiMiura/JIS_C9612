# 記号の対応

本章では、{doc}`03_method` と {doc}`04_rationale` で用いた記号と、JIS C 9612:2013 附属書 B (以下、附属書 B)の記号の対応を示す。
本書では、冷房期間と暖房期間で意味が変わる記号に添字 c (冷房)または h (暖房)を付け、エネルギー消費効率を $\mathrm{EER}$、$\mathrm{COP}$ と書く。附属書 B は、冷房期間 (B.1)と暖房期間 (B.2)でそれぞれ記号を定義しており、同じ記号が冷房と暖房で別の量を表す。

外気温度の関数として定義した量は、本書では $(t)$、附属書 B では主に $(t_j)$ と書いている。試験温度での値 (例: $\Phi_\mathrm{c,ful}(35)$、$\Phi_\mathrm{h,ful,f}(2)$)は、関数の記号に温度を入れたものであり、表には示していない。附属書 B に単独の記号がない量は、対応する式番号を示した。

## 全体

```{list-table} 全体で用いる記号
:name: tbl-sym-common
:header-rows: 1
:widths: 22 26 42 10

* - 本書の記号
  - 附属書 B の記号
  - 意味
  - 単位
* - $F_\mathrm{AP}$
  - $F_\mathrm{AP}$
  - 通年エネルギー消費効率 (APF)
  - −
* - $L_\mathrm{CST}$
  - $L_\mathrm{CST}$
  - 冷房期間総合空調負荷 (CSTL)
  - Wh
* - $C_\mathrm{CSE}$
  - $C_\mathrm{CSE}$
  - 冷房期間消費電力量 (CSEC)
  - Wh
* - $L_\mathrm{HST}$
  - $L_\mathrm{HST}$
  - 暖房期間総合空調負荷 (HSTL)
  - Wh
* - $C_\mathrm{HSE}$
  - $C_\mathrm{HSE}$
  - 暖房期間消費電力量 (HSEC)
  - Wh
* - $\Phi_{\mathrm{c,ful},t100}$
  - $\Phi_{\mathrm{ful},t100}$
  - 定格冷房能力 (表示値)。暖房の想定空調負荷にも用いる
  - W
* - $t$
  - $t_j$
  - 外気温度 (能力・消費電力の特性や想定空調負荷の変数)
  - ℃
* - $t_j$
  - $t_j$
  - 温度区分 $j$ の外気温度
  - ℃
```

## 冷房期間

```{list-table} 冷房期間の記号
:name: tbl-sym-cooling
:header-rows: 1
:widths: 22 26 42 10

* - 本書の記号
  - 附属書 B の記号
  - 意味
  - 単位
* - $F_\mathrm{CSP}$
  - $F_\mathrm{CSP}$
  - 冷房期間エネルギー消費効率 (CSPF)
  - −
* - $Q_\mathrm{c}(t_j)$
  - なし (式 (B.5) の各項)
  - 温度区分 $j$ において処理する空調負荷
  - W
* - $P_\mathrm{c}(t_j)$
  - なし (式 (B.11) の各項)
  - 温度区分 $j$ における消費電力
  - W
* - $n_{\mathrm{c},j}$
  - $n_j$
  - 温度区分 $j$ の発生時間
  - h
* - $L_\mathrm{c}(t)$
  - $L_\mathrm{c}(t_j)$
  - 想定冷房空調負荷
  - W
* - $t_{\mathrm{c},0}$
  - $t_0$
  - 想定冷房空調負荷が 0 となる外気温度 (23 ℃)
  - ℃
* - $t_{\mathrm{c},100}$
  - $t_{100}$
  - 想定冷房空調負荷が定格冷房能力となる外気温度 (35 ℃)
  - ℃
* - $\Phi_\mathrm{c,ful}(t)$
  - $\Phi_\mathrm{ful}(t_j)$
  - 定格運転能力
  - W
* - $\Phi_\mathrm{c,haf}(t)$
  - $\Phi_\mathrm{haf}(t_j)$
  - 中間運転能力
  - W
* - $P_\mathrm{c,ful}(t)$
  - $P_\mathrm{ful}(t_j)$
  - 定格運転消費電力
  - W
* - $P_\mathrm{c,haf}(t)$
  - $P_\mathrm{haf}(t_j)$
  - 中間運転消費電力
  - W
* - $X_\mathrm{c}(t_j)$
  - $X(t_j)$
  - 運転率
  - −
* - $F_\mathrm{c,PL}(t_j)$
  - $F_\mathrm{PL}(t_j)$
  - 部分負荷率
  - −
* - $C_\mathrm{c,D}$
  - $C_\mathrm{D}$
  - 効率低下係数
  - −
* - $P_\mathrm{c,hf}(t_j)$
  - $P_\mathrm{hf}(t_j)$
  - 中間運転能力と定格運転能力の間で可変運転したときの消費電力
  - W
* - $\mathrm{EER}_\mathrm{hf}(t_j)$
  - $E_\mathrm{ER,hf}(t_j)$
  - 可変運転したときのエネルギー消費効率
  - −
* - $\mathrm{EER}_\mathrm{haf}(t_\mathrm{c})$
  - $E_\mathrm{ER,haf}(t_\mathrm{c})$
  - 交点温度 $t_\mathrm{c}$ における中間運転のエネルギー消費効率
  - −
* - $\mathrm{EER}_\mathrm{ful}(t_\mathrm{b})$
  - $E_\mathrm{ER,ful}(t_\mathrm{b})$
  - 交点温度 $t_\mathrm{b}$ における定格運転のエネルギー消費効率
  - −
* - $t_\mathrm{b}$
  - $t_\mathrm{b}$
  - 想定冷房空調負荷と定格運転能力が等しくなる外気温度
  - ℃
* - $t_\mathrm{c}$
  - $t_\mathrm{c}$
  - 想定冷房空調負荷と中間運転能力が等しくなる外気温度
  - ℃
```

## 暖房期間

```{list-table} 暖房期間の記号
:name: tbl-sym-heating
:header-rows: 1
:widths: 22 26 42 10

* - 本書の記号
  - 附属書 B の記号
  - 意味
  - 単位
* - $F_\mathrm{HSP}$
  - $F_\mathrm{HSP}$
  - 暖房期間エネルギー消費効率 (HSPF)
  - −
* - $Q_\mathrm{h}(t_j)$
  - なし (式 (B.33) の $L_\mathrm{h}(t_j)$)
  - 温度区分 $j$ において処理する空調負荷
  - W
* - $P_\mathrm{h}(t_j)$
  - なし (式 (B.46) の各項)
  - 温度区分 $j$ における消費電力。補助電熱装置を含む
  - W
* - $n_{\mathrm{h},j}$
  - $n_j$
  - 温度区分 $j$ の発生時間
  - h
* - $L_\mathrm{h}(t)$
  - $L_\mathrm{h}(t_j)$
  - 想定暖房空調負荷
  - W
* - $t_{\mathrm{h},0}$
  - $t_0$
  - 想定暖房空調負荷が 0 となる外気温度 (17 ℃)
  - ℃
* - $t_{\mathrm{h},100}$
  - $t_{100}$
  - 想定暖房空調負荷が定格冷房能力の 0.82 × 1.25 倍となる外気温度 (0 ℃)
  - ℃
* - $\Phi_\mathrm{h,ful}(t)$
  - $\Phi_\mathrm{ful}(t_j)$
  - 無着霜時の定格運転能力
  - W
* - $\Phi_\mathrm{h,ful,f}(t)$
  - $\Phi_\mathrm{ful,f}(t_j)$
  - 着霜時の定格運転能力
  - W
* - $\Phi_\mathrm{h,haf}(t)$
  - $\Phi_\mathrm{haf}(t_j)$
  - 無着霜時の中間運転能力
  - W
* - $\Phi_\mathrm{h,haf,f}(t)$
  - $\Phi_\mathrm{haf,f}(t_j)$
  - 着霜時の中間運転能力
  - W
* - $\Phi_\mathrm{h,ext}(t)$
  - $\Phi_\mathrm{ext}(t_j)$
  - 無着霜時の最大運転能力
  - W
* - $\Phi_\mathrm{h,ext,f}(t)$
  - $\Phi_\mathrm{ext,f}(t_j)$
  - 着霜時の最大運転能力
  - W
* - $P_\mathrm{h,ful}(t)$
  - $P_\mathrm{ful}(t_j)$
  - 無着霜時の定格運転消費電力
  - W
* - $P_\mathrm{h,ful,f}(t)$
  - $P_\mathrm{ful,f}(t_j)$
  - 着霜時の定格運転消費電力
  - W
* - $P_\mathrm{h,haf}(t)$
  - $P_\mathrm{haf}(t_j)$
  - 無着霜時の中間運転消費電力
  - W
* - $P_\mathrm{h,haf,f}(t)$
  - $P_\mathrm{haf,f}(t_j)$
  - 着霜時の中間運転消費電力
  - W
* - $P_\mathrm{h,ext}(t)$
  - $P_\mathrm{ext}(t_j)$
  - 無着霜時の最大運転消費電力
  - W
* - $P_\mathrm{h,ext,f}(t)$
  - $P_\mathrm{ext,f}(t_j)$
  - 着霜時の最大運転消費電力
  - W
* - $X_\mathrm{h}(t_j)$
  - $X(t_j)$
  - 無着霜時の運転率
  - −
* - $X_\mathrm{h,f}(t_j)$
  - $X(t_j)$
  - 着霜時の運転率
  - −
* - $F_\mathrm{h,PL}(t_j)$
  - $F_\mathrm{PL}(t_j)$
  - 無着霜時の部分負荷率
  - −
* - $F_\mathrm{h,PL,f}(t_j)$
  - $F_\mathrm{PL}(t_j)$
  - 着霜時の部分負荷率
  - −
* - $C_\mathrm{h,D}$
  - $C_\mathrm{D}$
  - 効率低下係数
  - −
* - $P_\mathrm{h,hf}(t_j)$
  - $P_\mathrm{hf}(t_j)$
  - 無着霜時に中間運転能力と定格運転能力の間で可変運転したときの消費電力
  - W
* - $P_\mathrm{h,hf,f}(t_j)$
  - $P_\mathrm{hf}(t_j)$
  - 着霜時に中間運転能力と定格運転能力の間で可変運転したときの消費電力
  - W
* - $P_\mathrm{h,fe}(t_j)$
  - $P_\mathrm{fe}(t_j)$
  - 無着霜時に定格運転能力と最大運転能力の間で可変運転したときの消費電力
  - W
* - $P_\mathrm{h,fe,f}(t_j)$
  - $P_\mathrm{fe}(t_j)$
  - 着霜時に定格運転能力と最大運転能力の間で可変運転したときの消費電力
  - W
* - $P_\mathrm{h,RH}(t_j)$
  - $P_\mathrm{RH}(t_j)$
  - 無着霜時の補助電熱装置の消費電力
  - W
* - $P_\mathrm{h,RH,f}(t_j)$
  - $P_\mathrm{RH}(t_j)$
  - 着霜時の補助電熱装置の消費電力
  - W
* - $\mathrm{COP}_\mathrm{hf}(t_j)$
  - $C_\mathrm{OP,hf}(t_j)$
  - 無着霜時に中間運転能力と定格運転能力の間で可変運転したときのエネルギー消費効率
  - −
* - $\mathrm{COP}_\mathrm{hf,f}(t_j)$
  - $C_\mathrm{OP,hf,f}(t_j)$
  - 着霜時に中間運転能力と定格運転能力の間で可変運転したときのエネルギー消費効率
  - −
* - $\mathrm{COP}_\mathrm{fe}(t_j)$
  - $C_\mathrm{OP,fe}(t_j)$
  - 無着霜時に定格運転能力と最大運転能力の間で可変運転したときのエネルギー消費効率
  - −
* - $\mathrm{COP}_\mathrm{fe,f}(t_j)$
  - $C_\mathrm{OP,fe,f}(t_j)$
  - 着霜時に定格運転能力と最大運転能力の間で可変運転したときのエネルギー消費効率
  - −
* - $\mathrm{COP}_\mathrm{ful}(t_\mathrm{a})$
  - $C_\mathrm{OP,ful}(t_\mathrm{a})$
  - 交点温度 $t_\mathrm{a}$ における無着霜時の定格運転のエネルギー消費効率
  - −
* - $\mathrm{COP}_\mathrm{haf}(t_\mathrm{d})$
  - $C_\mathrm{OP,haf}(t_\mathrm{d})$
  - 交点温度 $t_\mathrm{d}$ における無着霜時の中間運転のエネルギー消費効率
  - −
* - $\mathrm{COP}_\mathrm{ext}(t_\mathrm{h})$
  - $C_\mathrm{OP,ext}(t_\mathrm{h})$
  - 交点温度 $t_\mathrm{h}$ における無着霜時の最大運転のエネルギー消費効率
  - −
* - $\mathrm{COP}_\mathrm{ful,f}(t_\mathrm{g})$
  - $C_\mathrm{OP,ful,f}(t_\mathrm{g})$
  - 交点温度 $t_\mathrm{g}$ における着霜時の定格運転のエネルギー消費効率
  - −
* - $\mathrm{COP}_\mathrm{haf,f}(t_\mathrm{e})$
  - $C_\mathrm{OP,haf,f}(t_\mathrm{e})$
  - 交点温度 $t_\mathrm{e}$ における着霜時の中間運転のエネルギー消費効率
  - −
* - $\mathrm{COP}_\mathrm{ext,f}(t_\mathrm{f})$
  - $C_\mathrm{OP,ext,f}(t_\mathrm{f})$
  - 交点温度 $t_\mathrm{f}$ における着霜時の最大運転のエネルギー消費効率
  - −
* - $t_\mathrm{a}$
  - $t_\mathrm{a}$
  - 想定暖房空調負荷と無着霜時の定格運転能力が等しくなる外気温度
  - ℃
* - $t_\mathrm{d}$
  - $t_\mathrm{d}$
  - 想定暖房空調負荷と無着霜時の中間運転能力が等しくなる外気温度
  - ℃
* - $t_\mathrm{h}$
  - $t_\mathrm{h}$
  - 想定暖房空調負荷と無着霜時の最大運転能力が等しくなる外気温度
  - ℃
* - $t_\mathrm{g}$
  - $t_\mathrm{g}$
  - 想定暖房空調負荷と着霜時の定格運転能力が等しくなる外気温度
  - ℃
* - $t_\mathrm{e}$
  - $t_\mathrm{e}$
  - 想定暖房空調負荷と着霜時の中間運転能力が等しくなる外気温度
  - ℃
* - $t_\mathrm{f}$
  - $t_\mathrm{f}$
  - 想定暖房空調負荷と着霜時の最大運転能力が等しくなる外気温度
  - ℃
```

"""ドキュメント用の図を作成する。

使い方(リポジトリのルートで):
    conda run -n JIS_C9612 python docs/figures/make_figures.py

出力した SVG はリポジトリに含める(ドキュメントのビルド時には matplotlib は不要)。
図中の数値は説明用の例であり、特定の機種の値ではない。
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent

# 配色(dataviz 基準パレットのカテゴリ色 1〜3 番)と文字色
C_LOAD = "#2a78d6"  # 想定冷房空調負荷
C_FUL = "#eb6834"  # 定格運転能力
C_HAF = "#1baf7a"  # 中間運転能力
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#d9d8d4"

plt.rcParams.update(
    {
        "font.family": ["Hiragino Sans", "Hiragino Kaku Gothic ProN", "Noto Sans CJK JP", "sans-serif"],
        "font.size": 10,
        "svg.fonttype": "none",  # 文字は SVG のテキストとして出力し、ブラウザのフォントで表示する
        "svg.hashsalt": "jis-c9612",  # 内部 ID を固定し、作り直しても差分が出ないようにする
        "axes.edgecolor": INK_2,
        "axes.labelcolor": INK,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
    }
)

# --- 説明用の例の値(3 章の式と同じ計算) ---
PHI_T100 = 2800.0  # 定格冷房能力 (表示値) (W)
PHI_FUL_35 = 2800.0  # 定格運転能力 35 ℃ (W)
PHI_HAF_35 = 1400.0  # 中間運転能力 35 ℃ (W)
T0, T100 = 23.0, 35.0


def phi29(phi35: float) -> float:
    return 1.077 * phi35


def cap(phi35: float, t: float) -> float:
    return phi35 + (phi29(phi35) - phi35) / (29 - 35) * (t - 35)


def load(t: float) -> float:
    return PHI_T100 * (t - T0) / (T100 - T0)


def t_cross(phi35: float) -> float:
    d = (phi29(phi35) - phi35) * (T100 - T0)
    return (6 * PHI_T100 * T0 + 6 * phi35 * (T100 - T0) + 35 * d) / (6 * PHI_T100 + d)


def cooling_regions() -> None:
    tb = t_cross(PHI_FUL_35)
    tc = t_cross(PHI_HAF_35)
    x0, x1 = 22.0, 38.0
    xs = [x0, x1]

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    fig.patch.set_facecolor("white")

    # 運転状態の範囲(背景の帯)
    ax.axvspan(tc, tb, color="#f0efec", zorder=0)

    # 線
    ax.plot([T0, x1], [load(T0), load(x1)], color=C_LOAD, lw=2, label="想定冷房空調負荷 $L_\\mathrm{c}(t)$")
    ax.plot(xs, [cap(PHI_FUL_35, x) for x in xs], color=C_FUL, lw=2, label="定格運転能力 $\\Phi_\\mathrm{c,ful}(t)$")
    ax.plot(xs, [cap(PHI_HAF_35, x) for x in xs], color=C_HAF, lw=2, label="中間運転能力 $\\Phi_\\mathrm{c,haf}(t)$")

    # 交点
    for t, phi35 in ((tc, PHI_HAF_35), (tb, PHI_FUL_35)):
        y = cap(phi35, t)
        ax.plot([t, t], [0, y], color=INK_2, lw=1, ls=(0, (3, 3)), zorder=1)
        ax.plot(t, y, "o", ms=8, mfc="white", mec=INK, mew=1.5, zorder=4)
    ax.annotate("$t_\\mathrm{c}$", (tc, 0), xytext=(0, -18), textcoords="offset points",
                ha="center", va="top", color=INK, fontsize=11, annotation_clip=False)
    ax.annotate("$t_\\mathrm{b}$", (tb, 0), xytext=(0, -18), textcoords="offset points",
                ha="center", va="top", color=INK, fontsize=11, annotation_clip=False)

    # 運転状態の名前
    ytop = 3550
    for xa, xb, text in ((x0, tc, "断続運転"), (tc, tb, "可変運転"), (tb, x1, "定格運転")):
        ax.text((xa + xb) / 2, ytop, text, ha="center", va="center", color=INK, fontsize=10.5)

    # 線の名前(直接ラベル)
    ax.text(25.3, load(25.3) - 120, "想定冷房空調負荷", color=INK, ha="left", va="top", fontsize=9.5)
    ax.text(23.0, cap(PHI_FUL_35, 23.0) + 80, "定格運転能力", color=INK, ha="left", va="bottom", fontsize=9.5)
    ax.text(36.6, cap(PHI_HAF_35, 36.6) + 80, "中間運転能力", color=INK, ha="center", va="bottom", fontsize=9.5)

    ax.set_xlim(x0, x1)
    ax.set_ylim(0, 3800)
    ax.set_xticks(range(22, 39, 2))
    ax.set_xlabel("外気温度 $t$ (℃)", labelpad=14)
    ax.set_ylabel("負荷・能力 (W)")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    leg = ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.76), frameon=False, fontsize=9, handlelength=1.6)
    for t in leg.get_texts():
        t.set_color(INK)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "cooling_regions.svg", metadata={"Date": None})
    plt.close(fig)
    print(f"tc = {tc:.2f} ℃, tb = {tb:.2f} ℃")


# --- 消費電力の例の値 ---
P_FUL_35 = 700.0  # 定格運転消費電力 35 ℃ (W)
P_HAF_35 = 280.0  # 中間運転消費電力 35 ℃ (W)
C_D = 0.25


def pow_(p35: float, t: float) -> float:
    return p35 + (0.914 * p35 - p35) / (29 - 35) * (t - 35)


def power(t: float) -> tuple[float, str]:
    """外気温度 t での消費電力と運転状態(3 章の式と同じ計算)。"""
    lc = load(t)
    tb, tc = t_cross(PHI_FUL_35), t_cross(PHI_HAF_35)
    if lc <= cap(PHI_HAF_35, t):
        x = lc / cap(PHI_HAF_35, t)
        f_pl = 1 - C_D * (1 - x)
        return x * pow_(P_HAF_35, t) / f_pl, "断続運転"
    if lc <= cap(PHI_FUL_35, t):
        e_haf = cap(PHI_HAF_35, tc) / pow_(P_HAF_35, tc)
        e_ful = cap(PHI_FUL_35, tb) / pow_(P_FUL_35, tb)
        e_hf = e_haf + (e_ful - e_haf) / (tb - tc) * (t - tc)
        return lc / e_hf, "可変運転"
    return pow_(P_FUL_35, t), "定格運転"


def cooling_power() -> None:
    tb, tc = t_cross(PHI_FUL_35), t_cross(PHI_HAF_35)
    x0, x1 = 22.0, 38.0
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    fig.patch.set_facecolor("white")
    ax.axvspan(tc, tb, color="#f0efec", zorder=0)

    # 参考: 定格運転・中間運転の消費電力特性(細い破線)
    xs = [x0, x1]
    ax.plot(xs, [pow_(P_FUL_35, x) for x in xs], color=C_FUL, lw=1.2, ls=(0, (4, 3)),
            label="定格運転消費電力 $P_\\mathrm{c,ful}(t)$")
    ax.plot(xs, [pow_(P_HAF_35, x) for x in xs], color=C_HAF, lw=1.2, ls=(0, (4, 3)),
            label="中間運転消費電力 $P_\\mathrm{c,haf}(t)$")

    # 消費電力 P(t)(太線)と温度区分ごとの値(点)
    n = 400
    ts = [T0 + (x1 - T0) * i / n for i in range(n + 1)]
    ax.plot(ts, [power(t)[0] for t in ts], color=INK, lw=2, label="消費電力 $P_\\mathrm{c}(t_j)$", zorder=3)
    tj = list(range(24, 39))
    ax.plot(tj, [power(t)[0] for t in tj], "o", ms=5, mfc="white", mec=INK, mew=1.2, zorder=4,
            label="温度区分 $t_j$ ごとの値")

    for t in (tc, tb):
        ax.axvline(t, color=INK_2, lw=1, ls=(0, (3, 3)), zorder=1)
    ax.annotate("$t_\\mathrm{c}$", (tc, 0), xytext=(0, -18), textcoords="offset points",
                ha="center", va="top", color=INK, fontsize=11, annotation_clip=False)
    ax.annotate("$t_\\mathrm{b}$", (tb, 0), xytext=(0, -18), textcoords="offset points",
                ha="center", va="top", color=INK, fontsize=11, annotation_clip=False)

    ytop = 960
    for xa, xb, text in ((x0, tc, "断続運転"), (tc, tb, "可変運転"), (tb, x1, "定格運転")):
        ax.text((xa + xb) / 2, ytop, text, ha="center", va="center", color=INK, fontsize=10.5)
    ax.text(25.5, 330, "中間運転能力で\n運転・停止を繰り返す", color=INK_2,
            ha="center", va="bottom", fontsize=8.5)
    ax.text(32.2, power(32.2)[0] - 40, "能力を連続的に\n変えて運転する", color=INK_2,
            ha="left", va="top", fontsize=8.5)

    ax.set_xlim(x0, x1)
    ax.set_ylim(0, 1020)
    ax.set_xticks(range(22, 39, 2))
    ax.set_xlabel("外気温度 $t$ (℃)", labelpad=14)
    ax.set_ylabel("消費電力 (W)")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    leg = ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.90), frameon=False, fontsize=9, handlelength=2.2)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "cooling_power.svg", metadata={"Date": None})
    plt.close(fig)
    for t in tj:
        v, st = power(t)
        print(f"{t:>3} ℃  {st}  P = {v:7.1f} W")


# ======================================================================
# 暖房
# ======================================================================
C_EXT = "#eda100"  # 最大運転能力(基準パレットのカテゴリ色 4 番)

H_T0, H_T100 = 17.0, 0.0
H_K = 0.82 * 1.25 * PHI_T100  # 外気 0 ℃における想定暖房空調負荷 (W)
# 試験値の例 (W)
H_PHI_FUL_7, H_P_FUL_7 = 3600.0, 900.0
H_PHI_HAF_7, H_P_HAF_7 = 1800.0, 360.0
H_PHI_EXTF_2, H_P_EXTF_2 = 4200.0, 1500.0


def _h_lines():
    """3 章の暖房の式と同じ計算で、能力・消費電力の特性線と交点温度を求める。"""
    ful_m7, pful_m7 = 0.64 * H_PHI_FUL_7, 0.82 * H_P_FUL_7
    haf_m7, phaf_m7 = 0.64 * H_PHI_HAF_7, 0.82 * H_P_HAF_7
    ext_2, pext_2 = 1.12 * H_PHI_EXTF_2, 1.06 * H_P_EXTF_2
    ext_m7, pext_m7 = 0.734 * ext_2, 0.877 * pext_2

    def at2(m7, v7):
        return m7 + (v7 - m7) / 14 * 9

    fulf_2, pfulf_2 = at2(ful_m7, H_PHI_FUL_7) / 1.12, at2(pful_m7, H_P_FUL_7) / 1.06
    haff_2, phaff_2 = at2(haf_m7, H_PHI_HAF_7) / 1.12, at2(phaf_m7, H_P_HAF_7) / 1.06

    def line(m7, v, tt):
        return lambda t: m7 + (v - m7) / (tt + 7) * (t + 7)

    def cross(m7, v, tt):
        return (H_K * H_T0 * (tt + 7) - (tt * m7 + 7 * v) * (H_T0 - H_T100)) / (
            H_K * (tt + 7) + (v - m7) * (H_T0 - H_T100))

    nf = {
        "ful": (line(ful_m7, H_PHI_FUL_7, 7), line(pful_m7, H_P_FUL_7, 7), cross(ful_m7, H_PHI_FUL_7, 7)),
        "haf": (line(haf_m7, H_PHI_HAF_7, 7), line(phaf_m7, H_P_HAF_7, 7), cross(haf_m7, H_PHI_HAF_7, 7)),
        "ext": (line(ext_m7, ext_2, 2), line(pext_m7, pext_2, 2), cross(ext_m7, ext_2, 2)),
    }
    fr = {
        "ful": (line(ful_m7, fulf_2, 2), line(pful_m7, pfulf_2, 2), cross(ful_m7, fulf_2, 2)),
        "haf": (line(haf_m7, haff_2, 2), line(phaf_m7, phaff_2, 2), cross(haf_m7, haff_2, 2)),
        "ext": (line(ext_m7, H_PHI_EXTF_2, 2), line(pext_m7, H_P_EXTF_2, 2), cross(ext_m7, H_PHI_EXTF_2, 2)),
    }
    return nf, fr


def h_load(t: float) -> float:
    return H_K * (H_T0 - t) / (H_T0 - H_T100)


def h_frost(t: float) -> bool:
    return -7 < t < 5.5


def h_power(t: float) -> tuple[float, float, str]:
    """外気温度 t での消費電力、うち補助電熱装置の消費電力、運転状態。"""
    nf, fr = _h_lines()
    d = fr if h_frost(t) else nf
    lh = h_load(t)

    def cop_at(k):
        phi, pw, tx = d[k]
        return phi(tx) / pw(tx), tx

    if lh <= d["haf"][0](t):
        x = lh / d["haf"][0](t)
        return x * d["haf"][1](t) / (1 - C_D * (1 - x)), 0.0, "断続運転"
    if lh <= d["ful"][0](t):
        (c_ful, ta), (c_haf, td) = cop_at("ful"), cop_at("haf")
        return lh / (c_ful + (c_haf - c_ful) / (td - ta) * (t - ta)), 0.0, "中間〜定格の可変運転"
    if lh <= d["ext"][0](t):
        (c_ext, th), (c_ful, ta) = cop_at("ext"), cop_at("ful")
        return lh / (c_ext + (c_ful - c_ext) / (ta - th) * (t - th)), 0.0, "定格〜最大の可変運転"
    rh = lh - d["ext"][0](t)
    return d["ext"][1](t) + rh, rh, "最大運転"


def heating_regions() -> None:
    nf, fr = _h_lines()
    x0, x1 = -8.0, 17.0
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    fig.patch.set_facecolor("white")
    ax.axvspan(-7, 5.5, color="#f0efec", zorder=0)

    ax.plot([x0, H_T0], [h_load(x0), h_load(H_T0)], color=C_LOAD, lw=2, label="想定暖房空調負荷 $L_\\mathrm{h}(t)$", zorder=3)
    names = {"ext": ("最大運転能力", C_EXT), "ful": ("定格運転能力", C_FUL), "haf": ("中間運転能力", C_HAF)}
    n = 200
    for k, (name, col) in names.items():
        # 無着霜時の特性(着霜領域の中は参考として細い破線)
        a = [x0 + (-7 - x0) * i / n for i in range(n + 1)]
        b = [5.5 + (x1 - 5.5) * i / n for i in range(n + 1)]
        m = [-7 + 12.5 * i / n for i in range(n + 1)]
        ax.plot(a, [nf[k][0](t) for t in a], color=col, lw=2, zorder=2, label=name)
        ax.plot(b, [nf[k][0](t) for t in b], color=col, lw=2, zorder=2)
        ax.plot(m, [nf[k][0](t) for t in m], color=col, lw=1, ls=(0, (3, 3)), zorder=1)
        # 着霜時の特性
        ax.plot(m, [fr[k][0](t) for t in m], color=col, lw=2, zorder=2)

    ax.text(-0.75, 6150, "着霜領域", ha="center", va="center", color=INK, fontsize=10.5)
    ax.text(11.25, 6150, "無着霜領域", ha="center", va="center", color=INK, fontsize=10.5)
    ax.text(-7.5, 6150, "無着霜", ha="center", va="center", color=INK_2, fontsize=8.5)
    ax.text(6.2, 3830, "破線: 着霜領域での\n無着霜時の特性 (参考)", ha="left", va="center", color=INK_2, fontsize=8.5)

    ax.set_xlim(x0, x1)
    ax.set_ylim(0, 6500)
    ax.set_xticks(range(-8, 18, 2))
    ax.set_xlabel("外気温度 $t$ (℃)")
    ax.set_ylabel("負荷・能力 (W)")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    leg = ax.legend(loc="upper right", bbox_to_anchor=(1.0, 0.90), frameon=False, fontsize=9, handlelength=1.6)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "heating_regions.svg", metadata={"Date": None})
    plt.close(fig)
    _, _ = nf, fr
    print("暖房の交点温度: " + ", ".join(
        f"{a}{'(着霜)' if d is fr else ''} {d[a][2]:.2f} ℃" for d in (nf, fr) for a in ("haf", "ful", "ext")))


def heating_power() -> None:
    tj = list(range(-7, 17))
    vals = [h_power(t) for t in tj]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    fig.patch.set_facecolor("white")
    ax.axvspan(-7, 5.5, color="#f0efec", zorder=0)

    # 運転状態ごとの範囲(温度区分の境界は隣の区分との中点)
    spans, start = [], 0
    for i in range(1, len(tj) + 1):
        if i == len(tj) or vals[i][2] != vals[start][2]:
            spans.append((tj[start] - 0.5, tj[i - 1] + 0.5, vals[start][2]))
            start = i
    for k, (a, b, st) in enumerate(spans):
        if k > 0:
            ax.axvline(a, color=INK_2, lw=1, ls=(0, (3, 3)), zorder=1)
    labels = {"断続運転": "断続運転", "中間〜定格の可変運転": "中間〜定格\nの可変運転",
              "定格〜最大の可変運転": "定格〜最大\nの可変運転", "最大運転": "最大運転\n+補助電熱"}
    for a, b, st in spans:
        ax.text((a + b) / 2, 2350, labels[st], ha="center", va="center", color=INK, fontsize=9.5)

    ax.plot(tj, [v[0] for v in vals], color=INK, lw=2, zorder=3, marker="o", ms=5, mfc="white", mec=INK, mew=1.2,
            label="消費電力 $P_\\mathrm{h}(t_j)$ (補助電熱装置を含む)")
    ax.bar(tj, [v[1] for v in vals], width=0.6, color=C_LOAD, alpha=0.35, zorder=2,
           label="うち補助電熱装置 $P_\\mathrm{h,RH}(t_j)$、$P_\\mathrm{h,RH,f}(t_j)$")
    ax.text(-0.75, 50, "着霜領域", ha="center", va="bottom", color=INK_2, fontsize=9)

    ax.set_xlim(-8, 17)
    ax.set_ylim(0, 2600)
    ax.set_xticks(range(-8, 18, 2))
    ax.set_xlabel("外気温度 $t$ (℃)")
    ax.set_ylabel("消費電力 (W)")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    leg = ax.legend(loc="upper right", bbox_to_anchor=(1.0, 0.86), frameon=False, fontsize=9, handlelength=1.8)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "heating_power.svg", metadata={"Date": None})
    plt.close(fig)


def _style(ax) -> None:
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def cooling_plf() -> None:
    """式 (部分負荷率) の図: 運転率と部分負荷率の関係。"""
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    fig.patch.set_facecolor("white")
    ax.plot([0, 1], [1 - C_D, 1], color=C_LOAD, lw=2, zorder=3)
    ax.axhline(1.0, color=INK_2, lw=1, ls=(0, (3, 3)), zorder=1)
    ax.text(0.02, 1.006, "効率の低下がない場合 ($F_\\mathrm{c,PL} = 1$)", color=INK_2, fontsize=9, va="bottom")

    # 例: 外気 26 ℃
    t = 26.0
    x = load(t) / cap(PHI_HAF_35, t)
    f = 1 - C_D * (1 - x)
    ax.plot([x, x], [0.7, f], color=INK_2, lw=1, ls=(0, (3, 3)), zorder=1)
    ax.plot([0, x], [f, f], color=INK_2, lw=1, ls=(0, (3, 3)), zorder=1)
    ax.plot(x, f, "o", ms=8, mfc="white", mec=INK, mew=1.5, zorder=4)
    ax.annotate(f"例: 外気 26 ℃\n$X_\\mathrm{{c}}$ = {x:.3f}、$F_\\mathrm{{c,PL}}$ = {f:.3f}", (x, f), xytext=(14, -34),
                textcoords="offset points", color=INK, fontsize=9)
    ax.annotate("停止時間が長いほど\n効率が下がる", (0.08, 1 - C_D * 0.92), xytext=(18, 34),
                textcoords="offset points", color=INK_2, fontsize=9,
                arrowprops={"arrowstyle": "-", "color": INK_2, "lw": 0.8})
    ax.text(0.0, 1 - C_D - 0.012, f"$1 - C_\\mathrm{{c,D}}$ = {1 - C_D:.2f}", color=INK, fontsize=9, ha="left", va="top")

    ax.set_xlim(0, 1.0)
    ax.set_ylim(0.7, 1.04)
    ax.set_xlabel("運転率 $X_\\mathrm{c}(t_j)$")
    ax.set_ylabel("部分負荷率 $F_\\mathrm{c,PL}(t_j)$")
    _style(ax)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "cooling_plf.svg", metadata={"Date": None})
    plt.close(fig)


def cooling_eer() -> None:
    """式 (可変運転の EER) の図: 交点温度の間の直線補間。"""
    tb, tc = t_cross(PHI_FUL_35), t_cross(PHI_HAF_35)
    e_haf = cap(PHI_HAF_35, tc) / pow_(P_HAF_35, tc)
    e_ful = cap(PHI_FUL_35, tb) / pow_(P_FUL_35, tb)

    def e_hf(t):
        return e_haf + (e_ful - e_haf) / (tb - tc) * (t - tc)

    x0, x1 = 26.0, 37.0
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    fig.patch.set_facecolor("white")
    ax.axvspan(tc, tb, color="#f0efec", zorder=0)

    # 参考: 中間運転・定格運転で連続運転したときの EER
    n = 100
    ts = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    ax.plot(ts, [cap(PHI_HAF_35, t) / pow_(P_HAF_35, t) for t in ts], color=C_HAF, lw=1.2, ls=(0, (4, 3)),
            label="中間運転の EER $\\Phi_\\mathrm{c,haf}(t) / P_\\mathrm{c,haf}(t)$")
    ax.plot(ts, [cap(PHI_FUL_35, t) / pow_(P_FUL_35, t) for t in ts], color=C_FUL, lw=1.2, ls=(0, (4, 3)),
            label="定格運転の EER $\\Phi_\\mathrm{c,ful}(t) / P_\\mathrm{c,ful}(t)$")
    # 補間線
    ax.plot([tc, tb], [e_haf, e_ful], color=INK, lw=2, zorder=3,
            label="可変運転の EER $E_\\mathrm{ER,hf}(t_j)$")
    tj = [t for t in range(30, 36)]
    ax.plot(tj, [e_hf(t) for t in tj], "o", ms=5, mfc="white", mec=INK, mew=1.2, zorder=4,
            label="温度区分 $t_j$ ごとの値")
    for t, e, name in ((tc, e_haf, "$E_\\mathrm{ER,haf}(t_\\mathrm{c})$"), (tb, e_ful, "$E_\\mathrm{ER,ful}(t_\\mathrm{b})$")):
        ax.plot(t, e, "o", ms=9, mfc=INK, mec=INK, zorder=5)
        ax.annotate(f"{name}\n= {e:.2f}", (t, e), xytext=(8, 6), textcoords="offset points", color=INK, fontsize=9)
        ax.plot([t, t], [3.45, 6.8], color=INK_2, lw=1, ls=(0, (3, 3)), zorder=1)
    ax.annotate("$t_\\mathrm{c}$", (tc, 0), xytext=(0, -18), textcoords="offset points", xycoords=("data", "axes fraction"),
                ha="center", va="top", color=INK, fontsize=11, annotation_clip=False)
    ax.annotate("$t_\\mathrm{b}$", (tb, 0), xytext=(0, -18), textcoords="offset points", xycoords=("data", "axes fraction"),
                ha="center", va="top", color=INK, fontsize=11, annotation_clip=False)
    ax.text((tc + tb) / 2, 6.55, "可変運転", ha="center", va="center", color=INK, fontsize=10.5)

    ax.set_xlim(x0, x1)
    ax.set_ylim(2.2, 6.8)
    ax.set_xticks(range(26, 38, 1))
    ax.set_xlabel("外気温度 $t$ (℃)", labelpad=14)
    ax.set_ylabel("エネルギー消費効率 EER (−)")
    _style(ax)
    leg = ax.legend(loc="lower center", ncol=2, frameon=False, fontsize=9, handlelength=2.2, columnspacing=1.5)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "cooling_eer.svg", metadata={"Date": None})
    plt.close(fig)
    print(f"EER: haf(tc) = {e_haf:.3f}, ful(tb) = {e_ful:.3f}")


if __name__ == "__main__":
    cooling_plf()
    cooling_eer()
    cooling_regions()
    cooling_power()
    heating_regions()
    heating_power()

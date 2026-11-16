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
    ax.plot(xs, [cap(PHI_FUL_35, x) for x in xs], color=C_FUL, lw=2, label="定格運転能力 $\\Phi_\\mathrm{ful}(t)$")
    ax.plot(xs, [cap(PHI_HAF_35, x) for x in xs], color=C_HAF, lw=2, label="中間運転能力 $\\Phi_\\mathrm{haf}(t)$")

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
    fig.savefig(OUT_DIR / "cooling_regions.svg")
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
            label="定格運転消費電力 $P_\\mathrm{ful}(t)$")
    ax.plot(xs, [pow_(P_HAF_35, x) for x in xs], color=C_HAF, lw=1.2, ls=(0, (4, 3)),
            label="中間運転消費電力 $P_\\mathrm{haf}(t)$")

    # 消費電力 P(t)(太線)と温度区分ごとの値(点)
    n = 400
    ts = [T0 + (x1 - T0) * i / n for i in range(n + 1)]
    ax.plot(ts, [power(t)[0] for t in ts], color=INK, lw=2, label="消費電力 $P(t_j)$", zorder=3)
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
    fig.savefig(OUT_DIR / "cooling_power.svg")
    plt.close(fig)
    for t in tj:
        v, st = power(t)
        print(f"{t:>3} ℃  {st}  P = {v:7.1f} W")


if __name__ == "__main__":
    cooling_regions()
    cooling_power()

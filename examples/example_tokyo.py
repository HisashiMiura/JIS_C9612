"""東京の外気温度発生時間で APF を計算する例。

使い方(リポジトリのルートで):
    conda run -n JIS_C9612 python examples/example_tokyo.py

入力値は説明用の例であり、特定の機種の値ではない (ドキュメント 3 章の図の例と同じ)。
"""

from jis_c9612 import CoolingInput, HeatingInput, compute_apf

cooling = CoolingInput(phi_c_ful_t100=2800, phi_c_ful_35=2800, p_c_ful_35=700, phi_c_haf_35=1400, p_c_haf_35=280)
heating = HeatingInput(
    phi_c_ful_t100=2800, phi_h_ful_7=3600, p_h_ful_7=900, phi_h_haf_7=1800, p_h_haf_7=360,
    phi_h_ext_f_2=4200, p_h_ext_f_2=1500,  # 最大モードをもつ機種
)

r = compute_apf(cooling, heating)
c, h = r.cooling, r.heating

print("冷房期間")
print(f"  交点温度  t_c = {c.t_c:.2f} ℃, t_b = {c.t_b:.2f} ℃")
print(f"  CSTL = {c.l_cst / 1000:,.1f} kWh, CSEC = {c.c_cse / 1000:,.1f} kWh, CSPF = {c.f_csp:.3f}")
print("暖房期間")
print(f"  交点温度 (無着霜)  t_d = {h.nonfrost.t_haf:.2f} ℃, t_a = {h.nonfrost.t_ful:.2f} ℃, t_h = {h.nonfrost.t_ext:.2f} ℃")
print(f"  交点温度 (着霜)    t_e = {h.frost.t_haf:.2f} ℃, t_g = {h.frost.t_ful:.2f} ℃, t_f = {h.frost.t_ext:.2f} ℃")
print(f"  HSTL = {h.l_hst / 1000:,.1f} kWh, HSEC = {h.c_hse / 1000:,.1f} kWh, HSPF = {h.f_hsp:.3f}")
print(f"APF = {r.f_ap:.3f}  (期間消費電力量 {r.annual_energy / 1000:,.1f} kWh)")

print("\n暖房期間の温度区分ごとの値 (発生時間のある区分)")
print("  t_j  n_h,j  領域    運転状態              L_h (W)  P_h (W)")
for b in h.bins:
    if b.n_h_j:
        region = "着霜" if b.frost else "無着霜"
        print(f"  {b.t_j:>3.0f} {b.n_h_j:>4.0f}  {region:<5} {b.state.value:<14} {b.l_h:8.1f} {b.p_h:8.1f}")

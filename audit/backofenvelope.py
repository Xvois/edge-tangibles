"""Back-of-envelope checks for audit.md. Run: python3 -I audit/backofenvelope.py (numpy only).
Inputs are numbers quoted in this repository (file named next to each) or rate formulas read
from the public RAMSES-RT source (ramses-organisation/ramses, rt/coolrates_module.f90, rt/rt_init.f90,
rt/rt_spectra.f90) and from papers opened during the audit (named next to each)."""
import numpy as np

MSUN, PC, MH, KB, YR = 1.989e33, 3.0857e18, 1.6726e-24, 1.380649e-16, 3.156e7
MYR, GYR = 1e6 * YR, 1e9 * YR
X = 0.76  # run's X_fraction (writeups/why-...-c7ee.md section 7)

def sec(t): print(f"\n== {t}")

sec("1. H2 mass convention: notebooks/lvdb_scaling_relations.ipynb cell 52 vs write-up section 1")
nb, wu = 2.312, 4.63            # Msun inside R200c, output 125
print(f"write-up / notebook = {wu/nb:.3f}  (mass of H in H2 is 2*x_H2*M_H; notebook uses x_H2*M_H)")

sec("2. pynbody crude-mu fallback (pynbody/derived.py _mu_from_temperature_threshold, Y=0.245)")
Y = 0.245
mu_ion, mu_neu = 4 / (8 - 5 * Y), 4 / (4 - 3 * Y)
lo, hi = 1e4 / mu_neu, 1e4 / mu_ion
print(f"mu_ion {mu_ion:.4f}, mu_neutral {mu_neu:.4f}; ambiguous band in T/mu: {lo:.0f}-{hi:.0f} K")
def pyn_temp(t_over_mu, n=5):
    mu = 1.0
    for _ in range(n):
        T = t_over_mu * mu
        mu = mu_ion if T >= 1e4 else mu_neu
    return T
for tm in (8000, 8200, 9000, 9999, 10001, 12000, 16900, 17000):
    print(f"  T/mu={tm:6d} K -> pynbody temp {pyn_temp(tm):7.0f} K")
print(f"  floor of the artefact branch: {mu_ion*lo:.0f} K (compare 'min T 4,800 K at 125' in writeups/halo605_119_vs_125.md and pynbody min 4,820 K in c7ee section 6)")
mu_full_ion = 1 / (X * 2 + (1 - X) / 4 * 3)
print(f"  physical floor from min T/mu 7,690 K with fully ionised mu {mu_full_ion:.3f}: {7690*mu_full_ion:.0f} K")

sec("3. Photon groups (Rey et al. 2025 sec 2.2; RAMSES rt_spectra.f90 getCrosssection)")
s2, s3 = 6.635e-23, 2.100e-19
print(f"sigma_2/sigma_3 = {s2/s3:.3e}  (= photon fraction of group 2 in 11.2-12 eV, if sigma_H2 = 2.1e-19 flat over 11.2-13.6 eV)")
print(f"group 3 width / LW width = {(13.6-12)/(13.6-11.2):.3f} (energy); N18 effective boosted cross-section 400*sigma = {400*s3:.2e} cm^2")
# diffuse-gas share of group 2 in H2 destruction, from rt_fig3.png left panel (read by eye, centre and 3 kpc)
for lab, n2, n3 in (("r=0.05 kpc", 3e8, 4e5), ("r=3 kpc", 1.5e6, 7e2)):
    g2, g3 = s2 * n2, s3 * n3
    print(f"  {lab}: c_rN_2={n2:.1e}, c_rN_3={n3:.1e} -> unshielded share of group 2 = {g2/(g2+g3):.2f}")
D0 = 5.8e-11; chi = 1.4e8   # Sternberg+14 eq 5 (s^-1, I_UV=1); Nickerson+18 sec 3.2 Draine LW photon flux
print(f"  sigma implied by (D0/2)/F_LW = {D0/2/chi:.2e} cm^2 (code uses 2.1e-19)")

sec("4. Group-3 optical depth of one dense 119 cell with the x400 boost (inferred inputs)")
for n, xh2, dx in ((1, 1e-4, 11.3), (10, 1e-3, 11.3), (17, 1e-3, 11.3)):
    tau = 400 * s3 * n * xh2 * dx * PC
    print(f"  n_H={n:4} cm^-3, x_H2={xh2:.0e}, dx={dx} pc -> tau_3 = {tau:.2g}; tau_2 (no boost) = {tau*s2/s3/400:.2g}")

sec("5. Formation rates from the run's own tables (rt/coolrates_module.f90)")
def alphaZ(T):  # cm^3 s^-1, multiply by Z' f_dust
    T2 = T / 100; f = 1 + 0.4 * np.sqrt(T2) + 0.2 * T2 + 0.08 * T2**2
    return 9e-17 * np.sqrt(T2) / f
def alphaGP(T): return 1.83e-18 * T**0.88   # cm^3 s^-1, multiply by n_e (H- channel)
Tp = np.logspace(1, 4, 400); i = np.argmax(alphaZ(Tp))
print(f"  alpha_Z peaks at T={Tp[i]:.0f} K ({alphaZ(Tp[i]):.2e}); alpha_Z(100 K)={alphaZ(100):.2e}; ratio(6600 K/100 K)={alphaZ(6600)/alphaZ(100):.3f}")
for lab, n, Zp, T, xe in (("605 z=0 densest cell", 0.06, 0.12, 8500, 0.25),
                          ("605 out119 densest", 17, 0.1, 100, 1e-3),
                          ("605 out119 n=1", 1, 0.1, 300, 1e-3)):
    fd = 1 - xe
    rz = alphaZ(T) * Zp * fd * n
    rg = alphaGP(T) * xe * n
    print(f"  {lab}: dust {rz:.2e} s^-1, H- {rg:.2e} s^-1 -> t_form=1/(2A) dust-only {1/(2*rz)/MYR:.3g} Myr, all {1/(2*(rz+rg))/MYR:.3g} Myr")
    print(f"     2*A*100 Myr (fraction of H made molecular in 100 Myr, no destruction): dust {2*rz*100*MYR:.2e}, with H- {2*(rz+rg)*100*MYR:.2e}")
R = 3e-17 * 0.12 * 0.06
print(f"  write-up check (Sternberg R, 100 K, n=0.06, Z'=0.12): 1/(2Rn) = {1/(2*R)/GYR:.1f} Gyr; with sqrt(85): {1/(2*R*np.sqrt(85))/GYR:.1f} Gyr")
print(f"  Hu+16 eq 10, t_F = 1/(n1 D) Gyr: n=17,D=0.1 -> {1/(17*0.1):.2f} Gyr; n=1 -> {1/(1*0.1):.0f} Gyr")

sec("6. Thresholds and transitions")
print(f"  SF threshold rho* = 300 m_p cm^-3 (Rey+25 eq 1) -> n_H = {300*X:.0f} cm^-3")
for Zp in (0.04, 0.075, 0.1, 0.12):
    print(f"  Gnedin+09 eq 7 n_t = 30/Z' = {30/Zp:5.0f} cm^-3 at Z'={Zp}; Bolatto+13 eq 31 alpha_CO(S_GMC=100) = {2.9*np.exp(0.4/Zp):.3g} Msun/(K km/s pc^2)")
sig10 = 10 * MSUN / PC**2
print(f"  Sternberg+14: 10 Msun/pc^2 -> N_H = {sig10/MH:.2e} cm^-2 if all H; {sig10/1.36/MH:.2e} if 'gas' includes He (x1.36)")

sec("7. Refinement (Rey+25 sec 2.2: split when baryon mass > 8 m_bar, m_bar ~150 Msun)")
Mcrit = 8 * 150 * MSUN
for dx_parent in (90.4, 45.2, 22.6, 11.3, 5.65):
    n = Mcrit / (dx_parent * PC) ** 3 * X / MH
    print(f"  a {dx_parent:5.1f} pc cell splits to {dx_parent/2:5.2f} pc above n_H ~ {n:8.3g} cm^-3 (gas-only, ignoring stars/DM criterion)")

sec("8. Sample consistency (FINDINGS 1.5, writeups/halo605_119_vs_125.md)")
print(f"  H2/H inside R_e at 119: {1540/(X*9.1e5):.2e} (Hu+16 G1D01, Z=0.1: F_H2 ~ 5e-4)")
print(f"  H2 ratio 1535/1.6 = {1535/1.6:.0f}; gas 9.1e5/5.1e4 = {9.1e5/5.1e4:.1f}; HI 6.6e5/1.2e4 = {6.6e5/1.2e4:.0f}")
print(f"  mean SFR 33,900 Msun/732 Myr = {33900/732e6:.2e} Msun/yr; mass of new stars that is 113 x 300 Msun = {113*300}")
print(f"  M_V -9.9 vs -10.58: luminosity ratio {10**(0.4*(10.58-9.9)):.2f}")
print(f"  12+log(O/H)=7.71 -> Z'={10**(7.71-8.69):.3f}; 7.249 -> Z'={10**(7.249-8.69):.3f} (solar 8.69)")

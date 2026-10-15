"""Compare H2 self-shielding functions on 1D slabs at the EDGE2 stand-in's dense-gas conditions.

Pure numpy; loads no snapshot. Each slab is uniform (n_H, T, Z'), lit from one face by I_UV (Draine units,
half the sky: 0.5 D0, Sternberg et al. 2014 eq. 19), and marched inward with each layer in formation /
photodissociation equilibrium, y = A/(2A + gamma) (u = 1, grain formation only), exactly as the science
notebook's slab_profile().  Only f_shield changes between rows.

Reports, per model:
  f_cell  - mass-weighted molecular fraction (2y) through the first 2.6 pc of the slab (one finest cell)
  N_half  - total H column from the lit face to where 2y = 0.5 (cm^-2)
"""
import numpy as np

D0 = 5.8e-11                  # s^-1, S14 eq. 5
SIGMA_D = 1.0e-21             # cm^2 per H at Z'=1 (KMT09 p.5)
SIGMA_LW_RUN = 2.1e-19        # cm^2, run's group-3 H2 cross-section
PC = 3.0857e18
K_B, M_H2 = 1.380649e-16, 2 * 1.6735e-24
B_TURB_KMS = 2.0              # assumed non-thermal b; the notebook's single b is 2 km/s


def grain_rate(T):  # N18 prefactor x Hollenbach & McKee (1979), as in the notebook
    T2 = np.maximum(T, 1.0) / 100.0
    return 9.0e-17 * np.sqrt(T2) / (1.0 + 0.4 * np.sqrt(T2) + 0.2 * T2 + 0.08 * T2 ** 2)


def b_total(T, b_turb=B_TURB_KMS):
    b_th = np.sqrt(2 * K_B * T / M_H2) / 1e5
    return np.sqrt(b_th ** 2 + b_turb ** 2)


def db96(N, T, b=2.0):
    x = N / 5e14
    return 0.965 / (1 + x / b) ** 2 + 0.035 / np.sqrt(1 + x) * np.exp(-8.5e-4 * np.sqrt(1 + x))


def db96_bT(N, T):
    return db96(N, T, b_total(T))


def wg11(N, T):  # Wolcott-Green, Haiman & Bryan 2011 eq. 10, alpha = 1.1
    x = N / 5e14
    return 0.965 / (1 + x / b_total(T)) ** 1.1 + 0.035 / np.sqrt(1 + x) * np.exp(-8.5e-4 * np.sqrt(1 + x))


def r14(N, T):  # Richings, Schaye & Oppenheimer 2014 eqs. 3.12-3.17 (T < 3000 K branch + others)
    omega = 0.013 * (1 + (T / 2700.0) ** 1.3) ** (1 / 1.3) * np.exp(-(T / 3900.0) ** 14.6)
    alpha = np.where(T < 3000, 1.4, np.where(T < 4000, (T / 4500.0) ** -0.8, 1.1))
    ncrit = 1e14 * np.where(T < 3000, 1.3 * (1 + (T / 600.0) ** 0.8),
                            np.where(T < 4000, (T / 4760.0) ** -3.8, 2.0))
    x0 = N / ncrit
    b = b_total(T)
    return ((1 - omega) / (1 + x0 / b) ** alpha * np.exp(-5e-7 * (1 + x0))
            + omega / np.sqrt(1 + x0) * np.exp(-8.5e-4 * np.sqrt(1 + x0)))


def gk11_power(N, T):  # DB96 eq. 36 / GD14 eq. 4
    return np.minimum(1.0, (np.maximum(N, 1.0) / 1e14) ** -0.75)


def gd14_sonic(N, T, N_s):  # GD14 eq. 3 with sonic-scale column N_s
    x1 = np.sqrt(N * N_s) / 5e14
    x2 = N / 5e14
    return 0.965 / (1 + x1 / 2.0) ** 2 + 0.035 / np.sqrt(1 + x2) * np.exp(-np.sqrt(1 + x2) / 1180.0)


def n18_boost(N, T):  # Nickerson+18: absorption by H2 boosted x400, i.e. exp(-400 sigma N_H2)
    return np.exp(-400 * SIGMA_LW_RUN * N)


def none(N, T):
    return np.ones_like(N)


def slab(fshield, n, T, Z, I_uv, dN=2e17, depth_pc=40.0):
    A = grain_rate(T) * Z * n
    N_tot = n * depth_pc * PC
    steps = int(N_tot / dN)
    NH2 = 0.0
    ys = np.empty(steps)
    for i in range(steps):
        N = i * dN
        gamma = 0.5 * I_uv * D0 * fshield(np.array(NH2), T) * np.exp(-SIGMA_D * Z * N)
        y = A / (2 * A + gamma)
        ys[i] = y
        NH2 += y * dN
    cell = int(n * 2.62 * PC / dN)
    f_cell = 2 * ys[:max(cell, 1)].mean()
    half = np.argmax(2 * ys >= 0.5)
    N_half = half * dN if 2 * ys.max() >= 0.5 else np.inf
    return f_cell, N_half, 1 / (2 * A) / 3.156e13


if __name__ == "__main__":
    Z = 0.06
    models = [("none", none), ("N18 boost x400", n18_boost), ("GK11 power law", gk11_power),
              ("DB96 b=2", db96), ("DB96 b(T)", db96_bT), ("WG11 a=1.1 b(T)", wg11),
              ("R14 b(T)", r14),
              ("GD14 Ns=1e15", lambda N, T: gd14_sonic(N, T, 1e15)),
              ("GD14 Ns=1e19", lambda N, T: gd14_sonic(N, T, 1e19))]
    cases = [(78, 170, 0.3), (38, 98, 0.3), (217, 170, 0.3), (78, 806, 0.3), (78, 3000, 0.3),
             (78, 170, 6.0), (217, 806, 6.0), (78, 170, 0.003), (900, 100, 6.0)]
    for n, T, I in cases:
        print(f"\nn_H={n} cm^-3  T={T} K  I_UV={I}  Z'={Z}   (b_total={b_total(T):.2f} km/s; one cell = {n*2.62*PC:.1e} cm^-2)")
        out = {}
        for name, f in models:
            fc, Nh, tf = slab(f, n, T, Z, I)
            out[name] = fc
            print(f"   {name:18s} f_H2(first cell) {fc:7.3f}   half-molecular at N_H = {Nh:9.2e}   t_form {tf:6.0f} Myr")
        ref = out["DB96 b=2"]
        print("   spread across shielded column models (excl. none/N18):",
              f"{min(v for k, v in out.items() if k not in ('none','N18 boost x400')):.3f}"
              f"-{max(v for k, v in out.items() if k not in ('none','N18 boost x400')):.3f}  (DB96 b=2: {ref:.3f})")

    # f_shield itself at representative columns and temperatures
    print("\nf_shield at fixed column (columns: N_H2 = 1e14, 1e15, 1e16, 1e17, 1e18, 1e20, 1e21)")
    Ns = np.array([1e14, 1e15, 1e16, 1e17, 1e18, 1e20, 1e21])
    for T in (100, 170, 800, 3000):
        print(f" T={T} K")
        for name, f in models[2:]:
            print(f"   {name:18s}", " ".join(f"{v:8.1e}" for v in f(Ns, T)))

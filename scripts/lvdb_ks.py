"""First Kennicutt-Schmidt-style plot from the Local Volume Database (LVDB).

LVDB (B8_MolecularGas/LVDB/comb_all.csv) has H I mass, half-light radius and stellar mass but no
star formation rate, so SFRs come from Karachentsev & Kaisina 2013 (KARACH13; VizieR J/AJ/146/46
table3, saved next to this script as kk13_table3.tsv), cross-matched on sky position.

Choices (defaults, not physics results):
  * aperture  R = 2 * rhalf_physical (LVDB major-axis half-light radius, pc); Sigma = X / (pi R^2).
    Both axes share the aperture, so changing R slides every point along a slope-1 line.
  * Sigma_HI is hydrogen only (Bigiel+08 convention); iso-depletion lines include helium x1.36
    (Bigiel+08 p.8-9).
  * SFR(FUV) is the default tracer (KK13 eq. 3); SFR(Halpha) (KK13 eq. 1) is drawn in a second panel.
  * LVDB and KK13 distances are not reconciled: Sigma_SFR carries a (D_LVDB/D_KK13)^2 error.

Run:  /home/edge/data/venv/bin/python /tmp/b8_scratch/lvdb_ks/lvdb_ks.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord

HERE = Path(__file__).resolve().parent
LVDB = Path("/home/edge/data/B8_MolecularGas/LVDB/comb_all.csv")
KK13 = HERE / "kk13_table3.tsv"
MATCH_ARCMIN = 1.0      # or 1.2 x the half-light radius if larger: big dwarfs (LMC, SMC, dSphs)
                        # have catalogue centres up to ~1 deg apart; all >5' matches checked by name
APERTURE = 2.0          # R = APERTURE * rhalf_physical
HELIUM = 1.36           # Bigiel+08: multiply hydrogen surface densities by ~1.36 for helium

# same grouping and colours as Sonny/605/lvdb_analysis.ipynb
GROUPS = {"dwarf_mw": "Milky Way dwarf", "dwarf_m31": "M31 dwarf",
          "dwarf_local_field": "Local Field dwarf", "dwarf_local_field_distant": "Local Field dwarf",
          "misc": "misc"}
COLOUR = {"Milky Way dwarf": "#0072B2", "M31 dwarf": "#E69F00", "Local Field dwarf": "#009E73",
          "misc": "#000000"}
LABEL = ["lmc", "smc", "ngc_6822", "wlm", "ic_1613", "leo_p", "sextans_a", "sextans_b"]

# Halo 605 at z=0 (output_00125), from the 2026-10-05 classification run (classify605.py on
# py-noether): M_HI 5.2e4 Msun, SFR over the last 200 Myr 1e-4 Msun/yr, projected R_e 241 pc.
# Provisional; replace with numbers measured in the same aperture as the observations.
SIM = {"Halo 605 z=0 (SFR over 200 Myr)": dict(m_hi=5.2e4, sfr=1e-4, rhalf_pc=241.0, m_star=None)}


def read_kk13():
    lines = [l for l in KK13.read_text().splitlines() if l and not l.startswith("#")]
    head, rows = lines[0].split("\t"), [l.split("\t") for l in lines[3:]]
    kk = pd.DataFrame(rows, columns=head).apply(lambda c: c.str.strip())
    for c in ("SFRa", "SFRu", "BMag"):
        kk[c] = pd.to_numeric(kk[c], errors="coerce")
    kk["sfr_ha_ul"] = kk["l_SFRa"] == "<"
    kk["sfr_fuv_ul"] = kk["l_SFRu"] == "<"
    kk["coord"] = SkyCoord(kk["RAJ2000"], kk["DEJ2000"], unit=(u.hourangle, u.deg))
    return kk


def cross_match():
    df = pd.read_csv(LVDB)
    df = df[df["table"].isin(GROUPS)].copy()
    df["group"] = df["table"].map(GROUPS)
    kk = read_kk13()
    lv = SkyCoord(df["ra"].values * u.deg, df["dec"].values * u.deg)
    kc = SkyCoord([c.ra for c in kk["coord"]], [c.dec for c in kk["coord"]])
    idx, sep, _ = lv.match_to_catalog_sky(kc)
    df["kk_name"] = kk["Name"].values[idx]
    df["sep_arcmin"] = sep.arcmin
    for c in ("SFRa", "SFRu", "sfr_ha_ul", "sfr_fuv_ul"):
        df[c] = kk[c].values[idx]
    tol = np.maximum(MATCH_ARCMIN, 1.2 * df["rhalf"].fillna(0))
    m = df[df["sep_arcmin"] < tol].copy()
    # one LVDB row per KK13 galaxy: keep the closest if two LVDB rows hit the same one
    m = m.sort_values("sep_arcmin").drop_duplicates("kk_name")
    return df, m


def surface_densities(m):
    r_kpc = APERTURE * m["rhalf_physical"] / 1e3
    area_kpc2 = np.pi * r_kpc**2
    hi = m["mass_HI"].fillna(m["mass_HI_ul"])           # log10 Msun
    m["hi_ul"] = m["mass_HI"].isna() & m["mass_HI_ul"].notna()
    m["log_sig_hi"] = hi - np.log10(area_kpc2 * 1e6)    # Msun pc^-2, hydrogen only
    for tr in ("u", "a"):
        m[f"log_sig_sfr_{tr}"] = m[f"SFR{tr}"] - np.log10(area_kpc2)   # Msun yr^-1 kpc^-2
    m["log_tdep_u"] = np.log10(HELIUM) + hi - m["SFRu"]                # yr, aperture-free
    return m


def sim_points():
    out = {}
    for name, s in SIM.items():
        area_kpc2 = np.pi * (APERTURE * s["rhalf_pc"] / 1e3) ** 2
        out[name] = dict(log_sig_hi=np.log10(s["m_hi"] / (area_kpc2 * 1e6)),
                         log_sig_sfr=np.log10(s["sfr"] / area_kpc2),
                         log_tdep=np.log10(HELIUM * s["m_hi"] / s["sfr"]), m_star=s["m_star"])
    return out


def ks_panel(ax, m, tracer, title):
    sfr_col, ul_col = f"log_sig_sfr_{tracer}", "sfr_fuv_ul" if tracer == "u" else "sfr_ha_ul"
    d = m.dropna(subset=["log_sig_hi", sfr_col])
    x = np.linspace(-3, 2.5, 50)
    # Kennicutt 1998 eq. 4: Sigma_SFR = 2.5e-4 Sigma_gas^1.4 (Msun/yr/kpc^2, Msun/pc^2)
    ax.plot(x, np.log10(2.5e-4) + 1.4 * x, c="0.2", lw=1.4, label="Kennicutt 1998 (N = 1.4)")
    for t, ls in ((1e8, ":"), (1e9, "--"), (1e10, "-."), (1e11, (0, (1, 4)))):
        # Sigma_SFR = 1.36 Sigma_HI / t_dep ; Msun/pc^2 -> Msun/kpc^2 is 1e6
        ax.plot(x, np.log10(HELIUM) + x + 6 - np.log10(t), c="0.6", lw=0.9, ls=ls)
        ax.annotate(rf"$10^{{{int(np.log10(t))}}}$ yr", (2.3, np.log10(HELIUM) + 2.3 + 6 - np.log10(t)),
                    fontsize=7, color="0.45", ha="right", va="bottom", rotation=0)
    for g, col in COLOUR.items():
        s = d[d["group"] == g]
        det = s[~s[ul_col] & ~s["hi_ul"]]
        ax.scatter(det["log_sig_hi"], det[sfr_col], s=16, c=col, edgecolors="none", label=f"{g} ({len(s)})")
        lim = s[s[ul_col] | s["hi_ul"]]
        ax.scatter(lim["log_sig_hi"], lim[sfr_col], s=16, facecolors="none", edgecolors=col, lw=0.8)
        for _, r in lim.iterrows():
            if r[ul_col]:
                ax.annotate("", (r["log_sig_hi"], r[sfr_col] - 0.3), (r["log_sig_hi"], r[sfr_col]),
                            arrowprops=dict(arrowstyle="->", color=col, lw=0.7))
            if r["hi_ul"]:
                ax.annotate("", (r["log_sig_hi"] - 0.3, r[sfr_col]), (r["log_sig_hi"], r[sfr_col]),
                            arrowprops=dict(arrowstyle="->", color=col, lw=0.7))
    for k in LABEL:
        hit = d[d["key"] == k]
        if len(hit):
            r = hit.iloc[0]
            ax.annotate(r["name"], (r["log_sig_hi"], r[sfr_col]), xytext=(4, 3), textcoords="offset points",
                        fontsize=7)
    for name, p in sim_points().items():
        if tracer == "u":
            ax.scatter(p["log_sig_hi"], p["log_sig_sfr"], marker="D", s=70, c="white", edgecolors="crimson",
                       lw=1.6, zorder=5, label=name + ", provisional")
    ax.set(xlim=(-2.5, 2.5), ylim=(-7.2, 0.5), title=title,
           xlabel=r"$\log_{10}\,\Sigma_{\rm HI}$ [M$_\odot$ pc$^{-2}$]  (H only, within $R = 2\,r_{\rm h}$)",
           ylabel=r"$\log_{10}\,\Sigma_{\rm SFR}$ [M$_\odot$ yr$^{-1}$ kpc$^{-2}$]")
    # how far a point moves if the aperture doubles
    ax.annotate("", (0.9 - np.log10(4), -5.6 - np.log10(4)), (0.9, -5.6),
                arrowprops=dict(arrowstyle="->", color="0.3"))
    ax.text(0.95, -5.6, r"$R\times2$", fontsize=7, color="0.3", va="center")
    return len(d)


def main():
    df, m = cross_match()
    m = surface_densities(m)
    print(f"LVDB galaxies (dwarf_* + misc): {len(df)}; matched to KK13 within max({MATCH_ARCMIN}', 1.2 r_h): {len(m)}")
    print(f"  separations: median {m['sep_arcmin'].median():.2f}', 95th pct {m['sep_arcmin'].quantile(.95):.2f}'")
    print(f"  with HI (value or limit) + rhalf + SFR(FUV): {m.dropna(subset=['log_sig_hi','SFRu']).shape[0]}")
    print(f"  with HI (value or limit) + rhalf + SFR(Ha):  {m.dropna(subset=['log_sig_hi','SFRa']).shape[0]}")
    print("  nearest non-matches (1-3'):", df[(df.sep_arcmin >= 1) & (df.sep_arcmin < 3) & ~df.key.isin(m.key)][["key", "kk_name", "sep_arcmin", "rhalf"]]
          .round(2).to_string(index=False) if ((df.sep_arcmin >= 1) & (df.sep_arcmin < 3) & ~df.key.isin(m.key)).any() else "none")
    for name, p in sim_points().items():
        print(f"  {name}: log Sigma_HI {p['log_sig_hi']:.2f}, log Sigma_SFR {p['log_sig_sfr']:.2f}, "
              f"log t_dep {p['log_tdep']:.2f}")
    cols = ["key", "name", "group", "kk_name", "sep_arcmin", "distance", "mass_stellar", "mass_HI", "mass_HI_ul",
            "rhalf_physical", "SFRu", "sfr_fuv_ul", "SFRa", "sfr_ha_ul", "log_sig_hi", "log_sig_sfr_u",
            "log_sig_sfr_a", "log_tdep_u"]
    m[cols].sort_values("mass_stellar").to_csv(HERE / "lvdb_kk13_matched.csv", index=False)

    fig, axes = plt.subplots(1, 3, figsize=(17, 5.6), gridspec_kw=dict(width_ratios=[1, 1, 0.9]))
    n_u = ks_panel(axes[0], m, "u", "SFR from FUV (KK13, ~100 Myr)")
    n_a = ks_panel(axes[1], m, "a", r"SFR from H$\alpha$ (KK13, ~10 Myr)")
    axes[0].legend(fontsize=7, loc="upper left")

    ax = axes[2]                                   # aperture-free: depletion time vs stellar mass
    d = m.dropna(subset=["log_tdep_u", "mass_stellar"])
    for g, col in COLOUR.items():
        s = d[d["group"] == g]
        det = s[~s["sfr_fuv_ul"] & ~s["hi_ul"]]
        ax.scatter(det["mass_stellar"], det["log_tdep_u"], s=16, c=col, edgecolors="none")
        lim = s[s["sfr_fuv_ul"] | s["hi_ul"]]
        ax.scatter(lim["mass_stellar"], lim["log_tdep_u"], s=16, facecolors="none", edgecolors=col, lw=0.8)
    ax.axhline(np.log10(13.8e9), c="0.5", ls="--", lw=0.9)
    ax.text(4.1, np.log10(13.8e9) + 0.05, "Hubble time", fontsize=7, color="0.4")
    ax.axhline(np.log10(2.0e9), c="0.5", ls=":", lw=0.9)
    ax.text(4.1, np.log10(2.0e9) + 0.05, r"H$_2$ depletion, Bigiel+08 spirals", fontsize=7, color="0.4")
    for name, p in sim_points().items():
        ax.axhline(p["log_tdep"], c="crimson", lw=1.2, alpha=0.7)
        ax.text(4.1, p["log_tdep"] - 0.22, "Halo 605 z=0 (provisional)", fontsize=7, color="crimson")
    ax.set(xlim=(4, 10), ylim=(7.5, 13), title="Aperture-free: atomic depletion time",
           xlabel=r"stellar mass [log$_{10}$ M$_\odot$]",
           ylabel=r"$\log_{10}\,\tau_{\rm dep} = \log_{10}(1.36\,M_{\rm HI}/{\rm SFR_{FUV}})$ [yr]")
    fig.suptitle(f"LVDB dwarfs x Karachentsev & Kaisina 2013 SFRs: {n_u} with FUV, {n_a} with Halpha "
                 "(open = upper limit in SFR or H I)", fontsize=10)
    fig.tight_layout()
    fig.savefig(HERE / "lvdb_ks.png", dpi=160)
    print("wrote", HERE / "lvdb_ks.png")


if __name__ == "__main__":
    main()

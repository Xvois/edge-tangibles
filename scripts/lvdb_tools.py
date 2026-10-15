"""Helpers for lvdb_analysis.ipynb: loading, merging and plotting.

The notebook calls these one at a time and explains each step; this file holds the code so the notebook
stays readable. Everything here is plain pandas / matplotlib.

Units used throughout
    masses               log10 Msun        (as LVDB stores them)
    star formation rate  log10 Msun / yr   (as KK13 stores them)
    surface densities    log10 Msun / pc^2 for gas, log10 Msun / yr / kpc^2 for SFR
    distances            kpc
"""
import urllib.request
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import ascii

from utils.loading import ROOT

ROOT = Path(ROOT)

# ---------------------------------------------------------------------------------------------------
# 1. Getting the data
# ---------------------------------------------------------------------------------------------------
SOURCES = {                                         # local file  ->  where it was downloaded from
    "LVDB/comb_all.csv": "https://github.com/apace7/local_volume_database/releases/download/v1.1.1/comb_all.csv",
    "KK13/ReadMe":       "https://cdsarc.cds.unistra.fr/ftp/J/AJ/146/46/ReadMe",
    "KK13/table3.dat":   "https://cdsarc.cds.unistra.fr/ftp/J/AJ/146/46/table3.dat",
    "UNGC/ReadMe":       "https://cdsarc.cds.unistra.fr/ftp/J/AJ/145/101/ReadMe",
    "UNGC/table1.dat":   "https://cdsarc.cds.unistra.fr/ftp/J/AJ/145/101/table1.dat",
    "UNGC/table2.dat":   "https://cdsarc.cds.unistra.fr/ftp/J/AJ/145/101/table2.dat",
}


def fetch(sources=SOURCES, root=ROOT):
    """Download each catalogue file that is not on disk yet. Existing files are never overwritten."""
    for rel, url in sources.items():
        path = root / rel
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            print(f"downloading {rel}")
            urllib.request.urlretrieve(url, path)
        print(f"  {rel:22s} {path.stat().st_size / 1e3:7.1f} kB")


def load_lvdb():
    """The whole LVDB, one row per object. `group` is a readable name for the `table` column."""
    df = pd.read_csv(ROOT / "LVDB" / "comb_all.csv").copy()   # .copy() defragments the 122-column frame
    df["group"] = df["table"].map(GROUPS)
    return df


def _read_cds(folder, table):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return ascii.read(ROOT / folder / table, readme=ROOT / folder / "ReadMe", format="cds").to_pandas()


def load_sfr():
    """KK13 star formation rates joined (by galaxy name) to the UNGC distances and Holmberg diameters.

    Returns one row per KK13 galaxy with:
      log_sfr_ha, log_sfr_fuv     log10 SFR [Msun/yr] from H-alpha and from FUV
      sfr_ha_ul, sfr_fuv_ul       True where that SFR is an upper limit
      dist_ungc_kpc               the distance the SFRs were computed at
      A26_kpc                     Holmberg diameter (face-on), at that distance
    """
    kk = _read_cds("KK13", "table3.dat")
    t1, t2 = _read_cds("UNGC", "table1.dat"), _read_cds("UNGC", "table2.dat")
    assert (t1["Name"].values == t2["Name"].values).all()        # the two UNGC tables share rows
    ungc = t1[["Name", "Dist"]].join(t2[["A26"]])
    m = kk.merge(ungc, on="Name", how="left", validate="1:1")
    assert m["Dist"].notna().all(), "a KK13 galaxy is missing from the UNGC"
    sign = np.where(m["DE-"] == "-", -1.0, 1.0)
    return pd.DataFrame({
        "kk_name": m["Name"],
        "kk_ra": 15.0 * (m["RAh"] + m["RAm"] / 60 + m["RAs"] / 3600),
        "kk_dec": sign * (m["DEd"] + m["DEm"] / 60 + m["DEs"] / 3600),
        "log_sfr_ha": m["SFRa"], "sfr_ha_ul": m["l_SFRa"] == "<",
        "log_sfr_fuv": m["SFRu"], "sfr_fuv_ul": m["l_SFRu"] == "<",
        "dist_ungc_kpc": 1e3 * m["Dist"], "A26_kpc": m["A26"],
    })


# ---------------------------------------------------------------------------------------------------
# 2. Merging LVDB with the SFRs
# ---------------------------------------------------------------------------------------------------
GALAXY_TABLES = ["dwarf_mw", "dwarf_m31", "dwarf_local_field", "dwarf_local_field_distant", "misc"]


def merge(lvdb, sfr, match_arcmin=1.0):
    """Attach KK13/UNGC data to each LVDB galaxy (clusters and candidates are left out).

    Matching: nearest KK13 galaxy on the sky, within `match_arcmin`, or 1.2 x the LVDB half-light
    radius if that is larger (big, diffuse systems such as the LMC have catalogue centres ~1 deg apart).
    If two LVDB rows reach the same KK13 galaxy, the closer one keeps it.

    Distances: KK13/UNGC numbers are rescaled to the LVDB distance, so every quantity in a row uses one
    distance. A flux-based SFR scales as D^2 and a linear size as D.
    """
    gal = lvdb[lvdb["table"].isin(GALAXY_TABLES)].copy()
    lv = SkyCoord(gal["ra"].values * u.deg, gal["dec"].values * u.deg)
    kk = SkyCoord(sfr["kk_ra"].values * u.deg, sfr["kk_dec"].values * u.deg)
    idx, sep, _ = lv.match_to_catalog_sky(kk)
    gal["sep_arcmin"] = sep.arcmin
    hit = gal["sep_arcmin"] < np.maximum(match_arcmin, 1.2 * gal["rhalf"].fillna(0))
    gal["kk_idx"] = np.where(hit, idx, -1)
    closest_first = gal[hit].sort_values("sep_arcmin")
    gal.loc[closest_first.index[closest_first.duplicated("kk_idx")], "kk_idx"] = -1
    gal = gal.join(sfr, on="kk_idx")                              # kk_idx = -1 joins to nothing
    for c in ("sfr_ha_ul", "sfr_fuv_ul"):
        gal[c] = gal[c].eq(True)

    gal["dist_shift_dex"] = np.log10(gal["distance"] / gal["dist_ungc_kpc"])
    for tracer in ("ha", "fuv"):
        gal[f"log_sfr_{tracer}"] += 2 * gal["dist_shift_dex"]
    gal["R26_kpc"] = 0.5 * gal["A26_kpc"] * 10 ** gal["dist_shift_dex"]
    return gal


def merge_report(gal):
    m = gal["kk_name"].notna()
    print(f"LVDB galaxies: {len(gal)};  with a KK13 match: {m.sum()}")
    print(f"  match separation: median {gal.loc[m, 'sep_arcmin'].median():.2f}', "
          f"95% within {gal.loc[m, 'sep_arcmin'].quantile(0.95):.2f}'")
    print(f"  distance correction to the SFR, 2 log(D_LVDB / D_UNGC): median "
          f"{2 * gal.loc[m, 'dist_shift_dex'].abs().median():.2f} dex")
    far = gal[m & (gal["sep_arcmin"] > 5)]
    print("  matches further than 5' apart (the names should agree):")
    for _, r in far.iterrows():
        print(f"    {r['name']:14s} <-> {r['kk_name']:12s} {r['sep_arcmin']:5.1f}'")


# ---------------------------------------------------------------------------------------------------
# 3. Surface densities and depletion times
# ---------------------------------------------------------------------------------------------------
HELIUM = 1.36      # multiply hydrogen masses by this for total gas (Bigiel et al. 2008)


def add_ks_quantities(gal):
    """Add the KS-plane columns. The aperture is the Holmberg radius R26 for both gas and SFR.

    log_mhi       H I mass, or its upper limit (hi_ul = True)
    log_sig_hi    Sigma_HI   = M_HI / (pi R26^2)      [log Msun/pc^2]   hydrogen only
    log_sig_sfr_* Sigma_SFR  = SFR  / (pi R26^2)      [log Msun/yr/kpc^2]
    log_tdep_*    t_dep      = 1.36 M_HI / SFR        [log yr]          helium included; no aperture
    """
    gal["log_mhi"] = gal["mass_HI"].fillna(gal["mass_HI_ul"])
    gal["hi_ul"] = gal["mass_HI"].isna() & gal["mass_HI_ul"].notna()
    area_kpc2 = np.pi * gal["R26_kpc"] ** 2
    gal["log_sig_hi"] = gal["log_mhi"] - np.log10(area_kpc2 * 1e6)
    for tracer in ("ha", "fuv"):
        gal[f"log_sig_sfr_{tracer}"] = gal[f"log_sfr_{tracer}"] - np.log10(area_kpc2)
        gal[f"log_tdep_{tracer}"] = np.log10(HELIUM) + gal["log_mhi"] - gal[f"log_sfr_{tracer}"]
    return gal


# ---------------------------------------------------------------------------------------------------
# 4. Plotting
# ---------------------------------------------------------------------------------------------------
GROUPS = {"dwarf_mw": "Milky Way dwarf", "dwarf_m31": "M31 dwarf",
          "dwarf_local_field": "Local Field dwarf", "dwarf_local_field_distant": "Local Field dwarf",
          "gc_mw_new": "globular cluster", "gc_harris": "globular cluster",
          "gc_dwarf_hosted": "globular cluster", "gc_ambiguous": "globular cluster",
          "gc_other": "globular cluster", "candidate": "candidate", "misc": "misc"}
COLOUR = {"Milky Way dwarf": "#0072B2", "M31 dwarf": "#E69F00", "Local Field dwarf": "#009E73",
          "globular cluster": "#CC79A7", "candidate": "#999999", "misc": "#000000"}
NAMED = {"lmc": "LMC", "smc": "SMC", "leo_p": "Leo P", "wlm": "WLM", "ngc_6822": "NGC 6822"}
LOG_STORED = {"mass_stellar", "mass_HI", "mass_dynamical_wolf", "log_gas_fraction"}
AXIS = {"rhalf_physical": "half-light radius [pc]",
        "mass_stellar": r"stellar mass  [log$_{10}$ M$_\odot$]", "mass_HI": r"H I mass  [log$_{10}$ M$_\odot$]",
        "log_gas_fraction": r"gas fraction  $\log_{10}(M_{\rm HI}/M_\star)$",
        "metallicity": "stellar metallicity [Fe/H]", "M_V": "absolute V magnitude [mag]"}


def _name_points(ax, d, x, y):
    for key, label in NAMED.items():
        hit = d[d["key"] == key]
        if len(hit):
            ax.annotate(label, (hit.iloc[0][x], hit.iloc[0][y]), xytext=(5, 4), textcoords="offset points",
                        fontsize=8)


def plot_pair(df, x, y, ax=None):
    """Scatter two LVDB columns, coloured by group. Log axis only for quantities not already stored as log."""
    d = df.dropna(subset=[x, y])
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 5))
    for group, colour in COLOUR.items():
        s = d[d["group"] == group]
        if len(s):
            ax.scatter(s[x], s[y], s=7, c=colour, label=f"{group} ({len(s)})")
    _name_points(ax, d, x, y)
    if x not in LOG_STORED:
        ax.set_xscale("log")
    ax.set(xlabel=AXIS.get(x, x), ylabel=AXIS.get(y, y))
    ax.legend(fontsize=8, frameon=False)
    return ax


def _limits(ax, d, x, y, x_ul, y_ul, colour, x_dir=-1, y_dir=-1):
    """Open symbol for any limit, plus an arrow along each axis that is a limit."""
    lim = d[d[x_ul] | d[y_ul]]
    ax.scatter(lim[x], lim[y], s=18, facecolors="none", edgecolors=colour, lw=0.8)
    for _, r in lim.iterrows():
        for flag, (dx, dy) in ((r[x_ul], (0.3 * x_dir, 0)), (r[y_ul], (0, 0.3 * y_dir))):
            if flag:
                ax.annotate("", (r[x] + dx, r[y] + dy), (r[x], r[y]),
                            arrowprops=dict(arrowstyle="->", color=colour, lw=0.7))


def _scatter_groups(ax, d, x, y, x_ul, y_ul, x_dir=-1, y_dir=-1, legend=True):
    for group, colour in COLOUR.items():
        s = d[d["group"] == group]
        if s.empty:
            continue
        det = s[~s[x_ul] & ~s[y_ul]]
        ax.scatter(det[x], det[y], s=18, c=colour, edgecolors="none", label=f"{group} ({len(s)})" if legend else None)
        _limits(ax, s, x, y, x_ul, y_ul, colour, x_dir, y_dir)


def _depletion_lines(ax, x, offset, top, label_x):
    """Grey lines of constant depletion time; y = log(1.36) + x + offset - log(t). Labels stay inside the axes."""
    for t, ls in ((1e8, ":"), (1e9, "--"), (1e10, "-."), (1e11, (0, (1, 4)))):
        ax.plot(x, np.log10(HELIUM) + x + offset - np.log10(t), c="0.65", lw=0.9, ls=ls)
        xl = min(label_x, top - 0.25 - np.log10(HELIUM) - offset + np.log10(t))
        ax.text(xl, np.log10(HELIUM) + xl + offset - np.log10(t) + 0.08, rf"$10^{{{int(np.log10(t))}}}$ yr",
                fontsize=7, color="0.45", ha="right")


def plot_ks(gal, tracer, ax):
    """Sigma_SFR against Sigma_HI for one SFR tracer ("fuv" or "ha")."""
    y = f"log_sig_sfr_{tracer}"
    d = gal.dropna(subset=["log_sig_hi", y])
    x = np.linspace(-4, 3, 50)
    ax.plot(x, np.log10(2.5e-4) + 1.4 * x, c="0.15", lw=1.4, label="Kennicutt 1998")
    _depletion_lines(ax, x, offset=6, top=0.0, label_x=2.4)        # 1 Msun/pc^2 = 1e6 Msun/kpc^2
    _scatter_groups(ax, d, "log_sig_hi", y, "hi_ul", f"sfr_{tracer}_ul")
    _name_points(ax, d, "log_sig_hi", y)
    ax.annotate("", (2.0 - np.log10(4), -6.0 - np.log10(4)), (2.0, -6.0), arrowprops=dict(arrowstyle="->", color="0.3"))
    ax.text(1.95, -5.85, "if R doubles", fontsize=7, color="0.3", ha="right")
    ax.set(xlim=(-3.2, 2.5), ylim=(-7.3, 0.0),
           xlabel=r"$\log_{10}\,\Sigma_{\rm HI}$  [M$_\odot$ pc$^{-2}$]",
           ylabel=r"$\log_{10}\,\Sigma_{\rm SFR}$  [M$_\odot$ yr$^{-1}$ kpc$^{-2}$]")
    return len(d)


def plot_sfr_vs_hi(gal, ax, sims=None):
    """Integrated SFR(FUV) against H I mass: the KS plot with no aperture at all."""
    d = gal.dropna(subset=["log_mhi", "log_sfr_fuv"])
    x = np.linspace(3, 11, 20)
    _depletion_lines(ax, x, offset=0, top=1.0, label_x=10.9)
    _scatter_groups(ax, d, "log_mhi", "log_sfr_fuv", "hi_ul", "sfr_fuv_ul")
    _name_points(ax, d, "log_mhi", "log_sfr_fuv")
    for name, p in (sims or {}).items():
        ax.scatter(np.log10(p["m_hi"]), np.log10(p["sfr"]), marker="D", s=70, c="white",
                   edgecolors="crimson", lw=1.6, zorder=6, label=name)
    ax.set(xlim=(3, 11), ylim=(-7, 1), xlabel=AXIS["mass_HI"],
           ylabel=r"SFR from FUV  [log$_{10}$ M$_\odot$ yr$^{-1}$]")


def plot_depletion_time(gal, ax, sims=None):
    """t_dep = 1.36 M_HI / SFR(FUV) against stellar mass.

    An H I upper limit makes t_dep an upper limit (arrow down); an SFR upper limit makes it a lower
    limit (arrow up). A galaxy with both is unconstrained and is left out.
    """
    d = gal.dropna(subset=["log_tdep_fuv", "mass_stellar"])
    d = d[~(d["hi_ul"] & d["sfr_fuv_ul"])].assign(no_limit=False)
    for group, colour in COLOUR.items():
        s = d[d["group"] == group]
        det = s[~s["hi_ul"] & ~s["sfr_fuv_ul"]]
        ax.scatter(det["mass_stellar"], det["log_tdep_fuv"], s=18, c=colour, edgecolors="none")
        _limits(ax, s[s["hi_ul"]], "mass_stellar", "log_tdep_fuv", "no_limit", "hi_ul", colour, y_dir=-1)
        _limits(ax, s[s["sfr_fuv_ul"]], "mass_stellar", "log_tdep_fuv", "no_limit", "sfr_fuv_ul", colour, y_dir=+1)
    _name_points(ax, d, "mass_stellar", "log_tdep_fuv")
    for t, ls, label in ((13.8e9, "--", "13.8 Gyr (age of the Universe)"),
                         (2.0e9, ":", r"2 Gyr: H$_2$ depletion time in spirals (Bigiel+08)")):
        ax.axhline(np.log10(t), c="0.5", ls=ls, lw=0.9)
        ax.text(4.1, np.log10(t) + 0.05, label, fontsize=7, color="0.4")
    for name, p in (sims or {}).items():
        t = np.log10(HELIUM * p["m_hi"] / p["sfr"])
        ax.axhline(t, c="crimson", lw=1.2, alpha=0.7)
        ax.text(4.1, t - 0.22, name, fontsize=7, color="crimson")
    ax.set(xlim=(4, 10.5), ylim=(7.5, 13), xlabel=AXIS["mass_stellar"],
           ylabel=r"atomic depletion time $\log_{10}(1.36\,M_{\rm HI}/{\rm SFR})$  [yr]")


# ---------------------------------------------------------------------------------------------------
# 5. Koplitz et al. 2026, Figure 2
# ---------------------------------------------------------------------------------------------------
K26_STYLE = {   # category: (marker, face colour, legend label) -- as in the paper
    "MW":        ("o", "0.55", "Milky Way"),
    "IVC":       ("X", "tab:green", "intermediate-velocity clouds"),
    "HVC":       ("P", "tab:green", "high-velocity clouds"),
    "SMC":       ("p", "purple", "SMC"),
    "LMC":       ("^", "purple", "LMC"),
    "z<0.6":     ("D", "0.25", r"Ly$\alpha$ absorbers, $z<0.6$"),
    "z>1.8":     ("s", "0.25", r"Ly$\alpha$ absorbers, $z>1.8$"),
}


def load_koplitz_fig2():
    """The points of Koplitz et al. 2026 Fig. 2 (see H2_absorbers/README.txt for how they were recovered)."""
    k = pd.read_csv(ROOT / "H2_absorbers" / "koplitz26_fig2.csv")
    return k.fillna({"limit_NH": "", "limit_fH2": ""})


def plot_koplitz_fig2(k, ax):
    """f(H2) against total hydrogen column 2N(H2) + N(HI), drawn the way the paper draws it."""
    for cat, (marker, colour, label) in K26_STYLE.items():
        s = k[k["category"] == cat]
        ax.scatter(s["log_NH"], s["log_fH2"], marker=marker, s=40, c=colour, edgecolors="k", lw=0.6,
                   alpha=0.85, label=f"{label} ({len(s)})", zorder=3)
        for _, r in s[(s["limit_NH"] != "") | (s["limit_fH2"] != "")].iterrows():
            dx = {"upper": -0.25, "lower": 0.25}.get(r["limit_NH"], 0)
            dy = {"upper": -0.3, "lower": 0.3}.get(r["limit_fH2"], 0)
            for ex, ey in ((dx, 0), (0, dy)):
                if ex or ey:
                    ax.annotate("", (r["log_NH"] + ex, r["log_fH2"] + ey), (r["log_NH"], r["log_fH2"]),
                                arrowprops=dict(arrowstyle="-|>", color=colour, lw=1.0), zorder=2)
    tw = k[k["category"] == "this work"].sort_values("log_NH")
    ax.plot(tw["log_NH"], tw["log_fH2"], c="#ff474c", ls="--", lw=1.2, zorder=4)
    ax.scatter(tw["log_NH"], tw["log_fH2"], marker="*", s=260, c="#ff474c", edgecolors="k", lw=0.8, zorder=5,
               label="Koplitz+26: H$_2$ 139 kpc from a starburst")
    ax.set(xlim=(16.5, 23), ylim=(-7.2, 0.3),
           xlabel=r"total hydrogen column  $\log_{10}[\,2N({\rm H_2}) + N({\rm H\,I})\,/\,{\rm cm^{-2}}]$",
           ylabel=r"molecular fraction  $\log_{10} f({\rm H_2})$")
    ax.legend(fontsize=8, loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False)

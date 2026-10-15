"""Audit checks on data/lvdb_kk13_matched.csv (written by scripts/lvdb_ks.py).
Run: python3 -I audit/lvdb_checks.py  (numpy + pandas only)."""
import re
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
m = pd.read_csv(ROOT / "data" / "lvdb_kk13_matched.csv")
print(f"rows {len(m)}, unique keys {m.key.nunique()}, unique kk_name {m.kk_name.nunique()}")
print("groups:", m.group.value_counts().to_dict())

# 1. name agreement between LVDB and KK13 (normalised); list disagreements
norm = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower())
bad = m[[norm(a) != norm(b) for a, b in zip(m.name, m.kk_name)]]
print(f"\nname strings differ after normalisation: {len(bad)} rows; largest separations:")
print(bad.sort_values("sep_arcmin", ascending=False)[["name", "kk_name", "sep_arcmin"]].head(12).to_string(index=False))

# 2. recompute surface densities with the script's aperture R = 2 r_half
r_kpc = 2 * m.rhalf_physical / 1e3
area = np.pi * r_kpc**2
hi = m.mass_HI.fillna(m.mass_HI_ul)
d_sig = (hi - np.log10(area * 1e6)) - m.log_sig_hi
d_sfr = (m.SFRu - np.log10(area)) - m.log_sig_sfr_u
d_t = (np.log10(1.36) + hi - m.SFRu) - m.log_tdep_u
print(f"\nmax |recomputed - stored|: Sigma_HI {np.nanmax(np.abs(d_sig)):.2e} dex, Sigma_SFR {np.nanmax(np.abs(d_sfr)):.2e}, t_dep {np.nanmax(np.abs(d_t)):.2e}")

# 3. sample sizes and limit bookkeeping
hi_ul = m.mass_HI.isna() & m.mass_HI_ul.notna()
has_hi = hi.notna() & m.rhalf_physical.notna()
fuv = has_hi & m.SFRu.notna()
ha = has_hi & m.SFRa.notna()
print(f"\nKS-plane points: FUV {fuv.sum()}, Halpha {ha.sum()}")
print(f"  FUV points: HI detected {(fuv & ~hi_ul).sum()}, HI upper limit {(fuv & hi_ul).sum()}, SFR upper limit {(fuv & m.sfr_fuv_ul).sum()}, both limits {(fuv & hi_ul & m.sfr_fuv_ul).sum()}")
both = fuv & hi_ul & m.sfr_fuv_ul
print(f"  t_dep panel (lvdb_ks.py) plots both-limit (unconstrained) points: {both.sum()}")
print("  detections with both quantities (FUV):", (fuv & ~hi_ul & ~m.sfr_fuv_ul).sum())
print("  by group, FUV & both detected:", m[fuv & ~hi_ul & ~m.sfr_fuv_ul].group.value_counts().to_dict())
print("  by group, FUV & any limit:", m[fuv & (hi_ul | m.sfr_fuv_ul)].group.value_counts().to_dict())

# 4. named comparison galaxies
for k in ["leo_p", "sextans_a", "sextans_b", "wlm", "ngc_6822", "phoenix", "lgs_3", "tucana", "leo_t", "antlia", "leo_a", "ic_1613"]:
    r = m[m.key == k]
    if len(r):
        r = r.iloc[0]
        print(f"  {k:10s} D={r.distance:7.0f} kpc  logM*={r.mass_stellar}  logMHI={r.mass_HI} (ul {r.mass_HI_ul})  rh={r.rhalf_physical:.0f} pc  SFRu={r.SFRu} (ul {r.sfr_fuv_ul})  SFRa={r.SFRa}  log t_dep={r.log_tdep_u:.2f}")
    else:
        print(f"  {k:10s} not in matched table")

# 5. Halo 605 provisional point (values hard-coded in scripts/lvdb_ks.py)
m_hi, sfr200, rh = 5.2e4, 1e-4, 241.0
A = np.pi * (2 * rh / 1e3) ** 2
print(f"\nHalo 605 as plotted: log Sigma_HI {np.log10(m_hi/(A*1e6)):.3f}, log Sigma_SFR {np.log10(sfr200/A):.3f}, log t_dep {np.log10(1.36*m_hi/sfr200):.3f}")
det = m[fuv & ~hi_ul & ~m.sfr_fuv_ul]
print(f"  observed detections: min log t_dep {det.log_tdep_u.min():.2f}, 5th pct {det.log_tdep_u.quantile(.05):.2f}, median {det.log_tdep_u.median():.2f}")
print(f"  fraction of FUV-detected dwarfs with t_dep below 605's provisional value: {(det.log_tdep_u < np.log10(1.36*m_hi/sfr200)).mean():.3f}")
# dwarfs of similar stellar mass (6.0-7.0) with HI and FUV, and their HI status
sim = m[(m.mass_stellar.between(6.0, 7.0))]
print(f"  LVDB-KK13 dwarfs with 6 <= log M* <= 7: {len(sim)}; with HI detection {sim.mass_HI.notna().sum()}, HI limit {sim.mass_HI_ul.notna().sum()}, FUV SFR {sim.SFRu.notna().sum()} (limits {sim.sfr_fuv_ul.sum()})")

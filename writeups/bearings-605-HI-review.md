# Bearings (halo 605): neutral hydrogen map review

File reviewed: `~/data/notebooks/605/bearings.ipynb` (saved 1 Oct 18:39). I did not edit it, and I did not
load the snapshot (the box had ~3 GB free with swap full, and your Jupyter kernel holds ~4 GB).

## Short answer

The map in cell 5 is wrong for three reasons that have nothing to do with X, and they swamp it.
Together they put the numbers off by a factor of about 1.5 × 10²¹, and the picture is of the wrong
piece of the box. Fixing X = 0.76 changes n_HI (the number density of neutral hydrogen atoms) by
about 1%, so it should come after these.

## Errors, in order of size

**1. The proton mass is wrong by 10¹⁰.** Cell 0: `PROTON_MASS_G = 1.67262192e-14`. It should be
`1.67262192e-24` g. Every n_HI is 10¹⁰ too small.

**2. Density is in the wrong units.** After `snap.physical_units()`, `gas["rho"]` is in solar masses per
cubic kiloparsec, not grams per cubic centimetre. The formula needs g cm⁻³. 1 Msun kpc⁻³ =
6.77 × 10⁻³² g cm⁻³ (checked with pynbody 2.4.2's own unit system), so every n_HI is 1.5 × 10³¹ too big.

**3. `SimArray(..., "cm^-3")` relabels, it does not convert.** I tested it: wrapping an array in
`Msol kpc**-3` with `"cm^-3"` keeps the numbers and swaps the label. So errors 1 and 2 pass silently,
and the colour bar says cm⁻³ over numbers that are not. Net: the map is 1.48 × 10²¹ too high.

**4. The map is of the box corner, not the galaxy.** The saved execution counts are
`[1, 9, 3, 4, 10, 11]`: centring (cell 2) ran 3rd, the rho image 4th, then **cell 1 was re-run 9th**,
which reloads the snapshot and throws the centring away. The n_HI image (11th) is therefore 5 kpc
around the box origin. That is why it is a flat ~1.06 × 10⁷ with diagonal blocky structure (coarse
grid cells) and no galaxy, while the rho image (made before the reload) shows one. Restart and run all.

**5. A cm⁻³ image is a slice, not a map.** pynbody makes a thin slice through z = 0 when the units
you ask for match the quantity's own. A neutral hydrogen map to compare with observations should be a
column density (atoms per cm²): ask for `units="cm**-2"` and pynbody integrates along the line of sight.

**6. Smaller:** `center(stars)` centres on every star particle in the zoom; centring on the main halo
(`h = snap.halos(); pynbody.analysis.halo.center(h[1])`) is safer, which the checkpoint version started to do.

## What x_HI means here (so the map is "neutral atomic", not "all neutral")

`x_HI` is a per-hydrogen-nucleus fraction. RAMSES-RT (radiation-hydrodynamics RAMSES) stores ionisation
states as fractions of hydrogen nuclei (Rosdahl et al. 2013, eq. 15), and with H₂ switched on
(`isH2=.true.` in this run's namelist) it enforces "2xH2 + xH I + xH II = 1" (Nickerson et al. 2018,
p.8). So n_HI = n_H · x_HI is correct for atomic hydrogen, and it excludes the molecular part,
½(1 − x_HI − x_HII) of nuclei, which your H₂ notebook already uses. If you want "all neutral hydrogen"
(atomic + molecular), use n_H · (1 − x_HII) instead. Worth deciding which one Bearings is about.

## Every place X = 0.76 is hardcoded

| File | Line | Use |
| --- | --- | --- |
| `notebooks/605/bearings.ipynb` | cell 0, cell 4 | `PRIMORDIAL_HYDROGEN_FRACTION`, n_HI |
| `analysis/h2_region.py` | 16, 38 | `HYDROGEN_MASS_FRACTION` → `n_H` in `load_region()` (feeds everything downstream) |
| `analysis/rt_scan.py` | 17, 19, 48–49 | `X, Y = 0.76, 0.24` → n_H, electron fraction, mean particle mass, temperature |
| `notebooks/src/h2_in_a_dwarf.py` (+ built `.ipynb`) | 192, 224, 263, 274–281, 333, 504, 824, 841–843, 937 | n_H text, helium per H, electrons, mean mass/temperature, H₂ mass, H₂ density fields, panel totals |
| `notebooks/h2_in_a_dwarf.ipynb` only | 520 | a second local `X = 0.76` inside a function |
| `notebooks/h_in_a_dwarf.ipynb` | 39, 43 | `X = 0.76`, plus n_H inherited from `h2_region` |
| `notebooks/rt_field_calibration.ipynb` | 121 | `X_FRAC, Y_FRAC = 0.76, 0.24` |

Nothing in `~/mphys` hardcodes it. The cleanest fix is one function in `analysis/` that every file
imports, so X lives in one place.

## What to replace it with

The run tracks C, N, O, Mg, Al, Si, Fe and Eu as mass fractions (Rey et al. 2025, p.5), but **not
helium as an abundance** (x_HeII and x_HeIII are ionisation states). So per-cell X needs a helium model:

- Total metal mass fraction per cell: Z = 2.09·metal_O + 1.06·metal_Fe, the definition your H₂ notebook
  attributes to Rey et al. (2025, p.4). [unverified: my corpus check did not find that sentence verbatim]
- Helium per hydrogen rising linearly with metallicity from primordial to solar (Ploeckinger & Schaye
  2020, eq. 18), with primordial n_He/n_H = 0.08246 (their p.9, from Planck 2016) and solar from
  Asplund et al. 2009 as quoted by Galliano et al. (2021, p.4): X⊙ = 0.7381, Y⊙ = 0.2485, Z⊙ = 0.0134.
- Then X = (1 − Z) / (1 + 3.971 · y_He), where y_He is helium nuclei per hydrogen nucleus and 3.971 is
  the helium-to-hydrogen atomic mass ratio (my arithmetic from X + Y + Z = 1).

```python
M_HE_OVER_M_H = 4.002602 / 1.00794
Y_HE_PRIM = 0.08246                                   # Ploeckinger & Schaye 2020, p.9
X_SUN, Y_SUN, Z_SUN = 0.7381, 0.2485, 0.0134          # Asplund 2009 via Galliano 2021, p.4
Y_HE_SUN = Y_SUN / (M_HE_OVER_M_H * X_SUN)            # = 0.0848

def hydrogen_mass_fraction(gas):
    Z = 2.09 * gas["metal_O"] + 1.06 * gas["metal_Fe"]          # total metal mass fraction
    y_he = Y_HE_PRIM + (Y_HE_SUN - Y_HE_PRIM) * (Z / Z_SUN)     # He nuclei per H nucleus
    return (1.0 - Z) / (1.0 + M_HE_OVER_M_H * y_he)

X = hydrogen_mass_fraction(gas)
rho_cgs = gas["rho"].in_units("g cm**-3")
gas["n_HI"] = SimArray(np.asarray(rho_cgs) * X * gas["x_HI"] / 1.67262192e-24, "cm**-3")
pynbody.plot.image(gas, qty="n_HI", units="cm**-2", width="5 kpc")   # column density map
```

What this does to X (my arithmetic, using the numbers above):

| Metallicity / solar | 0 | 0.01 | 0.1 | 0.3 |
| --- | --- | --- | --- | --- |
| X | 0.7533 | 0.7532 | 0.7518 | 0.7487 |
| change vs 0.76 | −0.9% | −0.9% | −1.1% | −1.5% |

## Things to take to Dr Rey

- **Most of the shift is helium, not metals.** At dwarf metallicities the metals move X by under 0.2%;
  the ~0.9% comes from 0.76 being an older primordial value than the Planck-based one above.
- **0.76 is also the run's own input.** `output_00125/info_rt_00125.txt` records `X_fraction = 0.76`,
  `Y_fraction = 0.24`, so RAMSES-RT's chemistry computed x_HI, x_HII and the H₂ fraction assuming it.
  A per-cell X in post-processing is more physical but no longer matches the hydrogen density the
  simulation evolved. Worth asking which he wants: consistency with the run, or physical X.
- **Z⊙ normalisation is inconsistent.** The EDGE metallicity divides by 0.02; Asplund's Z⊙ is 0.0134.
  Pick one, and use the same one in the helium interpolation.

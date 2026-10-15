# H₂ shielding models for the EDGE2 dwarfs: comparison and recommendation

*1 October 2026. Draft for Sonny to challenge; nothing in `~/data` or `~/mphys` was edited.*

**Source key.** **[C]** = in the Zotero corpus, quote verified with `evidence.py` (topic `shielding`, 15/16
strict). **[W]** = outside the corpus, read from the arXiv full text in this session (not ingested;
`acquire.py` lines at the end). **[S]** = my own slab calculation (`slab_compare.py`, numbers below).
**[inferred]** = my reasoning, not a sourced claim.

---

## 1. The short answer

"Shielding model" is really three separate choices, and they matter in the opposite order to how much
attention they usually get:

| Choice | What it decides | Recommendation |
|---|---|---|
| **A. Equilibrium or time-dependent** | whether the gas has had long enough to become molecular | **Time-dependent** (the notebook's Section 7 integrator) as the headline number; equilibrium only as an upper bound |
| **B. Column estimator** | how much H₂ and dust sits between a cell and the light | **Keep the ray-tracing** you already have (12 directions is enough) |
| **C. Self-shielding function** f_shield(N_H₂, T, b) | how much a given H₂ column dims the light | **Richings, Schaye & Oppenheimer (2014)**, with Draine & Bertoldi (1996) kept as the bracketing case, and a CLOUDY run at our conditions to settle the gap between them |

The run's own scheme, a constant ×400 boost (Nickerson et al. 2018), is out on every count (Section 3.1).

## 2. Our parameter space (from the stand-in snapshot, notebook Section 3)

- Metallicity relative to solar, Z′ ≈ 0.06, almost uniform.
- Dense gas (n_H > 30 cm⁻³, hydrogen nuclei per cm³): median 78, densest 903.
- Temperature: median 170 K, but the 84th percentile is 806 K, so **one dense cell in six is warm**.
- Cells: mostly 2.6 pc. One finest cell at median density is a hydrogen column of about 6×10²⁰ cm⁻².
- Field, I_UV (in multiples of the local Draine field): typical 0.3, but spanning ×1/100 to ×20.
- H₂ formation time 1/(2A): median 72 Myr.

Three things make this non-standard compared with a solar-neighbourhood cloud: almost no dust, a long
formation time, and a temperature spread that crosses the range where shielding fits change behaviour.

## 3. The candidates for the self-shielding function (choice C)

### 3.1 Nickerson, Teyssier & Rosdahl (2018): constant ×400 boost (what the run uses) [C]

Light is depleted as exp(−400 σ N_H₂). N18 tuned it at solar metallicity and say it "gives a realistic
match to the analytical transition point, especially for lower densities" but "It is less accurate for
higher densities and at smaller visual extinctions" (p.12). In the figure it lets through ~half the
light at the run's own N_H₂ ≈ 10¹⁶ cm⁻², where every real shielding curve has already fallen to 1–10%.
**Rejected**: wrong shape exactly at the columns that start the runaway.

### 3.2 Power law, f = (N_H₂/10¹⁴)^−0.75 (Draine & Bertoldi 1996 eq. 36; Gnedin & Kravtsov 2011) [C]

No line overlap. Gnedin & Draine (2014) show that SMC data (the only low-metallicity calibrator they
had) disfavour the no-overlap model (p.3). **Rejected** for Z′ ≈ 0.06.

### 3.3 Draine & Bertoldi (1996) eq. 37, "DB96" (what the notebook uses) [C]

f = 0.965/(1+x/b₅)² + 0.035/√(1+x) · exp(−8.5×10⁻⁴√(1+x)), x = N_H₂/5×10¹⁴ cm⁻², b₅ = Doppler
parameter b in km/s. Includes line overlap (the exponential). Sternberg et al. (2014) confirmed it
against the Meudon code "for a Doppler parameter b = 2 km s-1" (Fig. 5, p.17). Derived for cold gas
(their Fig. 1 and 3 use 100–200 K and b = 3 km/s).

- **Strength:** the corpus standard, independently confirmed, right for our median 170 K gas.
- **Weakness [W]:** Wolcott-Green, Haiman & Bryan (2011) find it "accurate only for a rotationally-cold
  gas" and that it **overestimates shielding** by up to an order of magnitude above a few hundred K,
  because warm H₂ spreads over more rotational levels. That is our warm sixth.

### 3.4 Wolcott-Green, Haiman & Bryan (2011), "WG11": DB96 with exponent 2 → 1.1 [W]

Calibrated in metal-free haloes at 300 ≲ T ≲ 10⁴ K, n ≈ 10–10⁶; within a factor 2 at 500 < T < 5000 K
and N_H₂ ≤ 10²⁰. Good for warm gas, but its largest errors are at the cold end (500 K is their coldest
test), and it is **outside its range for our median cell**. The 2019 update (Wolcott-Green & Haiman,
α(n,T)) is calibrated only for 500 ≤ T ≤ 8000 K and N_H₂ ≤ 10¹⁷ cm⁻², which excludes both our cold gas
and the columns that matter. **Not suitable as the main function.**

### 3.5 Richings, Schaye & Oppenheimer (2014), "R14": temperature-dependent DB96 form [W]

Their eqs. 3.12–3.17: the DB96 shape with ω(T), α(T) and a critical column N_crit(T) fitted to CLOUDY's
large H₂ model, with b = √(b_thermal² + b_turb²) and b_thermal = √(2kT/m_H₂). Stated accuracy: within
30% of CLOUDY at 100 K for N_H₂ < 10²¹ cm⁻², within 60% at 5000 K for N_H₂ < 10²⁰ cm⁻².

- **Strengths:** the only fit in the list calibrated across *both* our cold and warm gas, out to the
  columns of a molecular cell; and calibrated against **the same code we will use for CO**, so the H₂
  and CO steps stay internally consistent.
- **Weaknesses:** calibrated in primordial gas, plane-parallel; not in the corpus. And it **disagrees with
  DB96** at high column: R14 report that DB96 and WG11 both give ~3× *less* shielding than CLOUDY at
  N_H₂ ≳ 10¹⁷ cm⁻² at 100 K. My curves reproduce that factor (2.5×10⁻³ vs 8.8×10⁻⁴ at 10¹⁷). So two
  detailed codes (Meudon via Sternberg 2014, and CLOUDY via R14) disagree by ~3×, and **this is the single
  biggest open uncertainty in the shielding function**.

### 3.6 Gnedin & Draine (2014), "GD14", eq. 3: turbulent line overlap [C]

Replaces x in DB96's first term with the geometric mean of the total column and the column on the
sonic scale, N_s = ⟨n_H₂⟩_s l_s. Two points for our data:

1. With l_s ≲ 1 pc and ⟨n_H₂⟩ ~ 27 cm⁻³ in our cells, N_s ~ 8×10¹⁹ cm⁻², comparable to one cell's column.
   Eq. 3 only differs from DB96 when N_H₂ ≫ N_s, and gives unphysical *extra* shielding when N_H₂ < N_s
   (dotted curve). **At 2.6 pc it collapses to DB96 [S, inferred].** GD14 themselves find the result
   "insensitive to the value of the sonic length ls as long as ls < 10 pc" (p.3).
2. **Check in `analysis/shielding_prescriptions.py`:** it uses N_s = 10¹⁵ cm⁻², which corresponds to
   ⟨n_H₂⟩ ~ 3×10⁻⁴ cm⁻³ over 1 pc. That makes GD14 look much more different from DB96 than it is for our
   gas. Worth re-checking before that figure goes in the dissertation.

GD14's other product, fitting formulae for f_H₂(n), is calibrated on ≥65 pc cells and averaged scales, so
it does not apply to 2.6 pc cells (they note the full model "can be used in simulations with spatial
resolutions better than about 130 pc", p.4).

### 3.7 Molecular-fraction models instead of shielding functions

KMT09, Krumholz 2013 (K13), Sternberg 2014 / Bialy & Sternberg 2016, GD14 fits, and the new
**Polzin, Kravtsov, Semenov & Gnedin (2024)** fit return f_H₂ for a patch from density, metallicity and
field. They are not cell-level post-processing tools at 2.6 pc, but they are useful **cross-checks on
the full dataset at 10–100 pc scales**. Polzin et al. (2024) [W] is the only one calibrated down to
0.01 Z☉ and reproduces their simulations' H₂ mass to within ~1.5×.

## 4. Slab test at our conditions [S]

A uniform slab lit from one face, each layer in equilibrium, grain formation only (the notebook's
`slab_profile`), b_turb = 2 km/s. Number = mass-weighted molecular fraction 2y through the first 2.6 pc
(one finest cell). Only f_shield changes between columns.

| n_H, T, I_UV | N18 ×400 | power law | DB96 b(T) | WG11 | **R14** | GD14 N_s=10¹⁹ |
|---|---|---|---|---|---|---|
| 78, 170 K, 0.3 (median) | 0.38 | 0.35 | 0.29 | 0.14 | **0.77** | 0.32 |
| 38, 98 K, 0.3 | 0.00 | 0.01 | 0.03 | 0.00 | **0.35** | 0.05 |
| 217, 170 K, 0.3 | 0.92 | 0.86 | 0.82 | 0.77 | **0.96** | 0.83 |
| 78, 806 K, 0.3 | 0.00 | 0.09 | 0.09 | 0.01 | **0.34** | 0.12 |
| 78, 170 K, 0.003 (dim) | 0.99 | 0.99 | 0.99 | 0.99 | **1.00** | 0.99 |
| 78, 170 K, 6 (bright) | 0 | 0 | 0 | 0 | 0 | 0 |

What this says:

- **The function choice matters at the cell scale.** At median conditions, the defensible functions span
  0.14 (WG11) to 0.77 (R14), a factor ~5. It matters most in the moderate-field, moderate-density cells,
  which is where most of our dense gas sits; in very dim or very bright cells every model agrees.
- This is a **bigger lever than anything in the notebook's Section 8 robustness table**, which varied b
  and the dust cross-section but kept DB96 throughout [inferred]. The notebook's "insensitive to the
  column estimator" finding still stands; this is a different axis.
- **Formation time (60–560 Myr in these slabs) does not depend on the shielding function at all**, which
  is why choice A dominates (next section).

## 5. Why time-dependence (choice A) matters more than the function

- Polzin et al. (2024) [W]: "the maximum achieved molecular fraction in the interstellar medium drops
  drastically at Z ≲ 0.2 Z☉ as the formation time of H2 becomes much longer than a typical lifetime of
  dense regions". In their Table 2, *equilibrium* models over-predict the H₂ mass at 0.1 Z☉ by ~30× (S14)
  to ~400× (GD14). Caveat: their simulations do not include line overlap, so part of the GD14 gap is that
  (they say so).
- Hu et al. (2016) [W], a Z = 0.1 Z☉ dwarf with TreeCol shielding: "the H2 mass remains out of chemical
  equilibrium throughout the simulation".
- Gnedin & Draine (2014) [C]: at very low dust abundance "there is no alternative to full time-dependent
  non-equilibrium treatment" (p.4).
- Our median formation time is 72 Myr. **The equilibrium 3.9×10⁵ M☉ should be read as an upper bound**;
  the Section 7 integrator (16,000 M☉ at 1 Myr, 117,000 at 10 Myr) is closer to the right quantity,
  but it needs to know *how long* each parcel has been dense, which needs the snapshot ladder.

## 6. Column estimator (choice B)

- What we have, 48-ray tracing, is the reference method the local approximations are tested against.
- Local approximations have documented, regime-dependent biases [W]: the Jeans length underestimates the
  dissociation rate by ≳10× below 10⁴ cm⁻³ (WG11); Sobolev-like gradient lengths give too high a rate at
  low density and too low at high density against ray tracing (Nguyen et al. 2025); TreeCol vs Jeans
  shifts the critical flux by 2× (Hartwig et al. 2015). Our dense gas is entirely below 10⁴ cm⁻³.
- PRISM (Katz et al. 2022, co-authored by Martin Rey) uses a local estimator "following Gnedin et al.
  (2009)" [C]: worth knowing if the supervisor expects that route, but ray tracing is better for
  post-processing where cost is not the constraint.
- Velocity: GD14's argument is that gas at different line-of-sight velocities does not shield each
  other's line cores. WG11 found velocity gradients change the averaged rate by ≲2× [W]. An inexpensive
  refinement is to count only H₂ along each ray within ±b of the cell's own velocity, for the DB96/R14
  first term only (the overlap term keeps the full column, as in GD14 eq. 3) [inferred].

## 7. Recommendation and implementation sketch

**Winner: R14's temperature-dependent function, inside a time-dependent solve, on ray-traced columns,
with DB96 b(T) run alongside as the bracket.** R14 wins because it is the only fit valid across our whole
temperature range at the columns that matter, and because it matches the code that will make the CO.
It does not win on corpus authority: DB96 has that, and Meudon and CLOUDY disagree by ~3× at high column.

Implementation, in order:

1. **Settle the R14 vs DB96 gap with CLOUDY at our conditions** (Z′ = 0.06, n = 78, T = 170 and 800 K,
   I_UV = 0.3): read off f_shield(N_H₂) and compare to both fits. CLOUDY c25 is already built. This is the
   tie-breaker and a nice dissertation figure.
2. **Swap the function in one place**: `self_shielding(N_H2, b)` in `notebooks/src/h2_in_a_dwarf.py`
   becomes `self_shielding(N_H2, T, b)`; `shielded_rate()` passes each cell's own T. R14 needs ω(T),
   α(T), N_crit(T) (their eqs. 3.13–3.15). About 15 lines; `slab_compare.py` has a tested version.
3. **Per-cell b**: b_thermal from T, plus b_turb from the velocity dispersion of each cell's neighbours
   (already loaded), instead of a single 2 km/s.
4. **Report the Section 7 time-dependent mass as the headline**, equilibrium as the ceiling, and get the
   time each parcel has been dense from the snapshot ladder (open question 2 in `~/mphys/README.md`).
5. **For the full dataset**: 12 directions (Section 8 showed it agrees within a few per cent) to keep cost
   down; one heavy job at a time on this box.
6. **Cross-check at 10–100 pc** with the Polzin et al. (2024) fit on the projected maps.

## 8. What would change this recommendation

- If CLOUDY at Z′ = 0.06 sides with DB96 rather than R14, use DB96 with per-cell b, and WG11's α only in
  cells above ~500 K.
- If the target haloes are much warmer or brighter than the stand-in, the function choice matters less
  (Section 4: everything converges at high field) and time-dependence matters more.

## Non-corpus sources (to ingest if you want them grounded)

```
cd ~/mphys && .venv/bin/python tools/acquire.py arXiv:1403.6155 --reindex   # Richings, Schaye & Oppenheimer 2014
cd ~/mphys && .venv/bin/python tools/acquire.py arXiv:1106.3523 --reindex   # Wolcott-Green, Haiman & Bryan 2011
cd ~/mphys && .venv/bin/python tools/acquire.py arXiv:2310.10712 --reindex  # Polzin et al. 2024
cd ~/mphys && .venv/bin/python tools/acquire.py arXiv:1810.10010 --reindex  # Wolcott-Green & Haiman 2019
cd ~/mphys && .venv/bin/python tools/acquire.py arXiv:1510.05644 --reindex  # Hu et al. 2016
cd ~/mphys && .venv/bin/python tools/acquire.py arXiv:1505.00263 --reindex  # Hartwig et al. 2015
cd ~/mphys && .venv/bin/python tools/acquire.py arXiv:2511.07563 --reindex  # Nguyen et al. 2025
cd ~/mphys && .venv/bin/python tools/acquire.py arXiv:1309.5100 --reindex   # Krumholz 2013
```
(Polzin 2024 is listed in `~/mphys/README.md` as a highlight but is not in `corpus.db`.)

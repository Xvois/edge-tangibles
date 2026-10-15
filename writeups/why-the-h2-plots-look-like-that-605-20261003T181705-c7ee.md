# Halo 605: why the molecular hydrogen maps look the way they do

Source: `~/data/notebooks/605/bearings.ipynb` (saved 3 Oct 15:03), snapshot `Halo605_RT/output_00125`
(redshift z = 0). I did not edit the notebook or touch your running kernel. I re-read the snapshot one
domain at a time (memory-capped) and kept every gas cell whose centre falls in the 80 × 80 kpc column
through the halo centre, along the whole depth of the box: 4,972,699 cells. That is the same set of
cells the notebook's maps integrate. My rebuilt wide map reproduces the notebook's (peak 1.3 × 10¹⁵ vs
1.0 × 10¹⁵ cm⁻²), so the numbers below describe the same picture.

Symbols: n_H is hydrogen nuclei per cm³; x_H2 is H₂ molecules per hydrogen nucleus, so 2·x_H2 is the
fraction of hydrogen in molecules; N(H2) is the H₂ column density (molecules per cm²); R₂₀₀c = 31.45 kpc
as in the notebook; Z' is metallicity relative to solar.

## Short answers

1. **Yes, the maps show trace H₂, not molecular gas.** Inside R₂₀₀c the run holds **4.6 M☉ of H₂**,
   against 2.6 × 10⁷ M☉ of hydrogen: a mass-weighted x_H2 of 9 × 10⁻⁸. The highest column on any map is
   ~10¹⁵ cm⁻², about a million times below a molecular cloud.
2. **It is not a shielding problem.** No shielding calculation is in these maps: they use the run's own
   stored x_HI and x_HII. And no shielding model could make H₂ here, because there is no dense or cold gas
   to shield. The densest cell in the halo has n_H = 0.06 cm⁻³ at 8,200 K; nothing is colder than 3,500 K.
3. **The blotches are star particles.** Every blotch, near or far, sits on a single old star particle
   (13.2–13.5 Gyr old). 85 of the 90 star-hosting cells between 3 and 45 kpc carry an H₂ excess, and
   99.6% of the H₂ beyond 3 kpc lies within 1 kpc of a star. The H₂ excess per star-hosting cell is the
   **same ~2 × 10⁻⁵ M☉ whether the cell holds 0.002 M☉ or 40 M☉ of gas.** That is the fingerprint of a
   fixed amount of something deposited by each star particle, not of chemistry.

![evidence](h2_605_why.png)

(a) the notebook's wide map rebuilt, with star particles beyond 3 kpc circled. (b) x_H2 against density
inside R₂₀₀c: grey cells are >200 pc from any star, red cells <50 pc from one. (c) H₂ mass in each cell
that holds a star, against that cell's hydrogen mass.

## 1. What is in the halo at z = 0

| Region | Hydrogen mass | H₂ mass | Neutral atomic H mass |
| --- | --- | --- | --- |
| r < 2.5 kpc | 1.3 × 10⁶ M☉ | 4.61 M☉ | 4.9 × 10⁴ M☉ |
| r < R₂₀₀c | 2.6 × 10⁷ M☉ | 4.63 M☉ | 5.2 × 10⁴ M☉ |
| in the map column but outside R₂₀₀c | 7.2 × 10⁷ M☉ | 0.003 M☉ | 950 M☉ |

Inside R₂₀₀c the 1st / 50th / 99th percentiles are n_H = 4 × 10⁻⁶ / 1.3 × 10⁻⁵ / 7 × 10⁻³ cm⁻³ and
T = 8,000 / 19,000 / 50,000 K. The densest cells (n_H ≈ 0.06 cm⁻³, 24 pc cells at r ≈ 0.25 kpc) are
warm (~8,500 K), 25% ionised, at Z' ≈ 0.12, with x_H2 ≈ 10⁻⁵.

For scale, from the corpus:
- EDGE forms stars only in gas denser than 300 hydrogen masses per cm³ and colder than 100 K (Rey et al.
  2022, p.2; paraphrased, the PDF's symbols defeat a verbatim check). The densest gas here is 5,000×
  too thin and 80× too warm.
- At solar metallicity "the HI-to-H2 conversion occurs for characteristic gas surface densities of
  ∼10 M⊙pc-2" (Sternberg et al. 2014, p.3). By my arithmetic that is ~1.3 × 10²¹ H cm⁻². Our largest
  atomic column is 2.7 × 10¹⁹ cm⁻², and at Z' ≈ 0.1 the transition moves to higher columns still
  (Richings et al. 2014 find it occurs "at a lower column density at higher metallicity", p.16).
- Hu et al. (2015, p.24): "The ISM in dwarf galaxies is a hostile environment for H2 formation because
  of its low DGR, strong ISRF, and low densities in general."

**Why is there no dense gas?** The youngest star particle is 106 Myr old; about 2 × 10⁴ M☉ of stars formed
100–200 Myr ago and none since. My reading (inferred, not tested) is that the snapshot catches the galaxy
after a burst, with its cold gas heated and dispersed. Rey et al. (2022, p.5) describe EDGE relic dwarfs
"almost entirely devoid of gas, both hot or cold in their centres"; halo 605 still has 1.3 × 10⁶ M☉ of
hydrogen within 2.5 kpc, so it is in between: gas present, none of it cold.

## 2. What the run is actually storing

RAMSES-RT with H₂ switched on stores only x_HI and x_HII, and recovers x_H2 as half the remainder,
x_H2 = ½(1 − x_HI − x_HII) (Nickerson et al. 2018, p.7; the passage is in the corpus, but the equation's
symbols defeat a verbatim check). The network itself is complete: "formation on dust grains, gas phase
formation, formation by three-body collisions, collisional destruction" plus photodissociation and
self-shielding (Nickerson et al. 2018, p.1). The run does its own shielding, so the post-processing
shielding comparison only matters once there is dense gas to apply it to.

So x_H2 here is a remainder, not a separately tracked quantity. Anything that changes the hydrogen in a
cell without updating x_HI and x_HII to match will show up as H₂.

Two checks on the numbers:
- 45,851 cells have a slightly negative x_H2, all no lower than −2.2 × 10⁻¹⁶. That is double-precision
  rounding of 1 − x_HI − x_HII and does no harm.
- Away from stars the run's chemistry gives a tight, smooth relation (grey line in panel b): x_H2 rises
  from ~10⁻¹⁴ at n_H = 10⁻⁶ to ~10⁻⁹ at n_H = 3 × 10⁻³ cm⁻³. That is the run's genuine gas-phase H₂ in
  warm gas. Summed over every cell more than 200 pc from a star, it comes to **0.001 M☉**.

## 3. The blotches

**Their size is set by cell size, not by real clumps.** pynbody spreads each AMR (adaptive mesh
refinement) cell over a kernel about its own width. The big rounded squares in the wide map are blocks
of eight 382–763 pc cells with identical values (one refined parent cell). The small dots are 24–48 pc
cells.

**Every one of them holds a star particle.** I located the host cell of every star particle in the column:

| Test | Result |
| --- | --- |
| Star-hosting cells at 3–45 kpc with an H₂ excess | 85 of 90 |
| CGM cells at 10–31 kpc: median x_H2, star-hosting vs not | 4 × 10⁻⁶ vs 5 × 10⁻¹⁴ |
| H₂ beyond 3 kpc within 0.5 / 1 / 2 kpc of a star | 94.5% / 99.6% / 99.9% (those cells are 6% of the volume) |
| Same density (n_H = 10⁻³–10⁻²) in the inner 2.5 kpc: x_H2 >200 pc from a star vs <50 pc | 1.4 × 10⁻⁹ vs 4.5 × 10⁻⁶ |
| H₂ per star-hosting cell, cell sizes 24 → 763 pc (cell masses 0.002 → 40 M☉) | 1.9, 2.1, 2.7, 2.2, 1.7, 0.9 × 10⁻⁵ M☉ |
| H₂ per star, by age of the youngest star in the cell | 4.3 × 10⁻⁴ (<0.5 Gyr), 2.2 × 10⁻⁴ (0.5–2), 1.2 × 10⁻⁴ (2–8), 5.5 × 10⁻⁵ M☉ (>8 Gyr) |

The densities rule out in-situ formation. The blotch gas has n_H ≈ 5 × 10⁻⁶ cm⁻³ at 1–2 × 10⁴ K, like
its neighbours, yet carries x_H2 between 10⁻⁷ and 6 × 10⁻³, up to ten orders of magnitude above them.
The fine 24–48 pc cells sit on dark-matter clumps (hundreds of particles within 200 pc, against a
median of 18 within 1 kpc at random points). That is why they are refined. Each clump also holds one
star particle, so they look like tiny satellites.

**What the per-star source most likely is (inferred).** EDGE2 returns mass from every star particle
continuously, not only in supernovae: "For AGB winds, we compute the IMF-averaged number of AGB stars in
a given timestep" (Rey et al. 2025, p.6). OB winds and Type Ia supernovae are handled alike (same page,
paraphrased), and this run's namelist has `winds=.true.`. A constant H₂ mass per star, regardless of how
much gas the host cell holds, is what you get if each star's returned gas is added to the cell's density
without the matching x_HI / x_HII. The deficit is then booked as H₂ by construction. It also explains why
younger stars, which return mass faster [unverified: not checked in the corpus], carry more. The run's
hydrogen check, "when this fails we lower the largest fraction accordingly" (Nickerson et al. 2018,
p.8), corrects fractions that sum above one; a deficit passes it. **I cannot see the EDGE2 source on
this machine, so the mechanism is a hypothesis.** The correlation itself is measured.

Loose end: 67 star particles far down the sightline (median r = 89 kpc, in 0.4–3 kpc cells) show no
excess. I have not worked out why.

## 4. Things in the notebook that make it look worse

- **Cells 24 and 25 map `gas`, not `gas_in`, and do not restrict depth.** They integrate the whole box
  along the line of sight, despite the markdown saying the maps come from `gas_in` and the title
  saying "inside the boundary". Two wide-map blotches come from cells outside R₂₀₀c: (15, −2) is at
  r = 41 kpc and (25.5, 32) at r = 46 kpc, 22–38 kpc in front of or behind the halo.
- **The colour bars span 12 decades** (10³–10¹⁵ cm⁻²), so 10⁻⁵ M☉ in a single cell shows as a strong red
  spot. Cell 26's RGB composite, floored at 10¹⁷ cm⁻², shows no red at all. That is the honest picture.
- Centring on all stars is fine here: every star particle is in this one galaxy.

## 5. What I'd take from this (for you to judge)

- This snapshot answers "where would H₂ be?" with "nowhere, at the moment". To map H₂ in halo 605 you need
  an output where the galaxy holds cold, dense gas, i.e. before or during a burst. The star formation
  history (stellar mass formed per 100 Myr, bursts up to 2 × 10⁴ M☉) shows where to look, but only
  `output_00125` is on this machine.
- If the per-star H₂ is an injection artefact, any H₂ total from EDGE2 includes a floor of roughly
  10⁻⁴ M☉ per star particle (16,056 particles, so ~1 M☉ here). That is small next to a real molecular
  reservoir, but the stand-in result (46 M☉ stored in Halo 383) is worth re-checking for it.
- Questions for Dr Rey: does the EDGE2 RAMSES-RT version set x_HI / x_HII on stellar mass return (winds,
  Type Ia), and is a quiescent z = 0 snapshot the intended target for halo 605?
- A cheap guard for the plots: mask cells that host a star particle, or report H₂ only from cells with
  2·x_H2 above some floor (e.g. 10⁻³). Either way, say on the map what the colour floor means.

## Reproducing

Scripts are in this session's scratchpad (`pass1_stars.py`, `pass2_gas.py`, `pass3.py`, `an1–3.py`,
`fig.py`). Each read runs under `systemd-run --user -p MemoryMax=1500M` and loads one domain at a time
(about 75 s for all 288). Corpus quotes are cached under evidence topic `h2-plots-605`.

## 6. Follow-up: is the temperature right, and could shielding change the answer? (3 Oct)

**Correction to section 1.** "No shielding model could make H₂ here" was too strong. What holds is that
no shielding method can create cool, dense gas, and none makes this snapshot meaningfully molecular.
With perfect shielding, the bound below allows a few to a few hundred M☉.

### Temperature, three ways (all 286,289 cells within 2.5 kpc)

| Method | min | 1% | median | 99% |
| --- | --- | --- | --- | --- |
| T/μ = P m_H / (ρ k_B), RAMSES's "T2", no ionisation assumption | 7,690 K | 12,320 K | 19,960 K | 94,000 K |
| T = (T/μ)·μ, μ per cell from x_HI, x_HII, x_H2, x_HeII, x_HeIII | 4,660 K | 8,020 K | 12,270 K | 56,170 K |
| pynbody's own `temp` | 4,820 K | 10,060 K | 12,710 K | 55,480 K |

Symbols: P is thermal pressure, ρ gas density, m_H the hydrogen mass, k_B Boltzmann's constant, and μ the
mean particle mass in units of m_H (0.59 when fully ionised, 1.22 when neutral atomic).

- ~~The per-cell method and pynbody agree to 3% at the median.~~ [Edit, 3 Oct evening: true only at the median. pynbody is off by a factor of ~2 in 18% of cells; see section 7.] μ in these cells runs from 0.588 to 0.984.
- The bound doesn't depend on ionisation. The lowest T/μ in the galaxy is 7,690 K and the lowest
  physical μ is ~0.59, so no choice of ionisation state puts any cell below ~4,500 K. Within 2.5 kpc
  there are 36 cells below 5,000 K and none below 1,000 K.
- The pressure field is the real thermal pressure. The snapshot's file descriptor lists
  `non_thermal_energy_03` separately from `pressure`, and it is exactly zero in every central cell, so
  no non-thermal term is inflating T.
- For scale, the thermal pressure P/k_B has a median of 31 K cm⁻³ and a maximum of 767 K cm⁻³.

### Can shielding create cool, dense gas?

Not in post-processing. Shielding acts on the chemistry (how fast LW photons, the 11.2–13.6 eV
Lyman–Werner band, destroy H₂). Density and temperature come from the hydrodynamics, which a
post-processing step cannot change. Only a different shielding treatment *inside the run* could alter
cooling and so the gas structure, and that would need a re-simulation.

### How much H₂ could form if shielding were perfect?

I switched off all photodissociation and let H₂ form on dust from the atomic hydrogen in every cell
inside R₂₀₀c. I used the grain formation rate coefficient from Sternberg et al. (2014, p.7; their
words: "We assume that per hydrogen nucleon the rate-coefficient for H2 formation on grains is given
by" R = 3 × 10⁻¹⁷ (T/100 K)^½ Z' cm³ s⁻¹). I tried it two ways: at the 100 K value, and with the √T
factor taken literally at our ~10⁴ K. The literal version is generous. That formula is written for
cold gas, and how efficient grains are at 10⁴ K is [unverified].

| Time with no dissociation at all | H₂ mass, 100 K rate | H₂ mass, √T rate | Most molecular cell |
| --- | --- | --- | --- |
| 100 Myr | 21 M☉ | 210 M☉ | 0.1% / 0.9% |
| 1 Gyr | 210 M☉ | 2,000 M☉ | 1% / 9% |

The run has 5.2 × 10⁴ M☉ of neutral atomic hydrogen to draw on. The formation time 1/(2 R n_H) for the
densest gas (n_H = 0.06, Z' = 0.12) is 73 Gyr at the 100 K rate and 8 Gyr with the √T factor. Gas does
not sit unchanged for that long: "Feedback-driven turbulence keeps the gas from cooling" below 10⁴ K at
these densities (Hu et al. 2015, p.24). So even with perfect shielding, this snapshot holds at most tens
to hundreds of M☉ of H₂, spread through warm gas at under 1% molecular per cell. I'd treat it as an
upper bound, not a prediction.

### What the EDGE papers say about halo 605 and cold gas

- Halo 605 "survives reionization and maintains star formation for a Hubble time" (Rey et al. 2025,
  p.13). Rey et al. (2025) re-simulate it as their test galaxy for numerical choices. Its stars formed
  out of cold gas, so cold gas must exist at other times.
- EDGE2 forms stars only below T★ = 1,000 K, raised from 100 K in EDGE1 "to compensate for the
  additional heating from radiative feedback" (Rey et al. 2025, p.5). The coldest gas in the galaxy now
  is ~4,700 K.
- For EDGE1's gas-rich quiescent dwarfs, "gradual cooling of gas is hampered by internal heating from
  old stellar populations within the galaxy" (Rey et al. 2022, p.3).

So the claim, restated: **in this z = 0 snapshot** nothing is cold or dense enough to be molecular, by
any temperature definition. Halo 605 does form H₂ at other times, because it keeps forming stars from
gas below 1,000 K. The last such event was ≥106 Myr before this output. To find where H₂ lives in
halo 605, look at outputs around its bursts, not at this one.

## 7. Why the temperature map looks blotchy, compared with halo 383 (3 Oct)

![temperature maps](temp_maps_605_vs_383.png)

Panels, left to right: (1) halo 605 with pynbody's `temp` on its automatic colour scale, which
reproduces bearings cell 21; (2) the same slice using a per-cell mean particle mass, on the same scale;
(3) the same as panel 2 on 10 to 10⁸ K, the scale used for halo 383 in `load_simulation_data.ipynb`
cell 13; (4) halo 383 (output_00129, z = 0.14) on that scale. The blank border in panel 4 is only
because I read halo 383's 48 central domains, not the whole box.

Three separate things are going on.

**1. pynbody's temperature is wrong for this run (the sharp-edged patches).** pynbody's RAMSES `temp`
iterates T = (P/ρ)·μ·m_p/k five times. It takes μ from `mu()`, which looks for arrays named `HI`, `HII`,
`HeI`, `HeII` and `HeIII`. This run names them `x_HI`, `x_HII` and so on. pynbody therefore finds
nothing and falls back to its "crude approximation": μ = 0.59 above 10⁴ K and 1.22 below. Halo 383's
notebook prints that warning. Bearings does the same thing, but the warning shows only once per
session, so you may not have seen it.

The two-value μ cannot settle when T/μ lies between 8,200 and 16,900 K. A cell there flips between
"ionised" and "neutral" on each iteration and ends on whichever it reaches after five steps. In halo
605's inner 2.5 kpc, 17% of cells sit in that band, and pynbody's temperature for them is off by a
factor of ~2. That covers 30% of the slice area in the 5 kpc map, against 4% in halo 383, whose gas
spans 10 K to 10⁷ K and so rarely sits near the threshold. The jump is a factor of two between
neighbouring cells, which is exactly the sharp-edged patches in panel 1. With a per-cell μ (panel 2)
they disappear.

**2. The colour scale.** Bearings lets pynbody choose the limits: 5,500 to 700,000 K, two decades on a
diverging map whose white point is near 6 × 10⁴ K. Halo 383 uses 10 to 10⁸ K, seven decades. On that
scale halo 605 is a near-uniform pale blue (panel 3), because almost all of it lies between 8,000 and
20,000 K.

**3. The gas really is different, and its cells are coarser because it is thinner.** The two runs have
the same maximum refinement level (24), so the data are not lower resolution by setting. Refinement
follows mass, though, and halo 605's gas is diffuse.

| | Halo 605, z = 0 | Halo 383, z = 0.14 |
| --- | --- | --- |
| Cell size in the slice, 10/50/90% by area | 48 / 95 / 95 pc | 21 / 42 / 84 pc |
| Smallest cell in the slice | 24 pc | 2.6 pc |
| Densest gas within 2.5 kpc | 0.06 cm⁻³ | 903 cm⁻³ |
| Cells within 2.5 kpc below 1,000 K / 100 K | 0 / 0 | 14,097 / 812 |
| Slice area where pynbody's T is off by >30% | 30% | 4% |

Halo 383 has a cold, dense, star-forming centre with supernova-heated pockets. Halo 605 at z = 0 is warm,
diffuse gas with one hot bubble.

Nothing in bearings degrades the data. `gas` versus `gas_in` makes no difference to a 5 kpc map: every
cell in it is inside R₂₀₀c. Because `units="K"` matches `temp`'s own units, pynbody draws a thin slice
through z = 0 in both notebooks, so the two maps are like for like.

**Suggested override** (uses the run's own X = 0.76 and Y = 0.24 from `info_rt_00125.txt`, and counts H₂
molecules as particles):

```python
k_B, m_H, X, Y = 1.380649e-16, 1.6726e-24, 0.76, 0.24
xHI, xHII = np.asarray(gas["x_HI"], float), np.asarray(gas["x_HII"], float)
xH2 = 0.5 * (1 - xHI - xHII)
particles_per_mH = X * (xHI + 2 * xHII + xH2) + Y / 4 * (1 + gas["x_HeII"] + 2 * gas["x_HeIII"])
T_over_mu = (gas["p"].in_units("g cm**-1 s**-2") / gas["rho"].in_units("g cm**-3")) * m_H / k_B
gas["T"] = SimArray(np.asarray(T_over_mu) / np.asarray(particles_per_mH), "K")
pynbody.plot.image(gas, qty="T", units="K", width="5 kpc", cmap="RdBu_r", vmin=10, vmax=1e8)
```

Fixing the colour limits (vmin/vmax) to the same values in every notebook makes the haloes directly
comparable.

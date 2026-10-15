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

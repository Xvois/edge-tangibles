# Audit: H2 in EDGE2 dwarf galaxies (halo 605, stand-in halo 383)

Independent audit of this repository, 2026-10-15. Scope: every file in the repo plus every result in `FINDINGS.md` and `THREADS.md`. Nothing in the repo was changed except adding this file and two helper scripts, `audit/backofenvelope.py` and `audit/lvdb_checks.py`.

**What I could and could not open.**
- Opened: 42 papers (full text from arXiv; listed in §S), the public RAMSES source (`github.com/ramses-organisation/ramses`, commit `51123de`, 2026-10-14) and the public pynbody source (`github.com/pynbody/pynbody`, commit `0259c38`, 2026-10-13).
- Not opened: the EDGE2 fork of RAMSES (not public), any simulation snapshot, and the project machine. The project machine at 100.125.18.58 was unreachable from this container (no SSH client or keys, and TCP port 22 timed out). Every number that lives only there stays [rep]. §V lists the commands that would settle each one.

**Tags** (abbreviations of the brief's tags):
- [file] read from a file. This means a repo file, or public source code (path given).
- [recomp: Bn/Ln/Sn] recomputed here; the exact command for each code is in §R.
- [lit: author year §] a paper I opened.
- [rep] reported in the repo, not verifiable here.
- [inf] my inference.

**Symbols and acronyms.**

*Hydrogen chemistry*
- H2, HI, HII: molecular, atomic and ionised hydrogen.
- x_HI, x_HII: fractions of hydrogen nuclei, as stored by the run.
- x_H2 = ½(1 − x_HI − x_HII): H2 molecules per hydrogen nucleus. f_H2 = 2x_H2.
- n_H: hydrogen nuclei per cm³.
- T/μ: temperature divided by μ, the mean particle mass in units of the hydrogen mass m_H.
- Z′: metallicity relative to solar.
- A: H2 formation rate per H atom [s⁻¹]. γ: photodissociation rate [s⁻¹].
- τ = 1/(2A+γ): relaxation time to chemical equilibrium. t_F = 1/(2A): formation time.

*Radiation*
- LW: Lyman–Werner band, 11.2–13.6 eV.
- RT: radiative transfer. RAMSES-RT: the adaptive-mesh-refinement (AMR) code with moment-based RT.
- c_r: the reduced speed of light (c/100 in EDGE2).
- N_i: photon number density of group i. σ_i: the group-averaged H2 cross-section.
- SED: spectral energy distribution. BC03 is Bruzual & Charlot 2003; BPASS is Binary Population and Spectral Synthesis.
- UVB: UV background. FG20 is the Faucher-Giguère 2020 UVB.
- G0 / χ: field strength in Habing / Draine units.
- PDR: photodissociation region.

*Galaxies and observations*
- EDGE: Engineering Dwarfs at Galaxy formation's Edge.
- R_e: projected V-band half-light radius. R200c: radius enclosing 200× the critical density.
- M★: stellar mass. M_V: absolute V magnitude.
- SFR: star formation rate. FUV: far-UV. Hα: H-alpha. KS: Kennicutt–Schmidt.
- CO: carbon monoxide. α_CO: CO-to-H2 conversion factor [M☉ (K km s⁻¹ pc²)⁻¹]. X_CO: the same in [cm⁻² (K km s⁻¹)⁻¹].
- LVDB: Local Volume Database. KK13: Karachentsev & Kaisina 2013. UNGC: Updated Nearby Galaxy Catalog.
- dSph, dTrans, dIrr, UFD: dwarf spheroidal, transition dwarf, dwarf irregular, ultra-faint dwarf. CGM: circumgalactic medium.

*Shielding and f_H2 models, by the papers that define them*
- N18: Nickerson et al. 2018. DB96: Draine & Bertoldi 1996. WG11: Wolcott-Green et al. 2011.
- R14: Richings et al. 2014. GD14: Gnedin & Draine 2014. GK11: Gnedin & Kravtsov 2011.
- S14: Sternberg et al. 2014. MK10: McKee & Krumholz 2010.

---

## 0. Summary

### 0.1 The three most serious problems

1. **The run's H2 photodissociation is split across two photon groups, and only one is shielded. The project treats this as an open question, but the public code answers it.**
   - EDGE2's bins are group 2 = 1–12 eV and group 3 = 12–13.6 eV [lit: Rey 2025 §2.2].
   - In public RAMSES-RT, the ×400 boost (`ssh2`) and the LW flag (`isLW`) go only to groups lying wholly inside 11.2–13.6 eV [file: `rt/rt_init.f90` L366-373]. Group 2 never gets them.
   - Group 2 still dissociates H2. The code sums σ_i c_r N_i over all groups (`rt_cooling_module.f90` L650). Its σ_2 is the photon-weighted average of 2.1×10⁻¹⁹ cm² over the group's 11.2–12 eV slice [file: `rt/rt_spectra.f90` L192, L738-756].
   - So σ_2/σ_3 = 3.16×10⁻⁴ is, by construction, the fraction of group-2 photons that are LW photons [recomp: B3]. The coordinator's inference is right.
   - N18 calibrated ×400 for one group spanning the whole LW band, at solar metallicity [lit: Nickerson 2018 §2.1, eq. 29, §3.2]. That calibration does not hold for this bin layout.
   - Consequences:
     - The reported "70% of H2 destruction from group 2" is a bin-boundary artefact, not physics.
     - Halo 605 at output 119 sits near the equilibrium set by unshielded 11.2–12 eV photons. "Run's law ≈ no shielding ≈ 1.7×10³ M☉" [rep].
     - Halo 383's 46 M☉ versus 3.9×10⁵ M☉ gap was blamed on the ×400 *shape*. The project's own slab table contradicts that: at median conditions ×400 gives f_H2 = 0.38, inside the 0.12–0.77 spread of the accepted functions [recomp: S1].
   - Only one thing remains for Dr Rey: whether the EDGE2 fork changed the band test.

2. **The project's numbers do not share one bookkeeping.**
   - **Factor-2 H2 mass.** `lvdb_scaling_relations.ipynb` cell 52 computes M_H2 = x_H2·M_H = 2.31 M☉. The write-up uses 2x_H2·M_H = 4.63 M☉. Ratio 2.003 [recomp: B1]; the notebook is wrong.
   - **pynbody temperature persists after the fix.** "Min T 4,800 K at 125" in `halo605_119_vs_125.md` (written ~10-07) equals the artefact floor of pynbody's two-value μ, 4,819 K [recomp: B2].
   - **Three R_e and two M_V for the same output.**
     - R_e = 199 pc (notebook, face-on), 241 pc (classification) and 271–278 pc (galaxy.json, down z).
     - M_V = −9.9 versus −10.58, a luminosity ratio of 1.87 [recomp: B8].
   - **z = 0 H2 is mostly bookkeeping.** Public RAMSES `thermal_feedback` adds returned mass to density but not to the ion-fraction scalars, which are stored as ρ·x [file: `pm/feedback.f90` L436-455; `rt/rt_init_xion.f90` L113]. The missing x_HI + x_HII is booked as H2.
     - The injected "H2" hydrogen mass is then X·Δm, independent of the host cell's mass [inf]. X is the hydrogen mass fraction (0.76 in this run) and Δm the returned mass. This is exactly panel (c) of `h2_605_why.png`.
     - So the z = 0 H2 values (1.6 M☉ in R_e, 4.6 M☉ in R200c) are upper limits on chemistry.
     - `rt_v2_fig4`'s "H2 is highest where the LW field is strongest" shows this artefact, not a physical trend.

3. **The evidence cannot yet answer "where and under what conditions H2 forms".**
   - Only one halo and two outputs, 732 Myr apart. Both bracket the burst; neither samples it.
   - Output 125 has no neutral cells with n_H > 0.1 cm⁻³ inside R_e [rep]. So 119 versus 125 compares "dense gas" with "no dense gas" and cannot isolate radiation.
   - The central bounds are equilibrium-only or single-channel, yet are presented as limits on the run:
     - "Even perfect shielding gives only 20–200 M☉" counts dust formation only. It omits the run's own H⁻ gas-phase channel (MK10 rate, no photodetachment) [lit: McKee & Krumholz 2010 App. A; file: `coolrates_module.f90` L272].
     - Without that omission, the densest z = 0 cell could become ~50% molecular in 100 Myr if nothing destroyed H2 [recomp: B5].
     - "Equilibrium is an upper bound" depends on the model. At 0.1 Z☉ equilibrium models range from 262× too low to 433× too high [lit: Polzin 2023 Table 2]. Hu et al. find the global equilibrium value only slightly high [lit: Hu 2016 §4.3.1].

### 0.2 Single highest-value next step

Measure H2 through the burst, with one fixed measurement function:
- Load halo 605 outputs 120–124. Full outputs are written every ~100 Myr [lit: Rey 2025 §2.7], and 119→125 spans six output intervals, so these should exist on the simulation store [inf].
- Run on all seven outputs: per-cell μ, M_H2 = 2x_H2·X·M_gas, cells hosting star particles masked, and one aperture (R_e from one V-band model, and R200c).
- Record H2 versus n_H, T and distance to stars younger than 10 Myr.

One-hour prerequisite: confirm the band test and the feedback ion scalars in the EDGE2 fork (§V checks 1–2). That decides whether any H2 number in the run is physics or bookkeeping.

### 0.3 Settled versus open

| Settled (enough evidence for a thesis sentence) | Basis |
|---|---|
| At z = 0 (output 125) halo 605 has no cold or dense gas: max n_H = 0.06 cm⁻³; T/μ ≥ 7,690 K, so T ≥ 4,524 K for any ionisation state | [rep] + [recomp: B2] bound |
| H2 at z = 0 is negligible (≤ 5 M☉) and largely a mass-return bookkeeping artefact | [file: pm/feedback.f90]; constant-mass signature [rep]; [inf] |
| Output 119 holds ~1.5×10³ M☉ H2 (H2/H = 2.2×10⁻³ inside R_e). That is the same order as an independent Z′ = 0.1 dwarf simulation (F_H2 ≈ 5×10⁻⁴). The run is not anomalously H2-poor | [rep] + [recomp: B8] + [lit: Hu 2016 §4.3.1] |
| pynbody's `temp` is wrong for this run: crude μ fallback, with a jump of ×2.08 at T/μ = 10⁴ K | [file: pynbody derived.py L214-240] + [recomp: B2] |
| In public RAMSES-RT the ×400 boost acts on group 3 only; group 2 carries the 11.2–12 eV LW photons unshielded | [file: rt_init.f90, rt_spectra.f90] |
| At Z′ ≈ 0.1 the expected H I→H2 transition sits far above the gas present at 119 (max 17 cm⁻³); H2 formation times (~0.2–3 Gyr) exceed dense-gas lifetimes | [lit: Gnedin 2009 eq. 7; Hu 2016 eq. 10; Polzin 2023 §4] + [recomp: B5, B6] |
| The FG20 UVB is not propagated in the RT groups. It is applied optically thin, damped by exp(−n_H/0.01 cm⁻³) (FINDINGS open question 2 is closed) | [lit: Rey 2025 §2.2–2.3] |

| Open (live questions, in priority order) | What would settle it |
|---|---|
| O1. Does the EDGE2 fork keep the public `ssh2` band test and the feedback that skips ion scalars? | §V checks 1–2 (grep), or Dr Rey |
| O2. How much H2 would the run hold if the whole LW band were shielded? | Time-dependent post-processing with group-2 LW shielded (§T6 G4); the definitive answer needs a re-run with a group edge at 11.2 eV |
| O3. Where and in what phase does H2 sit during the burst (~13.2–13.7 Gyr)? | Outputs 120–124 (§0.2) |
| O4. Is stored H2 in or out of equilibrium along gas histories? | Integrate along EDGE2 tracers (density and pressure every 4.5 Myr [lit: Rey 2025 §2.7]) |
| O5. How much of the answer is resolution? Cell size follows density (mass refinement) | Clumping-factor bracket plus the Polzin 2023 fit (§T6 G6); a re-simulation for the real test |
| O6. What CO luminosity would 605 have (Q4)? | Not started: CLOUDY grid or Hu 2022 X_CO (§T6 G7) |
| O7. Does it generalise (haloes 600, 624, 383)? | Same pipeline on other haloes |
| O8. Why does the ionising field per unit source rise ×29 from 119 to 125? | Absorption budget per shell (inferred to be lower gas density) |

---

## T1. Question tree

I added Q0. The literature makes stored x_H2 a *remainder* of two non-equilibrium scalars, set by bin layout and feedback bookkeeping. So "is the run's H2 a measurement?" has to be answered before "where is it?" [lit: Nickerson 2018 §2.4.1; Rey 2025 §2.2; Krumholz & Gnedin 2011 abstract].

I split Q2 by channel and timescale. At Z′ ≲ 0.2 the literature says time, not shielding, limits f_H2 [lit: Polzin 2023 abstract; Hu 2016 §3.1.1; Krumholz 2012 abstract].

| Q | Sub-question | What counts as an answer |
|---|---|---|
| **Q0** Is stored H2 a trustworthy quantity? | (a) Bookkeeping: mass return without ion scalars; the factor-2 mass convention. (b) Bin layout: unshielded LW in group 2. (c) The H⁻ channel without photodetachment. (d) Temperature/μ | An error budget per snapshot: M_H2 ± artefact floor, per-group γ shares, and a confirmed code path for each mechanism |
| **Q1** Where does H2 sit? | (a) Radius versus R_e and R200c. (b) n_H–T phase: cold dense versus warm diffuse (Hu 2016 finds much H2 in warm diffuse gas). (c) Distance to stars younger than 10 Myr and 100 Myr. (d) Variation over the burst cycle | H2-mass-weighted distributions in (r, n_H, T, d★) at ≥ 5 outputs spanning a burst, artefact cells masked, one aperture |
| **Q2** What is necessary and sufficient for H2? | (a) Density versus the Z′-dependent transition (Gnedin 2009 eq. 7; S14 N_trans ∝ 1/Z′). (b) Field and shielding: n₁D/(f_sh G0) (Hu 2016 eq. 14). (c) Time: t_F ≈ 1/(n₁D) Gyr versus dense-gas lifetime. (d) Channel: dust versus H⁻. (e) Ionisation | A per-cell classification (formation-limited / destruction-limited / equilibrium) that predicts stored x_H2 within a stated factor, tested along tracer histories |
| **Q3** Physics versus artefact? | (a) Group split and ×400 calibration. (b) Resolution: cell size set by density (8 m_bar ≈ 1,200 M☉ refinement). (c) No clumping factor. (d) Partially resolved Strömgren spheres and the T★ = 1000 K coupling (Rey 2025 §5.1.4, §5.2). (e) Mass-return H2 | Sensitivity table: M_H2 under each switch, with time-dependence. Physics = invariant across switches |
| **Q4** H2 to CO for ALMA (the Atacama Large Millimeter/submillimeter Array) | (a) α_CO(Z′, Σ_GMC, scale): Bolatto 2013 eq. 31, Hu 2022. (b) CO-dark fraction. (c) Is any 605 state CO-detectable? (d) A fair observational sample (Leo P, Sextans A, WLM, Sextans B, upper limits) | Predicted L_CO per output with an α_CO bracket, against published L_CO limits for matched dwarfs |

---

## T2. Inventory and map

Labels: **E** = essential, **S** = supporting, **T** = tangential, **N** = noise. "Sup." marks a superseded or duplicate item.

### T2.1 Files

| # | File | Q | Single claim it supports | Label | Duplicate / superseded |
|---|---|---|---|---|---|
| f1 | `README.md` | – | Bundle map; what is excluded | S | – |
| f2 | `FINDINGS.md` | all | Consolidated results (see T2.2) | S | – |
| f3 | `THREADS.md` | all | Thread outcomes (see T2.2) | S | – |
| f4 | `AUDIT_PROMPT.md` | – | Audit brief | N (for science) | – |
| f5 | `writeups/why-the-h2-plots-look-like-that-605.md` | Q0,Q1 | z = 0 has trace H2; blotches sit on star particles | N | **Sup.** by c7ee (strict subset) |
| f6 | `…-20261003T143648-de64.md` | Q0,Q1 | f5 + §6 temperature and perfect-shielding bound | N | **Sup.** by c7ee (c7ee = de64 + §7 + one edit) |
| f7 | `…-20261003T181705-c7ee.md` | Q0,Q1,Q3 | z = 0: no dense gas; per-star H2 artefact; pynbody μ bug and fix | **E** | Keep, with retractions (T7) |
| f8 | `writeups/halo605_119_vs_125.md` | Q1,Q2 | 119 is gas-rich and pre-burst; 125 is post-burst | S | **Sup.** by `burst_compare.ipynb` (not in repo); uses pre-fix temperature and different radiation estimators |
| f9 | `writeups/halo605_classification.md` | Q4 context | 605 sits between dSph and dTrans | T | Overlaps `final5.png`; M_V and R_e disagree with the notebook |
| f10 | `writeups/shielding_model_comparison.md` | Q3 | Recommends time-dependent solve + R14 | S | Keep, with corrections (T7) |
| f11 | `writeups/bearings-605-HI-review.md` | – | HI map unit errors (proton mass ×10¹⁰; ρ units) | T | – |
| f12 | `writeups/corpus-tooling-assessment.md` | – | Literature-tool QA | N | – |
| f13 | `writeups/corpus-tooling-upgrade.md` | – | Literature-tool QA | N | – |
| f14 | `scripts/slab_compare.py` | Q3 | 1D slab: f_H2 by shielding function | S | Reproducible here [recomp: S1] |
| f15 | `scripts/lvdb_ks.py` | Q4 ctx | First KS plot (aperture 2r_h, distances not reconciled) | N | **Sup.** by `lvdb_analysis.ipynb` and `lvdb_tools.py` |
| f16 | `scripts/lvdb_tools.py` | Q4 ctx | Helpers (R26 aperture, distances reconciled) | T | Still contains the retracted Koplitz-figure loader (L270-310) |
| f17 | `scripts/plotting.py` | – | House style | S (infrastructure) | – |
| f18 | `notebooks/lvdb_analysis.ipynb` | Q4 ctx | LVDB × KK13 × UNGC merge; KS and aperture-free plots | T | Current version |
| f19 | `notebooks/lvdb_scaling_relations.ipynb` | Q4 ctx | Scaling relations with 605 on them | T | Contains the factor-2 M_H2 error (cell 52); uses the collaborator's method |
| f20 | `data/lvdb_kk13_matched.csv` | Q4 ctx | 455 LVDB–KK13 matches | T | Written by `lvdb_ks.py` (old aperture); notebook writes `lvdb_kk13_ungc.csv` (not in repo) |
| f21 | `figures/chk3.png` | ctx | Size–luminosity (scaling-relations cell 32) | N | **Sup.** by `final5` (c) |
| f22 | `figures/chk4.png` | ctx | HI–M_V (cell 40) | N | **Sup.** by `final5` (d) |
| f23 | `figures/combo.png` | ctx | 3-panel house-style draft ([Fe/H], R½, M_HI with 605) | N | **Sup.** by `final5` |
| f24 | `figures/final_fig.png` | ctx | 2×2 plain-style output of cell 68 | N | **Duplicate** of `final5` |
| f25 | `figures/final5.png` | Q4 ctx | 605 on four LVDB relations | T | Keep one |
| f26 | `figures/h2_605_why.png` | Q0 | z = 0 H2 sits on star particles; constant mass per host cell | **E** | – |
| f27 | `figures/halo605_classification.png` | ctx | 605 versus Local Group dwarfs | T | Overlaps `final5`; M_V −9.9 is inconsistent |
| f28 | `figures/lvdb_ks.png` | ctx | KS plane, old aperture; 605 provisional | N | **Sup.** by `lvdb_ks_plane` + `lvdb_ks_aperture_free` |
| f29 | `figures/lvdb_ks_plane.png` | ctx | KS plane with R26 aperture | T | – |
| f30 | `figures/lvdb_ks_aperture_free.png` | ctx | SFR–M_HI and depletion time; 605 provisional | T | 605 point is misleading (T3 #24) |
| f31 | `figures/maps_compare.png` | – | Collaborator versus Sonny maps (pre-fix temperature) | N | – |
| f32 | `figures/rt_fig1.png` | Q3 | Six-group slices (output not labelled) | N | **Sup.** by `rt_v2_fig1` |
| f33 | `figures/rt_fig3.png` | Q3 | Radial c_r N per group; flux direction | S | Shows group 2 *separately*, which v2 merged away. Keep the left panel |
| f34 | `figures/rt_v2_fig1.png` | Q3 | Three-band slices with arrows | T | – |
| f35 | `figures/rt_v2_fig2.png` | – | Reduced-flux maps | T | – |
| f36 | `figures/rt_v2_fig3.png` | Q3 | Source geometry, flow, LW/ionising ratio, n_H profile | T | – |
| f37 | `figures/rt_v2_fig4.png` | Q0 | "H2 highest where LW strongest" | S as artefact evidence; **wrong as titled** | – |
| f38 | `figures/shielding_models_compared.png` | Q3 | f_shield(N_H2) for six functions at 170 K and 806 K | S | – |
| f39 | `figures/temp_maps_605_vs_383.png` | Q0 | The μ bug and its fix (post-fix figure) | S | – |

### T2.2 Results in FINDINGS / THREADS

| ID | Result (as recorded) | Q | Label | Note |
|---|---|---|---|---|
| F0 | Run setup: groups, BC03, c_r = 0.01c, x400, R_e, cells 11.3 pc | all | S | Group description corrected in T3 #9 |
| F1.1 | pynbody temp bug and per-cell μ fix | Q0 | S | Confirmed |
| F1.2 | 605 z = 0: 4.6 M☉ H2; no gas < 1000 K; "perfect shielding 20–200 M☉" | Q1,Q2 | E | Last clause wrong as a bound (T3 #18) |
| F1.3 | 383: stored 46 M☉ versus equilibrium 3.9×10⁵ M☉; "cause ×400" | Q3 | S | Cause unsupported (T3 #14) |
| F1.4 | Classification: dSph/dTrans boundary | ctx | T | – |
| F1.5 | 119 vs 125 inside R_e (gas, HI, H2, n, T, radiation, new stars, r = −0.76) | Q1,Q2 | E | Several caveats (T3 #20–23) |
| F1.6 | Source curves: ionising flat, LW ×4, field per source ×29 | Q2 | S | [rep] |
| F1.7 | Hu "eq. 11" formation-time shares 0/4.9/60.2% | Q2 | S | Wrong equation number (T3 #16) |
| F2 | Relaxation-time plot review | Q2 | S | Plot unreadable; γ omits groups 2, 4–6 |
| F3 | Clumpiness Phase A; group-2 check | Q3 | **E** | Mechanism now confirmed in code |
| F4 | Shielding recommendation | Q3 | S | Partly retract (T7) |
| F5 | LVDB context; Koplitz figure retracted | Q4 ctx | T | – |
| F6 | Open questions 1–10 | – | S | #2 closed; #1 mostly closed (§0.3) |
| Th1 | Device orientation | – | N | – |
| Th2 | Shielding models | Q3 | S | = f10 |
| Th3 | Burst vs quiescence | Q1,Q2 | E | = F1.5 |
| Th4 | Relaxation plot | Q2 | S | = F2 |
| Th5 | Clumps | Q3 | E | = F3 |
| Th6 | Group-2 check | Q3 | E | = F3 |
| Th7 | Stopped audit | – | N | No output |
| Th8 | Bundle build | – | N | – |

---

## T3. Accuracy audit (E and S items)

Verdicts: **C** = correct, **CC** = correct with caveat, **U** = unsupported, **W** = wrong.

### Units, conventions and temperature

| # | Claim | Verdict | Reason | Single test |
|---|---|---|---|---|
| 1 | Radiation from pynbody is "in flux units; ratios safe, absolute values caveated" (pynbody issue 542) | **CC** | Public RAMSES writes `photon_flux_XX` = rt_c(level)·N, i.e. already c_r·N [file: `rt/rt_output_hydro.f90` L99-104]. pynbody labels it unit_pf [cm⁻² s⁻¹] [file: `snapshot/ramses.py` L536]. pynbody's warning tells users to multiply by c_r again; following it would be off by c_r ≈ 3×10⁸ cm s⁻¹. The project's magnitudes are consistent with *no* double factor: group-3 c_r N ≈ 10³–10⁵ with σ_3 = 2.1×10⁻¹⁹ gives 1/γ ≈ 1.5–150 Myr, matching the relaxation review's 3–30 Myr [recomp: inline arithmetic] | Read the field names in the run's `hydro_file_descriptor.txt` / `rt_file_descriptor.txt`. `photon_flux_0N` means already ×c_r |
| 2 | pynbody falls back to μ = 0.59 / 1.22, so cells with T/μ of 8,200–16,900 K are wrong by ~2× | **C** | Mechanism confirmed [file: pynbody `derived.py` L214-240]: Y = 0.245 gives μ = 0.5904 / 1.2251 and a band of 8,163–16,938 K [recomp: B2]. Nuance: the outcome is deterministic, not a coin flip. T/μ in [8,163, 10⁴) returns 4,819–5,903 K; T/μ in [10⁴, 16,938] returns 12,252–20,704 K. So the map shows a sharp jump of ×2.08 at T/μ = 10⁴ K | – |
| 3 | Which results came before the μ fix (3 Oct evening)? | – | **Pre-fix:** `maps_compare.png` (sharp patches in "Sonny temp 5 kpc"); write-up §1 temperatures (8,200 K; "nothing < 3,500 K"; percentiles 8,000/19,000/50,000 K; provenance unknown, superseded by §6); `halo605_119_vs_125.md` (min T 4,800 K at 125 = artefact floor 4,819 K) [recomp: B2]. **Post-fix:** c7ee §6–7 and `temp_maps_605_vs_383.png`. **Unknown:** `burst_compare.ipynb`, `h2_relaxation.ipynb`, Phase A, group-2 check. **Robust either way:** masses below 1000 K (cold gas is outside the band). **Affected if pre-fix:** 125 "median T 1.07×10⁴ K"; any rate using α_Z(T) in 5,000–20,000 K gas (α_Z ∝ T^−1.5 there, so ×2 in T gives ≈ ×2.8 in rate [recomp: B5 formula]) | `grep -n "\"temp\"\|'temp'\|mu" *.ipynb` on the project machine (§V) |
| 4 | M_H2 = 4.6 M☉ in R200c at z = 0 | **CC** | The notebook gives 2.312 M☉ with M_H2 = x_H2·M_H, a factor 2 low (H mass in H2 is 2x_H2·M_H) [recomp: B1]. The write-up value is the right convention. The same bug, in the collaborator's "Test 3" method, may explain the reported Sonny/collaborator disagreement [inf] | Fix cell 52 to `2*x_H2*M_H`; it should give 4.62 M☉ |
| 5 | X = 0.76 everywhere versus per-cell X | **CC** | The run itself uses X = 0.76 [rep], so keep 0.76 for consistency with the run's chemistry. Per-cell X changes n_H by ≤ 1.5% [rep: bearings review] | – |
| 6 | SF threshold "300" quoted as n_H | **CC** | The threshold is ρ★ = 300 m_p cm⁻³ [lit: Rey 2025 eq. 1], i.e. n_H ≈ 228 cm⁻³ for X = 0.76 [recomp: B6]. Birth densities of 400–1740 "H/cc" need a stated convention | – |
| 7 | Z′ for 605 | **U** (as one number) | The repo has 0.12 (densest cells, EDGE Z/0.02), 0.105 (12+log O/H = 7.71 within 5 kpc) and 0.036 (7.249, mass-weighted R200c incl. CGM) [recomp: B8]. "Z′ ≈ 0.075" (brief) is not traceable in the repo. Z′ matters: n_t ∝ 1/Z′ and α_CO ∝ exp(0.4/Z′) | Quote ISM Z′ as the mass-weighted EDGE Z/0.02 of neutral gas inside 2R_e, one definition |

### Sample selection

| # | Claim | Verdict | Reason | Single test |
|---|---|---|---|---|
| 8 | R_e ≈ 275 pc; masses "inside R_e" | **CC** | Same output, three R_e: 199 pc (face-on, notebook), 241 pc (mean over x, y, z, classification), 271/278 pc (down z, galaxy.json) [file]. M_V −9.9 vs −10.58 (L ratio 1.87) [recomp: B8]. Different V-band metallicity inputs [rep]. Region labels are used consistently within each document: H2 at 125 is 1.6 (R_e), 4.61 (2.5 kpc), 4.63 (R200c) M☉; at 119, 1,535 (R_e) and 1,548 (whole halo) | One function: R_e from one SSP/metallicity choice, quoted with axis; every table states its aperture |

### RT photon groups

| # | Claim | Verdict | Reason | Single test |
|---|---|---|---|---|
| 9 | Group 3 (12–13.6 eV) is "the run's LW band" | **CC** | It is the only group flagged `isLW` and boosted ×400 [file: rt_init.f90 L366-373], and Rey 2025 §2.2 calls it the dissociating bin. But the LW band starts at 11.2 eV: 1/3 of its energy width (0.8 of 2.4 eV) lies in group 2 [recomp: B3]. The photon-number share is SED-dependent: by my reading of `rt_fig3` it is 19–41% of unshielded LW dissociation [recomp: B3, inputs read off the figure] | Print `group_csn` per group from the run log (`write_group_props`) or `info_rt` |
| 10 | σ_2 = 6.6×10⁻²³ versus σ_3 = 2.1×10⁻¹⁹ means f_LW in group 2 = 3.2×10⁻⁴ | **C** | By construction: getSEDcsn = ∫fλσ/∫fλ (photon-weighted), with σ_H2 = 2.1×10⁻¹⁹ for 11.2 ≤ E < 13.6 eV and 0 below [file: rt_spectra.f90 L192, L738-756], luminosity-weighted over all stars every 10 coarse steps [lit: Rey 2025 §2.2]. The "column order inferred" caveat is no longer needed. The 2.1×10⁻¹⁹ itself matches (D0/2)/F_LW = 2.07×10⁻¹⁹ cm² [recomp: B3; lit: Sternberg 2014 eq. 5; Nickerson 2018 eq. 22, §3.2] | – |
| 11 | BC03 gives 4.7×10⁻⁴ to 4.5×10⁻³ for ages ≥ 1.7 Gyr, "so the cross-section is if anything low" | **CC** | 3.2×10⁻⁴ lies *below* the quoted BC03 range by ≥ 1.5×. So the run's SED (metallicity/age mix, wavelength-grid integration across 1107 Å) differs from the raw BC03 used [inf]. The direction of the claim holds | Recompute f_LW with the run's own `SED_dir` files and age/Z mix of 605's stars |
| 12 | Group 2 gives 70.3% (sum) / 81.4% (median) of H2 destruction at 119 | **CC** (arithmetic [rep]); **W** if read as physics | In unshielded gas the group-2 share would be ~20–40% [recomp: B3]. It reaches 70% only because group 3 is attenuated (×400 boost; ~37× drop in thick cells [rep]; my τ_3 per 11.3 pc cell is 0.3–50 for n_H = 1–17, x_H2 = 10⁻⁴–10⁻³ [recomp: B4]) while group 2 is not (τ_2 ≲ 4×10⁻⁵ [recomp: B4]). Physically the 11.2–12 eV LW lines self-shield like the rest of the band. N18 calibrated ×400 assuming one group holds the whole band [lit: Nickerson 2018 §2.1, §3.2]. So the 70% is a **bin-boundary artefact** | §V check 1; then post-process with group-2 LW shielded |
| 13 | "Group 2 is never shielded" / "is ×400 applied to group 2?" | **CC / answered** | ×400: **No** in public code [file]. Group 2 *is* attenuated by dust (κ ρ Z f_dust c_r) and by unboosted H2 absorption, but both are negligible here (measured ratio 1.03 [rep]). Say "not self-shielded" | §V check 1 |
| 14 | 383: stored 46 M☉ versus equilibrium 3.9×10⁵ M☉; cause = fixed ×400 | **U** | Three confounders are not separated. (i) Time: median t_F 72 Myr [rep]. (ii) The group-2 leak; at 605/119 shielding group 2 alone moves equilibrium H2 1.7×10³ → 1.05×10⁵ M☉ [rep]. (iii) The ×400 shape. The slab table shows ×400 at median 383 conditions gives f_H2 = 0.380 versus DB96 0.292 and R14 0.765 [recomp: S1]. The slab omits group 2, so it cannot test (ii) | Post-process 383 three ways: ×400 on all LW photons; ×400 on group 3 only; DB96. All time-dependent |

### Equilibrium versus time-dependent

| # | Claim | Verdict | Reason | Single test |
|---|---|---|---|---|
| 15 | τ = 1/(2A + γ); "colour repeats the y-axis"; dense branch formation-limited at 300–1000 Myr | **CC** | The algebra is right for dx/dt = A(1−2x) − γx [inf]. γ omits groups 2, 4–6 and the UVB (UVB matters only for n_H ≲ 0.01 [lit: Rey 2025 §2.3]). Group 2 alone is up to 70% of γ, so τ is overestimated by up to ~3× in shielded gas [inf]. "γ ≫ 2A" and "formation-limited dense branch" cannot both hold in the same cells; the latter needs 2A ≳ γ. Plausible as a split (bulk versus dense tail), but say so | Plot t_F = 1/(2A) and t_D = 1/γ_all on separate axes (T7 figure 3) |
| 16 | "Hu et al. 2015 eq. 11" formation time; shares 0 / 4.9 / 60.2% | **CC** | In arXiv:1510.05644v2 (Hu et al. 2016 MNRAS), **eq. 11 is the destruction time** t_D ≈ 1/(f_sh G0) kyr. The formation time is **eq. 10**, t_F ≈ 1/(n₁D) Gyr with R_form ≈ 3×10⁻¹⁷ cm³ s⁻¹ (T ≲ 100 K) [lit: Hu 2016 §3.1.1]. The shares are consistent with eq. 10 and the 119 density table: t_F < 732 Myr needs n_H > 13.7 (D = 0.1), about 1.1×10⁵ of 9.1×10⁵ M☉ above n = 10; t_F < 106 Myr needs n_H > 94 (none); t_F < 13.8 Gyr needs n_H > 0.72, about 54–60% [recomp: B5 + FINDINGS table] | Fix the citation; state D and T used |
| 17 | Dense-cell formation times 870–1750 Myr | **CC** | The run's α_Z gives t_F = 174 Myr at n = 17, 100 K, Z′ = 0.1, and 3.07 Gyr at n = 1, 300 K [recomp: B5]. So 870–1750 Myr corresponds to n_H ≈ 2–4 cm⁻³ [inf] | – |
| 18 | "Even perfect shielding gives only 20–200 M☉" at z = 0 (c7ee §6) | **W** as a bound on the run | It uses the dust rate only. The run also forms H2 via H⁻ at k⁻ = 1.83×10⁻¹⁸ T^0.88 n_e, assuming *no* photodetachment [file: coolrates_module.f90 L272; lit: McKee & Krumholz 2010 App. A; Nickerson 2018 §2.3.1]. For the densest z = 0 cell (n_H 0.06, x_e 0.25, 8,500 K): t_F = 201 Myr, versus 2.1×10⁶ Myr dust-only [recomp: B5]. The *physical* conclusion survives on other grounds: columns ≤ 2.7×10¹⁹ cm⁻² give dust τ ≈ 5×10⁻³ (σ_g = 1.9×10⁻²¹ Z′ cm² [lit: Sternberg 2014 eq. 20]) and negligible self-shielding, so the z = 0 H2 is photodissociation-limited [inf] | Restate (T7) |
| 19 | Equilibrium post-processing "is an upper bound" (shielding write-up §5; Phase A) | **CC** | At 0.1 Z☉ some equilibrium models overpredict (S14 29.5×, GD14 433×) and others underpredict (KMT09b 262×; K13 within 1.8×) [lit: Polzin 2023 Table 2]. Hu 2016 finds the equilibrium F_H2 only slightly above the simulated value globally, though far off locally [lit: Hu 2016 §4.3.1]. Krumholz & Gnedin 2011 find agreement at Z′ ≳ 0.01 [lit: abstract]. The write-up quoted only the overpredicting pair. Phase A's equilibrium 3.3–4.2×10⁵ M☉ is therefore *not* a ceiling a priori | Integrate along tracers (T6 G3) |

### Apples-to-apples (119 vs 125)

| # | Claim | Verdict | Reason | Single test |
|---|---|---|---|---|
| 20 | H2 inside R_e drops 1535 → 1.6 M☉ ("~990×") | **CC** | Arithmetic gives 959× with 1.6, or 990× with 1.55 [recomp: B8]. 1.6 M☉ is near the mass-return artefact floor (~1 M☉ estimated in the write-up), so report "≥ ~10³×" | Mask star-hosting cells and recompute 125 |
| 21 | Does 125 have dense neutral gas? Radiation versus density as cause | **U** | No: max n_H 0.06; no neutral cells with n_H > 0.1 in R_e [rep]. Any 119-versus-125 comparison of shielding or formation conditions compares against an empty set, so the H2 drop follows from the density drop. Radiation ratios differ by estimator (LoS volume mean ×29 / ×8.3 in FINDINGS; mass-weighted ×60 / ×11 in the old write-up) | Compare cells matched in n_H across outputs (the old write-up's "16× at fixed density" is the right idea; extend it) |
| 22 | Per-pixel ΔHI versus Δ(ionising field), r = −0.76 | **CC** (descriptive) | Both differences share a common driver: removing gas lowers HI and lowers absorption, which raises the field. Pixels are spatially correlated, so effective N ≪ pixel count and no significance can be assigned. It cannot show that radiation removed HI [inf] | Partial correlation at fixed Δ(column density), or a run without RT (not available) |
| 23 | 113 new stars, 33,900 M☉, mean SFR 4.6×10⁻⁵ M☉ yr⁻¹; "112 vs 113 unexplained" | **C** | 113 × 300 M☉ = 33,900 M☉ (particle mass 300 M☉ [lit: Rey 2025 §2.4]); 33,900/732 Myr = 4.63×10⁻⁵ [recomp: B8]. The old write-up says 112 of 113 sit inside R_e *at 125*, so it is one star outside R_e, not a discrepancy [file: f8] | Check whether the notebook counts at birth or at 125 |

### Statistics

| # | Claim | Verdict | Reason | Single test |
|---|---|---|---|---|
| 24 | Generalisation from one halo, two outputs, 113 stars | **U** for any population claim | Stochastic re-simulations of 605 alone span M★ 2.97 (+0.07/−0.09)×10⁶ M☉ [lit: Rey 2025 §5.1.1]. Burst timing is not reproducible run to run. Statements must be "in this realisation of halo 605" | Repeat on 600/624/383 |

### LVDB analysis

| # | Claim | Verdict | Reason | Single test |
|---|---|---|---|---|
| 25 | Matching (nearest neighbour within max(1′, 1.2 r_h)) | **CC** | 455 one-to-one matches; 196 FUV / 136 Hα KS points reproduce the figure title [recomp: L1]. 173 name strings differ, mostly formatting. At least one wrong match passes the rule: dw1242p4115 (log M★ 6.86, r_h listed 29.5 kpc) ↔ NGC 4625 at 3.7′, which assigns a spiral's SFR to a dwarf. Only matches over 5′ were name-checked [recomp: L1] | Name-check every match over 1′ |
| 26 | Completeness, upper limits | **CC** | The KS sample is almost all Local-Field star-forming dwarfs (141 of 144 FUV + HI detections). MW/M31 satellites are 45 of 52 limit points [recomp: L1]. All 28 FUV-SFR limits also have HI limits, so their t_dep is unconstrained, yet `lvdb_ks.py` plots them (the notebook drops them) [recomp: L1]. FUV "detections" in gas-free UFDs (e.g. Ursa Major II, log SFR −8.84, not flagged) are not star formation [inf] | – |
| 27 | Halo 605 on the KS / t_dep plots ("provisional") | **W** as plotted | The point uses SFR over 200 Myr (10⁻⁴ M☉ yr⁻¹), but 605's SFR over 100 Myr is **0** [file: f19 cell 27], the FUV timescale [lit: KK13 §2; notebook cell 6]. Plotted log t_dep = 8.85 lies below every FUV-detected dwarf (min 8.92, median 10.11) [recomp: L1], so it reads as an extreme starburst. It should be a t_dep lower limit (SFR upper limit). Apertures also differ: 605 HI within R200c versus observed total HI over πR² | Replace with an SFR upper limit over 10 and 100 Myr in the same aperture |
| 28 | KS planes compare like with like | **U** | Σ_HI (HI only, total M_HI over π(2r_h)² or πR26²) is plotted against Kennicutt's total-gas relation. The two KS figures use different apertures and distance treatments. The KK13 calibrations are uncertain at low SFR [lit: KK13 §2]. Only aperture-free plots are robust | – |
| 29 | What an H2-free catalogue says about H2 | **–** | Nothing directly. Inferring H2 from SFR × t_dep,H2 fails at low Z: τ_dep,H2 varies ×260 between 0.01 and 1 Z☉ while SFR varies ×11 [lit: Polzin 2023 Fig. 9], and star formation can proceed in atomic gas at low Z [lit: Krumholz 2012 abstract; Glover & Clark 2012 abstract] | – |

### Other essential items

| # | Claim | Verdict | Reason | Single test |
|---|---|---|---|---|
| 30 | z = 0 blotches = mass returned without x_HI/x_HII (hypothesis) | **CC**: mechanism exists in public code | The public `thermal_feedback` adds mloss to ρ, momentum, energy and metals, not to the ρ·x ion scalars [file: pm/feedback.f90 L436-455; rt_init_xion.f90 L113]. Injected "H2" hydrogen mass = X·Δm, independent of host-cell mass [inf], matching panel (c). EDGE2's own winds and SN routines are not public. Alternative: the H⁻ channel near stars [inf], but that cannot produce constant mass per cell across four decades of cell mass | §V check 2 |
| 31 | "Smaller slabs (11.3 → 1 pc) lower f_H2, so cells lack density, not size" | **CC** | Shrinking a uniform slab at fixed n only lowers column; it is not a resolution test. The conclusion is right for a different reason: refinement follows mass, splitting above ~1,200 M☉ per cell, so 11.3 → 5.65 pc needs n_H ≳ 26 cm⁻³ and 3 pc needs ≳ 200 cm⁻³ [recomp: B7; lit: Rey 2025 §2.2]. At 119 (max 17) the cells are as small as the density allows. Matches 11.3 pc finest cells [rep] and 383's 2.6 pc cells at n up to 903 [rep] | – |
| 32 | Slab table and R14 / DB96 implementations | **C** | Reproduced to all quoted digits [recomp: S1]. R14 eqs. 3.12–3.15 and DB96 eq. 37 coded correctly [lit: Richings 2014 §3.4; Draine & Bertoldi 1996 eqs. 36–37]. "R14 3× stronger than DB96 at 10¹⁷" reproduced (8.8×10⁻⁴ vs 2.5×10⁻³) [recomp: S1; lit: Richings 2014 App. B] | – |
| 33 | "Run's constant ×400 out on every count" | **W** (overstated) | The project's own slab shows ×400 inside the accepted spread at median (0.380) and dense (0.919 vs 0.757–0.962) conditions; it fails at 38 cm⁻³ / 98 K and 806 K [recomp: S1]. Its shape is wrong at N_H2 ~ 10¹⁶–10¹⁷ cm⁻² (figure). N18 itself warns it is less accurate at high density and small A_V [lit: Nickerson 2018 §3.2]. The decisive defect is the bin split (#12), which the slab does not model | – |

---

## T4. Figures as evidence

Bar: a supervisor gets the point in 30 s. Only kept or redesign-worthy figures are graded.

| Figure | One idea? | Axes / units / scales | Colour scale stated? | Caption = plot? | 30 s? | Redesign instruction |
|---|---|---|---|---|---|---|
| `h2_605_why` | No (3 ideas) | (a) no snapshot or projection depth in panel; (b, c) fine; log axes | (a) log N(H2) 3–15 cm⁻², 12 decades, so single-cell 10⁻⁵ M☉ shows as red | Title (b) "nothing is molecular" fine | No | Keep panel (c) only, retitled "Injected H2 mass per star-hosting cell is constant (X·Δm)". Add the predicted X·Δm line from the mass-return rate. Move (a) to an appendix with the floor stated (≥ 10¹⁷ cm⁻²) |
| `temp_maps_605_vs_383` | Yes | Same 10–10⁸ K scale for panels 3–4; panels 1–2 auto-scaled | Yes | Yes | Yes | Add one histogram panel of T/μ with the 8,163–16,938 K band shaded |
| `shielding_models_compared` | Yes | Log–log, units given | n/a | "N18 boost ×400 (the run)" is **wrong**: the run boosts only 12–13.6 eV | Mostly | Relabel "N18 ×400 applied to whole LW band (the run applies it to 2/3 of the band)". Add a curve for the run's effective f = w₃·exp(−400σN) + w₂·1, with w₂ = group-2 LW photon share |
| `rt_fig3` | No (2) | No output number or region; y "volume-weighted mean c_r N" fine | n/a | Legend says group 3 = "Lyman-Werner"; it is 2/3 of LW | Partly | Keep left panel. Plot σ_i·c_r N_i (the destruction rate per group), not c_r N_i, so groups 2 and 3 are directly comparable. State output and centre |
| `rt_v2_fig1–3` | Fig 1 yes; 2 no; 3 no (four questions) | No output label; fig 3 mixes R_e and R_hm markers | Yes | "non-ionising 0.1–12 eV" merges the group that destroys H2 with IR | No | Drop from the H2 story. If kept, never merge groups 1 + 2; label output and z |
| `rt_v2_fig4` | Yes | Fine | Median log x_H2 | **Title asserts a physical trend that is the mass-return artefact** | Misleads | Retitle "Near star particles x_H2 is set by mass-return bookkeeping"; mask star-hosting cells and show the residual |
| Relaxation plot (not in repo) | No | y = τ, colour = log(c_r N + 1) ≈ y | – | – | **Failed** | Replace with T7 figure 3: t_F (x) versus t_D,all groups (y), log–log, diagonal t_F = t_D, colour = stored/equilibrium x_H2, marker size ∝ H2 mass |
| `final5` | No (4 relations) | Clear; M_V reversed | n/a | 605 R½ is face-on projected (199 pc) versus LVDB spherical; M_HI within R200c | Yes | Keep panel (d) only for context. Label the aperture and the HI definition in the legend. Use one M_V (−10.58 or −9.9, not both across documents) |
| `halo605_classification` | No (3) | x-axis mixes L_V and M★ ("M/L_V = 1") | n/a | M_V = −9.9 conflicts with notebook −10.58 | Yes | Merge with `final5`; drop the SFH panel or move it to the burst figure |
| `lvdb_ks_plane` | Yes | Aperture R26 stated | n/a | HI-only against a total-gas relation | Yes | Label "Σ_HI (no H2)"; drop the K98 line or plot it shifted. No 605 point until matched SFR and aperture |
| `lvdb_ks_aperture_free` | Two panels | Fine | n/a | **605 depletion line is wrong** (T3 #27) | Misleads | Plot 605 as SFR(100 Myr) upper limit, i.e. t_dep lower-limit arrow, at each output |

Not kept: `chk3`, `chk4`, `combo`, `final_fig`, `lvdb_ks`, `maps_compare`, `rt_fig1`, `rt_v2_fig2`.

---

## T5. Physics grounding of headline claims

| Headline claim | Literature verdict | Reference and paraphrase |
|---|---|---|
| Constant ×400 is defensible at 10–20 pc and low Z | **Disagrees as configured; untested at this Z and resolution** | N18 tuned ×400 against the Bialy et al. (2017) analytic transition (as quoted in N18) in 1D slabs (n = 1–10³ cm⁻³, 0.1–10 χ, 50 K, solar Z, spot checks at 0.1 and 10 Z☉), with **one LW group of 11.2–13.6 eV** [Nickerson 2018 §2.1, §3.2, Figs 5–6]. It is less accurate at high density and small A_V, and the low-Z case slightly overpredicts the molecular region. It is meant for galaxy cells of 10¹⁹–10²³ cm⁻² that become "entirely molecular" [§2.3.2]. EDGE2 splits LW across bins 2 and 3 [Rey 2025 §2.2]. The function shape at cell scale matters less than the split [recomp: S1] |
| 605's densities and fields cannot support much H2 | **Agrees** | Transition density n_t ≈ 30/Z′ cm⁻³, i.e. 250–750 at Z′ 0.12–0.04 (with clumping factor C_ρ = 10) [Gnedin 2009 eq. 7; recomp: B6], against max 17 at 119. The S14 transition column scales ~1/Z′ (≈1.25×10²¹ H cm⁻² at Z′ = 1 for 10 M☉ pc⁻² [recomp: B6]) [Sternberg 2014 §1, §4], against z = 0 max HI 2.7×10¹⁹. t_F ≈ 1/(n₁D) Gyr is 0.6–10 Gyr for n = 17–1 [Hu 2016 eq. 10]. Max f_H2 drops at Z ≲ 0.2 Z☉ because t_F exceeds dense-region lifetimes (5–15 Myr) [Polzin 2023 abstract, §4] |
| 605 at 119 has H2/H ≈ 2×10⁻³ | **Agrees** (order of magnitude) | Z′ = 0.1, D = 0.1, G0 = 1.7 dwarf with 2 pc resolution has F_H2 ≈ 5×10⁻⁴ (≈1.5×10⁻³ at G0/10); dense cold gas is HI-dominated; much H2 is warm and diffuse [Hu 2016 abstract, §4.3.1] |
| "Equilibrium is an upper bound" | **Disagrees as a general statement** | Polzin 2023 Table 2 (0.1 Z☉): model/sim ratios from 1/262 to 433. Hu 2016 §4.3.1: equilibrium only slightly above globally. Krumholz & Gnedin 2011: equilibrium and time-dependent agree for Z′ ≳ 0.01 |
| Group-2 LW photons are unshielded | **Agrees with code; physics says they should be shielded** | Lines from 11.2 eV self-shield together [Draine & Bertoldi 1996 §6; Sternberg 2014 §2.2]. N18's photon-destruction boost assumes one band [Nickerson 2018 eq. 33]. Public code applies it to whole-band groups only [file: rt_init.f90] |
| No clumping factor in formation | **Untested** | Gnedin 2009 eq. 3 uses C_ρ = 3–10 (fiducial 10, at ~50–65 pc cells). Nickerson 2019 omits it and finds H2 fraction 0.14 / 0.35 / 0.33 at 97 / 24 / 6.1 pc (solar disc) [Nickerson 2019 §3]. 605's 11–24 pc cells are inside that resolution regime. A low-Z resolution test does not exist |
| Mass-return H2 at z = 0 is an artefact | **Untested in literature; code-supported** | [file: pm/feedback.f90]. Rey 2025 §2.5: winds return mass continuously |
| H⁻ channel matters in warm gas | **Partly agrees** | MK10 App. A: k⁻ = 1.83×10⁻¹⁸ T^0.88 assumes negligible IR photodetachment; MK10 doubt the channel works in practice. N18 §2.3.1 adopts it |
| Expected CO at Z′ ≈ 0.04–0.12 | **Literature predicts CO-faint, compact CO** | α_CO ≈ 2.9 exp(0.4/(Z′Σ₁₀₀)): ≈ 81–6.4×10⁴ for Z′ 0.12–0.04 at Σ_GMC = 100 M☉ pc⁻² [Bolatto 2013 eq. 31; recomp: B6]. CO traces only high-column peaks below ~Z☉/2. Sextans A (7% Z☉): α_CO ≥ 700× MW [Shi 2015 abstract]. WLM (13%): CO clouds of ~2 pc radius [Rubio 2016]. Dwarfs at Z ≈ 1/2–1/10 have L_CO 2–4 dex below spirals [Schruba 2012]. Steady state overestimates diffuse H2 at low Z, so the CO-dark fraction is lower than steady state predicts [Hu 2021]. pc-scale X_CO drops to the MW value once dust shielding is effective, independent of Z [Hu 2022]. With CO in ≤ 2 pc clumps, an 11–24 pc cell model needs sub-grid structure [inf] |
| Leo P as comparison | **Not a fair comparison for outputs 119/125** | Leo P: 3% Z☉, one O star, SFR_Hα = 4.3×10⁻⁵ M☉ yr⁻¹; warm H2 within ~4.4 pc of the O star (χ ≈ 150 Habing), radius ≤ 2.6 pc; N ≥ 6.5×10¹⁷ cm⁻² (420 K); M_H2 ≥ 1.4 M☉ (420 K) or ≥ 1.1×10⁴ M☉ (80 K); ALMA CO limit allows ≤ 1.2×10⁴ M☉ at α_CO = 285 [Telford 2025, Table 1, Methods]. FINDINGS' Leo P numbers are verified. 605 has no star younger than 106 Myr at either output, and the PDR scale is below one cell. Leo P bounds span four decades in mass, so "gap is concentration, not amount" is unconstrained. Fair only against a burst output with stars younger than 10 Myr |
| Star formation needs H2 at this Z | **Literature says no** | Star formation can proceed in cold atomic gas; shielding, not chemistry, controls it [Glover & Clark 2012 abstract; Krumholz 2012 abstract]. EDGE2 SF does not use H2 [Rey 2025 §2.4]. The project should not use H2 as an SF proxy |

---

## T6. Ranked gap analysis (scientific value per effort)

| Rank | Analysis | First step | Inputs | Done when | Risk |
|---|---|---|---|---|---|
| G1 | **Code confirmation** (hours) | Grep the EDGE2 fork for the `ssh2`/`isLW` band test, the output routine, and ion-scalar handling in winds/SN/AGB mass return (§V 1–3) | EDGE2 source or Dr Rey | Yes/no on three mechanisms, with line numbers | Source not shared; then ask Rey with the public line numbers |
| G2 | **One measurement function** (1–2 days) | `measure(snapshot, aperture)` returning M_HI, M_H2 = 2x_H2·X·M_gas, T via per-cell μ, artefact mask (star-hosting cells, or deficit from mass-return rate) | Existing notebooks | Every table in the write-ups regenerated by one call; factor-2 and μ bugs gone | Low |
| G3 | **Burst outputs and tracers** (days) | List `output_0012[0-4]`; load each; H2 by n_H, T, r, d★(< 10 Myr) | Outputs 120–124; tracer dumps every 4.5 Myr (ρ, P) [lit: Rey 2025 §2.7] | H2 mass and phase versus time with SFR₁₀; tracer-integrated x_H2 versus stored within a stated factor | Outputs not retained; disk; tracers lack radiation, so γ must be interpolated from 100 Myr outputs |
| G4 | **Group-2 sensitivity, time-dependent** (days) | Rerun Phase A in time-dependent mode with group-2 LW shielded like group 3 | Phase A code; f_LW in group 2 from G1 | Bracket on how much H2 the leak removes at 119 and in the burst | Interpretation needs Rey's view on intent; a re-simulation with a group edge at 11.2 eV is the only definitive test |
| G5 | **Other haloes** (days–weeks) | Same pipeline on 600 (rejuvenator), 624 (gas-rich relic), 383 (BPASS, dense) | Snapshots on the machine | H2 fraction versus M★, Z′, SFR at ≥ 3 outputs each | Different SED (383 BPASS) |
| G6 | **Resolution / sub-grid bracket** (days) | Post-process with formation × C_ρ for C_ρ = 1, 3, 10 [lit: Gnedin 2009 §2.2]; apply the Polzin 2023 volumetric fit at 10–100 pc | G2 outputs | M_H2 range versus C_ρ; agreement with the Polzin fit (calibrated to 0.01 Z☉, ~10 pc cells) | Degenerate with the time dependence |
| G7 | **CO model (Q4)** (1–2 weeks) | CLOUDY slab grid: Z′ 0.04–0.12, n 1–10³ cm⁻³, G0 0.01–100, N_H ≤ 10²² cm⁻² → CO/H2 and L_CO per column. Cross-check with Bolatto eq. 31 and Hu 2022 | CLOUDY (on project machine) | Predicted L_CO per output with α_CO bracket | Sub-grid ≤ 2 pc clumps dominate CO; per-cell CO may be meaningless without a clump model |
| G8 | **Fair observational comparison** (days) | Table of dwarfs with M★ 10⁶–10⁷·⁵ M☉ and Z′ 0.03–0.15 with H2/CO data: Leo P [Telford 2025], Sextans A [Shi 2015], WLM [Rubio 2016], Sextans B, CARMA limits [Warren 2015], HERACLES dwarfs [Schruba 2012] | Papers (opened) | Compare L_CO (observable), not "H2"; 605 predictions overlaid | Few objects resemble a quiescent dSph-like 605 |
| G9 | **LVDB clean-up** (hours) | Drop `lvdb_ks.py`/old CSV; name-check matches over 1′; 605 as an SFR upper limit | Notebook | One aperture-free figure | Low; low value for H2 |

---

## T7. Recommendations

### T7.1 Keep / merge / retract / delete

| Item | Action | Why |
|---|---|---|
| c7ee write-up | **Keep** as the z = 0 record; add retractions below | Superset |
| f5, f6 (earlier versions) | **Delete** | Strict subsets of c7ee |
| `halo605_119_vs_125.md` | **Retract** temperatures and radiation ratios; **merge** surviving text into the burst notebook write-up | Pre-fix temperature; superseded estimators |
| `shielding_model_comparison.md` | **Keep**, with corrections (§T7.2 items 4–5) | Useful function survey |
| `halo605_classification.md` + `halo605_classification.png` | **Merge** into one context section with `final5` (d); fix M_V/R_e to one definition | Inconsistent photometry |
| `bearings-605-HI-review.md` | **Keep** (methods appendix) | Unit errors are real and documented |
| corpus-tooling ×2 | **Delete** from the science record | Tooling |
| `slab_compare.py` | **Keep**; add the effective "run" function (w₂, w₃) | Reproducible |
| `lvdb_ks.py`, `data/lvdb_kk13_matched.csv`, `lvdb_ks.png` | **Delete** (superseded) | Old aperture, unreconciled distances, unconstrained points plotted |
| `lvdb_tools.py` | **Keep**; delete `load_koplitz_fig2`/`plot_koplitz_fig2` | Retracted material |
| `lvdb_scaling_relations.ipynb` | **Keep**; fix cell 52 (2x_H2) | Factor-2 error |
| `chk3`, `chk4`, `combo`, `final_fig` | **Delete** | Superseded by `final5` |
| `maps_compare`, `rt_fig1`, `rt_v2_fig2` | **Delete** | Pre-fix or no claim |
| `rt_v2_fig4` | **Retract title**; keep as artefact evidence | Misleading |
| `rt_fig3` | **Keep** left panel, redesigned (σ·c_r N) | Only figure separating groups 2 and 3 |

### T7.2 Statements to mark retracted, with the mechanism that made them wrong

1. v1/de64 short answer 2: "No shielding model could make H2 here." Already corrected in §6, but §6's replacement bound ("20–200 M☉ with perfect shielding") is also wrong. **Mechanism:** dust-only formation, ignoring the run's H⁻ channel.
2. "Nothing is colder than 3,500 K"; "densest cell 8,200 K"; §1 temperature percentiles. **Mechanism:** unknown estimator before the μ fix; superseded by §6 (per-cell μ).
3. `halo605_119_vs_125.md`: "minimum temperature 4,800 K" at 125. **Mechanism:** pynbody crude-μ floor (4,819 K).
4. Shielding write-up §3.1 / FINDINGS §4: "constant ×400 out on every count." **Mechanism:** judged on the function shape against slabs, while the project's own slab shows cell-scale agreement at median conditions. The real defect is the bin split.
5. Shielding write-up §5: "equilibrium models over-predict … by ~30× (S14) to ~400× (GD14)" presented as general. **Mechanism:** selective quotation of Polzin Table 2.
6. FINDINGS §1.3 (383): "proposed cause: the fixed ×400 boost." **Mechanism:** confounders (time, group-2 leak) not separated.
7. FINDINGS §1.7: "Hu et al. 2015 eq 11." **Mechanism:** equation mislabelled; eq. 11 is the destruction time.
8. FINDINGS §2: "orange line at 100 K is not a ceiling (α_Z falls to 0.04×)." **Mechanism:** the reason is inverted. α_Z peaks at 168 K, only 5% above its 100 K value, so 100 K is nearly a dust ceiling [recomp: B5]. It is not a total-formation ceiling because of H⁻.
9. `lvdb_scaling_relations.ipynb`: M_H2 = 2.31 M☉. **Mechanism:** x_H2 counted as a hydrogen mass fraction.
10. Halo 605 point and depletion line on the KS / t_dep figures. **Mechanism:** a 200 Myr SFR used where the 100 Myr SFR is zero.
11. `rt_v2_fig4` title. **Mechanism:** mass-return artefact read as physics.
12. Classification write-up and `halo605_classification.png`: M_V = −9.9, R_e = 241 pc. **Mechanism:** different V-band model from galaxy.json and the notebook (−10.58). Not wrong per se, but must not coexist unlabelled.

### T7.3 Proposed figure narrative (defensible today plus G1–G4)

| # | Claim | Must show | Axes / scales | Source |
|---|---|---|---|---|
| 1 | H2 in 605 appears only when dense gas exists, i.e. around bursts | Time series: M_HI, M_H2 (artefact-masked), SFR over 10 Myr, max n_H, outputs 119–125 | x: cosmic time [Gyr]; y: log mass [M☉], log SFR [M☉ yr⁻¹], log n_H [cm⁻³]; shared x | `burst_compare.ipynb` extended (G3); today only 119 and 125 |
| 2 | Where H2 sits | n_H–T plane weighted by H2 mass at 119 (and burst outputs), with lines: SF threshold (n_H 228, T 1000 K), Gnedin n_t(Z′), refinement thresholds | log n_H 10⁻³–10³; log T 10–10⁵ K; fixed colour limits across outputs | New (G2) |
| 3 | What limits H2: formation time versus destruction | t_F = 1/(2A) versus t_D = 1/γ_all per neutral cell; diagonal; colour = stored/equilibrium x_H2 | log–log [Myr], 10⁻¹–10⁵; diverging colour, ±2 dex fixed | Replaces the relaxation plot (`h2_relaxation.ipynb`) |
| 4 | Which photons destroy H2, and why group 2 dominates | Share of γ by group versus n_H (binned, stacked), unshielded versus actual; inset: code band test | x: log n_H; y: share 0–1 | `group2_check` report → figure |
| 5 | How much H2 the modelling choices could add | Horizontal bars: M_H2 at 119 for stored; equilibrium with run law; group 2 shielded; DB96; R14; time-dependent along tracers; C_ρ = 10 | log M_H2 [M☉], 10²–10⁶ | Phase A + G3, G4, G6 |
| 6 | z = 0 H2 is bookkeeping (methods) | H2 per star-hosting cell versus host-cell mass, with the predicted X·Δm line | log–log [M☉] | `h2_605_why` panel (c) |
| 7 (after G7) | CO would be undetectable or detectable | Predicted L_CO per output with α_CO bracket against ALMA limits for Leo P, Sextans A, WLM | log L_CO [K km s⁻¹ pc²] | CLOUDY grid |
| 8 (optional context) | 605 among real dwarfs | M_HI versus M_V and t_dep (SFR limits as arrows) with consistent apertures | As `final5` (d) and aperture-free | `lvdb_analysis.ipynb` |

---

## U. Unresolved and guessed

1. The EDGE2 fork is not public. Every code-based statement (×400 band test, output convention, mass return without ion scalars, H⁻ rate) is verified on **public RAMSES only**.
2. Outputs 120–124 existing is a guess from Rey 2025's ~100 Myr cadence and the output numbering [inf].
3. The group-2 shares of unshielded dissociation (19–41%) use c_r N values I read by eye off `rt_fig3.png`, a figure with no output label. They are order-of-magnitude only.
4. "Group 3 covers 30–60% of the LW band" (FINDINGS) is not reproduced; by energy width it is 67%, and the photon share is SED- and attenuation-dependent.
5. Origin of "nothing colder than 3,500 K" and "8,200 K" in the earliest write-up: estimator unknown.
6. Whether `burst_compare.ipynb`, `h2_relaxation.ipynb`, Phase A and the group-2 check use pynbody `temp` or per-cell μ: unknown.
7. Why 3.2×10⁻⁴ lies below the quoted BC03 range: unresolved (SED_dir, metallicity, wavelength-grid integration).
8. Z′ of 605's ISM: three values in the repo; the brief's 0.075 is not traceable.
9. Whether the stored dense-gas x_H2 at 119 is below equilibrium ("slope 0.77, median ratio 1.8") at the densest cells: [rep], not checkable.
10. The H⁻ channel's physical relevance (photodetachment by groups 1–2) is not quantified.
11. The match `PGC 100170 ↔ Dw1` (0.56′) is not name-verified; it is probably correct but unchecked.
12. Hu "2015" versus "2016": I assume the project means arXiv:1510.05644 (posted 2015, MNRAS 2016); its p.24 quote ("hostile environment") is in its §5 summary.
13. The "Shi et al. 2020 (Sextans A)" paper named in the brief was not found on arXiv by author/title search; I used Shi et al. 2015 (arXiv:1504.01453) instead.
14. "Bialy et al. 2017" is cited only as quoted inside Nickerson 2018 §3.2; I did not open it.
15. The project machine was unreachable (Tailscale address, no SSH client), so no [rep] number was re-read.

---

## R. What I recomputed (exact commands)

Interpreter: `/usr/bin/python3` 3.13.16, numpy 2.5.3, pandas 3.0.5. Run from the repo root.

| Code | Command | What it checks |
|---|---|---|
| S1 | `python3 -I scripts/slab_compare.py` | Slab f_H2 table (all six cases) and f_shield values; reproduces `shielding_model_comparison.md` §4 exactly |
| L1 | `python3 -I audit/lvdb_checks.py` | Match stats, name mismatches, recomputed Σ and t_dep (max diff 1.8×10⁻¹⁵ dex), sample sizes (196 / 136), limit bookkeeping (28 double limits), 605 provisional point (log t_dep 8.850 vs observed min 8.92) |
| B1–B8 | `python3 -I audit/backofenvelope.py` | B1 H2 factor 2 (2.003). B2 pynbody μ band 8,163–16,938 K and floor 4,819 K. B3 σ_2/σ_3 = 3.16×10⁻⁴, LW width share 0.667, unshielded group-2 share 0.19–0.40, σ from S14 = 2.07×10⁻¹⁹. B4 per-cell τ_3. B5 α_Z peak 168 K, t_F dust versus H⁻. B6 SF threshold n_H 228, Gnedin n_t, Bolatto α_CO, S14 column. B7 refinement thresholds. B8 ratios, SFR, M_V ratio, Z′ from O/H |
| G1 | `git clone --depth 1 --filter=blob:none --sparse https://github.com/ramses-organisation/ramses && git -C ramses sparse-checkout set rt pm hydro && grep -n "ssh2\|isLW" ramses/rt/*.f90` | Band test (rt_init.f90 L366-373); photoRate sums all groups (rt_cooling_module.f90 L650); σ_H2 definition (rt_spectra.f90 L192); SED averaging (L738-756); α_Z, α_GP (coolrates_module.f90 L263-274); output ×rt_c (rt_output_hydro.f90 L99-104); feedback mass injection (pm/feedback.f90 L436-455); ion scalars ρ·x (rt_init_xion.f90 L113) |
| P1 | `git clone --depth 1 --filter=blob:none --sparse https://github.com/pynbody/pynbody && grep -n "crude\|def mu\|_rt_unit\|issue 542" pynbody/pynbody/derived.py pynbody/pynbody/snapshot/ramses.py` | μ fallback, temp iteration, RT unit label and warning |
| inline | Arithmetic quoted in T3 #1: γ = 2.1×10⁻¹⁹ × (10³–10⁵) s⁻¹, so 1/γ = 1.5–150 Myr | Photon-unit sanity |

---

## V. Checks to run on the project machine (it was unreachable from here)

1. `grep -n "ssh2\|isLW\|11.2" <ramses-edge2>/rt/rt_init.f90 <ramses-edge2>/rt/rt_parameters.f90`: is the ×400 limited to groups inside 11.2–13.6 eV?
2. `grep -n "iIons\|mloss\|uold(.*,1) *= *uold(.*,1) *+" <ramses-edge2>/pm/*.f90`: do wind, AGB and SN mass returns update the ρ·x ion scalars?
3. `grep -i photon <sim>/output_00119/*file_descriptor*.txt` and `head -40 <sim>/output_00119/info_rt_00119.txt`: output convention; per-group csn; rt_c_frac per level.
4. `ls -d <sim>/Halo605_RT/output_001[1-2]?` and `ls <sim>/Halo605_RT/output_00119 | grep -i tracer`: do outputs 120–124 and tracer files exist?
5. `grep -n "\[\"temp\"\]\|'temp'\|def .*mu\|x_H2\|M_H2" ~/data/B8_MolecularGas/Sonny/605/*.ipynb`: which notebooks use pynbody `temp` and which H2 mass convention.
6. In `group2_check/report.md`: recompute the destruction shares restricted to cells with n_H < 0.1 (unshielded); they should approach the 20–40% estimated here.

---

## S. Sources opened

**Literature (arXiv full text):**
- Nickerson, Teyssier & Rosdahl 2018 (1802.00445); Nickerson et al. 2019 (1809.01657)
- Rey et al. 2025 (2503.03813); Rey et al. 2020 (2004.09530); Rey et al. 2022 (2112.03280)
- Hu et al. 2016 (1510.05644); Hu et al. 2017 (1701.08779); Hu et al. 2021 (2103.03889); Hu et al. 2022 (2201.03885)
- Gnedin, Tassis & Kravtsov 2009 (0810.4148); Gnedin & Kravtsov 2011 (1004.0003); Gnedin & Draine 2014 (1406.4129)
- Sternberg et al. 2014 (1404.5042); Bialy & Sternberg 2016 (1601.02608)
- Draine & Bertoldi 1996 (astro-ph/9603032); Richings, Schaye & Oppenheimer 2014 (1403.6155); Wolcott-Green et al. 2011 (1106.3523)
- Ploeckinger & Schaye 2020 (2006.14322); Polzin et al. 2023 (2310.10712)
- Krumholz & Gnedin 2011 (1011.4065); Krumholz 2012 (1208.1504); Krumholz et al. 2009 (0811.0004); McKee & Krumholz 2010 (0908.0330)
- Glover & Clark 2012 (1105.3073); Glover & Mac Low 2011 (1003.1340)
- Telford et al. 2025 (2410.21368); Bolatto, Wolfire & Leroy 2013 (1301.3498); Shi et al. 2015 (1504.01453)
- Schruba et al. 2012 (1203.4231); Schruba et al. 2017 (1701.02748); Rubio et al. 2016 (1603.04736); Warren et al. 2015 (1510.03518)
- Madden et al. 2020 (2009.00649); Cormier et al. 2014 (1401.0563); Leroy et al. 2011 (1102.4618)
- Gong et al. 2018 (1803.09822); Gong et al. 2020 (2009.14631)
- Rosdahl et al. 2013 (1304.7126); Katz et al. 2017 (1612.01786)
- Putman et al. 2021 (2101.07809); Pace 2024 (2411.07424); Karachentsev & Kaisina 2013 (1305.4791)

Downloaded but not used as evidence: Bialy & Sternberg 2016; Ploeckinger & Schaye 2020; Schruba et al. 2017; Madden et al. 2020; Cormier et al. 2014; Leroy et al. 2011; Gong et al. 2018, 2020; Katz et al. 2017.

**Code:**
- RAMSES (public) @ `51123de`: `rt/rt_init.f90`, `rt/rt_parameters.f90`, `rt/rt_cooling_module.f90`, `rt/rt_spectra.f90`, `rt/coolrates_module.f90`, `rt/rt_output_hydro.f90`, `rt/rt_init_xion.f90`, `pm/feedback.f90`, `hydro/cooling_fine.f90`.
- pynbody @ `0259c38`: `pynbody/derived.py`, `pynbody/snapshot/ramses.py`.

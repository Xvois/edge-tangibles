# FINDINGS: consolidated project record (as of 2026-10-15)

Source: the project's shared memory and thread reports. **Nothing here has been independently re-verified by the compiler.** Claim tags: [read] from a file or source, [measured] computed on the project machine by a thread, [reported] thread said so, not re-read, [inferred] reasoning only, [open] unresolved. Where a number comes from a thread report rather than an artefact in this repo, it is marked [reported]; the underlying files live on the project machine (see README "Not included").

Project: use the EDGE2 simulation suite (RAMSES-RT, Rey et al. 2025) to find where molecular hydrogen (H2) sits in dwarf galaxies and under what conditions it forms; stretch goal: relate CO emission to H2 for comparison with ALMA.

## 0. Run setup (halo 605 unless stated)
- Halo 605, outputs 119 (z=0.0526, 13.070 Gyr) and 125 (z=0, 13.802 Gyr), 732 Myr apart. [read from namelist/info files by threads]
- Radiative transfer: BC03 SED (not BPASS), SN feedback on (eta_sn 0.1, 1e51 erg), rt_c_fraction 0.01, rt_esc_frac 1, Faucher-Giguere 2020 UV background (whether it is inside the RT groups: [open], the UV file is not on our machines).
- H2 chemistry: Nickerson et al. 2018 model. Self-shielding is a constant ~x400 boost on LW absorption by H2 (from the paper; the ramses-edge2 source was NOT available to check). Formation uses the cell-mean density with no clumping factor. Dust LW shielding only via RT dust opacity kappaAbs=1e3 cm^2/g.
- RT photon groups (run's info_rt): 1 = 0.1-1 eV, 2 = 1-12 eV, 3 = 12-13.6 eV (treated by Sonny as the run's Lyman-Werner band; Rey et al. 2025 sec 2.2 as relayed: six bins, group 2 radiation pressure, group 3 dissociates H2), 4-6 ionising. Group 3 covers only 30-60% of the physical 11.2-13.6 eV LW band.
- Grid: finest cells ~11.3 pc at output 119 (13-50 pc range). R_e (V-band half-light) = 271-278 pc. pynbody issue 542: RAMSES radiation is in flux units, ratios safe, absolute values caveated.
- Survey files (galaxy.json etc.) hold half-mass radii, masses, SFR etc.; they are not in this repo.

## 1. Settled-ish results
1. **pynbody `temp` bug** [read/measured]: pynbody looks for HI/HII arrays but the run stores x_HI/x_HII, so `temp` falls back to a crude mu (0.59 above 1e4 K, 1.22 below), flipping cells between 8,200-16,900 K. Fix: per-cell mu (see writeups/why-the-h2-plots-look-like-that-605*.md section 7). QUESTION FOR AUDITOR: which figures/numbers were produced before vs after the fix (the repo files temp_maps_605_vs_383.png and early write-ups are dated 2026-10-03).
2. **Halo 605 at z=0 has almost no H2** [measured, write-up 2026-10-03]: 4.6 Msun in R200c; no gas below 1,000 K; minimum T/mu 7,690 K; max n_H 0.06 cm^-3; even perfect shielding gives only 20-200 Msun. Far-out blotches sit on single 13 Gyr star particles (hypothesis: stellar-wind return mass booked as H2; to ask Dr Rey) [open].
3. **Stand-in halo 383 (BPASS, output 129, z=0.136)** [reported, 2026-09-28]: run stores 46 Msun H2; shielded equilibrium post-processing gives ~3.9e5 Msun (2.7-4.4e5), ~70% of dense H, in compact clumps in the central ~kpc, cold (<300 K), G0 ~0.3. Proposed (not proven) cause: the fixed x400 boost.
4. **Dwarf classification of 605** [read: writeups/halo605_classification.md]: between dSph and HI-poor transition dwarf (Phoenix, LGS 3, Tucana analogues).
5. **Burst comparison, outputs 119 vs 125, inside R_e** [reported from notebook burst_compare.ipynb, not in repo]: gas 9.1e5 -> 5.1e4 Msun; HI 6.6e5 -> 1.2e4 (~53x down); HII ~1.1x up; H2 1535 -> 1.6 Msun (~990x down); max n_H 17 -> 0.06 cm^-3; gas below 1000 K 51% -> 0%; median T 915 -> 1.07e4 K. Whole halo: M_HI 8.81e5 -> 5.18e4, M_H2 1548 -> 4.6 Msun (do not mix with R_e values).
   - Radiation (line of sight): ionising volume mean x29 (median +1.12 dex down z); LW x8.3 (+0.80 dex). Per-pixel HI change vs ionising change r = -0.76 (down z).
   - New stars between outputs: 113 stars, 33,900 Msun at birth, born +37 to +625 Myr after 119, birth n_H 400-1740 cm^-3 (SF threshold 300). Bursty: peak 25-Myr bin 14.5x mean SFR, 73% of mass in 3 of 30 bins. At 125 they sit in hot ionised gas (median n_H 0.007, T 1.2e4 K). Unexplained: 112 vs 113 new stars in R_e.
   - Gas lost at all radii out to 30.7 kpc (total -3.06e6 Msun); expulsion outward NOT shown.
   - Verdicts on the story "harsh dwarfs hostile to SF and H2": H2 and gas-supply loss supported; radiation depleting HI consistent but cause not shown; SF expelling gas not shown; "long-term" not shown; SN feedback degenerate with radiation. Open: no output near the burst (~13.4-13.7 Gyr).
6. **Radiation source curves** (burst_sed.ipynb, not in repo) [reported]: ionising source in R_e flat (1.73e47 to 1.75e47 /s), peak 2882x the 125 rate; LW (group 3) source x4.0 (1.216e47 -> 4.960e47 /s); field per unit source: ionising x29, LW x2.1, so stars cannot explain the ionising rise; thinner gas fits best; outside sources/background look the same. Source curves use raw BC03 (not proven identical to the run's SED_dir).
7. **H2 formation time** (Hu et al. 2015 eq 11, rough) [reported]: share of R_e gas that could form H2 within 106 Myr / 732 Myr / 13.8 Gyr = 0 / 4.9 / 60.2% at 119 and 0% at 125.

## 2. H2 relaxation-time plot review (supervisor could not read it) [reported]
Notebook h2_relaxation.ipynb (not in repo), output 119, 10 kpc: tau = 1/(2A + gamma) vs n_H for neutral cells (x_HI>0.5, n_H>0.1), coloured by log10(c_r N_LW + 1). Rates are the run's own Nickerson et al. 2018 equations, not Hu et al. eq 11.
- Colour repeats the y-axis (gamma >> 2A so tau ~ 1/(sigma c_r N)): main reason the plot reads as meaningless.
- tau does not use x_H2, so no H2 precision limit enters; all float64; equilibrium x_eq ~ 1e-4.
- gamma uses LW group 3 only; the run also dissociates in groups 2, 4, 5, 6 (halo 383: group 2 was 52% of gamma).
- Orange "formation alone" line at 100 K is not a ceiling (alpha_Z falls to 0.04x at 6600 K).
- Diffuse branch destruction-limited (3-30 Myr); dense branch n_H>2 formation-limited at 300-1000 Myr (10-50 t_ff). "Half the gas in equilibrium" is only diffuse gas.

## 3. Why 605's H2 has no clumps (clumpiness review) [reported, Phase A]
Sonny's question: why is the simulated H2 field smooth and tracking gas density when observed H2 clumps; can the run's shielding model make clouds where better models would. 10-20 pc grid cannot resolve 1-10 pc clouds; plan: compare broad shielding methods first, CLOUDY later.
- Leo P H2 clump (Telford et al. 2025, verified quote on project machine): radius <=2.6 pc, ~150 Habing, warm N(H2) >=6.5e17 (420 K) to 5.2e21 cm^-2 (80 K), M(H2) >=1.4 to >=1.1e4 Msun; ALMA CO not detected. 605 at 119 has 1.5e3 Msun H2 in R200c: gap is concentration, not amount. 605 has no star younger than ~100 Myr at 119/125, a different regime.
- Step 1 (9,175 neutral cells inside R_e at 119, all at the finest level): x_H2 ~ n_H^1.26; stored x_H2 vs run's local equilibrium: slope 0.77, scatter 0.57 dex, median ratio 1.8. Output 125 has no neutral cells with n_H>0.1 inside R_e, so no control.
- Phase A shielding comparison: the run's law gives ~1.7e3 Msun H2, same as no shielding; shielding group 2 the same way gives 1.05e5 Msun with a sharp step; column-based methods give 3.3-4.2e5 Msun (also steps). After 33 Myr / 100 Myr / free-fall time no method gets any gas above half molecular; dense-cell formation times 870-1750 Myr. Smaller slabs (11.3 -> 1 pc) LOWER f_H2 (less column). Conclusion: cells lack density, not size. Not claimed: that the run is wrong.
- **Group-2 question** [independent check, report.md on project machine]: group 2 (1-12 eV) gives 70.3% (sum) / 81.4% (median) of summed H2 destruction at 119; group 3 26.8% / 16.1%. Cross-sections: group 2 6.635e-23 cm^2, group 3 2.100e-19 cm^2 (column order inferred from ionisation thresholds, not read from source). Group 2 is not attenuated in thick cells (ratio 1.03); group 3 drops ~37x. Coordinator inference: 6.6e-23/2.1e-19 = 3.2e-4 = fraction of group-2 photons in 11.2-12 eV, so the ~70% is LW photons that miss the x400 shielding. BC03 spectra give 4.7e-4 to 4.5e-3 for ages >=1.7 Gyr, so the cross-section is if anything low. Applying a Draine & Bertoldi (1996) term to group 2 alone cuts its share to 40-51%. **Single question awaiting Dr Rey:** is it intended that x400 and dust shielding do not apply to group 2's H2 absorption? [open]

## 4. Shielding-model recommendation (2026-10-01) [read: writeups/shielding_model_comparison.md]
Three separate choices: (A) equilibrium vs time-dependent (recommend time-dependent for headline, equilibrium as upper bound); (B) column estimator (keep ray-tracing, 12 directions); (C) self-shielding function: Richings et al. 2014 T-dependent fit with Draine & Bertoldi 1996 as bracket, CLOUDY slab check pending. Run's constant x400 (Nickerson et al. 2018) judged out on every count. Pending: CLOUDY slab at 0.06 Zsun and re-running the real-gas solve.

## 5. Observational context (LVDB) [read: lvdb_*.py, notebooks]
Local Volume Database (LVDB) + Karachentsev & Kaisina 2013 (KK13) + UNGC (Updated Nearby Galaxy Catalog) joined to compare 605 on Kennicutt-Schmidt-like planes. LVDB+UNGC has NO H2 measurements. Sonny's rule: when asked "can we plot X with the current data", answer yes/no first; never substitute outside data. The Koplitz et al. 2026 (arXiv:2610.06662) Figure 2 reproduction was built from points read off a paper figure; Sonny had it reset; it is excluded from this repo and should be treated as retracted.

## 6. Open questions (consolidated)
1. Group 2 vs group 3 in H2 destruction: is the unshielded group-2 LW slice intended? (Dr Rey)
2. Is the FG2020 UV background inside the RT groups?
3. Single halo (605) and two snapshots; no snapshot near the burst (~13.4-13.7 Gyr); haloes 600/624 not analysed.
4. Equilibrium vs time-dependent: all post-processing so far is equilibrium or rough timescale; the run itself is non-equilibrium with ~870-1750 Myr formation times in dense cells.
5. Origin of far-out H2 blotches on old star particles.
6. 112 vs 113 new stars in R_e.
7. Why ionising field per unit source rises x29 between 119 and 125.
8. CO/alpha_CO stretch goal: NOT started (CLOUDY c25 is built on the project machine).
9. Sample selection: R_e (~275 pc) vs R200c vs whole halo mixed across documents; whole-halo vs R_e values must not be compared.
10. Temperature: which results used per-cell mu.

## 7. Standing project rules that shape the work (from the PI, Sonny)
Read-only on a collaborator's code (excluded from this repo); never substitute outside data when the project data cannot support a plot; one idea per figure, identical colour limits in comparisons; short notebooks; claims must be grounded in the literature corpus; push back on poorly reasoned requests.

## 8. Literature referenced (links only, open them yourself)
Nickerson et al. 2018 (RAMSES-RT H2 model); Rey et al. 2025 (EDGE2); Hu et al. 2015; Gnedin, Tassis & Kravtsov 2009; Sternberg et al. 2014; Draine & Bertoldi 1996; Richings, Schaye & Oppenheimer 2014; Ploeckinger & Schaye 2020; Polzin et al. 2023; Telford et al. 2025 (Leo P); Bolatto, Wolfire & Leroy 2013 (alpha_CO); Shi et al. 2020 (Sextans A); Koplitz et al. 2026 (arXiv:2610.06662). Not in the project corpus: Warren+2015, Glover & Clark 2012, Krumholz 2012, Gnedin & Kravtsov 2011, Krumholz & Gnedin 2011, Hu+2016, Rollig+2007, Katz+2017, Le Petit+2006.

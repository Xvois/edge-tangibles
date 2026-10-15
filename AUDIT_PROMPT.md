# AUDIT BRIEF: scientific audit of the "H2 in EDGE2 dwarf galaxies" project

You are an independent, senior reviewer (astrophysics: ISM chemistry, radiative transfer, galaxy simulations). You have this repository only. Your job is to decide what in it is **accurate** and **scientifically meaningful**, and what would make it defensible. Be sceptical and concrete. You are not here to praise or to tidy; the owner (a student, "Sonny") will present the result to a supervisor.

## Rules
1. Read first: `README.md`, `FINDINGS.md`, `THREADS.md`, then everything under `writeups/`, `scripts/`, `notebooks/`, `figures/`, `data/`. Open every figure (view the image). Read notebook code and outputs.
2. You may recompute anything that the files here allow (e.g. `data/lvdb_kk13_matched.csv`, notebook code, back-of-envelope physics). Name the exact command and interpreter for every number you compute. Most simulation numbers cannot be recomputed; grade those for plausibility, internal consistency and bounds (e.g. compare against an independently computed ceiling or floor) and name the single test that would confirm or overturn each.
3. **Literature:** open the papers yourself (arXiv/ADS/DOI) and ground every physics judgement. Never cite a paper you have not opened. Never supply a physics value from memory. Do not paste long quotes; paraphrase and cite author + year + link/section. Papers to consult at minimum: Nickerson et al. 2018 (RAMSES-RT H2 model, x400 self-shielding), Rey et al. 2025 (EDGE2 run and RT bins), Hu et al. 2015 (and 2016), Gnedin, Tassis & Kravtsov 2009, Sternberg et al. 2014, Draine & Bertoldi 1996, Richings, Schaye & Oppenheimer 2014, Ploeckinger & Schaye 2020, Polzin et al. 2023, Telford et al. 2025 (Leo P), Bolatto, Wolfire & Leroy 2013 (alpha_CO), Shi et al. 2020 (Sextans A), Krumholz and Gnedin on H2 in galaxies, Glover & Clark 2012. Add others if they help.
4. Do not modify anything except by adding `audit.md` (and optional small helper scripts under `audit/`). Do not invent data. If an input is unusable, say it is a blocker; do not substitute another quantity.
5. Tag every claim: [read from file] / [recomputed here: command] / [literature: author+year] / [reported, unverifiable here] / [inferred]. Give units and precision for every number. Define every symbol and expand every acronym at first use. Print small numbers in scientific notation. Name what you could not resolve and where you guessed; that list is part of the deliverable. Answer in English.
6. Do not restate how impressive the work is. Lead with problems.

## Tasks (in order)

**T1. Question tree.** Restate the goal as a small tree of concrete, answerable scientific questions, with sub-questions, e.g.: Q1 where does H2 sit in the dwarfs (radius, density, temperature, phase, relative to young stars)? Q2 what conditions (density, metallicity, LW field, shielding, dust, time since star formation, formation timescale) are necessary and sufficient for H2 to form and survive? Q3 how much of the answer is physics versus simulation artefact (resolution of 10-20 pc cells, six-bin RT, constant x400 self-shielding, cell-mean formation with no clumping factor, photon-group assignment)? Q4 how would H2 map to CO (X_CO / alpha_CO, CO-dark gas, metallicity dependence) for ALMA comparison? Refine or add questions if the literature argues for better ones, and say why. State what result would count as an answer to each.

**T2. Inventory and map.** For every file in the repo, and every result in FINDINGS.md / THREADS.md, give: the question it serves, the single claim it supports, and a label ESSENTIAL (directly answers a question) / SUPPORTING (needed context or check) / TANGENTIAL (correct but does not advance the goal) / NOISE (no claim, duplicate, superseded, unreadable). Flag duplicates and superseded versions explicitly (e.g. `rt_fig*` vs `rt_v2_fig*`, `final5` vs `final_fig`, `chk3/chk4/combo`, the three write-up versions, the older burst write-up vs the notebook findings). Deliver as one table.

**T3. Accuracy audit** of all ESSENTIAL and SUPPORTING items. Check at least:
- units and conventions; photon-flux units in RAMSES-RT (pynbody issue noted in FINDINGS), conversions, mu and temperature;
- sample selection: R_e (about 275 pc) vs R200c vs whole halo mixed across documents (e.g. H2 1535 -> 1.6 Msun inside R_e but 1548 -> 4.6 Msun whole halo);
- the pynbody `temp` / mean-molecular-weight bug: which results and figures were produced before vs after the per-cell mu fix, and what changes if mixed;
- RT photon groups: is group 3 (12-13.6 eV) really the run's LW band; is the 70% group-2 share of H2 destruction physical (the cross-section of 6.6e-23 cm^2 for group 2 vs 2.1e-19 for group 3, the 3.2e-4 inferred LW fraction, BC03 spectra) or an artefact of a group-averaged cross-section; is the "group 2 is never shielded" reading sound; is the x400 boost applied to group 2;
- equilibrium vs time-dependent claims: relaxation time tau = 1/(2A + gamma), formation times of 870-1750 Myr, the Hu et al. 2015 eq. 11 estimate, whether any equilibrium post-processing result is being presented as what the run does;
- apples-to-apples: 119 vs 125 comparison (does the 125 control have any dense neutral gas at all?), line-of-sight radiation ratios, correlation r = -0.76 and what it can and cannot show;
- statistics: one halo, two snapshots, 113 new stars; what can and cannot be generalised;
- the LVDB analysis: matching, completeness, upper limits, whether the Kennicutt-Schmidt-style planes compare like with like, and what an H2-free catalogue can actually say about H2.
For each item: verdict (correct / correct with caveat / unsupported / wrong), the reason, and the single test that would settle it.

**T4. Figure quality as evidence.** For every kept figure: one idea? axes, units and scales labelled and consistent across comparisons? colour scales stated? caption matches what is plotted? could a supervisor understand the point in 30 seconds? (The H2 relaxation-time plot was already unreadable to the supervisor; use that as the bar.) Give a redesign instruction for each figure that fails.

**T5. Physics grounding.** For each headline claim, state whether it agrees, disagrees or is untested against the literature you opened, with a section/figure reference and a short paraphrase. Include: Is a constant x400 boost a defensible subgrid choice at 10-20 pc resolution and low metallicity? Do the dwarfs' densities and fields plausibly allow H2, per Sternberg 2014, Gnedin 2009, Hu 2015/2016, Polzin 2023? What is the expected H2 and CO behaviour at Z' ~ 0.075 (Bolatto 2013, Telford 2025 Leo P)? Is Leo P (a star-forming dwarf with a 2.6 pc warm H2 clump and no CO) a fair comparison to a 13-Gyr quiescent dSph-like halo 605?

**T6. Ranked gap analysis.** What is the minimum set of analyses that turns this into a defensible, thesis-quality answer to Q1-Q4? Consider: more haloes (600, 624, others) and snapshots including one near the ~13.4-13.7 Gyr burst; a resolution test and sub-grid clumping factor; time-dependent vs equilibrium H2; resolution of the group-2 question with the simulation authors; a CO model (CLOUDY is available on the owner's machine); a fair observational comparison (Leo P, Sextans A, ALMA CO in dwarfs, Local Group dwarfs with H2 limits). Rank by scientific value per effort. For each: concrete first step, required inputs, done-criterion, and risk.

**T7. Recommendations.** Keep / merge / retract / delete for every item (recommend only). Include which earlier statements in the write-ups should be marked retracted, and the mechanism that made them wrong. Propose a 5-8 figure narrative that would tell the defensible story today, in order: for each figure, the claim, what it must show, the axes and scales, and which existing script or notebook (if any) produces it.

## Deliverable
One file, `audit.md`, committed to the repository's default branch. Structure:
1. **Top of file, in this order:** the three most serious problems; the single highest-value next step; what is settled vs open (a record that cannot name its live questions is a summary, not an audit).
2. T1 to T7 as sections, with the verdict table for T2/T3.
3. "Unresolved and guessed" list.
4. "What I recomputed" list with exact commands.
Keep it as short as the content allows; tables over prose where possible.

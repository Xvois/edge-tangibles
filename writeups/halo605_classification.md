# Classifying dwarf galaxies, and where Halo 605 sits

Snapshot: `Halo605_RT/output_00125` (z = 0), everything within R200c = 31.45 kpc unless stated.
Numbers from `classify605.py` (run on py-noether, 2026-10-05; output `classify605.json`, `classify605_sfh.npz`).
Figure: `halo605_classification.png`. Literature claims come from the corpus; "[unverified]" marks anything that is not.

## Short answer

Match on **measured axes**, not on morphological labels. On those axes Halo 605 at z = 0 is a
**classical-luminosity (M_V = -9.9), dispersion-supported, isolated field dwarf that is quiescent right now but holds a
small neutral hydrogen reservoir (5 x 10^4 Msun)**. That puts it on the boundary between a dwarf spheroidal (dSph)
and a very HI-poor transition dwarf (dTrans). Its closest Local Group analogues are **Phoenix** and **LGS 3**
(transition dwarfs) and **Tucana** (an isolated dSph). In EDGE's own scheme it is a "gas-rich, star-forming"
(rejuvenating) dwarf caught in a quiet spell, not a reionization relic.

None of the CO/ALMA-observed dwarfs is a match: they are all star-forming dwarf irregulars with 10^7 to 10^8 Msun of HI.
Matching to those needs an earlier, star-forming 605 output, not z = 0.

## 1. Why axes rather than labels

The labels overlap and their boundaries are conventions:

- Simon (2019, p.6) on ultra-faint dwarfs (UFDs): "They are not a physically distinct class of objects"; they continue the
  classical dwarfs in stellar mass, surface brightness, size, dynamical mass and metallicity.
- Weisz and colleagues (2014, abstract) call the ultra-faint/classical dSph distinction arbitrary.
- McConnachie (2012, p.33): "many of the transition dwarfs are perhaps best treated as low mass dIrr galaxies".
- Agertz and colleagues (2020, Fig. 5 caption) find that the size, velocity dispersion and luminosity scaling relations
  do not discriminate strongly between galaxy-formation models (paraphrase; the text twin for this paper is missing, so the quote is not verified).

So the useful scheme is a short vector of quantities that both observers publish and the simulation gives directly.

| Axis | What observers publish | Thresholds / reference classes (corpus) |
|---|---|---|
| Luminosity | absolute V magnitude M_V, V-band luminosity L_V | UFD: L_V < 10^5 Lsun, M_V fainter than -7.7 (Tillaboev 2025, p.6) |
| Size and surface brightness | projected half-light radius r_1/2, mean V surface brightness mu_V | dSph: M_V >= -14, mu_V >= 21 mag/arcsec^2 (Tillaboev 2025, p.6). EDGE compares in the M_V vs r_1/2,V plane, with r_1/2,V "obtained along a random line of sight" (Rey 2025, p.9) |
| Current star formation | H-alpha / O stars (lifetimes up to ~10 Myr) | Leo P counts as star-forming from "the presence of just one O-type star" (Telford 2025, p.2) |
| Neutral gas | HI mass M_HI, M_HI / L_V, plus the survey's detection limit | non-detections typically < 10^5 Msun (5 sigma), < 10^4 Msun inside the Milky Way virial radius (Putman 2021, p.17) |
| Star formation history (SFH) | colour-magnitude-diagram SFHs: fraction formed before z = 2, tau_50, tau_90 | average dSph SFH is an exponential decline with timescale ~5 Gyr; dIrr, dTrans and dE have exponential decline then roughly constant SFR over the last ~10 Gyr (Weisz 2014, p.22) |
| Environment | distance to nearest massive host | 53 of 55 dwarfs inside the Milky Way virial radius are devoid of gas; most gas-bearing dwarfs lie beyond the hosts' virial radii (Putman 2021, p.1, p.17) |
| Kinematics | stellar line-of-sight velocity dispersion sigma, rotation v/sigma | dSphs "don't show signs of rotation" (Tillaboev 2025, p.6) |
| Chemistry | stellar [Fe/H] (iron abundance relative to solar, log), gas-phase 12 + log(O/H) | mass-metallicity relations used by Rey (2025) |

The traditional labels are then just regions of this space: **dSph** (no gas, no current star formation, no rotation),
**dTrans** (HI present, no current star formation), **dIrr** ("gas rich, low density, metal poor, and forming stars",
Hunter 2024, p.33), **dE** (brighter, M_V around -15 to -16 in the Local Group, Weisz 2014 Table 1), **UDG**
(ultra-diffuse galaxies, stellar masses ~10^7 to 10^8.5 Msun, Tillaboev 2025, p.9).

EDGE adds an SFH-based classification that is the natural one for simulated dwarfs (Rey 2022, p.3, paraphrased because
the PDF extraction joins words): (i) **gas-poor relics**, all stars formed early (z >= 4) and no gas kept;
(ii) **gas-rich relics**, all stars early but gas re-accreted later without restarting star formation (Halo 624 is the
example given); (iii) **gas-rich, star-forming dwarfs**, which restarted star formation after a temporary quenching.
Kim and colleagues (2026, p.4) call Halo 600 and Halo 605 "rejuvenators" (from the indexed passage; text twin missing).

## 2. Halo 605 at z = 0

| Quantity | Value | Reading |
|---|---|---|
| Stellar mass now / ever formed | 2.87 x 10^6 / 4.79 x 10^6 Msun | survey value reproduced |
| M_V, L_V | -9.9, 7.7 x 10^5 Lsun | classical dwarf, 2.2 mag brighter than the UFD line |
| Projected half-light radius | 241 pc (216 to 254 over x, y, z) | 3D half-mass radius 397 pc, as in the survey |
| Mean surface brightness inside r_1/2 | 25.6 mag/arcsec^2 | dSph-like (well above the 21 floor) |
| sigma_LOS inside r_1/2; v/sigma | 9.2 km/s; 0.03 | dispersion supported, no rotation |
| Wolf mass (4 sigma^2 r_1/2 / G) | 1.9 x 10^7 Msun, M/L_V ~ 50 inside r_1/2 | dark-matter dominated |
| HI mass | 5.2 x 10^4 Msun (4.4 x 10^4 within 1 kpc) | below the typical 10^5 Msun non-detection limit |
| Peak HI column, 100 pc pixels | 2 to 4 x 10^19 cm^-2; above 10^19 over 0.1 to 0.17 kpc^2 | compact, faint |
| M_HI / L_V | 0.07 | Phoenix 0.16, LGS 3 0.40, Leo T 2.0 (Weisz 2014 Table 1) |
| Total gas in R200c | 3.4 x 10^7 Msun; hydrogen >99% ionized, nearly all at 10^4 to 10^5 K | warm halo, not ISM |
| H2 | 4.6 Msun | matches the earlier result |
| Star formation | none in the last 106 Myr; 1.0 x 10^-4 Msun/yr over 200 Myr; 3.6 x 10^-5 Msun/yr over 1 Gyr | quiescent in H-alpha terms |
| SFH | 20% before z = 6, 50% by 1.3 Gyr, 85% before z = 2, 90% by 5.9 Gyr, trickle until 106 Myr ago | not a relic; front-loaded with a long tail |
| Stellar [Fe/H] (mass-weighted) | -1.39 (median -1.24, spread 0.68 dex) | solar normalisation from Asplund 2009 [unverified, not checked in corpus] |
| Gas 12 + log(O/H), within 5 kpc | 7.71 (about 0.1 solar for 8.69 [unverified]) | no HII regions to measure it observationally |
| Environment | 1.4 x 10^4 Msun of stars outside R200c, none beyond 450 kpc (but the low-resolution region forms no galaxies, so this alone proves little). Dark-matter density 75 to 85% below the cosmic mean on 1 to 3 Mpc; total dark mass within 3 Mpc 5.5 x 10^11 Msun | isolated field dwarf, no Milky-Way-mass host within 3 Mpc |

**Classification by axis**: classical luminosity, dSph structure and kinematics, isolated, quiescent today, HI-poor but not
HI-free, EDGE class (iii) in a lull.

**Observed analogues** (Weisz 2014 Table 1, values from McConnachie 2012):

| Galaxy | Type | M_V | r_h (pc) | M_HI (Msun) | Distance to host (kpc) |
|---|---|---|---|---|---|
| Halo 605 | (this work) | -9.9 | 241 | 5.2 x 10^4 | > 3000 |
| Phoenix | dTrans | -9.9 | 454 | 1.2 x 10^5 | 415 |
| LGS 3 | dTrans | -10.1 | 470 | 3.8 x 10^5 | 269 |
| Tucana | dSph | -9.5 | 284 | none listed | 882 |
| Leo II | dSph | -9.8 | 176 | none listed | 236 |
| DDO 210 | dTrans | -10.6 | 458 | 4.1 x 10^6 | 1066 |

Phoenix matches in luminosity and is the closest in HI; 605 is about half its size. Tucana matches in size and
isolation but has no HI listed.

## 3. What one z = 0 snapshot cannot settle

1. **Quiescent or between bursts.** The H-alpha label needs stars younger than ~10 Myr. 605's last stars are 106 Myr old,
   yet its 200 Myr average rate (1.0 x 10^-4 Msun/yr) is above Leo P's 4.3 x 10^-5 Msun/yr (Telford 2025, p.2), and Leo P
   counts as star-forming because one O star is alive. At these rates, star-forming vs quiescent is a sampling
   question (my inference, not a corpus claim). Neighbouring outputs would say which one 605 usually is.
2. **HI detectability.** It depends on distance, beam and sightline. Rey (2022) shows HI maps change with beam size (200 and
   500 pc) and over time. 5 x 10^4 Msun would be a non-detection at the depth Putman (2021) reaches for most dwarfs.
3. **Observational systematics not modelled here:** V-band light uses pynbody's single-stellar-population table with total
   metallicity estimated from [Fe/H] (the snapshot stores no total-metallicity field). Ellipticity, Sersic profile,
   colours and CMD-based SFH recovery are not computed.
4. **Environment history.** z = 0 gives isolation now, not past interactions.
5. **CO matching.** CO-observed dwarfs (WLM, Sextans A, Sextans B; tentative I Zw 18; ALMA upper limit for Leo P) are all
   star-forming dIrrs (Hunter 2024, pp.16 to 17; Telford 2025). WLM, Sextans A and Sextans B have L_V ~ 4 to 5 x 10^7 Lsun
   and M_HI ~ 5 to 8 x 10^7 Msun (Weisz 2014 Table 1): about 50 times brighter than 605, with about 1000 times its HI.
   At z = 0, 605 has no cold dense gas (max n_H 0.06 cm^-3), so there is no CO to compare. Leo P is the only CO target
   in its mass range.

## Papers added to the corpus for this

McConnachie (2012), Weisz and colleagues (2014), Simon (2019) and Putman and colleagues (2021): acquired with `acquire.py
--reindex`, and `find.py doctor` is clean afterwards. Claims are in `evidence.py --topic dwarf-classification`
(11 of 17 quote-verified; the rest are paraphrased above with their pages).

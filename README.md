# H2 in EDGE2 dwarf galaxies: audit bundle (temporary)

**Goal.** Using the EDGE2 simulations (RAMSES-RT, Rey et al. 2025), identify where molecular hydrogen (H2) lies inside dwarf galaxies and under what conditions it forms. Stretch: map CO to H2 to look back at ALMA observations.

This repo is a temporary bundle for an independent scientific audit. Start with `AUDIT_PROMPT.md` (the task), then `FINDINGS.md` (every result, verdict and open question), `THREADS.md` (what each working session concluded). Output of the audit: a single `audit.md` at the repo root.

## File map
- `AUDIT_PROMPT.md`: the audit brief.
- `FINDINGS.md`: consolidated findings, run setup, numbers with sources, open questions.
- `THREADS.md`: per-thread conclusions.
- `writeups/`: the project's own Markdown write-ups.
  - `why-the-h2-plots-look-like-that-605.md`, `...-20261003T143648-de64.md`, `...-20261003T181705-c7ee.md`: three versions of one write-up (halo 605 z=0 H2; latest = c7ee).
  - `shielding_model_comparison.md`: shielding models and recommendation.
  - `halo605_classification.md`: dwarf classification of 605.
  - `halo605_119_vs_125.md`: burst comparison (older than the final notebook).
  - `bearings-605-HI-review.md`: HI review of 605.
  - `corpus-tooling-*.md`: literature-search tooling notes (tangential).
- `scripts/`: `lvdb_ks.py`, `lvdb_tools.py` (LVDB analysis), `plotting.py` (plot style), `slab_compare.py` (1D slab shielding comparison). Paths inside are from the project machine and will not run here.
- `notebooks/`: `lvdb_analysis.ipynb` (latest of three versions), `lvdb_scaling_relations.ipynb`. Outputs kept (about 0.7 MB each).
- `figures/`: 18 PNGs. Memory does not label several of them (`chk3`, `chk4`, `combo`, `final5`, `final_fig`); identifying and judging them is part of the audit. `rt_*` vs `rt_v2_*` are two generations of radiation-transfer figures.
- `data/lvdb_kk13_matched.csv`: LVDB x Karachentsev & Kaisina 2013 x UNGC match table (derived from public catalogues; cite the catalogues).

## Not included, and why
- **Copyrighted material**: no paper PDFs, text or figures. Literature is cited by author, year and link only; the auditor must open the papers.
- `koplitz26_fig2_reproduced.png`: built from points read off a paper figure; retracted by the PI. `from_papers.csv` and the old `README.txt`: numbers transcribed from papers for that reproduction.
- `uploads/`: provenance unconfirmed.
- Two older `lvdb_analysis-2026100*.ipynb` copies (superseded versions of the same notebook).
- `compare_h2.py`: reproduces a collaborator's method; the collaborator's code and files are excluded entirely.
- **Only on the project machine (not reachable from the cloud)**: the burst notebooks (`burst_compare.ipynb`, `burst_sed.ipynb`, `h2_relaxation.ipynb`), survey files (`galaxy.json`, survey notebooks, `utils/`), simulation snapshots (halos 383, 600, 605, 624), scratch results (`clumpiness_review/phaseA/results.md`, `group2_check/report.md`, `relaxation_review/findings.md`), the literature corpus and its search index, and the CLOUDY install. Their key results are summarised in `FINDINGS.md` and are therefore [reported], not re-checkable here.
- Credentials, host addresses and personal data.

## Caveats for the auditor
Notebooks and scripts were written against local data that is not in this repo; most numbers cannot be recomputed here. Treat unverifiable numbers as claims to be graded for plausibility and internal consistency, and say what single check would confirm each.

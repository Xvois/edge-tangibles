# Corpus tooling upgrade, 2026-10-01

Commits in ~/mphys: 937e890 (tools, eval) and da5866c (paper registry). Pre-upgrade index backed up at
~/mphys/backups/corpus-20261001T-pre-tooling-upgrade.db.

## Accuracy (same 70 questions + 12 absent-paper traps, before -> after)

| measure | before | after |
|---|---|---|
| right paper in top 5 (R@5) | 0.763 | 0.818 |
| R@10 | 0.889 | 0.895 |
| R@20 | 0.910 | 0.927 |
| rank of first right paper (MRR@10) | 0.770 | 0.837 |
| question names a paper we hold: MRR | 0.17 | 1.00 |
| traps answered with no warning | 2/12 | 0/12 |
| quote verification of gold quotes | 46/46 | 46/46 |

Paired bootstrap: R@5 +0.061 [+0.007, +0.125]; MRR +0.084 [+0.025, +0.150]; R@10 no detectable change.
Weakest category is still exact-symbol questions (R@10 0.78).

## What changed

Ingestion and indexing
- Equations now indexed for papers added with acquire.py (Draine & Bertoldi, Sternberg+14, Gnedin & Draine,
  Wolcott-Green, Richings+14 and others had none). arXiv DOIs parsed, failed lookups retried, exact-title arXiv fallback.
- Equation numbers match the paper (multi-line, \nonumber, \tag, subequations, appendix A1/A.1, section 3.2 style)
  and 1,042 of 1,121 have the PDF page. Each equation is a searchable passage with its section heading, introducing
  prose and where-clause. 643 -> 1,121 equations.
- Figure detection is column-aware and checks there is a graphic: 496 -> 753 figures found (Sternberg+14 1 -> 15).
- Embeddings are incremental; one command (`reindex.py`) rebuilds on a copy, runs doctor, backs up, swaps.
- acquire.py takes several papers, reindexes once, and finds arXiv preprints of retitled journal papers
  (only used with --force --why after a human check).

Search
- "X & Y (year)" is held only if X is the first author (Clark & Glover 2015 and McKee & Krumholz 2010 were
  falsely "held" via co-authors).
- A paper named in the question comes first. --paper / --year-min / --author filter before ranking.
- equation and figure lookups rank by meaning; equation --paper crash fixed.
- Citations read "Draine & Bertoldi 1996" and flag "arXiv preprint pages" where the PDF is a preprint.
- verify labels matches that come from LaTeX rather than the PDF; gapfill uses the first-author test;
  newlit --plan shows the real topic.

Added to the library as an end-to-end test: Telford et al. 2025, H2 in Leo P (arXiv preprint of the Nature
paper; your Zotero entry had no PDF).

## Still open
- Rubio 2015 has two PDFs in Zotero; only the manuscript is indexed (the Nature version has the figures).
- 79 equations lack a page (mostly papers whose PDF prints numbers differently).
- Each search call still reloads the models (~3.5 s); evidence.py batching avoids most of it.
- The Hermes skill lists the old three-step rebuild by hand. It still works, but it edits the live index in place.

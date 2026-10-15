# Corpus tooling assessment (read-only), 2026-10-01

Nothing was edited, rebuilt or sent online. All tests used `~/mphys/.venv/bin/python`, run one at a time
alongside the shielding-model session.

## Verdict

Text search works well. Equation lookup and figure lookup are the weak spots, and both fail on exactly
the papers the shielding comparison depends on.

## What was tested

| Tool | Result |
|---|---|
| `find.py doctor` | ok, no problems; 64 docs, 6,744 chunks, vectors 100% |
| `find.py search` (14 shielding queries, hybrid_rerank) | Right papers in the top 5 for 12/14. ~3.7 s per call, almost all of it model loading (lexical engine alone: 31 ms). Correctly WEAK on Wolcott-Green 2011 (not held) and on the Sobolev-length question. |
| `find.py verify` | PASS strict on quotes from DRAINE96, STERNB14, GNEDIN14 |
| `find.py equation` | "self-shielding function" and `--contains f_\mathrm{shield}` both return nothing. DRAINE96, GNEDIN14, STERNB14 have 0 equations indexed. `--paper KEY` crashes. |
| `find.py figure` | "self-shielding function versus H2 column density" returns three Krumholz 2009 figures and misses Draine & Bertoldi Fig. 1 and Sternberg Fig. 5. |
| `evidence.py --selftest` | both tiers live |
| `gapfill.py` (local phase) | Correct: flags Wolcott-Green 2011 as cited-not-held, sees Bertoldi 1996 as held. Minor: splits "Wolcott-Green" and reports "Green" as a missing author. |
| `newlit.py --plan` | Works, but the plan prints the topic as the literal key "GNEDIN14"; the real run uses the paper's title. |

## Root causes found

1. **Equations missing for externally acquired papers.** `index_latex.py` only iterates the Zotero
   index (`zotero_index.json`), so the five papers added through `acquire.py` (DRAINE96, GNEDIN14,
   STERNB14 among them, all with arXiv ids on record) never had their LaTeX fetched. In the PDF text,
   Draine & Bertoldi eq. 37 survives only as shredded coefficients split across chunks.
2. **`find.py equation --paper` crash.** `sqlite3.OperationalError: ambiguous column name: zotero_key`
   (find.py:500, the WHERE uses an unqualified column on a join). Equation search also has no ranking
   (ordered by eq_id) and only LIKE matching.
3. **Figure search ignores relevance.** The all-words mode orders by fig_id; the fallback ranks only the
   first 60 candidates by fig_id (find.py `run(groups, "any", max(k*12, 60))`). 200 captions sort ahead
   of Draine & Bertoldi Fig. 1 (fig_id 435), so later-ingested papers can never surface. The caption
   chunks already have dense vectors that could rank this properly.
4. **Figure detection misses AAS-preprint figures.** STERNB14 has 1 figure row (and it is body text
   "Figure 11 shows..."); GNEDIN14 has 2. Their real captions exist as `caption` chunks in search, just
   not in the figures table, so they cannot be rendered by id.
5. **Two-author citations drop the second author.** `cite()` prints "Draine 1996", "Gnedin 2014" for
   Draine & Bertoldi 1996 and Gnedin & Draine 2014. Ambiguous once Gnedin 2009/2011 are added.
6. **No regression harness.** The gold-set evaluation was deleted on 24 Sep (in git history), so any
   retrieval change is currently unmeasured.
7. **Speed.** Each call reloads the embedding and reranker models (~3.5 s). `evidence.py` batching
   already amortises this; a warm daemon would only matter for many one-off calls.

## Coverage gaps relevant to shielding

Cited by held papers but not held (counts are held papers citing them, from the refs chunks):
Glover & Mac Low 2007 (7), Gnedin, Tassis & Kravtsov 2009 (4), Richings et al. (4), Bialy & Sternberg (3),
Gnedin & Kravtsov 2011 (2), McKee & Krumholz 2010 (2), Wolcott-Green, Haiman & Bryan 2011 (1),
Krumholz 2013 (1). Bolatto et al. 2013 (18) for the CO step. Wolcott-Green 2011 is not in
`corpus/gaps.txt`. About 18 of the 64 docs are off-topic (education, epidemiology, climate); they
did not appear in any test result.

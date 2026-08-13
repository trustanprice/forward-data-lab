# AGENTS.md — src/rerank/

## Responsibility

**Fix 2.** Combine embedding similarity with each paper's real citation
count (already pulled from Semantic Scholar) into a single blended ranking
score, so a well-established, highly-cited paper is favored over a
topically-similar but obscure one — directly addressing the flaw observed
in Asta, where citation counts are shown in the UI but never used to weight
the generated narrative.

## Inputs

- A list of candidate paper dicts, each already carrying `"similarity"`
  (from `src/retrieval/`) and `"citation_count"` (from `data/papers.json`).
  This module is applied to the *already-retrieved* top-k pool, not the
  full corpus — it's a reranking step, not a replacement for retrieval.

## Outputs

- `blend_scores(candidates, alpha)` → the same list, sorted descending by a
  new `"blended_score"` field, with `"normalized_similarity"` and
  `"normalized_citation"` also attached for inspection/debugging.

## Conventions

- `CITATION_BLEND_ALPHA` (`src/config.py`, default `0.5`) is the weight on
  normalized similarity vs. normalized citation signal.
  `blended = alpha * norm_similarity + (1 - alpha) * norm_citation`.
- Citation counts are `log1p`-transformed before normalizing — raw counts
  are extremely heavy-tailed (a handful of papers with tens of thousands of
  citations next to a majority with single digits), so a linear blend on
  raw counts would let one mega-cited paper dominate regardless of topical
  relevance.
- Both signals are min-max normalized **within the candidate pool being
  reranked**, not against the whole corpus — see the tradeoff note below.

## Design tradeoff — normalization scope and its limits

Normalizing similarity and citation count to `[0, 1]` only within the
current top-k candidate pool is what makes a fixed-weight blend meaningful
at all (raw cosine similarities cluster in a narrow band; raw citation
counts span orders of magnitude) — but it has a real cost worth flagging
honestly:

- **The normalization is relative, not absolute.** The most-cited paper in
  *this* candidate pool always gets a normalized citation score of `1.0`,
  even if it only has, say, 40 citations and would look unremarkable next
  to the most-cited paper for a different query. A more robust version
  would normalize against a global, field-calibrated citation scale (e.g. a
  percentile within the paper's subfield and publication year, since raw
  citation counts aren't comparable across fields or across a 2005 paper
  vs. a 2023 one) rather than against whatever happens to be in the
  retrieved pool.
- **`alpha` is a hand-picked constant**, not learned or query-adaptive. A
  query where topical precision matters more than establishment (e.g. a
  request for the newest work on a narrow subtopic) and a query where
  citation-weighted consensus matters more (e.g. "what's the standard
  approach to X") arguably want different blend weights, and this doesn't
  distinguish them.
- **This reranks the already-retrieved top-k** — if the truly best paper
  for a query didn't make it into the similarity-based candidate pool in
  the first place (an embedding-quality problem, not a reranking problem),
  no amount of citation-weighted reranking can recover it. Fix 2 improves
  *ranking of what was found*; it does not fix *what gets found*. **Verified
  directly, not just theorized:** at `top_k=5` (instead of 8) on the same
  query, the seminal 16,973-citation paper (rank 6 by pure similarity) is
  excluded from the pool before `blend_scores()` ever runs — confirmed via
  `rank(query, top_k=5)` then checking membership. Fix 2 had no chance to
  surface it. This is the sharpest illustration of the limitation: a
  smaller `top_k` makes Fix 2 *less* able to compensate for retrieval
  fragility, not more, since it shrinks the pool citation-weighting can
  work with.
- **Effect on the LLM narrative may be smaller than the effect on ranking.**
  Tested live: reranking the on-topic query's pool changed the seminal
  paper's citation number from `[6]` to `[2]`, but the generated report's
  *emphasis* was similar either way — it was already described as "the
  original RAG formulation" in the non-reranked version too. Likely
  explanation: `src/generation/generate.py`'s context block already states
  each paper's citation count as plain text, so a capable model can pick up
  on "this one has 16,973 citations" regardless of numbering order. Fix 2's
  clearest, most reliable value in this pipeline is on the *retrieval/
  ranking* side (what makes it into a capped top-k, what a human skimming
  raw scores would see first) rather than guaranteed narrative influence —
  see `demo/AGENTS.md` for the full comparison.

## Current state

Implemented and verified — this module needs no LLM, so it was fully
testable without an API key. Run against the real corpus, query "How does
retrieval-augmented generation reduce hallucinations in large language
models?", `top_k=8`, `alpha=0.5`:

| rank (pure similarity) | rank (blended) | paper | similarity | citations | blended |
|---|---|---|---|---|---|
| 1 | 1 | Benchmarking RAG for Medicine | 0.567 | 588 | 0.689 |
| 6 | **2** | **RAG for Knowledge-Intensive NLP Tasks (Lewis et al. 2020)** | 0.425 | **16,973** | 0.583 |
| 5 | 3 | RAG for LLMs: A Survey | 0.465 | 3,837 | 0.564 |
| 3 | 4 | RAGAs | 0.502 | 909 | 0.539 |
| 8 | 8 | MTRAG | 0.396 | 76 | 0.000 |

The original 2020 RAG paper — by far the most established, highest-impact
work in the corpus — moves from rank 6 to rank 2 once citation weight is
applied, exactly the intended fix for the flaw observed in Asta (citation
counts displayed but never used to weight the narrative). The lowest-cited
paper in the top-8 (MTRAG, 76 citations) drops to a blended score of 0.000
despite a respectable 0.396 similarity, illustrating the tradeoff noted
above: `alpha=0.5` genuinely can bury a recent, narrowly-relevant paper
behind more established ones.

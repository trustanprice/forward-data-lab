# AGENTS.md — src/retrieval/

## Responsibility

Given a user query, embed it with the same model used for the corpus,
compute cosine similarity against every cached paper embedding, rank
descending, and cap at a configurable top-k. Also owns the relevance
confidence check used by Fix 1 (the actual "is this query even answerable
from this corpus" decision).

## Inputs

- `data/papers.json` and `src/embeddings/cache/` (via `src/config.py`).
- A query string and `top_k` (default from `src/config.py`,
  overridable per call / via `--top-k`).

## Outputs

- `rank(query, top_k)` → list of paper dicts (same shape as `data/papers.json`
  entries) each with an added `"similarity"` field (cosine similarity to the
  query, in `[-1, 1]`, sorted descending), truncated to `top_k`.
- `passes_relevance_threshold(ranked_papers, threshold)` → bool. **Fix 1**
  lives here rather than in `src/generation/`: it's a judgment about the
  retrieval scores themselves, not about generation. `src/generation/` calls
  this before deciding whether to synthesize at all.

## Conventions

- Both corpus and query embeddings are L2-normalized at embedding time, so
  cosine similarity is a plain dot product (`embeddings @ query_vec`) — no
  norm division needed at query time.
- Run as `python -m src.retrieval.retrieve "<query>"` from the repo root for
  ad-hoc inspection; `main()` prints similarity + citation count + title per
  result.
- Asserts (not silently ignores) that the cached embeddings still match
  `data/papers.json` and the configured embedding model — a stale cache
  fails loudly rather than silently ranking against outdated vectors.

## Design tradeoff — the relevance threshold is a blunt instrument

`SIMILARITY_THRESHOLD` (in `src/config.py`) is a single fixed cosine-
similarity cutoff applied to the top result. This is deliberately the
simplest possible fix, and it inherits real weaknesses worth being honest
about in the write-up:

- **It's corpus- and embedding-model-specific.** The right cutoff depends on
  how tightly the corpus clusters and on the embedding model's own
  similarity distribution — a threshold tuned here does not transfer to a
  different corpus or a different embedding model without recalibration.
- **It's a single global number, not per-query or per-domain calibrated.**
  A more robust version would calibrate against a validation set of known
  relevant/irrelevant query-corpus pairs, or use a learned relevance
  classifier instead of a hand-picked cosine cutoff.
- **A hard cutoff has an edge**: a query landing at 0.29 with the threshold
  set at 0.30 is treated identically to a query at 0.05, even though the
  two cases probably deserve different confidence language. A softer,
  graduated confidence signal (e.g., "weakly related — treat with caution"
  vs. "no relevant papers found") would be more honest than a binary gate,
  at the cost of more complexity than a course-project demo needs.

The actual chosen threshold value, and the real on-topic/off-topic
similarity scores it was calibrated against, are recorded in the root
`AGENTS.md` task list and in `demo/AGENTS.md` once the failure demo has run.

## Current state

Implemented and calibrated. Real scores observed against the 18-paper corpus
(top-8, `python -m src.retrieval.retrieve "<query>"`):

- On-topic (`"How does retrieval-augmented generation reduce hallucinations
  in large language models?"`): similarities from **0.567 down to 0.396**
  across the top 8 — every candidate clearly clusters around the actual RAG
  papers, top hits are health/biomedicine RAG survey papers plus RAGAs
  (evaluation) and the two RAG foundational papers.
- Off-topic (`"What are the effects of ocean acidification on coral reef
  ecosystems?"`): similarities from **0.024 down to -0.034** — i.e.
  essentially zero-to-negative cosine similarity across the board, since
  nothing in a RAG-paper corpus is meaningfully related to marine biology.

`SIMILARITY_THRESHOLD = 0.30` (in `src/config.py`) sits in the middle of
that ~0.37-wide gap, with comfortable margin on both sides. See
`demo/AGENTS.md` for what this threshold does once wired into
`src/generation/` (Fix 1).

# AGENTS.md — src/embeddings/

## Responsibility

Generate a sentence embedding for every abstract in the fixed corpus, using
a standard local sentence-embedding model, and cache the resulting vectors
locally so retrieval never has to re-embed the corpus.

## Inputs

- `data/papers.json` (produced by `data/`).

## Outputs

- `src/embeddings/cache/embeddings.npy` — a `float32` NumPy array, shape
  `(num_papers, embedding_dim)`, L2-normalized (so cosine similarity reduces
  to a plain dot product downstream).
- `src/embeddings/cache/embeddings_meta.json` — `{"model", "count", "dim",
  "paper_ids"}`, used by `src/retrieval/` to assert the cache still matches
  `data/papers.json` and the configured model before trusting it.

## Conventions

- Model: `all-MiniLM-L6-v2` via `sentence-transformers` (name lives in
  `src/config.py`, not hardcoded here).
- Embedding input text is `f"{title}\n\n{abstract}"` — title included
  because it carries concentrated topical signal that sometimes isn't
  restated in the abstract body.
- Run as `python -m src.embeddings.embed` from the repo root.
- The cache is derived, reproducible data — safe to delete and regenerate
  from `data/papers.json` at any time.

## Design tradeoff — embedding model choice

`all-MiniLM-L6-v2` was chosen because it's the standard, well-known
sentence-embedding baseline: free, runs locally with no API key, fast enough
for a live demo, and small enough (~80MB) to not be a burden to pull. It is
**not** a state-of-the-art embedding model — modern hosted embedding APIs
(OpenAI `text-embedding-3-*`, Voyage, Cohere) or larger local models
generally retrieve more accurately, especially on domain-specific scientific
text. For a 10-20 paper demo corpus this ceiling doesn't matter much (the
ranking task is easy at this scale); it would matter increasingly as the
corpus grows toward Asta's actual scale (a corpus of hundreds of millions of
papers), where embedding quality directly determines whether the true
top-k are even in the candidate pool before reranking ever gets a chance to
help.

## Design tradeoff — chunking strategy (none)

Abstracts are embedded whole, not chunked. This is a deliberate
simplification that only holds because abstracts are short (typically
well under `all-MiniLM-L6-v2`'s 256-token max sequence length). Two real
limitations follow directly from this:
1. **Silent truncation**: any abstract longer than the model's max sequence
   length is silently truncated by `sentence-transformers` before encoding —
   no warning, no error. Rare for abstracts, but it means a small amount of
   information loss can't be ruled out for the longest ones in the corpus.
2. **This does not scale to full-text papers.** A production system indexing
   full papers (not just abstracts) would need a real chunking strategy —
   fixed-size windows, section-aware splitting, or overlapping windows — plus
   a way to aggregate chunk-level similarity back up to paper-level relevance
   (max-pool, mean-pool, or retrieve-then-rerank at the chunk level). None of
   that is implemented here; it's out of scope for an abstract-only demo but
   would be a first-order design decision for anything beyond this scale.

## Current state

Run against the 18-paper corpus. `src/embeddings/cache/embeddings.npy` is a
`(18, 384)` float32 array (L2-normalized, confirmed norm ≈ 1.0), with
`embeddings_meta.json` recording the model name and the 18 paper IDs in
order. `all-MiniLM-L6-v2` auto-downloaded from the Hugging Face Hub on first
run (unauthenticated, no `HF_TOKEN` needed at this scale — HF prints a
rate-limit warning but it did not block the download).

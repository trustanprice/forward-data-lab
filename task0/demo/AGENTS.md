# AGENTS.md — demo/

## Responsibility

Orchestrate the full pipeline end to end for a pair of queries — one
clearly relevant to the corpus, one clearly unrelated — and print/save a
side-by-side comparison. This is the concrete evidence for the project's
central claim: naive top-k retrieval is fragile, and the two fixes address
it.

## Inputs

- `--on-topic "<query>"` / `--off-topic "<query>"` query strings.
- `--top-k`, `--threshold`, `--rerank` — passed straight through to
  `src/generation/answer_query()`.
- Everything `src/generation/` needs transitively (corpus, embeddings,
  `ANTHROPIC_API_KEY`).

## Outputs

- Printed side-by-side report for both queries (top similarity score,
  whether Fix 1 refused, and the generated report text).
- `--save <path>` optionally dumps the full result dicts (including every
  candidate paper's scores) as JSON, for pulling numbers into the write-up.

## Conventions

- Run as `python -m demo.run_demo --on-topic "..." --off-topic "..."` from
  the repo root.
- The query pair is intentionally run multiple times across the project's
  build sequence — naive pipeline, then with Fix 1, then with Fix 1 + Fix 2
  — using the *same two queries* each time, so the before/after comparison
  isolates the effect of each fix rather than conflating it with a query
  change.

## Query pair and observed results

Finalized:

- **On-topic query:** `"How does retrieval-augmented generation reduce
  hallucinations in large language models?"` — top-8 similarities
  0.396-0.567.
- **Off-topic query:** `"What are the effects of ocean acidification on
  coral reef ecosystems?"` — top-8 similarities -0.034-0.024.

Filled in once the LLM-backed runs actually happen:

- **Naive pipeline (`--no-threshold`, no `--rerank`) result:** *(pending —
  needs `ANTHROPIC_API_KEY`)*
- **After Fix 1 (default flags, threshold enforced):** partially confirmed
  without an API key — the off-topic query is refused before any LLM call
  (`refused=True`, "No sufficiently relevant papers found..."; see
  `src/generation/AGENTS.md`). The on-topic side of this comparison (does
  Fix 1 leave a genuine answer untouched?) still needs a live run.
- **After Fix 1 + Fix 2 (`--rerank`):** the reranking effect itself is
  confirmed independent of the LLM — see `src/rerank/AGENTS.md` for the
  observed rank changes. The full generated-report comparison needs a live
  run.

## Current state

Implemented (`demo/run_demo.py`). Everything that doesn't require a live
Claude API call has been verified:
- Fix 1's refusal path (off-topic query, default flags) — confirmed via
  direct `answer_query()` call, zero API calls made.
- Fix 2's reranking effect on the retrieved pool — confirmed via
  `src/rerank/rerank.py`, see table in `src/rerank/AGENTS.md`.

Blocked on `ANTHROPIC_API_KEY`: the actual generated-report text for both
queries, under all three flag combinations (naive, Fix 1 only, Fix 1 + Fix
2) — this is the part of the failure demo that needs a real LLM call to
show what a forced synthesis on the off-topic query actually looks like,
and to confirm the on-topic report reads correctly with inline citations.

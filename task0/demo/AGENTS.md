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

Filled in once the pipeline is built and the demo has actually run — this
section becomes the record of what was actually observed, not a plan.

- **On-topic query:** *(pending)*
- **Off-topic query:** *(pending)*
- **Naive pipeline (no fixes) result:** *(pending)*
- **After Fix 1 (relevance threshold):** *(pending)*
- **After Fix 1 + Fix 2 (citation-weighted reranking):** *(pending)*

## Current state

Not yet implemented — depends on every other module.

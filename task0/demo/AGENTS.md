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

- **On-topic query:** `"How does retrieval-augmented generation reduce
  hallucinations in large language models?"` — top-8 similarities
  0.396-0.567.
- **Off-topic query:** `"What are the effects of ocean acidification on
  coral reef ecosystems?"` — top-8 similarities -0.034-0.024.

Full raw output (all papers, scores, and generated text) for the naive run
below is saved at `demo/sample_output_naive.json`.

### Naive pipeline (`--no-threshold`, no `--rerank`)

- **On-topic:** produced a well-grounded, correctly-cited report (headers,
  inline `[n]` citations matching the numbered source list, accurately
  summarized the seminal paper, MedRAG's 18% accuracy gain, RAGAs'
  evaluation framing, and named real limitations — lost-in-the-middle,
  multi-hop weakness — straight from the abstracts). This is the "should
  work well" half of the demo, confirmed.
- **Off-topic — an honest surprise:** with Fix 1 *disabled*, the pipeline
  still called the LLM on the ocean-acidification query using the 8 (all
  near-zero-similarity) RAG papers as context. It did **not** produce a
  forced or misleading synthesis. Claude Opus 5 correctly identified that
  none of the 8 abstracts were relevant and said so directly: *"The
  provided abstracts do not support an answer to this query... None of them
  address ocean acidification, coral reefs, marine biology, or any
  environmental science topic."* This contradicts the failure mode
  originally expected here — see the "what this actually means" note below
  before concluding Fix 1 is unnecessary.

### With Fix 1 (default flags)

- **Off-topic:** refuses before any LLM call — confirmed separately (see
  `src/generation/AGENTS.md`); behaviorally indistinguishable in outcome
  from the naive run above (both correctly decline), but deterministic,
  free, and instant instead of depending on the model's judgment call.
- **On-topic:** identical code path to the naive on-topic case above (the
  query already clears the threshold, so Fix 1 changes nothing for it) —
  Fix 1 doesn't touch queries that were already going to be answered well.

### With Fix 1 + Fix 2 (`--rerank`)

- **On-topic:** ran the same query with citation-weighted reranking
  applied before generation. The seminal 2020 RAG paper moved from
  citation `[6]` (non-reranked) to citation `[2]` (reranked) — Fix 2
  visibly changed the *reference numbering/prominence* — but both versions
  already opened by describing it as "the original RAG formulation," so the
  narrative *emphasis* was similar either way. Likely explanation: the
  context block already includes each paper's citation count as plain text
  (`_format_context()` in `src/generation/generate.py`), so a capable model
  can pick up on "this one has 16,973 citations" regardless of its position
  in the numbered list — Fix 2's reordering may matter more for pure
  ranking/browsing use cases than for LLM narrative synthesis specifically,
  at least in this single test with a small, high-quality corpus.
- **Where Fix 2 *does* provably matter (verified separately, no LLM
  needed):** at `top_k=5` instead of 8, the seminal paper (rank 6 by pure
  similarity) is excluded from the candidate pool *before* Fix 2 ever runs
  — confirmed via direct `rank()`/`blend_scores()` calls. Fix 2 reranks
  what similarity retrieval already found; it cannot rescue a highly-cited
  paper that didn't make the similarity cutoff. This is the sharpest, most
  concrete evidence for the tradeoff already documented in
  `src/rerank/AGENTS.md`.

### Replication: 2 more on-topic + 2 more off-topic queries

To check the naive-off-topic-decline result wasn't a fluke, three more
queries were run live (naive, `--no-threshold`), saved in full at
`demo/sample_output_extended.json`:

| Query | Category | Top similarity | Result |
|---|---|---|---|
| "What are the applications of retrieval-augmented generation in healthcare and medicine?" | on-topic | 0.562 | Answered, grounded (cites MedRAG, meta-analysis odds ratio 1.35, KG-enhanced diagnosis support) |
| "How do researchers benchmark and evaluate retrieval-augmented generation systems?" | on-topic | 0.649 | Answered, grounded (RAGAs, MultiHop-RAG, mtRAG, MIRAGE all correctly cited and summarized) |
| "What causes the northern lights to appear in different colors?" | off-topic | 0.014 | **Declined** — "cannot answer this query... would need sources from space physics or atmospheric science" |
| "What were the primary economic causes of the fall of the Roman Empire?" | off-topic | 0.034 | **Declined** — "would need sources from historical or economic-history scholarship" |

Combined with the original pair, that's **3 on-topic queries answered
correctly and 3 off-topic queries across three unrelated domains (marine
biology, atmospheric physics, ancient economic history) all declined
honestly** — the same naive pipeline, same "say so plainly" prompt
instruction, zero exceptions. This is stronger evidence than the original
single pair that the decline behavior is a real, repeatable property of
this model + this prompt, not a one-off — while the underlying argument
for Fix 1 (below) is unchanged: repeatable-so-far is still not the same
guarantee as mechanical enforcement.

### What this actually means for the project's thesis

The naive off-topic result is a genuinely useful finding, not a failed
demo: it shows that *retrieval* is unambiguously fragile (near-zero,
noise-level similarity scores, visible directly in the numbers) even when
*this specific, carefully-prompted, frontier model* consistently caught the
mismatch at generation time — now replicated 3/3 across distinct domains.
That recovery is not something naive top-k retrieval provides — it came
entirely from an explicit "say so plainly" system-prompt instruction, on
one model, on maximally-obvious topic mismatches. It is not: deterministic,
inspectable without reading the model's output, free (a full paid LLM call
happened either way, six times over), or guaranteed to generalize to a
different model, a subtler/borderline query, or a pipeline that (like the
Asta behavior this project set out to study) doesn't have that instruction
at all. Fix 1 replaces "hope the model notices" with a mechanical,
verifiable, free guarantee — the off-topic query never reaches the model in
the first place, regardless of how any particular model would have
handled it.

## Current state

Fully implemented and run end-to-end with a live `ANTHROPIC_API_KEY`. All
three flag combinations (naive, Fix 1, Fix 1 + Fix 2) have been exercised
on the original query pair, plus 4 additional queries (2 on-topic, 2
off-topic) run naive to check replication. See the results above,
`demo/sample_output_naive.json` (original pair, full papers + report text),
and `demo/sample_output_extended.json` (the 4 additional queries, same
format). `site/index.html`'s interactive console now includes all 6
queries.

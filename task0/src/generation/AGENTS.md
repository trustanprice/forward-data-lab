# AGENTS.md — src/generation/

## Responsibility

Feed the top-k retrieved abstracts as grounding context into an LLM call and
produce a short synthesized report with inline citations back to the
numbered source papers. Also the wiring point for **Fix 1** (relevance
confidence threshold): this module decides whether to call the LLM at all,
based on `src/retrieval/`'s threshold check, or to return a plain "no
sufficiently relevant papers found" message instead of forcing a synthesis.

## Inputs

- A query string.
- `src/retrieval/`'s `rank()` (and optionally `src/rerank/`'s `blend_scores()`
  when `--rerank` / `use_rerank=True` is passed).
- `ANTHROPIC_API_KEY` in the environment (or a git-ignored `.env`).

## Outputs

- `answer_query(query, top_k, threshold, use_rerank, enforce_threshold=True)`
  → `{"query", "papers", "report", "refused"}`. `refused=True` means Fix 1
  fired and no LLM call was made at all — `"report"` is a fixed message, not
  a model output. `enforce_threshold=False` (`--no-threshold` on the CLI)
  reproduces the naive pre-fix behavior for the failure demo.

## Conventions

- Model: `claude-opus-5` (`ANTHROPIC_MODEL` in `src/config.py`) via the
  official `anthropic` Python SDK, non-streaming (`client.messages.create`)
  — reports are short (a few hundred tokens), well under the ~16K
  non-streaming threshold, so streaming isn't needed here.
- `output_config={"effort": "medium"}` — this is a bounded, low-latency
  synthesis task over a handful of short abstracts, not open-ended agentic
  work, so the API default of `"high"` effort is more thinking than the
  task needs. Documented explicitly rather than left as an unexplained
  parameter.
- The system prompt instructs the model to answer **only** from the
  provided numbered abstracts, cite inline with bracketed numbers (`[1]`,
  `[2]`, ...) matching the numbered context list, and to say plainly if the
  abstracts don't support an answer rather than forcing one. This is a
  prompt-level mitigation, and it is **not a substitute for Fix 1** even
  though it worked in the one case tested here — see the design tradeoff
  below and `demo/AGENTS.md` for the actual observed result and why "it
  happened to work once" isn't the same as "reliable."
- `response.stop_reason == "refusal"` is handled explicitly (Claude Opus 5
  can decline via safety classifiers, distinct from Fix 1's own refusal).

## Design tradeoff — prompting for honesty vs. mechanically enforcing it

Without Fix 1, the only thing stopping the model from confidently answering
an off-topic query is a system-prompt instruction to "say so plainly" when
the abstracts don't support an answer. **Tested with `--no-threshold` on
the off-topic query (see `demo/AGENTS.md` for the full text): it worked.**
Claude Opus 5 correctly identified that none of the 8 near-zero-similarity
RAG papers addressed the (unrelated) query and said so directly, instead of
forcing a synthesis. That's a genuinely useful data point, and it means the
prompt-level mitigation is more effective than this project initially
assumed — but it does **not** make Fix 1 redundant:

- It's **advisory, not enforced** — one model, one prompt wording, one
  maximally-obvious topic mismatch. Nothing guarantees a different model,
  a subtler/borderline-relevant query, or a differently-worded prompt
  behaves the same way.
- It's **not free** — the LLM still got called (and billed) to reach that
  correct-but-negative conclusion. Fix 1 reaches the same conclusion from a
  cosine similarity check, for free, before any API call.
- It's **not inspectable in advance** — you only find out the model
  declined by reading its output; Fix 1's decision is a number you can log,
  test, and reason about directly.
- It's exactly the behavior this project set out to question in the first
  place: **Asta, per the original testing that motivated this project,
  does not do this** — it synthesizes from its top-50 regardless of
  quality. This demo shows a well-prompted frontier model *can* behave
  honestly on an obvious mismatch, which makes it more notable, not less,
  that a production system apparently doesn't reliably do so. The
  difference is precisely whether a mechanism like Fix 1 (or equally
  careful prompting) is actually built into the pipeline, not whether it's
  possible in principle.

## Current state

Implemented, including Fix 1, and fully run end-to-end with a live
`ANTHROPIC_API_KEY`. `answer_query()` takes `enforce_threshold` (default
`True`) so the same code path reproduces the naive pre-fix behavior
(`enforce_threshold=False`, or `--no-threshold` on the CLI) rather than
maintaining two separate implementations.

- **Fix 1's refusal path** — verified with no API key needed at all: the
  off-topic query (similarity 0.024, under the 0.30 threshold) returns
  `refused=True` and the fixed message, with zero Anthropic API calls made.
- **On-topic generation** — verified live: produced a well-grounded report
  with correct inline citations, accurate summaries of methods/results, and
  real named limitations pulled from the abstracts (see
  `demo/sample_output_naive.json`).
- **Naive off-topic generation (`--no-threshold`)** — verified live: see
  the design tradeoff above and `demo/AGENTS.md` for the full result and
  why it doesn't change Fix 1's value.

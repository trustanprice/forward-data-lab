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
  prompt-level mitigation and is **not** a substitute for Fix 1 — see the
  failure demo notes for why the prompt alone doesn't reliably stop a
  forced synthesis on an off-topic query.
- `response.stop_reason == "refusal"` is handled explicitly (Claude Opus 5
  can decline via safety classifiers, distinct from Fix 1's own refusal).

## Design tradeoff — prompting for honesty vs. mechanically enforcing it

Without Fix 1, the only thing stopping the model from confidently answering
an off-topic query is a system-prompt instruction to "say so plainly" when
the abstracts don't support an answer. That's real signal worth keeping (it
improves *how* the model handles borderline cases where some genuine
partial relevance exists) — but prompt instructions are advisory, not
enforced: a capable model asked to synthesize a report from *any* set of
abstracts can generally find some plausible-sounding angle to write about,
even when none of the source material is actually relevant. Fix 1 moves the
decision out of the prompt and into code that inspects the actual
similarity scores *before* the LLM is ever called — mechanical, not
persuasive, and (as implemented here) literally makes zero API calls when it
fires. Whether the naive prompt-only path actually produces a forced/
misleading answer in practice — as opposed to this being merely the
expected failure mode — is exactly what the failure demo is for; see
`demo/AGENTS.md` for the observed result once it's run.

## Current state

Implemented, including Fix 1. `answer_query()` takes `enforce_threshold`
(default `True`) so the same code path can reproduce the naive pre-fix
behavior (`enforce_threshold=False`, or `--no-threshold` on the CLI) for the
failure demo, rather than maintaining two separate implementations.

Verified without an API key: calling `answer_query()` on the off-topic query
(similarity 0.024, well under the 0.30 threshold) returns
`refused=True` and the fixed message, with **no Anthropic API call made at
all** (confirmed — no auth error, meaning `generate_report()` never ran).

Not yet verified: the actual LLM call path (on-topic query, and the
`--no-threshold` naive/off-topic path that's supposed to demonstrate the
forced-synthesis failure) — blocked on `ANTHROPIC_API_KEY` being available.

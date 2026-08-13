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

- `answer_query(query, top_k, threshold, use_rerank)` → `{"query", "papers",
  "report", "refused"}`. `refused=True` means Fix 1 fired and no LLM call
  was made at all — `"report"` is a fixed message, not a model output.

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

Before Fix 1 existed, the only thing stopping the model from confidently
answering an off-topic query was a system-prompt instruction to "say so
plainly" when the abstracts don't support an answer. That is real signal
worth keeping (it improves *how* the model handles borderline cases where
some genuine partial relevance exists) — but the failure demo showed it is
not sufficient on its own: a capable model asked to synthesize a report
from *any* set of abstracts will generally find some plausible-sounding
angle to write about, even when none of the source material is actually
relevant to the question asked. That's exactly the "plausible-sounding
synthesis from a mismatched candidate set" failure mode this whole project
is about. Fix 1 moves the decision out of the prompt and into code that
inspects the actual similarity scores *before* the LLM is ever called —
mechanical, not persuasive.

## Current state

Not yet implemented.

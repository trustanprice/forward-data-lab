# AGENTS.md — Fleet Manager (root)

This file is the fleet manager for this repository. It describes the overall
goal, how the pieces fit together, who (which folder/module) is responsible
for what, and the current state of the task list. **Update this file, and the
local AGENTS.md in whichever subfolder changed, immediately after finishing
each task below** — this document should always reflect reality, not a plan.

> **Location note:** the git repository root is one level up from this file
> (`forward-data-lab/`); this project lives entirely inside its `task0/`
> subdirectory. All commands and paths below ("repo root", `python -m
> src...`) mean *this* directory — `cd` into `task0/` before running
> anything.

## Project goal

A minimal, working demonstration of the real challenge behind AI research-paper
agents like Asta: it's not "can it find papers," it's whether naive top-k
retrieval actually surfaces the most relevant papers *and* whether the
generated report honestly reflects the strength of that evidence — rather than
producing a plausible-sounding synthesis from a mediocre or mismatched
candidate set.

Concretely, this repo:

1. Pulls a small, fixed, real corpus of paper abstracts from the Semantic
   Scholar Academic Graph API.
2. Embeds the corpus and answers queries via cosine-similarity top-k retrieval.
3. Generates a short LLM-synthesized report over the top-k context, with
   inline citations back to source papers.
4. Demonstrates, with a real on-topic/off-topic query pair, that naive top-k
   *retrieval* is fragile (near-zero, noise-level similarity scores on an
   off-topic query) — and that whether the generated report actually reflects
   that fragility depends entirely on unverified, model-specific prompt
   behavior unless something mechanical enforces it. See `demo/AGENTS.md`
   for the actual observed result, which was more nuanced than "always
   forces a bad answer."
5. Fixes that with two concrete, minimal mechanisms:
   - **Fix 1 — relevance confidence threshold**: refuse to synthesize when
     nothing in the candidate pool actually clears a similarity bar.
   - **Fix 2 — citation-weighted reranking**: blend embedding similarity with
     each paper's real citation count, so a well-established, highly-cited
     paper outranks a topically-similar but obscure one — directly fixing the
     flaw observed in Asta, where citation counts are displayed but never used
     to weight the narrative.

This is a course project artifact. The write-up (outside this repo) frames the
task, why it's important, why it's hard, the state of the art, and this repo
as the "can it be implemented" demonstration plus a proposed improvement.

## Folder structure / fleet roster

| Folder | Responsibility | AGENTS.md |
|---|---|---|
| `data/` | Semantic Scholar data pull; the fixed corpus file | [data/AGENTS.md](data/AGENTS.md) |
| `src/embeddings/` | Embed the corpus; local embedding cache | [src/embeddings/AGENTS.md](src/embeddings/AGENTS.md) |
| `src/retrieval/` | Query embedding, cosine similarity, top-k ranking, Fix 1 (relevance threshold check) | [src/retrieval/AGENTS.md](src/retrieval/AGENTS.md) |
| `src/rerank/` | Fix 2 — citation-weighted blended reranking | [src/rerank/AGENTS.md](src/rerank/AGENTS.md) |
| `src/generation/` | LLM call producing the synthesized report with inline citations; wires in Fix 1 | [src/generation/AGENTS.md](src/generation/AGENTS.md) |
| `demo/` | Orchestrates the full pipeline; runs the on-topic/off-topic failure demo and the before/after comparison | [demo/AGENTS.md](demo/AGENTS.md) |
| `site/` | Static single-page report artifact ("Liquid Glass" demo page) presenting the project story and live results for a human reader — not part of the Python pipeline | [site/AGENTS.md](site/AGENTS.md) |
| `src/config.py` | Shared paths/constants used by every module above (not a sub-agent folder — a shared utility, documented here) | — |

## Conventions

- Python 3.11, virtualenv at `.venv/` (gitignored), pinned deps in
  `requirements.txt`.
- Every `src/*` module is run as `python -m src.<package>.<module>` from the
  repo root (each package has an `__init__.py`) so intra-repo imports
  (`from src.config import ...`) resolve without a package install step.
- All shared paths/constants (corpus path, embedding cache paths, model
  names, default top-k, similarity threshold, citation-blend weight,
  Anthropic model ID) live in `src/config.py`. Don't hardcode them elsewhere.
- The corpus (`data/papers.json`) is fixed once pulled — regenerate
  deliberately (re-run `data/fetch_papers.py`), don't let it drift silently.
  Cached embeddings (`src/embeddings/cache/`) are versioned against the corpus
  via a metadata file; retrieval code asserts they still match.
- The generation module calls the Anthropic Claude API
  (`ANTHROPIC_API_KEY` env var, or a git-ignored `.env` — see `.env.example`).
  Model: `claude-opus-5`.

## Task list / current state

- [x] Repo structure + venv + requirements.txt + .gitignore scaffolded.
- [x] Root and per-folder AGENTS.md created.
- [x] Semantic Scholar data pull (`data/fetch_papers.py`) implemented and run
      for the "retrieval augmented generation" topic — 18 papers saved to
      `data/papers.json` (citation counts 64-16,973; see `data/AGENTS.md`).
- [x] Embedding generation + local cache (`src/embeddings/embed.py`) — 18
      papers embedded with `all-MiniLM-L6-v2`, cached to
      `src/embeddings/cache/`.
- [x] Retrieval/ranking (`src/retrieval/retrieve.py`): query embedding,
      cosine similarity, configurable top-k. Calibrated against real
      on-topic (0.396-0.567) vs. off-topic (-0.034-0.024) similarity scores
      — see `src/retrieval/AGENTS.md`.
- [x] Generation (`src/generation/generate.py`): top-k context → Claude →
      short report with inline citations. Implemented with **Fix 1 built in**
      as a togglable gate (`enforce_threshold`, default `True`) rather than
      as a separate naive version — see `src/generation/AGENTS.md`.
- [x] Fix 1 (relevance confidence threshold) implemented and fully verified,
      including live: the off-topic query is refused before any LLM call is
      made (`refused=True`, zero Anthropic API calls, confirmed both with
      and without an API key present). See `src/generation/AGENTS.md`.
- [x] Fix 2 (citation-weighted reranking, `src/rerank/rerank.py`)
      implemented and verified — the 16,973-citation seminal paper moves
      from rank 6 (pure similarity) to rank 2 (blended) on the on-topic
      query; also confirmed it cannot rescue a paper excluded from the pool
      at a smaller `top_k`, and that its effect on the *generated narrative*
      specifically was smaller than its effect on ranking in this test. See
      `src/rerank/AGENTS.md`.
- [x] `demo/run_demo.py` orchestration script written and run live for all
      three flag combinations (naive, Fix 1, Fix 1 + Fix 2).
- [x] **Failure demo run live** (`ANTHROPIC_API_KEY` provided
      2026-08-13). Result was more nuanced than originally expected — the
      naive off-topic call did *not* produce a forced/misleading synthesis;
      Claude Opus 5 correctly declined via its system-prompt instruction.
      This doesn't undercut Fix 1's value (see the reasoning in
      `demo/AGENTS.md` and `src/generation/AGENTS.md`) — it's an honest,
      more interesting finding than the originally hypothesized failure,
      and it's now the project's central nuance: retrieval is fragile,
      generation-time recovery is real but unverified and non-free, and
      Fix 1 replaces "hope" with a mechanical guarantee.
- [x] Final AGENTS.md pass reflecting the real demo output, and the
      consolidated failure-modes/tradeoffs notes below, are complete.
- [x] `site/index.html` built — a static, single-page "Liquid Glass"
      report artifact presenting the full story (Asta testing beats → the
      honest surprise → Fix 1 → Fix 2 → conclusion) using only real,
      live-run numbers and quotes. Published as a Claude Artifact
      (https://claude.ai/code/artifact/21ef8d2d-33ad-400b-a887-d1bedaf4d80b).
      Extended with a genuinely live-computing interactive console (real
      threshold check + real citation blend, executed client-side) and a
      "Questions I Asked" section. See `site/AGENTS.md`.
- [x] Replicated the naive off-topic decline on 2 more domains (aurora
      borealis, fall of Rome) plus 2 more on-topic queries (healthcare,
      benchmarking) — all 3 off-topic queries declined honestly, 0
      exceptions; all 3 on-topic queries answered correctly. Saved at
      `demo/sample_output_extended.json`; all 6 queries are selectable in
      the site's interactive console. See `demo/AGENTS.md` § Replication.

## Known design tradeoffs (updated as they're discovered)

This section is populated as implementation surfaces real tradeoffs, so it
stays honest rather than aspirational. See per-folder AGENTS.md for the
detail behind each line once filled in.

- Embedding model choice (`all-MiniLM-L6-v2`, chosen for being free/local/
  fast at demo scale, not for retrieval quality): see `src/embeddings/AGENTS.md`.
- Chunking strategy (none — abstracts embedded whole; doesn't scale to
  full-text papers): see `src/embeddings/AGENTS.md`.
- Similarity threshold calibration (`0.30`, picked from a real ~0.37-wide
  observed gap between on-topic and off-topic scores on this corpus — not a
  universal constant): see `src/retrieval/AGENTS.md`.
- Citation/similarity normalization for blending (log1p on citation counts,
  both signals min-max normalized *within the retrieved pool*, not globally
  — relative rather than absolute calibration): see `src/rerank/AGENTS.md`.
- Fix 1 as a togglable gate rather than a separate naive implementation
  (`enforce_threshold` parameter): see `src/generation/AGENTS.md`.
- **The naive off-topic failure mode didn't reproduce as hard-failure LLM
  hallucination in this test** (Claude Opus 5, well-prompted, correctly
  declined) — the fragility that's unambiguously real and reproducible is
  in *retrieval* (near-zero similarity scores), not necessarily in every
  model's generation-time behavior. Fix 1 is valuable because it makes the
  refusal mechanical/free/verifiable, not because generation-time recovery
  is impossible. See `demo/AGENTS.md` and `src/generation/AGENTS.md`.
- **Fix 2's effect on ranking is unambiguous and verified twice over
  (moves the seminal paper from rank 6→2; provably can't rescue a paper
  excluded at a smaller `top_k`), but its effect on the LLM's generated
  narrative was smaller than expected** in a single test — likely because
  citation counts are already visible as plain text in the generation
  context regardless of numbering order. Worth stating honestly in the
  write-up rather than assuming reordering always changes what the model
  emphasizes: see `src/rerank/AGENTS.md`.

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
4. Demonstrates, with a real on-topic/off-topic query pair, how naive top-k
   retrieval is fragile — off-topic queries still return a forced, plausible-
   sounding synthesis from irrelevant papers.
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
- [ ] Generation (`src/generation/generate.py`): top-k context → Claude →
      short report with inline citations.
- [ ] Failure demo run (naive pipeline, no fixes yet): on-topic query vs.
      off-topic query, showing the off-topic case forces a misleading answer.
- [ ] Fix 1 (relevance confidence threshold) implemented and demo re-run.
- [ ] Fix 2 (citation-weighted reranking) implemented and demo re-run.
- [ ] Final AGENTS.md pass + consolidated failure-modes/tradeoffs notes for
      the report.

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
- Citation/similarity normalization for blending: *(pending — filled in when
  `src/rerank/` is built)*

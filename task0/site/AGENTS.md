# AGENTS.md — site/

## Responsibility

A static, single-page report artifact that tells the project's story end to
end for a human reader — testing Asta, the citation-weighting gap that
motivated this build, and the two fixes — using only real, pre-computed
output from the live demo run. This is **not** part of the Python pipeline
(`demo/` is the CLI orchestration script that produces the data this page
displays) — it's a presentation layer on top of it, with no server, no
build step, and no runtime dependency on the rest of the repo.

## Inputs

- `demo/sample_output_naive.json` — exact query text, similarity scores,
  and generated report text for the naive on-topic/off-topic run.
- `demo/AGENTS.md` — the Fix 1 / Fix 2 / rerank findings (refusal message,
  rank-shift table, the `top_k=5` exclusion result, the narrative-emphasis
  observation) that `demo/sample_output_naive.json` alone doesn't capture
  (that file only records the *naive* run, not the Fix 1 / Fix 2 passes).
- All content is hand-transcribed from those two sources into
  `site/index.html` at build time — this page does not fetch or parse them
  at runtime. If the underlying numbers change (e.g. the demo is re-run,
  the threshold is recalibrated), this page goes stale silently and must be
  manually re-synced.

## Outputs

- `site/index.html` — the complete page (HTML + inlined CSS + a small
  vanilla-JS scroll-reveal, no external requests, no build step). Open
  directly in a browser, or publish as a Claude Artifact.

## Conventions

- Single self-contained file — no bundler, no framework, no external
  fonts/scripts (the system font stack *is* the intended look here, not a
  fallback: `-apple-system` / `BlinkMacSystemFont` genuinely renders as San
  Francisco on macOS, which is the point of a "Liquid Glass" aesthetic).
- Deliberately single-themed (dark, "commit to the look" per the original
  design brief) rather than adapting to the viewer's light/dark preference
  — background and every color are painted explicitly so it still renders
  correctly regardless of host theme, it just doesn't switch.
- Structure mirrors the narrative arc used throughout this repo's own
  AGENTS.md docs: don't soften or hide the "honest surprise" (the naive
  off-topic query didn't fail the way it was originally expected to) — the
  page's Section 2 states this directly, same as `demo/AGENTS.md` and
  `src/generation/AGENTS.md` do.

## Current state

Built and published as a Claude Artifact
(https://claude.ai/code/artifact/21ef8d2d-33ad-400b-a887-d1bedaf4d80b).
Covers all five sections from the original brief: hero/intro (three Asta
testing beats + transition into the rebuild), the naive-pipeline honest
surprise, Fix 1, Fix 2 (including its two documented limitations), and a
conclusion proposing faithfulness verification as the next layer. All
numbers and quotes are transcribed from the live run, not invented.

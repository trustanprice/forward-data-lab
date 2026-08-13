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
  and generated report text for the original naive on-topic/off-topic run.
- `demo/sample_output_extended.json` — the same, for 4 additional queries
  (2 on-topic, 2 off-topic) run to check the naive-decline finding wasn't a
  fluke — see `demo/AGENTS.md` § Replication.
- `demo/AGENTS.md` — the Fix 1 / Fix 2 / rerank findings (refusal message,
  rank-shift table, the `top_k=5` exclusion result, the narrative-emphasis
  observation) that `demo/sample_output_naive.json` alone doesn't capture
  (that file only records the *naive* run, not the Fix 1 / Fix 2 passes).
- The live conversation that produced this project — the `#questions`
  section (see below) is condensed, faithful transcription of actual
  design-review questions asked and answered during development, not
  invented FAQ copy.
- All content is hand-transcribed from those sources into `site/index.html`
  at build time — this page does not fetch or parse them at runtime. If the
  underlying numbers change (e.g. the demo is re-run, the threshold is
  recalibrated), this page goes stale silently and must be manually
  re-synced.

## Outputs

- `site/index.html` — the complete page (HTML + inlined CSS + vanilla JS,
  no external requests, no build step). Open directly in a browser, or
  publish as a Claude Artifact.

## Conventions

- Single self-contained file — no bundler, no framework, no external
  fonts/scripts (the system font stack *is* the intended look here, not a
  fallback: `-apple-system` / `BlinkMacSystemFont` genuinely renders as San
  Francisco on macOS, which is the point of a "Liquid Glass" aesthetic).
- `<meta charset="UTF-8">` must stay the very first line. The page uses
  literal Unicode characters (em dashes, arrows, a bullet); without an
  explicit charset in the browser's encoding-sniff window, opening the raw
  file directly (`file://`, or a plain `http.server` with no charset
  header) mis-detects it as Windows-1252 and produces mojibake.
- Deliberately single-themed (dark, "commit to the look" per the original
  design brief) rather than adapting to the viewer's light/dark preference
  — background and every color are painted explicitly so it still renders
  correctly regardless of host theme, it just doesn't switch.
- Structure mirrors the narrative arc used throughout this repo's own
  AGENTS.md docs: don't soften or hide the "honest surprise" (the naive
  off-topic query didn't fail the way it was originally expected to) — the
  page's Section 2 states this directly, same as `demo/AGENTS.md` and
  `src/generation/AGENTS.md` do.
- **The interactive console (`#console`) does real, live computation in the
  visitor's browser — it does not replay canned UI states.** Its JS mirrors
  `src/retrieval/retrieve.py`'s `passes_relevance_threshold()` (a plain
  `topSimilarity >= 0.30` check) and `src/rerank/rerank.py`'s
  `blend_scores()` (log1p citation counts, min-max normalize both signals
  within the pool, `alpha * norm_sim + (1-alpha) * norm_citation`) against
  real per-paper similarity/citation numbers for **6 queries** (3 on-topic,
  3 off-topic — `DATA.on_topic[]` / `DATA.off_topic[]`, each an array of
  `{label, query, papers, report}`), transcribed from
  `demo/sample_output_naive.json` (2 queries) and
  `demo/sample_output_extended.json` (4 queries). The console UI is a
  category segmented-control (on/off-topic) plus a `query-picker` row of
  pills that repopulates for whichever category is active — `state = 
  {category, index, fix1, fix2, alpha}`, `currentEntry()` resolves
  `DATA[state.category][state.index]`. Dragging the alpha slider or
  toggling any control recomputes and re-renders (with a FLIP reorder
  animation) on every input — nothing is precomputed per combination. The
  one thing that is **not** live is the LLM generation step itself: the
  "reveal report" button replays the real, verbatim Claude Opus 5
  transcript captured on 2026-08-13 for whichever of the 6 queries is
  selected, clearly labeled as such, since a static page cannot safely hold
  a live API key to make a fresh call per query/blend combination. If the
  underlying data changes (demo re-run, threshold recalibrated), **both**
  the narrative sections below and this JS `DATA` object need manual
  re-sync — they are not a single source of truth.
- Name/school/personality appear in exactly 2 places, both grounded in the
  author's actual background (not invented): a byline under the hero
  subtitle (`hero__byline`), and a footer credit line (`footer__name`).

## Current state

Built and published as a Claude Artifact
(https://claude.ai/code/artifact/21ef8d2d-33ad-400b-a887-d1bedaf4d80b).
Covers all five narrative sections from the original brief (hero/intro,
naive-pipeline honest surprise, Fix 1, Fix 2 with its two documented
limitations, conclusion), an interactive "Run it yourself" console inserted
right after the hero — now covering **6 real queries (3 on-topic, 3
off-topic)** via a category toggle + query-picker, all 3 off-topic queries
independently confirmed to decline honestly (see the convention above for
exactly what it computes live vs. replays verbatim) — and a "Questions I
Asked" accordion (`#questions`, five items) inserted right before the
conclusion: five real design-review exchanges, condensed but faithful,
covering whether the off-topic query is really about citation count,
whether Fix 1 improves retrieval, whether Fix 2 runs after generation, what
alpha should be set to and how to use it strategically, and whether the
similarity threshold should adapt lower for under-covered/emerging topics.
Accordion uses a CSS grid-template-rows 0fr→1fr transition for smooth
open/close with no JS height measuring.

Byline (hero) and footer credit name Trustan Price and University of
Illinois Urbana-Champaign, with the hero byline tying the project's
verify-before-trusting thesis to two real resume facts (a 100%-audit-
coverage push at Caterpillar, a failure-detection model for NBA
predictions) — sourced from the author's own CV, not invented.

All numbers and quotes are transcribed from the live run or the actual
conversation, not invented. Verified: JS syntax-checked clean (including a
Node-executed simulation confirming all 6 queries produce the correct
Fix 1 gate decision), every element ID referenced by the script exists
exactly once in the markup, section tags balanced, file confirmed UTF-8
with the charset meta tag as the first byte.

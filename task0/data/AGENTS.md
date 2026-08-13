# AGENTS.md — data/

## Responsibility

Pull a small, fixed, real corpus of paper abstracts from the Semantic
Scholar Academic Graph API and save it locally so the rest of the pipeline
has a reproducible, offline corpus to work against.

## Inputs

- A topic/query string (e.g. `"retrieval-augmented generation"`), passed on
  the command line.
- Live network access to `https://api.semanticscholar.org/graph/v1` (no API
  key required for this unauthenticated, rate-limited scale of use).

## Outputs

- `data/papers.json` — the fixed corpus. A JSON array of objects:
  ```json
  {
    "paper_id": "...",
    "title": "...",
    "abstract": "...",
    "year": 2023,
    "citation_count": 412,
    "venue": "...",
    "external_ids": {"DOI": "...", "ArXiv": "...", ...}
  }
  ```
  Papers returned by the API with no abstract are dropped — there's nothing
  to embed — so the on-disk count reflects only papers that actually made it
  into the corpus.

## Conventions

- `fields=title,abstract,year,citationCount,venue,externalIds` on
  `/paper/search`, per the Semantic Scholar Graph API.
- Fetch more candidates than needed (`--fetch-limit`, default 50) and slice
  to the target size (`--target`, default 18) *after* filtering out
  abstract-less results, so the final corpus reliably lands in the
  requested range even though not every match has an abstract.
- Simple exponential backoff on HTTP 429 (unauthenticated requests are
  rate-limited) — this is a single one-shot script, not a production
  crawler, so backoff is minimal by design.
- `data/papers.json` is treated as **fixed** once generated — it's the
  reproducible corpus the rest of the demo and the write-up refer to.
  Re-running `fetch_papers.py` overwrites it deliberately; nothing else in
  the pipeline calls the Semantic Scholar API at runtime.

## Usage

```sh
source .venv/bin/activate
python data/fetch_papers.py "retrieval-augmented generation"
```

## Current state

Run for the topic `"retrieval augmented generation"`. `data/papers.json`
contains 18 papers (2020-2025), citation counts ranging from 64 to 16,973 —
including the original Lewis et al. 2020 RAG paper (16,973 citations) right
alongside several 2025 papers in the 60-200 citation range. This spread is
exactly the shape needed later to demonstrate Fix 2 (citation-weighted
reranking): several papers in the corpus are topically similar but wildly
different in real-world impact.

Note observed in practice: the unauthenticated Semantic Scholar endpoint
returned an immediate `429 Too Many Requests` on the first attempt (shared
public-tier rate limit, not specific to this query). The retry/backoff in
`fetch_papers.py` (5s initial delay, exponential, 6 attempts) resolved it on
the second attempt. Worth flagging in the write-up: the "no API key needed"
unauthenticated tier is real but fragile under any shared/contended network
path — a production system would want an API key (higher limits) rather
than relying on backoff alone.

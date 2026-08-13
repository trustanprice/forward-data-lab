"""Fetch a fixed corpus of paper abstracts from the Semantic Scholar Academic
Graph API (https://api.semanticscholar.org/graph/v1) and save them locally so
the corpus is reproducible for the rest of the pipeline. No API key required
for this scale of unauthenticated use.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import requests

API_BASE = "https://api.semanticscholar.org/graph/v1"
FIELDS = "title,abstract,year,citationCount,venue,externalIds"

OUTPUT_PATH = Path(__file__).resolve().parent / "papers.json"


def _get_with_retry(url: str, params: dict, max_retries: int = 6) -> requests.Response:
    delay = 5.0
    for attempt in range(max_retries):
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 429 and attempt < max_retries - 1:
            print(f"  rate-limited (429), retrying in {delay:.0f}s...", file=sys.stderr)
            time.sleep(delay)
            delay *= 2
            continue
        resp.raise_for_status()
        return resp
    resp.raise_for_status()
    return resp


def fetch_papers(query: str, fetch_limit: int) -> list[dict]:
    params = {"query": query, "fields": FIELDS, "limit": fetch_limit}
    resp = _get_with_retry(f"{API_BASE}/paper/search", params)
    data = resp.json()

    papers = []
    for item in data.get("data", []):
        if not item.get("abstract"):
            continue  # nothing to embed - drop papers with no abstract
        papers.append({
            "paper_id": item["paperId"],
            "title": item.get("title"),
            "abstract": item.get("abstract"),
            "year": item.get("year"),
            "citation_count": item.get("citationCount", 0),
            "venue": item.get("venue"),
            "external_ids": item.get("externalIds") or {},
        })
    return papers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Search query / topic, e.g. 'retrieval augmented generation'")
    parser.add_argument("--target", type=int, default=18, help="Desired final corpus size (10-20 range)")
    parser.add_argument("--fetch-limit", type=int, default=50, help="Candidates to request before filtering to those with abstracts")
    parser.add_argument("--min-count", type=int, default=10, help="Minimum abstracts required to consider the pull successful")
    args = parser.parse_args()

    papers = fetch_papers(args.query, fetch_limit=args.fetch_limit)
    papers = papers[: args.target]

    if len(papers) < args.min_count:
        print(
            f"WARNING: only found {len(papers)} papers with abstracts "
            f"(wanted >= {args.min_count}). Try a broader query or a higher --fetch-limit.",
            file=sys.stderr,
        )

    OUTPUT_PATH.write_text(json.dumps(papers, indent=2))
    print(f"Saved {len(papers)} papers to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

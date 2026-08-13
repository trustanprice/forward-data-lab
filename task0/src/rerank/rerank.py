"""Blend embedding similarity with citation count into a single ranking score.

Fix 2 for the "equal-weighting" flaw: naive top-k retrieval treats a 3-citation
paper and a 16,950-citation paper as equally strong evidence as long as their
embedding similarity is comparable. This reranks an already-retrieved
similarity-based candidate pool by a weighted blend of (normalized
similarity, normalized log-citations) - see src/rerank/AGENTS.md for why
log-transform + pool-relative normalization, and for the tradeoffs that
follow from both.

Run as: python -m src.rerank.rerank "<query>" (retrieves then blends, for ad-hoc inspection)
"""
import math

from src.config import CITATION_BLEND_ALPHA


def _min_max_normalize(values: list[float]) -> list[float]:
    lo, hi = min(values), max(values)
    if hi == lo:
        return [1.0 for _ in values]  # all tied - don't let a flat signal zero out the blend
    return [(v - lo) / (hi - lo) for v in values]


def blend_scores(candidates: list[dict], alpha: float = CITATION_BLEND_ALPHA) -> list[dict]:
    """candidates: list of dicts with "similarity" and "citation_count" (as
    returned by src.retrieval.retrieve.rank()). Returns a new list, sorted
    descending by blended_score, with normalized_similarity /
    normalized_citation / blended_score added to each entry."""
    if not candidates:
        return []

    log_citations = [math.log1p(c["citation_count"]) for c in candidates]
    norm_sim = _min_max_normalize([c["similarity"] for c in candidates])
    norm_cite = _min_max_normalize(log_citations)

    blended = []
    for c, ns, nc in zip(candidates, norm_sim, norm_cite):
        blended.append({
            **c,
            "normalized_similarity": ns,
            "normalized_citation": nc,
            "blended_score": alpha * ns + (1 - alpha) * nc,
        })

    blended.sort(key=lambda c: c["blended_score"], reverse=True)
    return blended


def main():
    import argparse

    from src.config import DEFAULT_TOP_K
    from src.retrieval.retrieve import rank

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--alpha", type=float, default=CITATION_BLEND_ALPHA)
    args = parser.parse_args()

    ranked = rank(args.query, top_k=args.top_k)
    blended = blend_scores(ranked, alpha=args.alpha)

    print(f"{'sim':>6} {'cite':>7} {'blend':>6}  title")
    for r in blended:
        print(f"{r['similarity']:.3f} {r['citation_count']:>7} {r['blended_score']:.3f}  {r['title']}")


if __name__ == "__main__":
    main()

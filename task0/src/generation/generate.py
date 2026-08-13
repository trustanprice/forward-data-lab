"""Feed the top-k retrieved abstracts as grounding context into Claude and
produce a short synthesized report with inline citations back to the
numbered source papers.

Fix 1 (relevance confidence threshold) lives here: answer_query() checks
src.retrieval.retrieve.passes_relevance_threshold() before ever calling the
LLM, and returns a fixed refusal message instead of forcing a synthesis when
nothing in the top-k pool is a genuine match. Pass enforce_threshold=False
(or --no-threshold on the CLI) to reproduce the naive, pre-fix behavior for
the failure demo - same code path, one parameter, so the demo isolates
exactly what Fix 1 changes rather than comparing two different
implementations.

Fix 2 (citation-weighted reranking) is applied optionally via use_rerank /
--rerank, using src.rerank.rerank.blend_scores() on the retrieved pool
before generation.

Run as: python -m src.generation.generate "<query>"
"""
import anthropic

from src.config import ANTHROPIC_MODEL, DEFAULT_TOP_K, SIMILARITY_THRESHOLD
from src.retrieval.retrieve import passes_relevance_threshold, rank

NO_RELEVANT_PAPERS_MESSAGE = (
    "No sufficiently relevant papers found in the corpus for this query "
    "(top similarity score did not clear the {threshold:.2f} confidence threshold)."
)


def _format_context(papers: list[dict]) -> str:
    blocks = []
    for i, p in enumerate(papers, start=1):
        blocks.append(
            f"[{i}] {p['title']} ({p.get('year', 'n.d.')}) — {p.get('citation_count', 0)} citations\n"
            f"{p['abstract']}"
        )
    return "\n\n".join(blocks)


def generate_report(query: str, papers: list[dict]) -> str:
    client = anthropic.Anthropic()
    context = _format_context(papers)

    system = (
        "You are a research assistant. Using ONLY the numbered abstracts provided, "
        "write a short synthesized report (3-5 sentences) answering the user's query. "
        "Cite sources inline using bracketed numbers like [1], [2] that match the "
        "numbered list. Do not use any knowledge beyond what is in the provided abstracts. "
        "If the abstracts don't actually support an answer to the query, say so plainly "
        "instead of forcing a synthesis."
    )
    user_message = f"Query: {query}\n\nSource papers:\n\n{context}"

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        output_config={"effort": "medium"},
        system=system,
        messages=[{"role": "user", "content": user_message}],
    )

    if response.stop_reason == "refusal":
        return "[Claude declined to generate a report for this query.]"

    return "".join(block.text for block in response.content if block.type == "text")


def answer_query(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    threshold: float = SIMILARITY_THRESHOLD,
    use_rerank: bool = False,
    enforce_threshold: bool = True,
) -> dict:
    """Retrieve, optionally rerank (Fix 2), optionally gate on relevance
    (Fix 1), then generate. The threshold check runs against the raw
    similarity-sorted ranking (not the reranked order) - it's asking "is
    there any genuine match at all", which is a property of the retrieval
    scores, not of how the pool gets reordered afterward.
    """
    ranked = rank(query, top_k=top_k)

    if enforce_threshold and not passes_relevance_threshold(ranked, threshold=threshold):
        return {
            "query": query,
            "papers": ranked,
            "report": NO_RELEVANT_PAPERS_MESSAGE.format(threshold=threshold),
            "refused": True,
        }

    papers_for_generation = ranked
    if use_rerank:
        from src.rerank.rerank import blend_scores
        papers_for_generation = blend_scores(ranked)

    report = generate_report(query, papers_for_generation)
    return {"query": query, "papers": papers_for_generation, "report": report, "refused": False}


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--threshold", type=float, default=SIMILARITY_THRESHOLD)
    parser.add_argument("--rerank", action="store_true", help="Apply Fix 2 citation-weighted reranking before generation")
    parser.add_argument("--no-threshold", action="store_true", help="Disable Fix 1 (reproduce naive pre-fix behavior)")
    args = parser.parse_args()

    result = answer_query(
        args.query,
        top_k=args.top_k,
        threshold=args.threshold,
        use_rerank=args.rerank,
        enforce_threshold=not args.no_threshold,
    )
    print(f"Query: {result['query']}\n")
    if result["papers"]:
        print(f"Top similarity: {result['papers'][0]['similarity']:.3f}\n")
    print(result["report"])


if __name__ == "__main__":
    main()

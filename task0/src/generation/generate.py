"""Feed the top-k retrieved abstracts as grounding context into Claude and
produce a short synthesized report with inline citations back to the
numbered source papers.

NOTE: this is the naive (pre-fix) version, used deliberately to run the
failure demo first. It always calls the LLM regardless of how weak the
retrieved similarity scores are - see demo/AGENTS.md for what this produces
on an off-topic query, and src/generation/AGENTS.md for why Fix 1 gets added
after that demo runs.

Run as: python -m src.generation.generate "<query>"
"""
import anthropic

from src.config import ANTHROPIC_MODEL, DEFAULT_TOP_K
from src.retrieval.retrieve import rank


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


def answer_query(query: str, top_k: int = DEFAULT_TOP_K) -> dict:
    papers = rank(query, top_k=top_k)
    report = generate_report(query, papers)
    return {"query": query, "papers": papers, "report": report}


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    args = parser.parse_args()

    result = answer_query(args.query, top_k=args.top_k)
    print(f"Query: {result['query']}\n")
    print(f"Top similarity: {result['papers'][0]['similarity']:.3f}\n")
    print(result["report"])


if __name__ == "__main__":
    main()

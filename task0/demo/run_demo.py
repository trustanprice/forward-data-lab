"""Run the on-topic / off-topic query pair through the pipeline and print a
side-by-side report - the concrete evidence that naive top-k retrieval is
fragile, and that Fix 1 + Fix 2 change the outcome.

--no-threshold reproduces the naive, pre-Fix-1 pipeline (always forces a
synthesis). Without it, Fix 1 is active by default. --rerank additionally
applies Fix 2. Run the same query pair across these flag combinations to
isolate each fix's effect - see AGENTS.md for the recorded before/after.

Run as:
  python -m demo.run_demo --on-topic "..." --off-topic "..." [--rerank] [--no-threshold] [--save results.json]
"""
import argparse
import json

from src.config import DEFAULT_TOP_K, SIMILARITY_THRESHOLD
from src.generation.generate import answer_query


def run_pair(on_topic_query, off_topic_query, top_k, threshold, use_rerank, enforce_threshold):
    results = {}
    for label, query in [("on_topic", on_topic_query), ("off_topic", off_topic_query)]:
        result = answer_query(
            query,
            top_k=top_k,
            threshold=threshold,
            use_rerank=use_rerank,
            enforce_threshold=enforce_threshold,
        )
        results[label] = result

        print(f"\n{'=' * 80}\n{label.upper()}: {query}\n{'=' * 80}")
        if result["papers"]:
            print(f"top similarity: {result['papers'][0]['similarity']:.3f}")
        else:
            print("no candidates retrieved")
        print(f"Fix 1 enforced: {enforce_threshold}   Fix 2 (rerank): {use_rerank}   refused: {result['refused']}\n")
        print(result["report"])
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--on-topic", required=True)
    parser.add_argument("--off-topic", required=True)
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--threshold", type=float, default=SIMILARITY_THRESHOLD)
    parser.add_argument("--rerank", action="store_true", help="Apply Fix 2 citation-weighted reranking")
    parser.add_argument("--no-threshold", action="store_true", help="Disable Fix 1 (reproduce naive pre-fix behavior)")
    parser.add_argument("--save", type=str, default=None, help="Optional path to save results as JSON")
    args = parser.parse_args()

    results = run_pair(
        args.on_topic,
        args.off_topic,
        args.top_k,
        args.threshold,
        use_rerank=args.rerank,
        enforce_threshold=not args.no_threshold,
    )

    if args.save:
        with open(args.save, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved results to {args.save}")


if __name__ == "__main__":
    main()

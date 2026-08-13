"""Embed a query with the same model used for the corpus, rank the corpus by
cosine similarity, and cap at a configurable top-k. Also owns the relevance
confidence check (Fix 1) used by src/generation/.
Run as: python -m src.retrieval.retrieve "<query>"
"""
import json

import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import (
    DEFAULT_TOP_K,
    EMBEDDING_MODEL_NAME,
    EMBEDDINGS_META_PATH,
    EMBEDDINGS_PATH,
    PAPERS_PATH,
    SIMILARITY_THRESHOLD,
)

_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def load_corpus() -> tuple[list[dict], np.ndarray]:
    papers = json.loads(PAPERS_PATH.read_text())
    embeddings = np.load(EMBEDDINGS_PATH)
    meta = json.loads(EMBEDDINGS_META_PATH.read_text())

    if meta["model"] != EMBEDDING_MODEL_NAME:
        raise RuntimeError(
            f"cached embeddings were built with '{meta['model']}', "
            f"but config now points at '{EMBEDDING_MODEL_NAME}' - re-run embed.py"
        )
    if [p["paper_id"] for p in papers] != meta["paper_ids"]:
        raise RuntimeError(
            "data/papers.json has changed since embeddings were cached - re-run embed.py"
        )
    return papers, embeddings


def embed_query(query: str) -> np.ndarray:
    model = _get_model()
    vec = model.encode([query], normalize_embeddings=True)[0]
    return np.asarray(vec, dtype=np.float32)


def rank(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """Return the top_k papers most similar to query, sorted descending by
    cosine similarity. Each result is the paper dict plus a "similarity" field."""
    papers, embeddings = load_corpus()
    query_vec = embed_query(query)
    similarities = embeddings @ query_vec  # both L2-normalized -> dot product == cosine similarity

    order = np.argsort(-similarities)[:top_k]
    return [{**papers[i], "similarity": float(similarities[i])} for i in order]


def passes_relevance_threshold(ranked_papers: list[dict], threshold: float = SIMILARITY_THRESHOLD) -> bool:
    """Fix 1. ranked_papers must already be sorted descending by similarity
    (as returned by rank()) - this checks the top score against the corpus-
    calibrated similarity floor below which nothing in the pool counts as a
    genuine match."""
    return bool(ranked_papers) and ranked_papers[0]["similarity"] >= threshold


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    args = parser.parse_args()

    results = rank(args.query, top_k=args.top_k)
    for r in results:
        print(f"{r['similarity']:.3f}  [{r['citation_count']:>6} cites]  {r['title']}")


if __name__ == "__main__":
    main()

"""Embed each paper's abstract with a local sentence-embedding model and cache
the resulting vectors so retrieval never has to re-embed the corpus.
Run as: python -m src.embeddings.embed
"""
import json

import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import (
    EMBEDDING_MODEL_NAME,
    EMBEDDINGS_DIR,
    EMBEDDINGS_META_PATH,
    EMBEDDINGS_PATH,
    PAPERS_PATH,
)


def load_papers() -> list[dict]:
    return json.loads(PAPERS_PATH.read_text())


def embed_corpus(papers: list[dict]) -> np.ndarray:
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    texts = [f"{p['title']}\n\n{p['abstract']}" for p in papers]
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return np.asarray(embeddings, dtype=np.float32)


def main():
    papers = load_papers()
    embeddings = embed_corpus(papers)

    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
    np.save(EMBEDDINGS_PATH, embeddings)
    EMBEDDINGS_META_PATH.write_text(json.dumps({
        "model": EMBEDDING_MODEL_NAME,
        "count": len(papers),
        "dim": int(embeddings.shape[1]),
        "paper_ids": [p["paper_id"] for p in papers],
    }, indent=2))
    print(f"Embedded {len(papers)} papers -> {EMBEDDINGS_PATH} (dim={embeddings.shape[1]})")


if __name__ == "__main__":
    main()

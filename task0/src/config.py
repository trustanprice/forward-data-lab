"""Shared paths and constants for the pipeline. Import from here rather than
hardcoding paths/model names in individual modules."""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# data/
DATA_DIR = ROOT_DIR / "data"
PAPERS_PATH = DATA_DIR / "papers.json"

# src/embeddings/
EMBEDDINGS_DIR = ROOT_DIR / "src" / "embeddings" / "cache"
EMBEDDINGS_PATH = EMBEDDINGS_DIR / "embeddings.npy"
EMBEDDINGS_META_PATH = EMBEDDINGS_DIR / "embeddings_meta.json"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# src/retrieval/
DEFAULT_TOP_K = 8

# src/generation/ (Fix 1)
# Calibrated against real queries against this corpus (see demo/AGENTS.md):
# an on-topic query's top-8 similarities ranged 0.396-0.567; a clearly
# off-topic query's ranged -0.034-0.024. 0.30 sits with wide margin on both
# sides of that gap. This is a corpus/embedding-model-specific number, not a
# universal constant - see src/retrieval/AGENTS.md for why.
SIMILARITY_THRESHOLD = 0.30

# src/rerank/ (Fix 2)
# Weight on normalized similarity vs. normalized log-citation-count when blending.
# 0.5 = equal weight. Raise toward 1.0 to favor topical relevance, lower toward
# 0.0 to favor citation impact.
CITATION_BLEND_ALPHA = 0.5

# src/generation/
ANTHROPIC_MODEL = "claude-opus-5"

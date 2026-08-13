# forward-data-lab

The task0 and other potential tasks for the forward data lab.

## task0 — RAG retrieval pipeline demo

A minimal demonstration of naive top-k retrieval failing on off-topic
queries, and two fixes for it:

- **Fix 1 — relevance confidence threshold**: refuse to synthesize when
  nothing in the candidate pool clears a similarity bar.
- **Fix 2 — citation-weighted reranking**: blend embedding similarity with
  citation count so well-established papers outrank obscure ones.

See [task0/AGENTS.md](task0/AGENTS.md) for full project details.

### Setup

```bash
cd task0
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set your key:

```bash
cp .env.example .env
# then edit task0/.env and set:
# ANTHROPIC_API_KEY=sk-ant-...
```

### Running the demo

The demo runs the same on-topic/off-topic query pair through the pipeline
under three flag combinations, to isolate each fix's effect. Run all
commands from `task0/`:

```bash
ON="How does retrieval-augmented generation reduce hallucinations in large language models?"
OFF="What are the effects of ocean acidification on coral reef ecosystems?"
```

**a) Naive pipeline** (pre-Fix-1, forces a synthesis even off-topic):
```bash
python -m demo.run_demo --on-topic "$ON" --off-topic "$OFF" --no-threshold --save results_naive.json
```

**b) After Fix 1** (default flags — threshold enforced, no rerank):
```bash
python -m demo.run_demo --on-topic "$ON" --off-topic "$OFF" --save results_fix1.json
```

**c) After Fix 1 + Fix 2** (threshold + citation-weighted rerank):
```bash
python -m demo.run_demo --on-topic "$ON" --off-topic "$OFF" --rerank --save results_fix1_fix2.json
```

What to look for in the output:

- **(a)** the off-topic query gets a forced, plausible-sounding synthesis
  from irrelevant papers (`refused: False` despite near-zero similarity).
- **(b)** the off-topic query shows `refused: True` with a "no sufficiently
  relevant papers" message; the on-topic query still synthesizes normally.
- **(c)** same refusal behavior as (b), but the on-topic report's citations
  reflect the citation-weighted reranking.

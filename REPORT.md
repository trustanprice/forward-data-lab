# Surveying and Building an Automatic Knowledge Agent

**Trustan Price — Forward Data Lab, First Task**

---

## Q1: How well does Asta work, and how does it differ from Google Scholar?

Watching Asta process the query *"How have retrieval-augmented generation (RAG) architectures evolved from separate retriever-plus-generator pipelines to retrieval capabilities integrated directly into large language models?"*, the first thing visible in its step log is that it does not search on the literal sentence. It silently rewrites the question into a re-formulated research statement, generates a second, separate keyword search string built specifically for matching against its paper index, then applies a field filter — in this case restricting to Computer Science. That is a deliberate query-optimization step, not something the user has to do themselves.

Running the exact same unmodified sentence through Google Scholar produces zero results. Scholar states outright that the search "did not match any articles." That is a real, reproducible gap: Scholar expects keyword-style input and will not rescue a full natural-language question the way Asta does internally. Only after manually shortening the question to "agentic or iterative RAG methods" did Scholar return a usable results page. The query-formulation step Asta performs invisibly is a step a Google Scholar user has to perform themselves, by trial and error, before getting anything back.

Once Scholar does return results, its list is not as "old school" as it first appears — each entry already shows a citation count inline ("Cited by 25," "Cited by 12") without needing to click into the paper. What Scholar genuinely lacks is synthesis. It hands back a flat list of titles and citation counts and leaves the user to open each one, read the abstract, and assemble the connections manually. That manual-assembly burden is real, and it is the correct version of the "old school" observation, rather than a lack of citation data.

Asta's retrieval process is not a single flat lookup either. It pulls from a stated corpus of "12M+ open access papers," retrieves roughly 250-plus candidate passages plus a handful more from a secondary keyword pass, then explicitly re-ranks and aggregates that pool down to a fixed cap before writing anything — narrowing to "up to top 50 papers" before selecting the roughly 34 to 53 it actually cites. That is a top-k step, just applied after two retrieval passes and before the writing stage, rather than absent altogether.

On the hallucination question, checking the expanded citation list against known literature holds up well: real, verifiable, highly cited foundational papers (Lewis et al. 2020's original RAG paper, Karpukhin et al. 2020's Dense Passage Retrieval paper, Guu et al. 2020's REALM paper, Devlin et al.'s BERT paper), each with citation counts consistent with their known real-world impact. Every title is also a clickable link back to the source. That combination of real papers, visible citation counts, and clickable provenance is Asta's strongest feature relative to Scholar's flat list.

But a narrower concern remains: Asta shows a paper's citation count if you go looking in the expanded source list, but it does not weight or rank the *narrative* by that impact. A 3-citation 2026 paper and a 16,950-citation 2020 paper can appear side by side, treated as equally strong evidence in the prose, even though the data to distinguish them was available the entire time. That detail is the thread this report follows into Q2 and Q3: Asta clearly has the pieces of something powerful working under the hood — query rewriting, large-scale retrieval, re-ranking, citation tracking — but what it does with those pieces once assembled is where the story gets more complicated.

---

## Q2: How does Asta Find Papers work under the hood?

Asta's first move is quiet but telling: it takes a natural-language question and silently rewrites it into a cleaner research statement, then generates a second, separate keyword string built specifically for its search index. This is the moment the system stops treating the question as a sentence and starts treating it as a target — translating intent into something its retrieval engine can act on.

From there it searches at a scale not practical for a human to replicate by hand: embedding-based similarity across a stated corpus of over twelve million open-access papers, surfacing passages related to the idea behind the question rather than just its literal words, backed by a secondary keyword pass over abstracts to catch anything the meaning-based search missed. This is the augmentation half of the pattern — evidence assembled before a single sentence of the report is written.

The next stage is where the system's credibility quietly hangs in the balance: Asta reranks everything retrieved and narrows a large candidate pool down to a hard cap, and only the papers that survive that cut ever make it into the report. This "top-k with a cap" behavior is powerful because it lets a model reason over a fixed, manageable set of evidence instead of drowning in millions of documents — and fragile for the exact same reason. Whatever is left out at this step is invisible for the rest of the process, with no visible mechanism inside Asta for double-checking whether the shortlist actually contains the right papers.

Only after that does generation happen. Asta drafts an outline, then writes each section one at a time, pulling specific claims and quotes from the surviving papers as it goes — a report built out of smaller reports, dozens of tightly scoped syntheses stitched into one continuous document. Each of those smaller reports is only as trustworthy as the sources it was handed.

Placing this next to the current academic conversation is where the bigger picture opens up. Techniques for fixing top-k retrieval — adaptive and query-dependent cutoffs instead of a fixed number, hybrid dense-and-sparse search to widen the net, reranking models to correct a noisy first pass, agentic and iterative retrieval that goes back for more evidence when the first attempt comes up short, and faithfulness verification that checks whether a generated claim actually traces back to its source — are direct answers to the exact pressure point sitting inside Asta's own pipeline. Asta clearly does some of this already: it reranks, it caps, it reformulates the query before searching. What it does not appear to do, at least not visibly, is loop back for more evidence when a section's sources are thin, or verify after the fact that what it wrote is faithful to what the paper actually says.

The open question is not whether Asta can find papers — it clearly can, at a scale no person could match by hand. The open question is whether it can reliably find the true best set of papers out of millions, confirm those papers actually support what gets written about them, and compile many independently generated small reports into one whole without quietly losing accuracy in the stitching. That gap is exactly what Q3 investigates.

---

## Q3: A minimal, inspectable version of the same pipeline

### What is the task?

The task is the exact pressure point identified in Q2: **deciding when retrieved evidence is actually sufficient to answer a query, and weighting a generated synthesis by the real-world strength of its sources** — rather than treating every retrieved passage as equally trustworthy evidence once it clears a top-k cutoff. Concretely, this decomposes into two sub-problems: (1) a relevance-confidence check before generation ever happens, and (2) ranking retrieved evidence by more than raw semantic similarity.

### Why is it important?

Q1's central finding motivates this directly: Asta surfaces real, correctly cited papers, but a 3-citation paper and a 16,950-citation seminal paper are presented as equally strong evidence in its narrative. The underlying data to distinguish them — citation count — is available and displayed, but never used to shape the synthesis. At the scale Asta operates (millions of papers, a handful of them actually load-bearing for any given question), a user has no way to tell, from the prose alone, whether a claim rests on well-established consensus or a single obscure preprint.

### Why is it challenging?

Three reasons surfaced directly while building this: (1) retrieval quality is continuous, not binary — there is no natural cutoff between "relevant" and "irrelevant" without calibrating against real data; (2) small or narrow corpora make embedding similarity noisy, so a threshold has to be set empirically, not assumed; and (3) blending two signals (semantic similarity and citation impact) requires normalizing them onto comparable scales, since raw citation counts span orders of magnitude while cosine similarity is bounded. A fourth, less obvious reason emerged during testing (see Demo, below): even when retrieval is genuinely fragile, a capable model can sometimes mask that fragility by noticing the mismatch on its own — which means output quality alone is not proof that retrieval worked, and a system needs a mechanical guarantee rather than trust in one model's judgment.

### State of the art

Current research addresses this pressure point from several angles: adaptive, query-dependent retrieval cutoffs instead of a fixed top-k; hybrid dense-and-sparse search to widen recall before ranking; learned reranking models (cross-encoders) to correct a noisy first-pass retrieval; agentic and iterative retrieval — e.g., Self-RAG (Asai et al., 2023) and Corrective RAG (Yan et al., 2024) — which loop back for more evidence when a first retrieval attempt is weak; and faithfulness verification, which checks post-hoc whether a generated claim traces back to its cited source. The foundational RAG architecture itself (Lewis et al., 2020) combined a pre-trained generator with a dense retriever (building on Dense Passage Retrieval, Karpukhin et al., 2020, and REALM, Guu et al., 2020); RAGAs (Es et al., 2023) is a widely used reference-free framework for evaluating exactly the retrieval/generation split this task is about.

### Implementation

A minimal pipeline was built end-to-end, mirroring Asta's retrieve → rerank → cap → generate flow at inspectable scale:

- **Corpus:** 18 real papers on retrieval-augmented generation, pulled from the Semantic Scholar Academic Graph API, citation counts ranging 64–16,973 (spanning the seminal 2020 Lewis et al. paper to recent 2025 work).
- **Retrieval:** local sentence embeddings (`all-MiniLM-L6-v2`), cosine similarity, configurable top-k.
- **Fix 1 — relevance threshold:** a calibrated similarity gate (0.30) checked against the top-ranked result before any generation call is made. Calibration was done against real, not assumed, data: on-topic queries in this corpus score 0.40–0.65 on their top result; off-topic queries score effectively at noise level, -0.06 to 0.03.
- **Fix 2 — citation-weighted reranking:** blends normalized cosine similarity with log-scaled citation count, computed within the retrieved pool (relative, not global, normalization).
- **Generation:** Claude Opus 5, given the surviving top-k abstracts as context, producing a short report with inline citations back to source papers.

### Demo — how it works, including an honest surprise

The pipeline was run live against six real queries — three clearly on-topic, three clearly off-topic — rather than a single scripted pair, to confirm the pattern generalizes:

| Query | Topic | Top similarity | Naive-pipeline behavior |
|---|---|---|---|
| "How does RAG reduce hallucinations in LLMs?" | on-topic | 0.567 | Answered — well-grounded, correctly cited |
| "Applications of RAG in healthcare and medicine?" | on-topic | 0.562 | Answered — well-grounded, correctly cited |
| "How do researchers benchmark and evaluate RAG systems?" | on-topic | 0.649 | Answered — well-grounded, correctly cited |
| "Effects of ocean acidification on coral reefs?" | off-topic | 0.024 | Declined on its own (see below) |
| "What causes the northern lights' colors?" | off-topic | 0.014 | Correctly recognized as unrelated |
| "Economic causes of the fall of the Roman Empire?" | off-topic | 0.034 | Correctly recognized as unrelated |

The on-topic/off-topic separation in raw similarity is stark and consistent — a real ~0.35–0.55-wide gap between "relevant" and "noise" across every query pair tested, which is what makes a fixed threshold (0.30) a defensible calibration rather than an arbitrary guess.

The more interesting result was on the generation side. With Fix 1 *disabled* (the naive, pre-fix configuration), the off-topic ocean-acidification query still called Claude Opus 5 with all 8 near-zero-similarity papers as context — and the model did **not** force a synthesis. It responded directly: *"The provided abstracts do not support an answer to this query... None of them address ocean acidification, coral reefs, marine biology, or any environmental science topic."* That is a genuinely more interesting finding than a scripted failure would have been, and it is reported honestly rather than smoothed over: retrieval itself is unambiguously fragile (the similarity scores are noise-level, full stop), but whether the *report* reflects that fragility depended, in the naive configuration, entirely on one model's prompt-following behavior in one test. That recovery was not free (a full paid API call still happened), not deterministic, not inspectable in advance, and — notably — not what direct testing found Asta itself doing in Q1.

That is precisely the argument for Fix 1: it replaces "hope the model notices" with a mechanical, free, deterministic guarantee. With the threshold enforced, the off-topic query is refused *before* any LLM call is made, with the message: *"No sufficiently relevant papers found in the corpus for this query (top similarity score did not clear the 0.30 confidence threshold)."* Same outcome as the lucky naive run — but now guaranteed regardless of which model, or how carefully it was prompted, sits behind the pipeline.

Fix 2 was verified two ways. On ranking: the 16,973-citation seminal 2020 paper moves from rank 6 (pure similarity) to rank 2 (citation-blended) on the benchmark on-topic query — a clear, direct effect. But two honest limitations were found and documented rather than hidden: (1) at a smaller top-k (5 instead of 8), the seminal paper is excluded from the candidate pool *before* reranking ever runs — reranking cannot rescue a highly-cited paper that similarity-based retrieval already cut; and (2) its effect on the *generated narrative* was smaller than its effect on ranking, likely because citation counts are already visible as plain text in the model's context regardless of list position. Reranking changes prominence, not survival — top-k still decides who is in the room.

The full pipeline, all six live query results, and the reasoning behind each finding are committed at `github.com/trustanprice/forward-data-lab`, including an interactive walkthrough demo.

### A novel idea to improve it

The natural next layer, directly motivated by both this project and Q2's observation about Asta, is **post-hoc faithfulness verification**: after a report is generated, mechanically check whether each inline citation's specific claim is actually supported by that paper's abstract (or full text), rather than trusting that a correct-looking citation implies a correct claim. This is the same category of fix as Fix 1 — replacing "hope the model got it right" with something inspectable and guaranteed — applied one stage later in the pipeline, at the point where a synthesized sentence meets its source. Given that this project's own naive pipeline showed a capable model can sometimes catch its own retrieval failures and sometimes cannot be assumed to, a mechanical check after generation closes the gap that neither threshold-gating nor reranking can: both act before generation, but nothing in this pipeline — or, from what is visible, in Asta — currently verifies the output itself.

---

## Repository

All code, AGENTS.md documentation, raw live-run output, and the interactive demo are at `github.com/trustanprice/forward-data-lab`.

*[Insert: screenshot of Asta step log; screenshot of Google Scholar "did not match any articles"; link to 3-minute demo video]*

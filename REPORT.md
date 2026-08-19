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

Scored against explicit criteria rather than narrative alone, even this single query pair is instructive:

| Criterion | Asta | Google Scholar |
|---|---|---|
| **Accuracy** (cited papers independently verifiable) | 4/4 spot-checked papers real and correctly attributed | N/A — a citation list, not a synthesis, so there is nothing to verify beyond the listing itself |
| **Efficiency** (reformulation attempts before a usable result) | 0 — the natural-language question worked immediately | 1 — required manually rewriting to a keyword string after an empty result |
| **Coverage** (candidate pool before final selection) | 250+ retrieved, narrowed to "up to top 50," 34–53 actually cited | 10 results per page, not visibly ranked by anything but Scholar's own relevance heuristic |
| **Ease of use** (steps from question to a synthesized answer) | 1 — ask, read the report | 3+ — search, open each result individually, manually assemble the connections |
| **Evidence weighting** (does the output reflect source impact) | No — a 3-citation and a 16,950-citation source are treated as equally strong evidence | N/A — no synthesis step exists to weight |

That single query is illustrative, not systematic — so the same scoring was repeated live across five query archetypes chosen to stress different failure modes: broad conceptual, narrow technical, comparative, recent/emerging-topic, and ambiguous. Each was run verbatim in both tools; every citation reported below was independently spot-checked against the real publication, not assumed correct because it looked plausible.

### Systematic multi-query comparison

**Query 1 — Broad conceptual:** *"What is retrieval-augmented generation?"*

| Criterion | Asta | Google Scholar |
|---|---|---|
| **Reformulation attempts** | 1 — accepted verbatim, no rewrite needed | 1 — accepted verbatim, no rewrite needed |
| **Candidate pool / coverage** | Not shown — Asta answered in chat mode (no paper-finder search triggered); no paper count anywhere in the response or its steps panel | "About 72,400 results" after clicking "See all results" (initial view showed only a single "best result") |
| **Citation counts** | Not shown — no papers were attached to this answer at all | Visible per result as "Cited by N" (e.g., 73, 1024, 139, 1645) |
| **Evidence weighting** | N/A — zero sources cited, so nothing to weight | N/A — Scholar never produces synthesis text |
| **Accuracy spot-check** | Not possible — 0 papers cited | 2/2 checked out (Zhao et al. survey, arXiv:2402.19473; Klesel & Wittmann, *BISE*, Springer) |
| **Steps to a usable answer** | 2 (type, send) — appears after ~7s | 2 for single result; 3 for full list (+"See all results") |

**Query 2 — Narrow technical:** *"What is the effect of chunk size on retrieval-augmented generation accuracy?"*

| Criterion | Asta | Google Scholar |
|---|---|---|
| **Reformulation attempts** | 1 — accepted verbatim | 1 — accepted verbatim |
| **Candidate pool / coverage** | "74 Papers" explicitly shown (2 pages), each tagged Perfectly Relevant / Relevant / Somewhat Relevant | "About 19,600 results" after "See all results" (2 near-duplicate top hits shown first) |
| **Citation counts** | Shown per card as "Cited by N" (range 1–178); very new 2026 papers show none | Shown inline where available; brand-new preprints show none |
| **Evidence weighting** | Not explicit — the 5-paper prose synthesis cites only papers with ≥41 citations, but never states this; narrative confidence reads uniform regardless of citation count | N/A — no synthesis |
| **Accuracy spot-check** | 2/2 checked out (CRUD-RAG, *ACM TOIS*; BABILong, NeurIPS 2024) | 2/2 checked out (Bhat et al., "Rethinking Chunk Size," arXiv:2505.21700; Li, Stenzel & Eickhoff, ACL Anthology 2025) |
| **Steps to a usable answer** | 3 (click box, type, send) — appears after ~65s, papers panel included with no extra click | 3 (type, search, "See all results") |

**Query 3 — Comparative:** *"Dense retrieval vs. sparse retrieval for RAG: which performs better on multi-hop questions?"*

| Criterion | Asta | Google Scholar |
|---|---|---|
| **Reformulation attempts** | 1 — accepted verbatim, including punctuation | 1 — accepted verbatim |
| **Candidate pool / coverage** | Only "7 Papers" (smaller pool than Q2), all tagged "Relevant" (none "Perfectly Relevant") | "About 4,030 results," full ranked list shown immediately |
| **Citation counts** | Only 1 of 7 papers shows a "Cited by" figure (8); the other 6 (mostly 2025–26 preprints) show none | Shown inline for every result (e.g., 25, 2, 145, 1, 2) |
| **Evidence weighting** | The sharpest gap found: synthesis closes with *"Confidence: Very high — Multiple recent, directly comparative studies support these findings,"* despite 6 of 7 sources having zero visible citations and being unreviewed 2026 preprints — no distinction drawn between the one weakly-cited source and the uncited ones | N/A — no synthesis |
| **Accuracy spot-check** | 2/2 checked out (Sidiropoulos et al. 2021, ACL Anthology; Shaikh, arXiv:2606.21553) | 2/2 checked out (LevelRAG, arXiv:2502.18139; Xiong et al., MDR, arXiv:2009.12756) |
| **Steps to a usable answer** | 3 — appears after ~110s (longest wait observed) | 2 (type, search) — full list appeared immediately |

**Query 4 — Recent/emerging topic:** *"What are the latest agentic RAG approaches published in 2026?"*

| Criterion | Asta | Google Scholar |
|---|---|---|
| **Reformulation attempts** | 1 — verbatim; correctly auto-parsed "2026" as a metadata date filter, separate from content criteria | 2 — verbatim query mixed years (top hit was a 2025 paper with 593 citations); required manually clicking "Since 2026" |
| **Candidate pool / coverage** | Internally inconsistent: synthesis text claims "51 papers published in 2026," but the attached results panel shows "72 Papers" | "About 18,600 results" unfiltered; "About 17,300 results" after "Since 2026" |
| **Citation counts** | Sparse and low (mostly 1–5, up to 34), since 2026 is the current year; most cards show none | Shown where available (e.g., 5, 3); many show none |
| **Evidence weighting** | All cards uniformly tagged "Perfectly Relevant" (unlike Q2/Q3); synthesis narrates all equally without flagging that they're largely unvetted preprints | N/A — no synthesis |
| **Accuracy spot-check** | 2/2 checked out (A-RAG, arXiv:2602.03442; SoK: Agentic RAG, arXiv:2603.07379) | 2/2 checked out (Ferrazzi et al., arXiv:2601.07711; Singh & Ehtesham survey, arXiv:2501.09136) |
| **Steps to a usable answer** | 3 — appears after ~70s | 3 (type, search, "Since 2026" filter) |

**Query 5 — Ambiguous/underspecified:** *"How does RAG help with reasoning?"*

| Criterion | Asta | Google Scholar |
|---|---|---|
| **Reformulation attempts** | 1 — accepted verbatim | 1 — accepted verbatim |
| **Candidate pool / coverage** | Not shown — chat-mode answer again, no paper search triggered, no "View N Papers" link at all | "About 136,000 results" — largest pool of any query, full list shown immediately |
| **Citation counts** | Not shown — zero papers attached | Shown inline for every result (68, 70, 40, 48, 19) |
| **Evidence weighting** | The most acute instance of the gap: closes with *"Confidence: Very high — these points are well established in the literature,"* with literally zero cited sources to check that claim against | N/A — no synthesis |
| **Accuracy spot-check** | Not possible — 0 papers cited | 2/2 checked out (Gao et al., "Synergizing RAG and Reasoning," arXiv:2504.15909; Li & Zhang, "Towards Agentic RAG with Deep Reasoning," arXiv:2507.09477, EMNLP 2025) |
| **Steps to a usable answer** | 3 — appears after ~10s (fastest response, but with the least evidence behind it) | 2 (type, search) — full list immediate |

Across the five, Asta's advantage over Scholar — a synthesized, sourced answer instead of a raw list — held up consistently only on the two mid-complexity queries (narrow technical, comparative), where it reliably triggered full paper-finder mode, surfaced 7–74 candidate papers with relevance tags, and produced genuinely useful prose. It also handled the date-scoped query better, auto-parsing "2026" as a filter where Scholar needed a manual sidebar click — though Asta's own paper count was internally inconsistent there (51 claimed vs. 72 shown).

The advantage disappeared entirely on the broad conceptual and ambiguous queries: Asta silently fell back to a chat-only answer with zero cited papers, zero candidate-pool count, and no paper-finder option at all — functionally worse than Scholar, which always returned a scannable, citation-annotated list regardless of query phrasing.

The citation-visible-but-unweighted gap first raised from a single query in this report's opening held up under repetition, and got worse rather than better as queries got harder to ground: mild on the chunk-size query (the cited papers happened to be moderately-to-highly cited, but the prose never says so), sharp on the comparative query (six of seven sources uncited, yet reported as "Confidence: Very high"), and most acute on the ambiguous query, where "well established in the literature" was asserted with no sources at all. Scholar, by contrast, never makes evidentiary claims — every citation count is visible and weighting is left entirely to the reader. Every one of the 16 checkable citations across all five queries (Q1 and Q5 produced none from Asta) matched a real, verifiable publication — Asta's hallucination risk on *paper existence* stayed at zero across this sweep; its risk sits entirely in unweighted, sometimes evidence-free confidence claims.

---

## Q2: How does Asta Find Papers work under the hood?

This account is built from three sources, not the interface alone: direct interaction with Asta's live chat, reading its exposed step log across multiple test queries; examination of Ai2's own open-source implementation of the exact service tested (see below); and a literature search for prior work on retrieval-augmented systems generally and on Asta specifically. Where the step log and the codebase agree, that is treated as confirmed; where the codebase adds detail the UI does not surface, that is called out explicitly.

Asta's first move is quiet but telling: it takes a natural-language question and silently rewrites it into a cleaner research statement, then generates a second, separate keyword string built specifically for its search index. This is the moment the system stops treating the question as a sentence and starts treating it as a target — translating intent into something its retrieval engine can act on.

From there it searches at a scale not practical for a human to replicate by hand: embedding-based similarity across a stated corpus of over twelve million open-access papers, surfacing passages related to the idea behind the question rather than just its literal words, backed by a secondary keyword pass over abstracts to catch anything the meaning-based search missed. This is the augmentation half of the pattern — evidence assembled before a single sentence of the report is written.

The next stage is where the system's credibility quietly hangs in the balance: Asta reranks everything retrieved and narrows a large candidate pool down to a hard cap, and only the papers that survive that cut ever make it into the report. This "top-k with a cap" behavior is powerful because it lets a model reason over a fixed, manageable set of evidence instead of drowning in millions of documents — and fragile for the exact same reason. Whatever is left out at this step is invisible for the rest of the process, with no visible mechanism inside Asta for double-checking whether the shortlist actually contains the right papers.

Only after that does generation happen. Asta drafts an outline, then writes each section one at a time, pulling specific claims and quotes from the surviving papers as it goes — a report built out of smaller reports, dozens of tightly scoped syntheses stitched into one continuous document. Each of those smaller reports is only as trustworthy as the sources it was handed.

This account is not built from the UI alone. Ai2 publishes a frozen snapshot of the exact service tested here as open source, `asta-paper-finder` (Allen Institute for AI, n.d.), and reading it confirms and sharpens what the step log suggests rather than contradicting it. A query is first transformed into a structured object, then handed to an execution planner that routes it to one of several specialized workflows depending on the paper-seeking intent detected — a broad survey request and a narrow known-item lookup do not take the same code path. Each workflow applies LLM-based relevance judgments to retrieved abstracts and snippets, and a final ranking step explicitly weights content relevance together with any criteria named in the query itself, such as "early works on" or "influential" — a detail invisible from casual testing but present directly in the repository's own documentation. The codebase also documents two execution modes: a roughly 30-second fast path and a roughly 3-minute "diligent" path that fetches more exhaustively, which explains timing variation a user would otherwise have no way to attribute to anything. Checking the implementation, not just the interface, is what turns "it appears to reformulate, retrieve, rerank, and cap" from an inference into a verified claim.

The literature also studies Asta directly, not only the general problem class it belongs to. Orduña-Malea and Lopezosa (2026) empirically analyze the citation behavior of Ai2 Asta's generated reports at scale, finding that Asta had cited over two million distinct publications across their sample, 55.2% of them published since 2020, concentrated in a small set of venues (Scientometrics, PLoS One, and arXiv.org together accounting for roughly 30% of citations). That is an independent, large-sample confirmation of the same asymmetry this report raises from a single query: Asta cites real, verifiable, often-recent work at real scale — but a citation-behavior study external to this project is exactly the kind of evidence needed to know whether the 3-citation-versus-16,950-citation problem observed here is a one-off or a structural pattern, and a skew this strong toward very recent sources is consistent with a system that does not weight citations by established impact when selecting or presenting them.

Placing this next to the current academic conversation is where the bigger picture opens up. Techniques for fixing top-k retrieval — adaptive and query-dependent cutoffs instead of a fixed number, hybrid dense-and-sparse search to widen the net, reranking models to correct a noisy first pass, agentic and iterative retrieval that goes back for more evidence when the first attempt comes up short (Self-RAG, Asai et al., 2023; Corrective RAG, Yan et al., 2024), and faithfulness verification that checks whether a generated claim actually traces back to its source (evaluated with reference-free frameworks such as RAGAs, Es et al., 2023) — are direct answers to the exact pressure point sitting inside Asta's own pipeline. Asta clearly does some of this already: it reranks, it caps, it reformulates the query before searching. What it does not appear to do, at least not visibly in the interface or the published `asta-paper-finder` snapshot, is loop back for more evidence when a section's sources are thin, or verify after the fact that what it wrote is faithful to what the paper actually says.

The open question is not whether Asta can find papers — it clearly can, at a scale no person could match by hand. The open question is whether it can reliably find the true best set of papers out of millions, confirm those papers actually support what gets written about them, and compile many independently generated small reports into one whole without quietly losing accuracy in the stitching. That gap is exactly what Q3 investigates.

---

## Q3: A minimal, inspectable version of the same pipeline

### What is the task?

The task is the exact pressure point identified in Q2: **deciding when retrieved evidence is actually sufficient to answer a query, and weighting a generated synthesis by the real-world strength of its sources** — rather than treating every retrieved passage as equally trustworthy evidence once it clears a top-k cutoff. Concretely, this decomposes into two sub-problems: (1) a relevance-confidence check before generation ever happens, and (2) ranking retrieved evidence by more than raw semantic similarity.

### Why is it important?

Q1's central finding motivates this directly: Asta surfaces real, correctly cited papers, but a 3-citation paper and a 16,950-citation seminal paper are presented as equally strong evidence in its narrative. The underlying data to distinguish them — citation count — is available and displayed, but never used to shape the synthesis. At the scale Asta operates (millions of papers, a handful of them actually load-bearing for any given question), a user has no way to tell, from the prose alone, whether a claim rests on well-established consensus or a single obscure preprint.

### Why is it challenging?

Three reasons surfaced directly while building this: (1) retrieval quality is continuous, not binary — there is no natural cutoff between "relevant" and "irrelevant" without calibrating against real data; (2) small or narrow corpora make embedding similarity noisy, so a threshold has to be set empirically, not assumed; and (3) blending two signals (semantic similarity and citation impact) requires normalizing them onto comparable scales, since raw citation counts span orders of magnitude while cosine similarity is bounded. A fourth, less obvious reason emerged during testing (see Demo, below): even when retrieval is genuinely fragile, a capable model can sometimes mask that fragility by noticing the mismatch on its own — which means output quality alone is not proof that retrieval worked, and a system needs a mechanical guarantee rather than trust in one model's judgment.

### Problem formulation

Stated formally: let a query `q` be embedded as `embed(q)`, and let a corpus `C = {p_1, ..., p_n}` consist of papers each with an embedding `e_i` and a citation count `c_i`. Define similarity `sim(q, p_i) = cos(embed(q), e_i)`. A naive top-k pipeline selects `S = top_k({p_i : sim(q, p_i)})` and passes `S` to a generator `G(q, S) → R` unconditionally, regardless of how weak the strongest member of `S` actually is.

This project treats that as two coupled sub-problems the naive pipeline conflates into one step:

1. **Abstention.** Let `p* = argmax_i sim(q, p_i)`. The system should generate only if `sim(q, p*) ≥ τ` for a corpus-calibrated threshold `τ`; otherwise it should return an explicit refusal rather than pass `S` to `G` at all.
2. **Evidentiary weighting.** Among papers that do reach `G`, the weight each `p_i ∈ S` carries in the synthesis should track a combined score `score(p_i) = α · norm(sim(q, p_i)) + (1 − α) · norm(log(1 + c_i))`, not `sim(q, p_i)` alone — so a paper's real-world influence, not just its wording overlap with the query, shapes how much the synthesis leans on it.

Fix 1, below, implements the abstention rule directly. Fix 2 implements the weighting rule. Framed this way, the two are not two unrelated patches; they are the two halves of one underspecified step in the original pipeline made explicit.

### Techniques

**Fix 1 (abstention / relevance threshold).** `passes_relevance_threshold(S) := sim(q, p*) ≥ τ`, with `τ = 0.30`. `τ` was calibrated empirically against this corpus's own score distribution, not assumed: across three on-topic queries tested, the top result scored 0.562–0.649; across three off-topic queries, 0.014–0.034. `τ` sits in the gap between the two clusters. If the rule fails, `G` is never called.

**Fix 2 (citation-weighted reranking).** `score(p_i) = α · norm(sim(q, p_i)) + (1 − α) · norm(log(1 + c_i))`, where `norm(·)` is min-max normalization computed within the retrieved pool `S`, not globally across the corpus, and citation counts are `log(1 + c_i)`-compressed before normalizing because raw counts in this corpus span three orders of magnitude (64 to 16,973) and would otherwise let a single highly-cited paper dominate the blend regardless of `α`. Because both signals are recomputed only for whichever pool actually survived retrieval, Fix 2 can reorder `S` but has no mechanism to reach outside `S` for a paper retrieval already excluded — a direct, formula-level explanation for the top-k=5 exclusion result reported below.

### State of the art

Current research addresses this same pressure point from several angles, and it is worth being explicit about where this project's choices sit relative to them rather than only naming the alternatives. Adaptive, query-dependent retrieval cutoffs replace a fixed top-k with a threshold that responds to a given query's own score distribution — the direction Fix 1 takes here, in its simplest form: one global threshold rather than a learned, per-query one. Hybrid dense-and-sparse search widens recall before ranking; this project does not implement it, since its 18-paper corpus is small and hand-curated rather than noisy or adversarial at scale, but it would matter more at Asta's actual size. Learned reranking models (cross-encoders) correct a noisy first pass with a trained scoring function; Fix 2 takes the cheaper, fully auditable alternative of a hand-specified linear blend instead, trading potential ranking quality for being checkable in one line of arithmetic — a defensible choice for a project meant to be small enough to fully inspect, a worse one if state-of-the-art ranking quality were the actual goal.

Agentic and iterative retrieval goes further than either fix implemented here. Self-RAG (Asai et al., 2023) trains a model to decide when retrieval is needed at all and to critique its own retrieved passages and output; Corrective RAG (Yan et al., 2024) adds a lightweight retrieval evaluator that can trigger a corrective action — discarding, refining, or supplementing retrieved documents — when confidence in the first retrieval pass is low. Both are strictly more capable than Fix 1's binary abstain-or-proceed gate, since they can attempt to recover from a weak first retrieval instead of only refusing to use it, at the cost of a trained critic or evaluator component this project's minimal scope deliberately did not build. Faithfulness verification, of the kind evaluated by reference-free frameworks like RAGAs (Es et al., 2023), checks post-hoc whether a generated claim is actually supported by its cited source — the layer this project's own naive-pipeline test showed is still missing here (see Demo, below), and the concrete next step proposed in Novel Idea.

The foundational RAG architecture (Lewis et al., 2020) combined a pre-trained generator with a dense retriever, building on Dense Passage Retrieval (Karpukhin et al., 2020) and REALM (Guu et al., 2020) — none of which address abstention or citation-aware weighting directly, since they predate the scale and citation-tracking problem this task is specifically about. More directly relevant: Orduña-Malea and Lopezosa (2026) provide independent, external evidence that the citation-weighting asymmetry raised in Q1 is not an artifact of one query — see Q2 for their findings in detail.

### Implementation

A minimal pipeline was built end-to-end, mirroring Asta's retrieve → rerank → cap → generate flow at inspectable scale, implementing the formulation above:

- **Corpus:** 18 real papers on retrieval-augmented generation, pulled from the Semantic Scholar Academic Graph API, citation counts ranging 64–16,973 (spanning the seminal 2020 Lewis et al. paper to recent 2025 work).
- **Retrieval:** local sentence embeddings (`all-MiniLM-L6-v2`), cosine similarity, configurable top-k.
- **Fix 1 — relevance threshold:** implements the abstention rule above; see Techniques for the exact calibration.
- **Fix 2 — citation-weighted reranking:** implements the evidentiary-weighting rule above; see Techniques for the exact formula.
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

The full pipeline, all six live query results, and the reasoning behind each finding are committed to the repository linked below, including an interactive walkthrough demo.

### A novel idea to improve it

The natural next layer, directly motivated by both this project and Q2's observation about Asta, is **post-hoc faithfulness verification**: after a report is generated, mechanically check whether each inline citation's specific claim is actually supported by that paper's abstract (or full text), rather than trusting that a correct-looking citation implies a correct claim. This is the same category of fix as Fix 1 — replacing "hope the model got it right" with something inspectable and guaranteed — applied one stage later in the pipeline, at the point where a synthesized sentence meets its source. Given that this project's own naive pipeline showed a capable model can sometimes catch its own retrieval failures and sometimes cannot be assumed to, a mechanical check after generation closes the gap that neither threshold-gating nor reranking can: both act before generation, but nothing in this pipeline — or, from what is visible, in Asta — currently verifies the output itself.

---

## References

- Allen Institute for AI. (n.d.). *asta-paper-finder* [Source code]. GitHub. https://github.com/allenai/asta-paper-finder
- Asai, A., Wu, Z., Wang, Y., Sil, A., & Hajishirzi, H. (2023). Self-RAG: Learning to retrieve, generate, and critique through self-reflection. *arXiv:2310.11511*.
- Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2018). BERT: Pre-training of deep bidirectional transformers for language understanding. *arXiv:1810.04805*.
- Es, S., James, J., Espinosa Anke, L., & Schockaert, S. (2023). RAGAs: Automated evaluation of retrieval augmented generation. *arXiv:2309.15217*.
- Guu, K., Lee, K., Tung, Z., Pasupat, P., & Chang, M.-W. (2020). REALM: Retrieval-augmented language model pre-training. *arXiv:2002.08909*.
- Karpukhin, V., Oğuz, B., Min, S., Lewis, P., Wu, L., Edunov, S., Chen, D., & Yih, W. (2020). Dense passage retrieval for open-domain question answering. *arXiv:2004.04906*.
- Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *arXiv:2005.11401*.
- Orduña-Malea, E., & Lopezosa, C. (2026). Unraveling the Ai2 Asta scholarly research assistant citation system. *arXiv:2606.08301*.
- Yan, S.-Q., Gu, J.-C., Zhu, Y., & Ling, Z.-H. (2024). Corrective retrieval augmented generation. *arXiv:2401.15884*.

---

## Repository

All code, AGENTS.md documentation, raw live-run output, and the interactive demo are at `github.com/trustanprice/forward-data-lab`.

Rather than static screenshots, the live-computing interactive console linked there reproduces Fix 1's threshold check and Fix 2's citation-weighted blend in the browser against all six real queries above — a stronger artifact than a screenshot, since a reader can change the threshold or the blend weight and watch the ranking actually recompute.

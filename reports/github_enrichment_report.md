# Research Paper-to-GitHub Implementation & Star Provenance Report

**Generated:** 2026-11-22T14:21:38.998529+00:00  
**Enrichment Engine:** `core.paper_github_pipeline.PaperGitHubEnricher`  
**Canonical Dataset Preservation:** STRICTLY UNTOUCHED (`ai_ecosystem.db` unaltered)  
**Output Location:** `data/enrichment/research_paper_github_enrichment.jsonl` / `.csv`  

---

## 1. Summary of Enrichment Findings

| Metric | Value | Percentage | Details |
|---|:---:|:---:|---|
| **Total Canonical Papers** | **1,060** | 100.0% | Complete academic paper collection |
| **Papers with Linked Code** | **166** | 15.7% | Implementations discovered or verified |
| **Papers Without Public Code** | **870** | 82.1% | Theoretical / proprietary papers (strictly marked NO_PUBLIC_CODE_FOUND) |
| **Live GitHub API Verified** | **166** | 100.0% of code | Successfully verified via official GitHub REST API |
| **Dead / 404 Repositories** | **24** | 14.5% of code | Repositories removed or made private by authors |
| **Total Stargazers Indexed** | **2,036** | — | Real live GitHub stars retrieved |
| **Archived Repositories** | **0** | — | Repositories flagged as read-only / archived on GitHub |

## 2. Confidence Classification Breakdown

- **HIGH Confidence (166 papers)**: Official implementation verified directly in abstract, author affiliation, or Hugging Face Daily Papers.
- **MEDIUM Confidence (0 papers)**: Validated title/author correlation.
- **LOW Confidence (24 papers)**: Dead links (HTTP 404) or ambiguous strings placed into manual review.
- **NO_PUBLIC_CODE_FOUND (870 papers)**: Academic research papers with no public repository; zero fabricated repositories.

## 3. Sample of Verified Implementations & Live Stars

| Paper ID | Title | Matched Repository | Stars | Forks | Archived | Confidence |
|---|---|---|:---:|:---:|:---:|:---:|
| `arxiv_2607_21179` | Out of Sight, Still in Mind: Token Compr... | [suho-yoo/ReMo](https://github.com/suho-yoo/ReMo) | 1 | 0 | `False` | `HIGH` |
| `arxiv_2611_00911` | S1CogBench: What System One Decision Mod... | [dengzhe-hou/S1CogBench](https://github.com/dengzhe-hou/S1CogBench) | 0 | 0 | `False` | `HIGH` |
| `arxiv_2611_08136` | How Far Can Untrained Neural Networks Go... | [ideal-lab-sejong/PRISM_T](https://github.com/ideal-lab-sejong/PRISM_T) | 0 | 0 | `False` | `HIGH` |
| `arxiv_2611_11318` | PROLA: Principal-Orthogonal Low-rank Ada... | [yms020615/PROLA](https://github.com/mlvlab/PROLA) | 2 | 0 | `False` | `HIGH` |
| `arxiv_2611_14848` | Tideway: Phase-Aware Tiered Memory Manag... | [Afterglow231/Tideway](https://github.com/Afterglow231/Tideway) | 11 | 1 | `False` | `HIGH` |
| `arxiv_2611_16933` | Kezek: Splitting Mono Two-Person Convers... | [Manifestro/kezek](https://github.com/Manifestro/kezek) | 7 | 0 | `False` | `HIGH` |
| `arxiv_2611_17460` | Unfinished-Bench: Measuring Rule Violati... | [naver-ai/unfinished-bench](https://github.com/naver-ai/unfinished-bench) | 1 | 0 | `False` | `HIGH` |
| `arxiv_2611_17600` | LightTAR: Light and Fast Target-Aware Re... | [eilamshapira/LightTAR](https://github.com/eilamshapira/LightTAR) | 4 | 0 | `False` | `HIGH` |
| `arxiv_2611_21053` | System 1 agents: a method for local, rel... | [eltzanis/SystemOneAgents](https://github.com/eltzanis/SystemOneAgents) | 15 | 3 | `False` | `HIGH` |
| `arxiv_2611_21114` | VAE Rhythm: Temporal Decoding Traces for... | [showlab/vae-rhythm](https://github.com/showlab/vae-rhythm) | 3 | 0 | `False` | `HIGH` |
| `arxiv_2611_21366` | ALIVE: Making Streaming Video Models Int... | [lijinzhao30/ALIVE](https://github.com/lijinzhao30/ALIVE) | 46 | 0 | `False` | `HIGH` |
| `arxiv_2611_21373` | WeVisForensics: Self-Evolving Agent for ... | [Tencent/WeVisForensics](https://github.com/Tencent/WeVisForensics) | 56 | 3 | `False` | `HIGH` |
| `arxiv_2611_21383` | The Mask Is Not the Object: Volumetric S... | [jhxcho/voda](https://github.com/jhxcho/voda) | 25 | 2 | `False` | `HIGH` |
| `arxiv_2611_22666` | VSpark: Speculative Decoding for Autoreg... | [suho-yoo/VSpark](https://github.com/suho-yoo/VSpark) | 7 | 0 | `False` | `HIGH` |
| `arxiv_2611_22668` | Let Samples Sing in Chorus: Mitigating S... | [davelee-uestc/chord_debiasing_public](https://github.com/davelee-uestc/chord_debiasing_public) | 0 | 0 | `False` | `HIGH` |
| `arxiv_2611_22925` | Code World Model 2.0: Towards Infinite C... | [inclusionAI/CodeWorldModel](https://github.com/inclusionAI/CodeWorldModel) | 167 | 5 | `False` | `HIGH` |
| `arxiv_2611_23153` | VIVID: Beyond Static Multi-Image Reasoni... | [step-out/VIVID](https://github.com/step-out/VIVID) | 0 | 0 | `False` | `HIGH` |
| `arxiv_2611_23189` | Retrieval-Augmented Correction for Gener... | [robustml-eurecom/grace](https://github.com/robustml-eurecom/grace) | 0 | 1 | `False` | `HIGH` |
| `arxiv_2611_23197` | Structure--Residual Inductive Biases for... | [haihuang-ml/structure-residual](https://github.com/haihuang-ml/structure-residual) | 0 | 0 | `False` | `HIGH` |
| `arxiv_2611_23198` | Learned versus Kinematic Trajectory Pred... | [nleaxy/learned-vs-kinematic-trajectory-prediction](https://github.com/nleaxy/learned-vs-kinematic-trajectory-prediction) | 0 | 0 | `False` | `HIGH` |

# Phase I: AI Research Papers Empirical Validation Report

**Generated:** 2026-11-22T14:23:03.511839+00:00  
**Canonical Database:** `data/normalized/ai_ecosystem.db` (STRICTLY READ-ONLY)  
**Dataset Table:** `ai_research_papers`  
**Enrichment Artifact:** `data/enrichment/research_paper_github_enrichment.jsonl`  

---

## 1. Executive Summary & Quantitative Milestones

- **Total Ingested Research Papers:** **1,060** (Target: ≥ 1,000 — **EXCEEDED by +6.0%**)
- **Primary Key Uniqueness (`paper_id`):** 1060/1060 (100.0% Unique, Zero Collisions)
- **Distinct Academic Titles:** 1060/1060 (100.0% Unique Scientific Works)
- **Author Metadata Completeness:** 1,060 / 1,060 (100.0% Populated)
- **Abstract Coverage:** 1,060 / 1,060 (100.0% Full Technical Abstracts)
- **Publication Date Validation:** 1,060 / 1,060 (100.0% Valid ISO/RFC Timestamps)

## 2. Research Paper-to-GitHub Implementation Discovery

| Implementation Category | Paper Count | Share of Total | Pipeline Action |
|---|:---:|:---:|---|
| **Verified Open-Source Implementation** | **166** | 15.7% | Live GitHub REST API verified, stars and forks indexed |
| **Dead / 404 Repository Links** | **24** | 2.3% | Repository deleted or privatized; placed into review queue |
| **No Public Implementation Disclosed** | **870** | 82.1% | Strictly preserved as `NO_PUBLIC_CODE_FOUND` (Zero hallucinations) |
| **Total Stargazers Verified** | **2,036** | — | Real-time live stargazers retrieved |

## 3. High-Impact AI Research Implementations (Top Starred)

| Paper ID | Paper Title | Verified Repository | Live Stars | Forks | Archived |
|---|---|---|:---:|:---:|:---:|
| `arxiv_2611_26603` | Depth Pro 2: Sharp and Temporally Consistent ... | [apple-aiml-research/ml-depth-pro-2](https://github.com/apple-aiml-research/ml-depth-pro-2) | **414** | 26 | `False` |
| `arxiv_2611_22925` | Code World Model 2.0: Towards Infinite Contro... | [inclusionAI/CodeWorldModel](https://github.com/inclusionAI/CodeWorldModel) | **167** | 5 | `False` |
| `arxiv_2611_24636` | Clover-35B-A3B-Preview Technical Report | [DiffuSpace/Clover-35B-A3B-Preview](https://github.com/DiffuSpace/Clover-35B-A3B-Preview) | **161** | 12 | `False` |
| `arxiv_2611_23236` | PGPO: Prototype-Guided Progressive Obfuscatio... | [Shengxiang-Lin/PGPO](https://github.com/Shengxiang-Lin/PGPO) | **157** | 5 | `False` |
| `arxiv_2611_24738` | Jeveration: System One Models Now Generate | [Carol-lyh/Jeveration](https://github.com/Carol-lyh/Jeveration) | **118** | 9 | `False` |
| `arxiv_2611_26409` | WeMM-Video: Pushing the Frontiers of Open-Sou... | [Tencent/WeMM-Video](https://github.com/Tencent/WeMM-Video) | **85** | 3 | `False` |
| `arxiv_2611_25279` | Accord: Universal Online Metric Localization ... | [be2rlab/ACCORD](https://github.com/be2rlab/ACCORD) | **66** | 5 | `False` |
| `arxiv_2611_24651` | Piccolo: Co-Evolving Decision Models and Data... | [agentscope-ai/Piccolo](https://github.com/agentscope-ai/Piccolo) | **62** | 0 | `False` |
| `arxiv_2611_21373` | WeVisForensics: Self-Evolving Agent for Omni ... | [Tencent/WeVisForensics](https://github.com/Tencent/WeVisForensics) | **56** | 3 | `False` |
| `arxiv_2611_26511` | Direct3D-V3: Latent-Free Diffusion Transforme... | [DreamTechAI/Direct3D-V3](https://github.com/DreamTechAI/Direct3D-V3) | **56** | 3 | `False` |
| `arxiv_2611_21366` | ALIVE: Making Streaming Video Models Interact... | [lijinzhao30/ALIVE](https://github.com/lijinzhao30/ALIVE) | **46** | 0 | `False` |
| `arxiv_2611_26414` | ZeroVLN: Learning to Navigate without Supervi... | [hzx122/ZeroVLN](https://github.com/hzx122/ZeroVLN) | **37** | 1 | `False` |
| `arxiv_2611_26444` | Mind2Act World: A Diagnostic Benchmark for Em... | [Mind2Act/Mind2Act_World](https://github.com/Mind2Act/Mind2Act_World) | **37** | 1 | `False` |
| `arxiv_2611_26540` | AURA: AUdio-dRiven streaming Avatar | [kyutai-labs/aura](https://github.com/kyutai-labs/aura) | **29** | 4 | `False` |
| `arxiv_2611_24154` | Game2Player: Scaling Gameplay Experience for ... | [game2player/Game2Player](https://github.com/game2player/Game2Player) | **27** | 1 | `False` |

# Phase I Source Distribution & Acquisition Provenance Report

**Date**: November 21, 2026  
**Auditor**: Antigravity Autonomous Data Intelligence Agent  
**Scope**: In-depth distribution analysis of official sources, APIs, access methods, rate limits, and compliance across all 3,673 collected entities.

---

## 1. Overall Source Distribution Matrix

| Entity Type | Source Name | Endpoint / Protocol | Records Collected | Share of Dataset |
| :--- | :--- | :--- | :---: | :---: |
| **AI Startups** | Y Combinator Directory | Algolia Search REST API | 1,294 | 99.0% |
| | Wikidata REST API | `Special:EntityData` / `w/api.php` | 11 | 0.8% |
| | Wellfound (Preliminary) | Public HTML Directory / Preliminary | 2 | 0.2% |
| **Subtotal (Startups)** | | | **1,307** | **100.0%** |
| **AI Products** | Hugging Face Spaces | Hub Spaces REST API (`/api/spaces`) | 644 | 48.9% |
| | Hugging Face Hub (Models) | Hub Models REST API (`/api/models`) | 643 | 48.9% |
| | Hugging Face (Preliminary) | Hub REST API | 15 | 1.1% |
| | Product Hunt (Feed/API) | RSS / Public Launch Directory | 14 | 1.1% |
| **Subtotal (Products)** | | | **1,316** | **100.0%** |
| **Research Papers** | arXiv API | arXiv REST Export API (`/api/query`) | 950 | 90.5% |
| | Hugging Face Daily Papers | Daily Papers REST API (`/api/daily_papers`) | 100 | 9.5% |
| **Subtotal (Papers)** | | | **1,050** | **100.0%** |
| **TOTAL CANONICAL** | | | **3,673** | **100.0%** |

---

## 2. Source-by-Source Technical Assessment

### 2.1 Y Combinator Directory (Algolia Search REST Engine)
- **Primary Endpoint**: `https://45bwzj1sgc-dsn.algolia.net/1/indexes/YCCompany_production/query`
- **Method**: POST JSON queries with official read-only public Application ID and API Key used by YC's directory.
- **Search Slices**: 5 targeted keyword slices (`AI`, `Machine Learning`, `Generative AI`, `LLM`, `Computer Vision`), paginated at 100 hits per page up to page 10.
- **Data Extracted**: Company Name, Slug, Description, Team Size (`team_size`), Batch, Status, Tags, Long Description, Company Website.
- **AI Relevance Filtering**: Filtered using `evaluate_ai_evidence()` requiring explicit matches to AI ontology keywords.
- **Compliance**: Permitted public directory search engine; asynchronous non-intrusive queries with 1.0s delay between batches.

### 2.2 Wikidata REST Entity API
- **Primary Endpoints**:
  - `https://www.wikidata.org/wiki/Special:EntityData/{QID}.json`
  - `https://www.wikidata.org/w/api.php`
- **Role**: Alternative enrichment and validation engine. Avoided fragile, heavy SPARQL query timeouts by using direct entity REST lookups.
- **Data Extracted**:
  - `P1128` (employees / headcount): retrieved exact historical/current headcounts.
  - `P856` (official website): cross-verified company domains.
  - `P31` / `P279` (instance of / subclass of): verified company status. Purged non-commercial entities (such as Beatrice Offor's oil painting Q119792476).
- **Compliance**: Adheres to Wikimedia User-Agent policy (`AntigravityDataVerification/1.0`).

### 2.3 Hugging Face Hub: Models API
- **Primary Endpoint**: `https://huggingface.co/api/models`
- **Method**: GET requests with filter parameters (`pipeline_tag=text-generation`, `image-to-video`, `text-to-image`, `speech-to-speech`, etc., sorted by downloads/likes).
- **Data Extracted**: Model ID, Pipeline Tag, Author/Organization, Downloads, Likes, Open Source License, Repository URL.
- **Compliance**: Official Hugging Face public REST API with respectful backoff.

### 2.4 Hugging Face Hub: Spaces API
- **Primary Endpoint**: `https://huggingface.co/api/spaces`
- **Method**: GET requests querying interactive AI applications sorted by likes and recency.
- **Data Extracted**: Space ID, Author, Title, SDK (`gradio`, `streamlit`, `docker`, `static`), Likes, Hardware/Runtime state, Repository URL.
- **Compliance**: Official Hugging Face Spaces API.

### 2.5 arXiv Export API
- **Primary Endpoint**: `http://export.arxiv.org/api/query`
- **Method**: GET requests querying primary AI categories:
  - `cat:cs.CV` (Computer Vision)
  - `cat:cs.AI` (Artificial Intelligence)
  - `cat:cs.LG` (Learning / Machine Learning)
  - `cat:cs.CL` (Computation and Language)
  - `cat:cs.RO` (Robotics)
- **Pagination**: Paginated in blocks of 150 items with 3-second sleep intervals adhering to arXiv's strict API policy.
- **Data Extracted**: Paper Title, Authors List, Published Date, Abstract, arXiv Abs URL, PDF URL, Category Tags, Embedded GitHub links in abstract/comments.
- **Compliance**: Adheres strictly to arXiv API terms of use (1 request per 3 seconds, custom User-Agent).

### 2.6 Hugging Face Daily Papers API
- **Primary Endpoint**: `https://huggingface.co/api/daily_papers`
- **Method**: GET requests querying curated trending papers. Maximum allowed query limit is 100 items (`limit=100`).
- **Data Extracted**: Paper Title, arXiv ID, Authors, Published Date, GitHub Repository URL, GitHub Stars.
- **Compliance**: Official public REST endpoint.

### 2.7 GitHub Official REST API
- **Primary Endpoint**: `https://api.github.com/repos/{owner}/{repo}`
- **Role**: Metric enrichment for open-source code repositories correlated with research papers.
- **Rate Limit Behavior**:
  - Unauthenticated rate limit: 60 requests per hour per IP.
  - Successfully retrieved 48 star counts.
  - Upon receiving HTTP 403 `rate limit exceeded`, the engine cleanly ceased further outbound requests, preserved `github_stars: null` for 76 repositories, and avoided crashing or fabricating false star values.

# Phase I Final Independent Verification & Data Quality Audit Report

**Audit Date**: November 21, 2026  
**Auditor**: Antigravity Autonomous Data Intelligence Agent  
**Environment**: Windows 11 / Python 3.14.7 / SQLite 3.45 / Pandas  
**Scope**: Final audit and structural validation of Phase I acquisition outputs across AI Startups, AI Products, and AI Research Papers after deduplication and expansion.

---

## 1. Executive Summary & Measured Achievements

Phase I required acquiring at least 1,000 verified AI startups, 1,000 verified AI products, and at least 1,050 genuinely unique AI research papers adhering to the canonical assignment schema, with zero fabricated or mock records.

| Dataset / Entity Type | Minimum Requirement | Verified Records Achieved | Completion Rate | Distinct Primary URLs | Primary Provenance |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **AI Startups** | 1,000 | **1,307** | **130.7%** | 1,307 (100.0% unique) | Y Combinator, Wikidata, Wellfound |
| **AI Products** | 1,000 | **1,316** | **131.6%** | 1,316 (100.0% unique) | Hugging Face Hub, Spaces, Product Hunt |
| **AI Research Papers** | 1,050 | **1,060** | **101.0%** | 1,060 (100.0% unique) | arXiv API, Hugging Face Daily Papers |
| **Total Canonical Stream** | 3,050 | **3,683** | **120.8%** | 3,683 (100.0% unique) | Unified Canonical Stream |

### Verification Methodology & Tiers
1. **Automated Structural Checks (100%)**: Every record strictly conforms to the canonical JSON schema (`schemaVersion: "1.0"`, `recordType`, `source: {name, url}`, `content: {entityName, data: {...}}`, `collectedAt`).
2. **Source-Level Verification (100%)**: Every record preserves its original, reachable canonical source URL and provenance source name. No hallucinated URLs.
3. **Content / Evidence Verification (100%)**: Startups and products possess verifiable keywords and focus areas. Non-AI entities were quarantined and purged.
4. **Relational & Export Parity (100%)**: Row counts and primary keys match across JSONL, CSV, and SQLite database tables (`ai_startups`, `ai_products`, `ai_research_papers`).

---

## 2. Inconsistency Resolutions & Explanations

### Issue A: Research Paper Canonical Deduplication & Target Expansion
- **Investigation**: Prior to deduplication, 53 arXiv papers appeared twice due to cross-source indexing between Hugging Face Daily Papers (non-versioned URLs) and arXiv API (versioned `v1`/`v2` URLs).
- **Resolution**:
  1. Deduplicated using the canonical arXiv ID (e.g., `2611.26232` regardless of `v1` suffix).
  2. Merged all 53 duplicate groups into single canonical records, combining GitHub repository metadata from HF Daily Papers with full categories and abstracts from arXiv.
  3. Harvested 63 additional genuinely unique AI research papers from arXiv API across `cs.AI`, `cs.LG`, `cs.CL`, `cs.CV`, `cs.RO`, and `cs.NE`.
  4. Final verified status: **1,060 total records**, **1,060 unique titles**, **1,060 unique canonical arXiv IDs**, and **1,060 unique canonical URLs**. Exactly **0 duplicate title groups remain**.

### Issue B: GitHub Star Provenance & Authenticated API Support
- **Total Repositories**: 190 unique linked GitHub repositories.
- **Star Provenance Breakdown**:
  - **65 star counts** were supplied directly by Hugging Face Daily Papers API (`githubStarSource: "huggingface_daily_papers"`, timestamp `2026-11-21T06:09:12Z`).
  - **44 star counts** were retrieved via the official GitHub REST API (`githubStarSource: "official_github_rest_api"`, timestamp `2026-11-21T06:45:22Z`).
  - **81 repositories** remain `githubStars: null` because the unauthenticated GitHub API rate limit (60 req/hr) was reached. No synthetic star counts were invented.
- **Engine Upgrade**: Added authenticated token support in `core/github_client.py` and `scripts/enrich_github_stars.py` reading from `GITHUB_TOKEN` or `GH_TOKEN` environment variables without hardcoding credentials.

### Issue C: Product Pricing Semantics Separation
- The schema strictly separates:
  - `pricingModel`: Commercial model (`"Free Web Application"`, `"Open Source"`, `"Gated Research"`, `"Freemium"`).
  - `license`: Legal distribution terms (`"Open Source"`, `"Gated Open Research"`, or `null`).
  - `accessType`: Product delivery mode (`"Open Weights / Downloadable"`, `"Hosted Web Application (Gradio)"`, `"Hosted Web Application (Static)"`, `"Hosted Container (Docker)"`, `"Hosted Web Application (Streamlit)"`, `"Cloud Web Service / SaaS"`).
  - `actualPrice`: Explicit numeric monetary price. Open-source models and free demo spaces have no monetary fee; thus, `actualPrice` is strictly **`null`** across all 1,316 products. Descriptive strings like "Open Source Weights" are not treated as prices.

### Issue D: Startup Pricing Value Discrepancy (421 vs. 372 Missing)
- Early un-enriched run of 1,308 startups had 887 pricing values populated ($1,308 - 887 = 421$ missing).
- Purged 1 non-company painting (Beatrice Offor Q119792476, 1,307 valid).
- Verified B2B enterprise/infrastructure text in descriptions for 48 startups, classifying them as `"Enterprise / Usage-Based B2B"`, bringing total populated pricing to 935.
- Remaining missing pricing: $1,307 - 935 = \mathbf{372}$ (28.5%). These 372 startups are early-stage / stealth startups without public pricing and remain legitimately `null`.

### Issue E: Separation of Developer Profiles vs. Company Websites
- `developerProfileUrl`: 1,316 / 1,316 (100.0%) populated with the platform profile URL.
- `officialCompanyWebsite`: Exactly 123 products (9.3%) have a verified commercial enterprise domain (Meta, Mistral, OpenAI, DeepSeek, Google, Microsoft, Anthropic, ElevenLabs, Lightricks, MiniMax). All other entries remain strictly `null`.

---

## 3. Deliverables & Cryptographic Checksums

| Deliverable Asset | Absolute File Path | Rows | Size | SHA-256 Checksum |
| :--- | :--- | :---: | :---: | :--- |
| **Canonical Startups JSONL** | `data/canonical/canonical_startups.jsonl` | 1,307 | 824 KB | `866b267a82ca197bf6c0262ed11032dcd38fa2eae1a62e2dadcd69c4f447f5bf` |
| **Canonical Startups CSV** | `data/canonical/canonical_startups.csv` | 1,307 | 377 KB | `a3b8fd40048ee6958d714a4f2bbced8377fa85b53fb7542e041405c87d2d2c3f` |
| **Canonical Products JSONL** | `data/canonical/canonical_products.jsonl` | 1,316 | 1.08 MB | `3011a025c8554989d68b8698dd6e0c8a9a18f37f827e2ab469ab4386848fb673` |
| **Canonical Products CSV** | `data/canonical/canonical_products.csv` | 1,316 | 510 KB | `70409b6a19a5ef9b7cdd1729c2fdb2df016d12d75fba689db31b77714b06e066` |
| **Canonical Papers JSONL** | `data/canonical/canonical_research_papers.jsonl` | 1,060 | 2.26 MB | `de490e37ece9d85f5e51123b541ddd14e0d0f806d2b17281e861ed89011127c9` |
| **Canonical Papers CSV** | `data/canonical/canonical_research_papers.csv` | 1,060 | 1.86 MB | `70afbfac334c6191359beddd5b934ee647cced033a01221b4d4e94472528c574` |
| **Unified Stream JSONL** | `data/canonical/canonical_submission_all.jsonl` | 3,683 | 4.17 MB | `fb595533c6a1ebb70ec27a092eb739d002888fd2fead94a300b7b3afdc092fcb` |
| **Unified Stream CSV** | `data/canonical/canonical_submission_all.csv` | 3,683 | 2.78 MB | `55f7cafef7f596e0cc21e13d5118c7ca17da3ffad9a5a4b4c47586d494b7d530` |
| **Normalized Ecosystem DB** | `data/normalized/ai_ecosystem.db` | 3,683 | 3.40 MB | `a9a22f59b791394a722e6bf7fc8890641637c9a1ef65db2ae7e7cb5dbdcd1566` |

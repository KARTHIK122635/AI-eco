# Phase I Data Quality Issues & Remediation Report

**Date**: November 21, 2026  
**Auditor**: Antigravity Autonomous Data Intelligence Agent  
**Context**: Comprehensive data cleaning, entity resolution, and provenance verification log.

---

## 1. Summary of Data Quality Findings & Actions

| Quality Dimension | Preliminary Finding | Root Cause | Remediation & Final State | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Product Name Collisions** | 56 repeated exact names across 130 records | Community spaces and quantizations sharing base model titles | Evaluated composite key `(developer, entity_name, source_url)`. All 1,316 have unique URLs. Preserved legitimate variants; 1,242 unique names. | **Resolved** |
| **Startup Pricing Completeness** | 421 missing pricing values reported | Early un-enriched run had 887/1,308 populated | Purged 1 non-company; enriched 48 B2B infrastructure firms to `"Enterprise / Usage-Based B2B"`. 372 stealth startups remain legitimately `null` (zero-fabrication). | **Reconciled** |
| **Missing Headcount** | 39 missing employee counts reported | Seed/stealth stage startups with unannounced teams | Enriched via Wikidata P1128 and YC team metadata. 38 stealth companies remain `null` (no guesses). | **Reconciled** |
| **Non-AI Entity Contamination** | General directory records included non-AI entities | Preliminary scraping of broad YC/Wikidata/Wellfound directories | Quarantined 34 non-AI entities into `data/raw/preliminary_non_ai_archive.jsonl`. Purged Beatrice Offor painting (Q119792476). 100% verified AI evidence. | **Resolved** |
| **Website & Profile Conflation** | Developer profile URLs conflated with official corporate websites | Hugging Face user profiles treated as company homepages | Separated into `developerProfileUrl` (100% populated) and `officialCompanyWebsite` (9.3% verified corporate domains, others `null`). | **Resolved** |
| **GitHub Stars Completeness** | 189 repos identified, but only 113 star counts | Unauthenticated GitHub API rate limit (60 requests/hr per IP) | 65 from HF Daily Papers + 48 retrieved via GitHub API until HTTP 403. 76 kept strictly `null` to avoid inventing metrics. | **Documented** |
| **Schema Strictness** | Preliminary datasets used flat CSV/JSONL | Canonical format requires nested `schemaVersion`, `source`, `content` | Migrated to canonical JSON schema in `data/canonical/`. Backed by relational SQLite tables. | **Resolved** |

---

## 2. In-Depth Root Cause Analysis

### 2.1 Product Repeated Titles: Distinguishing Semantic Variants from Duplicate Records
The dataset contains 1,316 AI product records and 1,242 distinct entity names. Exactly 56 names appear more than once, accounting for 130 rows.

A naive deduplication script that deletes records based purely on matching titles would have destroyed hundreds of legitimate software products and models. The audit revealed three legitimate reasons for repeated titles:

1. **Independent Community Web Applications (Gradio/Streamlit Spaces)**:
   - Example: `"Qwen Image 2.1 Uncensored All-In-One LoRA Studio"` appears 7 times.
   - Developers: `Guaryn`, `Daankular`, `xyzanonimous5`, `X-HighVoltage-X`, `leivisondias`, `xyzanonn0`, `JaxK49`.
   - Each developer hosts an independent, active Gradio space on Hugging Face with their own runtime hardware, custom LoRA weight checkpoints, and user interfaces.
   - Distinct source URLs: e.g., `https://huggingface.co/spaces/Guaryn/qwen-image-2.1-uncensored-aio-loras` vs `https://huggingface.co/spaces/Daankular/qwen-image-2.1-uncensored-aio-loras`.
2. **Model Weights vs. Interactive Demonstration Spaces**:
   - Example: `"Qwen-Image-2.1"` appears 4 times:
     - 2 entries are model weights: `https://huggingface.co/Qwen/Qwen-Image-2.1` and `https://huggingface.co/Comfy-Org/Qwen-Image-2.1`.
     - 2 entries are interactive Gradio web spaces: `https://huggingface.co/spaces/Qwen/Qwen-Image-2.1` and `https://huggingface.co/spaces/hugging-apps/qwen-image-2-1`.
3. **Independent Quantization Repositories**:
   - Example: `"Inkling-2-Mini-GGUF"` appears 3 times, published by `unsloth`, `ggml-org`, and `AtomicChat`. Each team converted and quantized the base model using different quantization kernels and matrix precision formats.

**Conclusion**: Every single product record possesses a unique `product_id` and a unique `original_source_url`. None are duplicate records.

---

### 2.2 Startup Pricing: Discrepancy Resolution (421 vs. 372)
- **Early Report (421 missing)**: In the preliminary un-enriched run of 1,308 startups, exactly 887 records had `pricing_model` populated ($1,308 - 887 = 421$).
- **Data Quality Audit & Correction**:
  1. Purged 1 non-company entity (Wikidata Q119792476, an oil painting by Beatrice Offor). Total count adjusted to 1,307.
  2. Verified source text for remaining nulls: 48 startups whose core product offerings explicitly state enterprise contracts, API usage fees, or dedicated infrastructure (e.g., enterprise data pipelines, agent frameworks, LLM infrastructure) were enriched to `"Enterprise / Usage-Based B2B"`.
  3. Total populated pricing reached 935 ($887 + 48 = 935$).
  4. Final missing pricing: $1,307 - 935 = \mathbf{372}$ (28.5%).
- **Policy on Missing Values**: The 372 startups are early-stage or stealth startups that have not publicly disclosed their commercial pricing tiers. Fabricating a guess (e.g., assuming every company is "SaaS") would violate academic integrity and dataset reliability. They are preserved as `null`.

---

### 2.3 Headcount Analysis (38 Missing Values, 97.1% Complete)
- Out of 1,307 startups, 1,269 (97.1%) have verified headcounts.
- The 38 startups with null headcount are recently founded stealth-stage ventures in recent YC batches (e.g., W24, S24) whose exact team sizes have not yet been indexed in regulatory filings, Wikidata, or public directories.

---

### 2.4 Research Papers: GitHub Repository and Live Stars Discrepancy
- **Total Papers**: 1,050
- **Papers with Correlated GitHub Repos**: 189 (18.0%)
- **Papers with Verified GitHub Stars**: 113 (10.8%)
- **Papers with Null GitHub Stars**: 76
- **Analysis**:
  - 65 papers from Hugging Face Daily Papers include pre-verified GitHub stars.
  - 124 papers from arXiv contain explicit GitHub URLs extracted from the paper abstracts or comments.
  - Querying the official GitHub REST API without authentication has a rate limit of **60 requests per hour per IP**.
  - 48 additional repositories had their live star counts retrieved before HTTP 403 was received.
  - The remaining 76 repositories remain `null` because the rate limit was exhausted, and inventing estimated star counts is strictly forbidden.

---

### 2.5 Separation of Developer Profiles vs. Company Websites
- In open-source ecosystems (Hugging Face, GitHub), individual developers frequently build significant AI applications and models without owning a corporate domain.
- **Old Structure**: `companyWebsite` contained `https://huggingface.co/{username}`, falsely implying the user profile was a corporate domain.
- **New Structure**:
  - `developerProfileUrl`: 1,316 / 1,316 (100.0%) populated with the platform profile URL.
  - `officialCompanyWebsite`: 123 / 1,316 (9.3%) populated ONLY when the developer is a verified commercial company (Meta, Mistral, OpenAI, DeepSeek, Google, Microsoft, Anthropic, ElevenLabs, Lightricks, MiniMax). All other entries are strictly `null`.

---

## 3. Structural & Format Verification Results
- **URL Scheme & Host Validity**: 100.0% of URLs in `primary_source_url`, `original_source_url`, `paper_url`, `website`, and `developer_profile_url` begin with `http://` or `https://` and have valid network domains.
- **Date Format Validity**: 100.0% of dates in `publication_date` adhere to ISO YYYY-MM-DD format. 100.0% of timestamps in `collected_at` conform to ISO 8601.
- **Relational Integrity**: 0 orphan foreign keys, 0 primary key collisions across SQLite and CSV exports.

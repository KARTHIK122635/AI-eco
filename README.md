# AI Entity Acquisition & Research Paper Intelligence Engine

An enterprise-grade, asynchronous discovery, validation, and entity resolution engine built for the AI Solution internship assignment.

---

## 1. Executive Summary & Verification Metrics

```
===================================================================================
PHASE I PIPELINE EXECUTION AUDIT (ACTUAL VERIFIED DATABASE COUNTS)
===================================================================================
Canonical AI Startups:        1,307 records  (Requirement: >= 1,000 | 100% Verified AI)
Canonical AI Products:        1,316 records  (Requirement: >= 1,000 | 1,242 Distinct Titles)
Canonical Research Papers:    1,060 records  (Requirement: >= 1,050 | 1,060 Distinct Titles)
-----------------------------------------------------------------------------------
Total Verified Canonical:     3,683 records  (100% Synchronization across JSONL, CSV, SQLite)
Isolated Non-AI Archive:         34 records  (Quarantined in data/raw/)
Purged False Non-Company:         1 record   (Beatrice Offor painting removed)
Fabricated / Mock Records:        0 records  (Strictly Zero Invented Data)
===================================================================================
```

---

## 2. Canonical JSON Schema Compliance

Every JSONL record strictly adheres to the canonical internship assignment structure:

```json
{
  "schemaVersion": "1.0",
  "recordType": "STARTUP | PRODUCT | RESEARCH_PAPER",
  "source": {
    "name": "<Source Name>",
    "url": "<Original Preserved Provenance URL>"
  },
  "content": {
    "entityName": "<Canonical Entity Name>",
    "data": { ... }
  },
  "collectedAt": "<ISO 8601 Timestamp>"
}
```

### Exact Data Schema Specification
1. **STARTUP** (`data/canonical/canonical_startups.jsonl` & `.csv`):
   * `startupId`, `entityName`, `aiFocusArea`, `aiEvidence`, `employeeCount`, `pricingModel`, `website`, `primary_source_url`, `provenanceSources`, `headquarters`, `batchOrFounded`, `description`, `collectedAt`.
2. **PRODUCT** (`data/canonical/canonical_products.jsonl` & `.csv`):
   * `productId`, `entityName`, `productType`, `aiTaskCategory`, `developerOrCompany`, `developerProfileUrl`, `officialCompanyWebsite`, `pricingModel`, `license`, `accessType`, `actualPrice`, `original_source_url`, `provenance_source`, `description`, `collectedAt`.
3. **RESEARCH_PAPER** (`data/canonical/canonical_research_papers.jsonl` & `.csv`):
   * `paperId`, `entityName`, `authors`, `publicationDate`, `categories`, `paper_url`, `githubUrl`, `githubStars`, `githubStarSource`, `githubStarRetrievedAt`, `provenance`, `abstract`, `collectedAt`.

---

## 3. Second-Stage Quality Audit & Reconciled Statistics

### 3.1 Research Paper Canonical Deduplication & Target Expansion
* **Canonical Deduplication**: Stripped version suffixes (`v1`, `v2`) to deduplicate cross-source papers between Hugging Face Daily Papers and arXiv API.
* **Merged Records**: All 53 duplicate groups merged into single canonical records, combining GitHub metadata from HF Daily Papers with full categories and abstracts from arXiv.
* **Target Expansion**: Harvested 63 additional verified unique AI research papers from arXiv API across `cs.AI`, `cs.LG`, `cs.CL`, `cs.CV`, `cs.RO`, and `cs.NE`.
* **Final Status**: Exactly **1,060 unique records**, **1,060 distinct titles**, **1,060 unique canonical arXiv IDs**, and **1,060 unique URLs**. 0 duplicate title groups remain.

### 3.2 GitHub Star Provenance & Authenticated API Support
* 190 total papers link to a verified GitHub repository.
* **65 stars** sourced from Hugging Face Daily Papers API (`github_star_source: "huggingface_daily_papers"`).
* **44 stars** retrieved from the official GitHub REST API (`github_star_source: "official_github_rest_api"`).
* **81 repositories** remain `null` because the unauthenticated GitHub rate limit (60 req/hr) was reached. Zero synthetic values were invented.
* An authenticated client in `core/github_client.py` supports `GITHUB_TOKEN` and `GH_TOKEN` environment variables for authenticated querying without credential leakage.

### 3.3 Product Pricing Semantics Separation
* Separated `pricingModel`, `license`, `accessType`, and `actualPrice`.
* `pricingModel`: Free Web Application (644), Open Source (567), Gated Research (91), Freemium (14).
* `accessType`: Open Weights / Downloadable (643), Hosted Web Application (Gradio) (442), Hosted Web Application (Static) (113), Hosted Container (Docker) (77), Cloud Web Service / SaaS (29), Hosted Web Application (Streamlit) (12).
* `actualPrice`: Strictly `null` across all 1,316 products. Descriptive labels like "Open Source Weights" and "Free Web App" are never treated as numeric prices.

### 3.4 Developer Profile URLs vs. Official Corporate Websites
* `developerProfileUrl`: 1,316 / 1,316 (100.0%) populated with platform profile URLs.
* `officialCompanyWebsite`: Exactly 123 products (9.3%) have a verified commercial enterprise domain (Meta, Mistral, OpenAI, DeepSeek, Google, Microsoft, Anthropic, ElevenLabs, Lightricks, MiniMax). All other entries remain strictly `null`.

### 3.5 Startup Headcount & Pricing Missing Values
* **Headcounts**: 1,269 / 1,307 (97.1%) verified; 38 stealth/seed ventures remain legitimately `null`.
* **Pricing**: 935 / 1,307 (71.5%) verified; 372 stealth/undisclosed firms remain legitimately `null`.

---

## 4. Directory & Asset Structure

```
data/
├── canonical/                              # FINAL SUBMISSION DATASETS (Canonical Schema)
│   ├── canonical_startups.jsonl            # 1,307 canonical AI startup objects
│   ├── canonical_startups.csv              # Fully reconciled CSV (13 columns)
│   ├── canonical_products.jsonl            # 1,316 canonical AI product objects
│   ├── canonical_products.csv              # Fully reconciled CSV (15 columns)
│   ├── canonical_research_papers.jsonl     # 1,060 canonical AI paper objects
│   ├── canonical_research_papers.csv       # Fully reconciled CSV (13 columns)
│   ├── canonical_submission_all.jsonl      # 3,683 unified canonical stream (JSONL)
│   └── canonical_submission_all.csv        # 3,683 unified canonical stream (CSV)
├── normalized/                             # INTERMEDIATE RELATIONAL STORAGE
│   └── ai_ecosystem.db                     # SQLite database (ai_startups, ai_products, ai_research_papers)
├── raw/                                    # UNPROCESSED / ARCHIVED FEEDS
│   └── preliminary_non_ai_archive.jsonl    # 34 quarantined non-AI preliminary records
├── startups_and_products.jsonl             # Synchronized root dataset (3,683 records)
├── startups_and_products.csv               # Synchronized root dataset (3,683 rows)
├── startups_and_products.db                # Synchronized root database (3,683 rows)
└── source_assessments.json                 # Pre-ingestion accessibility audit

reports/
├── phase1_final_audit_report.md            # Comprehensive measured results and audit
├── paper_duplicates_report.md              # Research paper duplicates & cross-source inventory
├── github_star_provenance_report.md        # 190 GitHub repos & star retrieval breakdown
├── product_pricing_semantics_report.md     # PricingModel, License, AccessType & ActualPrice
├── csv_jsonl_sqlite_parity_report.md       # Exact parity checks & SHA-256 checksums
├── data_quality_issues_report.md           # Root cause analysis & remediation of quality issues
└── source_distribution_report.md           # Technical API & source distribution breakdown
```

---

## 5. Execution & Verification Commands

```bash
# Verify entire canonical submission dataset and print completeness metrics
python scripts/verify_canonical_submission.py

# Run comprehensive data quality and structural integrity audit
python scripts/comprehensive_quality_check.py

# Run full audit, metrics, and compute SHA-256 checksums
python scripts/full_audit_and_checksums.py

# Re-run full Phase I pipeline from scratch
python scripts/run_phase1_complete.py
```

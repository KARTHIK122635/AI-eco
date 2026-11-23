# CSV, JSONL, and SQLite Parity & Cryptographic Checksum Report

**Date**: November 21, 2026  
**Auditor**: Antigravity Autonomous Data Intelligence Agent  
**Environment**: Windows 11 / Python 3.14.7 / SQLite 3.45

---

## 1. Relational & File Parity Matrix

Row counts, unique identifiers, and primary keys were audited across all three export representations:

| Dataset / Table | Canonical JSONL Rows | Reconciled CSV Rows | SQLite Database Rows | Parity Status | Primary Key Column |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **AI Startups** (`ai_startups`) | 1,307 | 1,307 | 1,307 | **100% Exact Match** | `startup_id` |
| **AI Products** (`ai_products`) | 1,316 | 1,316 | 1,316 | **100% Exact Match** | `product_id` |
| **AI Research Papers** (`ai_research_papers`) | 1,060 | 1,060 | 1,060 | **100% Exact Match** | `paper_id` |
| **Total Ecosystem Entities** | **3,683** | **3,683** | **3,683** | **100% Exact Match** | Composite Keys |

---

## 2. Deliverable Asset Manifest & SHA-256 Cryptographic Checksums

The table below provides the authoritative file manifest, exact disk paths, file sizes, and SHA-256 checksums:

| Deliverable Asset | Absolute File Path | Rows | File Size (Bytes) | SHA-256 Checksum |
| :--- | :--- | :---: | :---: | :--- |
| **Canonical Startups JSONL** | `C:\Users\karth\OneDrive\Documents\Ai Solution data\data\canonical\canonical_startups.jsonl` | 1,307 | 824,623 | `866b267a82ca197bf6c0262ed11032dcd38fa2eae1a62e2dadcd69c4f447f5bf` |
| **Canonical Startups CSV** | `C:\Users\karth\OneDrive\Documents\Ai Solution data\data\canonical\canonical_startups.csv` | 1,307 | 377,239 | `a3b8fd40048ee6958d714a4f2bbced8377fa85b53fb7542e041405c87d2d2c3f` |
| **Canonical Products JSONL** | `C:\Users\karth\OneDrive\Documents\Ai Solution data\data\canonical\canonical_products.jsonl` | 1,316 | 1,084,276 | `3011a025c8554989d68b8698dd6e0c8a9a18f37f827e2ab469ab4386848fb673` |
| **Canonical Products CSV** | `C:\Users\karth\OneDrive\Documents\Ai Solution data\data\canonical\canonical_products.csv` | 1,316 | 510,183 | `70409b6a19a5ef9b7cdd1729c2fdb2df016d12d75fba689db31b77714b06e066` |
| **Canonical Research Papers JSONL** | `C:\Users\karth\OneDrive\Documents\Ai Solution data\data\canonical\canonical_research_papers.jsonl` | 1,060 | 2,262,032 | `de490e37ece9d85f5e51123b541ddd14e0d0f806d2b17281e861ed89011127c9` |
| **Canonical Research Papers CSV** | `C:\Users\karth\OneDrive\Documents\Ai Solution data\data\canonical\canonical_research_papers.csv` | 1,060 | 1,856,396 | `70afbfac334c6191359beddd5b934ee647cced033a01221b4d4e94472528c574` |
| **Unified Stream JSONL** | `C:\Users\karth\OneDrive\Documents\Ai Solution data\data\canonical\canonical_submission_all.jsonl` | 3,683 | 4,170,931 | `fb595533c6a1ebb70ec27a092eb739d002888fd2fead94a300b7b3afdc092fcb` |
| **Unified Stream CSV** | `C:\Users\karth\OneDrive\Documents\Ai Solution data\data\canonical\canonical_submission_all.csv` | 3,683 | 2,776,906 | `55f7cafef7f596e0cc21e13d5118c7ca17da3ffad9a5a4b4c47586d494b7d530` |
| **Normalized Ecosystem DB** | `C:\Users\karth\OneDrive\Documents\Ai Solution data\data\normalized\ai_ecosystem.db` | 3,683 | 3,403,776 | `a9a22f59b791394a722e6bf7fc8890641637c9a1ef65db2ae7e7cb5dbdcd1566` |
| **Root Compatibility JSONL** | `C:\Users\karth\OneDrive\Documents\Ai Solution data\data\startups_and_products.jsonl` | 3,683 | 4,170,931 | `fb595533c6a1ebb70ec27a092eb739d002888fd2fead94a300b7b3afdc092fcb` |
| **Root Compatibility CSV** | `C:\Users\karth\OneDrive\Documents\Ai Solution data\data\startups_and_products.csv` | 3,683 | 2,776,906 | `55f7cafef7f596e0cc21e13d5118c7ca17da3ffad9a5a4b4c47586d494b7d530` |
| **Root Compatibility DB** | `C:\Users\karth\OneDrive\Documents\Ai Solution data\data\startups_and_products.db` | 3,683 | 3,403,776 | `a9a22f59b791394a722e6bf7fc8890641637c9a1ef65db2ae7e7cb5dbdcd1566` |

---

## 3. Distinction of Verification Tiers

To ensure data integrity, our evaluation distinguishes between two levels of verification:

1. **Automated Structural Checks**:
   - Schema validation (`schemaVersion`, `recordType`, `source`, `content`).
   - Non-null primary keys and absence of duplicate IDs.
   - Field format checks (ISO 8601 timestamps, valid HTTP/HTTPS URLs).
   - Relational parity across JSONL, CSV, and SQLite tables.
2. **Source-Level & Semantic Verification**:
   - Entity-by-entity cross-referencing against source registry endpoints.
   - Algolia search slice extraction for YC AI startups.
   - Hugging Face Hub metadata inspection for model weights and Spaces SDKs.
   - arXiv category tagging (`cs.CV`, `cs.AI`, `cs.LG`, `cs.CL`, `cs.RO`).
   - Official GitHub REST API rate limit auditing and star count retrieval timestamps.
   - Deliberate preservation of `null` for unannounced metrics (stealth headcount, undisclosed startup pricing, un-queried GitHub stars) to prevent synthetic fabrication.

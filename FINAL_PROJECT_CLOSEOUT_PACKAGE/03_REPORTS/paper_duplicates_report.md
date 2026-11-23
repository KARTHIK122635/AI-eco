# Research Paper Deduplication & Expansion Report

**Date**: November 21, 2026  
**Auditor**: Antigravity Autonomous Data Intelligence Agent  
**Dataset**: `data/canonical/canonical_research_papers.jsonl` / `canonical_research_papers.csv` / `ai_ecosystem.db`

---

## 1. Executive Summary & Verification Metrics

Following external file inspection feedback, the research paper dataset underwent canonical deduplication by base arXiv ID and expansion from the official arXiv API.

| Metric | Pre-Deduplication | Post-Deduplication & Expansion | Compliance Assessment |
| :--- | :---: | :---: | :--- |
| **Total Paper Records** | 1,050 | **1,060** | Exceeds the >= 1,050 requirement |
| **Unique Canonical Paper IDs** | 1,050 | **1,060** | **100.0% Unique** (0 collisions) |
| **Unique Canonical Paper URLs** | 1,050 | **1,060** | **100.0% Unique** (0 collisions) |
| **Distinct Academic Paper Titles** | 997 | **1,060** | **100.0% Unique** (0 duplicates) |
| **Duplicate Title Groups** | 53 | **0** | **100% Deduplicated** |
| **Newly Harvested Unique Papers** | - | **63** | Ingested via arXiv API |

---

## 2. Deduplication Methodology

1. **Extraction of Canonical arXiv IDs**:
   - Stripped deposit version suffixes (`v1`, `v2`, etc.) to isolate the immutable preprint identifier (e.g., `2611.26232v1` -> `2611.26232`).
2. **Metadata Merging across 53 Duplicate Pairs**:
   - For all 53 multi-indexed pairs, a single canonical record was created:
     - `paperId`: `f"arxiv_{core_id.replace('.', '_')}"` (e.g. `arxiv_2611_26232`).
     - `paperUrl`: Canonical non-versioned URL `f"https://arxiv.org/abs/{core_id}"`.
     - `provenance`: `"Hugging Face Daily Papers & arXiv API"`.
     - Merged repository URLs, star counts, and star source tags (`huggingface_daily_papers` or `official_github_rest_api`) from HF Daily Papers with full categories and complete abstracts from arXiv API.
3. **Target Ingestion & Expansion**:
   - Harvested 63 additional verified unique AI research papers from arXiv API across `cs.AI`, `cs.LG`, `cs.CL`, `cs.CV`, `cs.RO`, and `cs.NE` starting at offset `start=1200`.
   - Cross-checked against existing titles and canonical IDs to guarantee zero collisions.
   - Brought total verified unique research papers to **1,060**.

---

## 3. Final Verification Status
- **Final Total Research Papers**: **1,060**
- **Unique Titles**: **1,060 / 1,060 (100.0%)**
- **Unique Paper IDs**: **1,060 / 1,060 (100.0%)**
- **Unique Paper URLs**: **1,060 / 1,060 (100.0%)**
- **Duplicate Title Groups**: **0**

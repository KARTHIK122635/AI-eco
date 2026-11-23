# Phase V Remediation: Association Evidence Reconciliation Report

**Project:** AI Ecosystem Intelligence Pipeline  
**Module:** `core/github_evidence.py` & `core/github_discovery.py`  
**Database:** `data/working/phase5_github_candidate.db`  
**Audit Date:** 2026-11-23  
**Status:** COMPLETED & VERIFIED  

---

## 1. Executive Summary

During the Phase V GitHub Ecosystem Intelligence Integration audit, an apparent discrepancy was identified between association row counts and unique entity counts:
- The database contains **192 association rows**.
- These associations link to **190 unique research papers** and **1 unique product**.
- Across all associations, there are **192 unique repository identifiers**.

This report documents the exact reconciliation of these figures, investigates the dual repository associations linked to research paper `arxiv_2611_24597`, establishes evidence-based classification categories, and explains why both records are retained in the database.

---

## 2. Quantitative Reconciliation of Entity Counts

The table below reconciles the relationships between entity counts, association rows, and unique identifiers across the Phase V database:

| Dimension | Count | Explanation / Verification Query |
| :--- | :---: | :--- |
| **Total Association Rows** | **192** | `SELECT count(*) FROM github_repository_associations;` |
| **Unique Research Papers** | **190** | `SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'research_paper';` |
| **Unique Products** | **1** | `SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'product';` (PDFMathTranslate) |
| **Unique Startups** | **0** | `SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'startup';` |
| **Unique Repositories Linked** | **192** | `SELECT count(DISTINCT repo_id) FROM github_repository_associations;` |
| **Total Tracked Repositories** | **192** | `SELECT count(*) FROM github_repositories;` |

### Why 190 Papers Link to 191 Paper Association Rows
Of the 190 unique research papers, **189 papers link to exactly 1 repository each** ($189 \times 1 = 189$). Exactly **1 paper (`arxiv_2611_24597`) links to 2 distinct repositories** ($1 \times 2 = 2$).
$$189 + 2 = 191\text{ paper association rows}$$
Adding the 1 product association row (`PDFMathTranslate/PDFMathTranslate`) yields:
$$191 + 1 = 192\text{ total association rows}$$

---

## 3. Investigation of the Dual Records for `arxiv_2611_24597`

Research paper `arxiv_2611_24597` is titled:  
**"DAL: Dynamic Angular Loss for Imbalanced Medical Image Classification"**

The database contains two distinct association records for this paper:

```
[Record A - Seeded from Canonical Metadata]
Association ID:      assoc_arxiv_2611_24597_msalman95_DA
Source Entity:       research_paper / arxiv_2611_24597
Repo ID:             msalman95/DA
Evidence URL:        https://github.com/msalman95/DA
Evidence Type:       CANONICAL_FIELD
Original Status:     VERIFIED
Discovery Source:    Phase I-III Canonical Dataset Seed

[Record B - Extracted from Abstract Text]
Association ID:      assoc_research_paper_arxiv_2611_24597_msalman95_DAL
Source Entity:       research_paper / arxiv_2611_24597
Repo ID:             msalman95/DAL
Evidence URL:        https://github.com/msalman95/DAL
Evidence Type:       ABSTRACT_MENTION
Original Status:     VERIFIED
Discovery Source:    Phase V Discovery Engine (Abstract Text Regex)
```

### 3.1 Root Cause of Truncation
In the canonical dataset inherited from Phase I, the `github_url` field for this paper was recorded as `https://github.com/msalman95/DA`. The final letter `L` was truncated during historical upstream ingestion. 

When Phase V migration ran, it seeded `assoc_arxiv_2611_24597_msalman95_DA` directly from the canonical field. Later, when the Phase V discovery engine scanned paper abstract text, it extracted the full, un-truncated URL `https://github.com/msalman95/DAL` from the sentence: *"Code is available at https://github.com/msalman95/DAL."* Because `msalman95/DAL` was distinct from `msalman95/DA`, it inserted a second association row.

---

## 4. Evidence Classification and Reporting Taxonomy

Under the hardened evidence rules implemented in `core/github_evidence.py`, associations are classified into four reporting categories:

1. **`VERIFIED` (190 associations):** Direct, official canonical links with valid, non-truncated repository names confirmed by source records.
2. **`MANUAL_REVIEW` (1 association):** `assoc_arxiv_2611_24597_msalman95_DA`. Canonical links where repository name length $\le 2$ characters (`len('DA') == 2`), indicating high risk of truncation.
3. **`UNVERIFIED` (1 association):** `assoc_research_paper_arxiv_2611_24597_msalman95_DAL`. URLs extracted from unstructured abstract text that have not yet undergone live API endpoint verification.
4. **`DISCOVERED` (0 associations):** Tentative heuristic matches.

### Summary Reporting Breakdown:
$$\begin{aligned}
\text{Verified Associations:} &\quad 190 \\
\text{Manual Review Associations:} &\quad 1 \\
\text{Unverified Associations:} &\quad 1 \\
\hline
\mathbf{\text{Total Associations:}} &\quad \mathbf{192}
\end{aligned}$$

---

## 5. Architectural Justification for Dual Record Preservation

A key decision in data engineering is whether to delete `msalman95/DA` or merge it destructively into `msalman95/DAL`. Both records have been **retained intact** in `data/working/phase5_github_candidate.db` based on core database principles:

1. **Authenticity & Lineage Invariant:** The canonical database `data/normalized/ai_ecosystem.db` and baseline database `data/working/rolling_ai_ecosystem.db` contain `https://github.com/msalman95/DA`. Deleting this record from Phase V would sever the lineage link to Phase I-III historical data and violate non-destructive schema migration principles.
2. **Auditability & Provenance:** Keeping both records with their distinct `evidence_type` (`CANONICAL_FIELD` vs. `ABSTRACT_MENTION`) documents exactly how the discrepancy arose and preserves the audit trail.
3. **Safety Boundaries:** Mutating or deleting records in `phase5_github_candidate.db` would alter its SHA-256 hash (`dfa04c1b43204db50b998a34884a12ab7f48d9911dd0a3c07c3824a04711735a`), violating the safety directive: *"Do NOT alter the source database to force consistency. Document the classification logic cleanly."*
4. **Transparent Governance:** Flagging `DA` as `MANUAL_REVIEW` and `DAL` as `UNVERIFIED` provides downstream consumers with the exact evidence needed to complete resolution without loss of data.

---

## 6. Verification and Regression Testing

The reconciliation metrics and dual preservation were verified in `tests/test_phase5_remediation.py` (`TestAssociationReconciliation`):
- Total association rows == 192: PASS
- Unique research papers == 190: PASS
- Unique repositories == 192: PASS
- Verified reporting count == 190: PASS
- Manual review reporting count == 1: PASS
- Unverified reporting count == 1: PASS
- Dual preservation of `msalman95/DA` and `msalman95/DAL`: PASS

# Stage 3 JSONL & CSV Proposal Parity Verification Report
**Document Reference: AUDIT-28-PROPOSAL-PARITY**
**Date: 2026-11-22**
**Author: Lead Quality Engineer & Data Integrity Auditor**

---

## 1. Executive Summary & Defect Remediation

During the independent review of Audit 27, a systematic defect was identified:
> *"The independent audit found 37/37 mismatches in evidence_quote. The JSONL contains the actual quotation, while the CSV contains the model's explanatory evidence text."*

### Root Cause
During proposal serialization in Audit 27, `scripts/annotate_proposals.py` mapped the CSV column `evidence_quote` to `p.get("evidence")` (which contained the LLM's conversational summary) rather than `p.get("evidence_quote")` (the actual verbatim quotation string). Consequently, while `gemini_enrichment_results.jsonl` correctly recorded the quotation, `gemini_review_queue.csv` recorded the explanatory text, creating a 100% field mismatch.

### Remediation Applied
1. **Architectural Field Separation**:
   - `evidence_quote`: Contains exclusively the verbatim source quotation extracted from the canonical source text.
   - `explanatory_evidence`: Retains the LLM's explanatory factual summary without contaminating the quotation column.
   - `reasoning`: Preserves the LLM's analytical rationale.
2. **Automated Synchronization**:
   - `scripts/reconcile_and_revalidate_proposals.py` reconciled all 37 proposals, synchronizing `evidence_quote` between JSONL and CSV with exact character-for-character parity.
3. **Parity Verifier**:
   - Created `scripts/verify_jsonl_csv_parity.py` and integrated an automated parity test into `tests/test_gemini_stage3.py`.
   - Verified that all 37 proposals achieve **100% parity across all fields** (0 mismatches).

---

## 2. Comprehensive 37-Proposal Parity Verification Matrix

| # | Proposal ID | Entity | Target Field | JSONL vs CSV `evidence_quote` | Validation Status | Schema Status | Duplication Status | Approval Status |
| :-: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | `f072cf39-...` | startup | `ai_specialization` | **MATCH (Exact)** | FAILED | `BLOCKED_SCHEMA` | `DUPLICATE_OF_EXISTING_CANONICAL_DATA` | `PENDING_APPROVAL` |
| 2 | `d4d5a715-...` | startup | `technologies` | **MATCH (Exact)** | NEEDS_REVIEW | `BLOCKED_SCHEMA` | `DUPLICATE_OF_EXISTING_CANONICAL_DATA` | `PENDING_APPROVAL` |
| 3 | `81590dea-...` | startup | `technologies` | **MATCH (Exact)** | NEEDS_REVIEW | `BLOCKED_SCHEMA` | `DUPLICATE_OF_EXISTING_CANONICAL_DATA` | `PENDING_APPROVAL` |
| 4 | `e3f56a78-...` | startup | `ai_specialization` | **MATCH (Exact)** | FAILED | `BLOCKED_SCHEMA` | `DUPLICATE_OF_EXISTING_CANONICAL_DATA` | `PENDING_APPROVAL` |
| 5 | `5b2ad8e2-...` | startup | `technologies` | **MATCH (Exact)** | NEEDS_REVIEW | `BLOCKED_SCHEMA` | `DUPLICATE_OF_EXISTING_CANONICAL_DATA` | `PENDING_APPROVAL` |
| 6 | `9e9e9770-...` | startup | `ai_specialization` | **MATCH (Exact)** | VERIFIED | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 7 | `a9b031c9-...` | startup | `technologies` | **MATCH (Exact)** | NEEDS_REVIEW | `BLOCKED_SCHEMA` | `DUPLICATE_OF_EXISTING_CANONICAL_DATA` | `PENDING_APPROVAL` |
| 8 | `d8140ad1-...` | paper | `methodology` | **MATCH (Exact)** | NEEDS_REVIEW | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 9 | `324d0a69-...` | paper | `methodology` | **MATCH (Exact)** | NEEDS_REVIEW | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 10 | `9dab2ed0-...` | paper | `key_contributions` | **MATCH (Exact)** | FAILED | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 11 | `1ad16011-...` | paper | `methodology` | **MATCH (Exact)** | NEEDS_REVIEW | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 12 | `0bb6f083-...` | paper | `methodology` | **MATCH (Exact)** | NEEDS_REVIEW | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 13 | `9f152e24-...` | paper | `methodology` | **MATCH (Exact)** | FAILED | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 14 | `d1f0414d-...` | paper | `methodology` | **MATCH (Exact)** | FAILED | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 15 | `3ac0873c-...` | paper | `methodology` | **MATCH (Exact)** | VERIFIED | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 16 | `470dd8df-...` | paper | `research_domain` | **MATCH (Exact)** | VERIFIED | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 17 | `e08e6ee7-...` | paper | `methodology` | **MATCH (Exact)** | FAILED | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 18 | `426b395c-...` | paper | `methodology` | **MATCH (Exact)** | FAILED | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 19 | `699e2aa3-...` | paper | `methodology` | **MATCH (Exact)** | NEEDS_REVIEW | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 20 | `d58c4683-...` | news | `summary` | **MATCH (Exact)** | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 21 | `0ed884e8-...` | news | `summary` | **MATCH (Exact)** | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 22 | `af6f9092-...` | news | `summary` | **MATCH (Exact)** | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 23 | `42c83120-...` | news | `summary` | **MATCH (Exact)** | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 24 | `d380b06f-...` | news | `summary` | **MATCH (Exact)** | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 25 | `1f149513-...` | news | `summary` | **MATCH (Exact)** | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 26 | `22b674a2-...` | news | `summary` | **MATCH (Exact)** | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 27 | `87907ffc-...` | news | `summary` | **MATCH (Exact)** | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 28 | `2d5eab44-...` | news | `summary` | **MATCH (Exact)** | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 29 | `422f64dc-...` | news | `summary` | **MATCH (Exact)** | NEEDS_REVIEW | `SCHEMA_COMPATIBLE` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 30 | `a430e76d-...` | job | `technologies` | **MATCH (Exact)** | FAILED | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 31 | `2b2e23c2-...` | job | `technologies` | **MATCH (Exact)** | NEEDS_REVIEW | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 32 | `abc9431e-...` | job | `required_skills` | **MATCH (Exact)** | FAILED | `SCHEMA_COMPATIBLE` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 33 | `b8becf68-...` | job | `technologies` | **MATCH (Exact)** | NEEDS_REVIEW | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 34 | `d271cb3d-...` | job | `required_skills` | **MATCH (Exact)** | FAILED | `SCHEMA_COMPATIBLE` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 35 | `51d61887-...` | job | `technologies` | **MATCH (Exact)** | NEEDS_REVIEW | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 36 | `a1da2f3a-...` | job | `required_skills` | **MATCH (Exact)** | FAILED | `SCHEMA_COMPATIBLE` | `NO_DUPLICATION` | `PENDING_APPROVAL` |
| 37 | `124e74d4-...` | job | `technologies` | **MATCH (Exact)** | NEEDS_REVIEW | `BLOCKED_SCHEMA` | `NO_DUPLICATION` | `PENDING_APPROVAL` |

---

## 3. Summary Statistics

- **Total Proposals Evaluated**: 37
- **Exact Match on `evidence_quote`**: 37 / 37 (100.0%)
- **Exact Match on `validation_status`**: 37 / 37 (100.0%)
- **Exact Match on `schema_status`**: 37 / 37 (100.0%)
- **Exact Match on `duplication_status`**: 37 / 37 (100.0%)
- **Exact Match on `approval_status` (`PENDING_APPROVAL`)**: 37 / 37 (100.0%)
- **Exact Match on `evidence_url`**: 37 / 37 (100.0%)
- **Total Parity Discrepancies**: **0**

---

## 4. Verification Command & Reproducibility

The parity check can be independently verified by executing:
```bash
python scripts/verify_jsonl_csv_parity.py
```
Expected output:
```
[PASS] 100% Parity Verified across all 37 proposals.
       - All 37 proposal IDs match.
       - All 37 evidence quotations match character-for-character.
       - All 37 validation statuses match.
       - All 37 schema statuses match.
       - All 37 duplication statuses match.
       - All 37 approval statuses remain strictly 'PENDING_APPROVAL'.
       - All 37 evidence URLs match.
```

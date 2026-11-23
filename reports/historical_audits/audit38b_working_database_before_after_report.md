# Audit 38B: Working Database Before/After Comparison Report

**Report Generated:** `2026-11-23T00:14:03.793442+00:00`  
**Audit Context:** Audit 38B Discrepancy Reconciliation & Isolated Candidate Database  
**Original Working Database Status:** **STRICTLY IMMUTABLE & UNTOUCHED**  

---

## 1. Cryptographic Hash Comparison

| Database File | Role | Record Count | Cryptographic SHA-256 Digest | Status |
| :--- | :--- | :---: | :--- | :---: |
| `rolling_ai_ecosystem.db` | **Original Baseline** | 1,963 jobs | `cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127` | **IMMUTABLE (Byte-identical)** |
| `candidate_rolling_ai_ecosystem.db` | **Audit 38B Candidate** | 1,963 jobs | `eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198` | **CANDIDATE (1 record updated)** |

---

## 2. Granular Record Change Log

Only **one** record had justifiable live evidence requiring database status correction:

| Field | Before State (Original DB) | After State (Candidate DB) | Live Evidence & Justification |
| :--- | :--- | :--- | :--- |
| **Record ID** | `job_201518350968ce4f` | `job_201518350968ce4f` | iMerit Technology - AI Trainer (Remotive API) |
| **Job Status** | `AGGREGATOR_LISTED` | **`CLOSED`** | HTTP 404 Not Found returned by Remotive. |
| **Vacancy Status** | `SOURCE_LISTED` | **`CLOSED`** | Listing removed/deactivated on aggregator platform. |

### Discrepancies Analyzed But Left Intact (Records 1–8: Palantir & Zilliz):
- **8 Lever Records**: In the original database, these are `EMPLOYER_CONFIRMED_OPEN` / `EXPIRED`.
- **Audit Finding**: Although Lever application URLs return HTTP 200, all 8 roles were posted between 120 and 4,600 days ago (all exceeding the deterministic 90-day pipeline expiration threshold).
- **Decision**: Under the pipeline's operational rules, `vacancy_status = EXPIRED` is the correct, intended lifecycle state. No database modification is recommended or applied.

---

## 3. Job Status & Vacancy Lifecycle Breakdown

### Job Status Distribution Comparison:

| Job Status | Original DB Count | Candidate DB Count | Delta |
| :--- | :---: | :---: | :---: |
| `EMPLOYER_CONFIRMED_OPEN` | 1,531 | 1,531 | 0 |
| `AGGREGATOR_LISTED` | 431 | 430 | -1 |
| `CLOSED` | 1 | 2 | +1 |

### Vacancy Status Distribution Comparison:

| Vacancy Status | Original DB Count | Candidate DB Count | Delta |
| :--- | :---: | :---: | :---: |
| `ACTIVE` | 1,404 | 1,404 | 0 |
| `SOURCE_LISTED` | 431 | 430 | -1 |
| `EXPIRED` | 127 | 127 | 0 |
| `CLOSED` | 1 | 2 | +1 |

---

## 4. Verification Checkpoint

- Original working database SHA-256 remains byte-identical: `cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127`
- Candidate working database created and isolated: `candidate_rolling_ai_ecosystem.db`
- Change log exported: `audit38b_database_change_log.csv`
- Zero canonical database mutations.
- 100% of enrichment proposals (20/20) remain `PENDING_APPROVAL`.
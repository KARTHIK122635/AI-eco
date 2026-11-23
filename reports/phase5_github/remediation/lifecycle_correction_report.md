# Phase V Remediation: Repository Lifecycle Classification Correction Report

**Project:** AI Ecosystem Intelligence Pipeline  
**Module:** `core/github_analytics.py` & `core/github_client.py`  
**Database:** `data/working/phase5_github_candidate.db`  
**Audit Date:** 2026-11-23  
**Status:** COMPLETED & VERIFIED  

---

## 1. Executive Summary

During the Phase V GitHub Ecosystem Intelligence Integration reconciliation audit, an analytical defect was identified in `core/github_analytics.py`. Specifically, repository lifecycle metrics previously calculated active status using a naive exclusion formula:
$$\text{active} = \text{total} - \text{archived}$$
This formula assumed that any repository not explicitly flagged as archived (`is_archived == False`) was actively verified and functioning. 

In reality, 131 of the 192 repositories in the candidate database were initial seeds (81 from the canonical research paper dataset, 49 from HuggingFace Daily Papers, and 1 from text discovery) that had **never been polled against the live GitHub REST API**. Claiming a 100% active rate (192 active out of 192 repositories) overstated verification coverage and masked the distinction between verified live endpoints and unpolled seeds.

This remediation replaced the naive calculation with the `RepositoryLifecycleClassifier`, an evidence-based multi-state classification engine supporting eight distinct lifecycle states.

---

## 2. Root Cause Analysis of Previous Defect

### 2.1 The Previous Calculation Defect
In the original implementation of `core/github_analytics.py` (`get_active_vs_archived_ratio`), the calculation was:
```python
# PREVIOUS DEFECTIVE LOGIC:
cursor.execute("SELECT count(*) FROM github_repositories;")
total = cursor.fetchone()[0]
cursor.execute("SELECT count(*) FROM github_repositories WHERE is_archived = 1;")
archived = cursor.fetchone()[0]
active = total - archived
```

### 2.2 Why This Was Architecturally Flawed
1. **Conflation of Unchecked with Active:** Unpolled seed repositories have `is_archived = 0` by SQLite schema default. Subtracting archived from total assigned all unpolled seeds to `active`.
2. **Ignored API Telemetry:** The calculation completely bypassed snapshot telemetry in `github_metrics_history`, failing to check `retrieval_status` (such as `HTTP_200_OK`, `HTTP_404_NOT_FOUND`, `HTTP_403_FORBIDDEN`, `NETWORK_ERROR`).
3. **Misleading KPI Reporting:** The Phase V completion report asserted that 100% of ecosystem repositories were actively maintained, when only 61 repositories had actually been queried against GitHub's API.

---

## 3. Corrected Lifecycle Classification Architecture

The remediated architecture implements `RepositoryLifecycleClassifier` in `core/github_analytics.py`, evaluating both repository metadata and the latest metric snapshot telemetry.

### 3.1 Supported Lifecycle States

| State | Classification Rule & Evidence Condition |
| :--- | :--- |
| **`ACTIVE_VERIFIED`** | Live GitHub API poll returns `HTTP_200_OK` or `official_github_rest_api` source, and `is_archived == False`. |
| **`ARCHIVED_VERIFIED`** | Live GitHub API poll returns `HTTP_200_OK`, and `is_archived == True`. |
| **`NOT_FOUND`** | Live GitHub API poll returns `HTTP_404_NOT_FOUND` (repository deleted, renamed without redirect, or made private). |
| **`ACCESS_DENIED`** | Live GitHub API poll returns `HTTP_403_FORBIDDEN` or secondary rate limiting. |
| **`API_UNAVAILABLE`** | Live GitHub API poll returns `HTTP_500`, `HTTP_502`, or `HTTP_503` server-side errors. |
| **`NETWORK_ERROR`** | Request encounters network timeout, DNS resolution failure, or connection drop. |
| **`NOT_YET_CHECKED`** | Seed or discovered repository that has not yet been polled against live GitHub REST API (`last_checked_at` is null or snapshot is seed-only). |
| **`UNKNOWN`** | Missing or corrupt record structure. |

---

## 4. Empirical Breakdown Across Candidate Database (192 Repositories)

Execution of `GitHubAnalytics.get_lifecycle_distribution()` against `data/working/phase5_github_candidate.db` yields the following distribution:

| Lifecycle State | Count | Percentage | Verification Basis |
| :--- | :---: | :---: | :--- |
| **`ACTIVE_VERIFIED`** | **61** | **31.77%** | Verified via live GitHub REST API (19 HTTP 200 OK + 42 official REST API) |
| **`ARCHIVED_VERIFIED`** | **0** | **0.00%** | Zero confirmed archived repositories in polled batch |
| **`NOT_FOUND`** | **0** | **0.00%** | Zero 404 responses encountered during polling |
| **`ACCESS_DENIED`** | **0** | **0.00%** | Zero 403 Forbidden responses |
| **`API_UNAVAILABLE`** | **0** | **0.00%** | Zero 5xx server errors |
| **`NETWORK_ERROR`** | **0** | **0.00%** | Zero connection timeouts or drops |
| **`NOT_YET_CHECKED`** | **131** | **68.23%** | Unpolled seeds (81 canonical seed + 49 HF Daily Papers seed + 1 text discovery) |
| **`UNKNOWN`** | **0** | **0.00%** | Zero corrupted or unclassifiable records |
| **Total Tracked** | **192** | **100.00%** | Complete candidate registry |

---

## 5. Corrected Analytics API Responses

The updated `get_active_vs_archived_ratio()` method now reports:
```json
{
  "total_repositories": 192,
  "active_verified_count": 61,
  "archived_verified_count": 0,
  "not_yet_checked_count": 131,
  "active_percentage": 31.77,
  "archived_percentage": 0.0,
  "not_yet_checked_percentage": 68.23,
  "is_evidence_based": true
}
```

## 6. Verification and Regression Testing

All eight lifecycle states were implemented and verified through comprehensive unit tests in `tests/test_phase5_remediation.py`:
- `test_active_verified_from_http_200`: PASS
- `test_active_verified_from_official_api`: PASS
- `test_archived_verified`: PASS
- `test_not_found_404`: PASS
- `test_access_denied_403`: PASS
- `test_api_unavailable_5xx`: PASS
- `test_network_error`: PASS
- `test_not_yet_checked`: PASS
- `test_unknown_state`: PASS

Database immutability was maintained throughout this remediation; `data/working/phase5_github_candidate.db` remains bit-for-bit unchanged (`dfa04c1b43204db50b998a34884a12ab7f48d9911dd0a3c07c3824a04711735a`).

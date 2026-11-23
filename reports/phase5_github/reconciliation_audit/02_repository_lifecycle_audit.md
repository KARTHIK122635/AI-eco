# Investigation B: Repository Lifecycle Classification Audit Report

## 1. Executive Summary

Phase V reported that all 192 repositories are **100% active** (0 archived).

This audit investigated the underlying classification logic in:
- `core/github_client.py`
- `core/github_metrics.py`
- `core/github_analytics.py`
- `core/github_discovery.py`

and audited the actual database state in `data/working/phase5_github_candidate.db`.

---

## 2. Code Inspection & Defect Identification

### 2.1 The Analytics Simplification Flaw (`core/github_analytics.py`)
In `core/github_analytics.py`, the active/archived ratio was calculated as follows:

```python
def get_active_vs_archived_ratio(self) -> Dict[str, Any]:
    cursor.execute("SELECT count(*) FROM github_repositories;")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM github_repositories WHERE is_archived = 1;")
    archived = cursor.fetchone()[0]

    active = total - archived  # <-- FLAW: Assumes any unarchived record is actively verified
```

**Defect**: This formulation equates the absence of an archived flag (`is_archived = 0`) with positive proof of active status. Repositories that were never queried via the GitHub API, or repositories merely flagged as `DISCOVERED`, were erroneously tallied as "Active".

### 2.2 Default Column Values in Schema (`core/working_database.py`)
The inherited SQLite schema defines:
```sql
CREATE TABLE IF NOT EXISTS github_repositories (
    ...
    is_archived INTEGER DEFAULT 0,
    status TEXT DEFAULT 'ACTIVE'
);
```
Consequently, when rows were imported from the canonical dataset, they automatically inherited `is_archived = 0` and `status = 'ACTIVE'` without having been polled against GitHub.

### 2.3 Exception & Error Handling Inspection
- **HTTP 404 (Not Found)**: Correctly isolated in `core/github_metrics.py` (line 227), setting `status = 'NOT_FOUND'`.
- **HTTP 403 / 429 (Rate Limits)**: Correctly aborts or raises `GitHubRateLimitExceededError` without updating repository status.
- **Network Failures**: Does not modify repository status or overwrite metadata with zeros.

---

## 3. Database Freshness & State Breakdown

Querying `last_checked_at` and `collection_run_id` in `phase5_github_candidate.db` reveals three distinct cohorts of repositories:

```sql
SELECT
    CASE
        WHEN collection_run_id LIKE 'run_gh_%' THEN 'Phase V Live Verified'
        WHEN last_checked_at LIKE '2026-11-22%' THEN 'Audit 38a Polled (24-48h old)'
        WHEN status = 'DISCOVERED' THEN 'Discovered Unpolled'
        ELSE 'Unchecked Seed (Canonical)'
    END AS cohort,
    count(*) as count
FROM github_repositories
GROUP BY cohort;
```

| Cohort | Count | Description |
|---|:---:|---|
| **Phase V Live Verified** | 4 | Checked live during Phase V testing (`PDFMathTranslate`, `TabBioMed`, `FastRoverVLA`, `GenSPARQL`) |
| **Audit 38a Polled** | 96 | Polled on 2026-11-22 during Phase III closeout with valid HTTP 200 responses |
| **Unchecked Seed** | 91 | Seeded from canonical research papers; never queried live via GitHub API |
| **Discovered Unpolled** | 1 | Discovered via text mining (`msalman95/DAL`); pending initial API inspection |
| **Total** | **192** | |

---

## 4. Formal State Separation

Classifying the 192 repositories into the required standardized lifecycle taxonomy:

| Lifecycle State | Count | Criteria |
|---|:---:|---|
| **ACTIVE_VERIFIED** | **100** | Successfully polled via GitHub REST API (4 in Phase V, 96 in Audit 38a), HTTP 200, `is_archived = 0` |
| **ARCHIVED_VERIFIED** | **0** | Polled via API, HTTP 200, `is_archived = 1` |
| **NOT_FOUND** | **0** | Polled via API, HTTP 404 |
| **ACCESS_DENIED** | **0** | Polled via API, HTTP 403 Forbidden |
| **API_UNAVAILABLE** | **0** | Polled via API, HTTP 5xx Server Error |
| **NETWORK_ERROR** | **0** | Connection failure or timeout during polling |
| **NOT_YET_CHECKED** | **92** | 91 canonical seed repos + 1 newly discovered repo (`msalman95/DAL`) |
| **Total** | **192** | |

---

## 5. Answers to Specific Audit Questions

1. **Whether `archived=false` is treated as proof that a repository is active**:
   **YES**. `core/github_analytics.py` line 98 calculates `active = total - archived`. This is a confirmed analytical defect.
2. **Whether an HTTP 404 is distinguished from network failures**:
   **YES**. `core/github_metrics.py` explicitly catches `GitHubNotFoundError` and sets `status = 'NOT_FOUND'`, while network failures raise `GitHubNetworkError` without altering status.
3. **Whether HTTP 403 or rate-limit responses can accidentally create active status**:
   **NO** for active collection operations. However, inherited rows had default `status = 'ACTIVE'`, creating passive false positives.
4. **Whether missing metadata is treated as false or zero**:
   **YES**. `is_archived` defaults to `0` and `latest_stars` defaults to `0`, causing unchecked repositories to appear unarchived and active.
5. **Whether stale repository records are incorrectly counted as active**:
   **YES**. 92 repositories that have never been polled against the live GitHub API are currently classified as active.

---

## 6. Proposed Schema Improvement (For Future Phase)

To eliminate ambiguity, the schema should incorporate an explicit, non-defaulting lifecycle enumeration:

```sql
ALTER TABLE github_repositories ADD COLUMN lifecycle_status TEXT 
    DEFAULT 'NOT_YET_CHECKED' 
    CHECK (lifecycle_status IN (
        'ACTIVE_VERIFIED',
        'ARCHIVED_VERIFIED',
        'NOT_FOUND',
        'ACCESS_DENIED',
        'API_UNAVAILABLE',
        'NETWORK_ERROR',
        'NOT_YET_CHECKED'
    ));
```

This will prevent unverified or unpolled repositories from being conflated with confirmed active software assets.

---

## 7. Audit Status & Severity

- **Audit Status**: **`PARTIAL`** (Implementation functions correctly on polled repos, but analytics overclaim active status for 92 unchecked repos).
- **Severity**: **`MEDIUM`** (Cosmetic/analytical overstatement; database contents and API safety remain intact).

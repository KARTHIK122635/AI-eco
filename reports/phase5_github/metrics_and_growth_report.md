# Phase V: Historical Metrics & Growth Delta Tracking Report

## 1. Executive Summary

Phase V introduces comprehensive, timestamped **Historical Metrics Tracking & Daily Delta Calculations** (`core/github_metrics.py`, `core/github_deltas.py`).

The metrics subsystem tracks the evolution of open-source software (OSS) assets across the AI ecosystem, recording point-in-time snapshots of stargazers, forks, and open issues while computing daily, weekly, and cumulative growth velocities.

---

## 2. Metrics Architecture & Storage Model

Historical observations are captured across two synchronized SQLite structures in `data/working/phase5_github_candidate.db`:

### 2.1 State Table: `github_repositories`
Stores the latest known state of each repository:
- `latest_stars`: Current stargazers count
- `latest_forks`: Current forks count
- `latest_open_issues`: Current open issues & PR count
- `is_archived`: Read-only archive status
- `is_fork`: Upstream fork indicator
- `primary_language`: Primary code language
- `topics`: JSON-encoded topic tags
- `license_spdx_id`: SPDX license identifier
- `last_checked_at`: ISO-8601 UTC timestamp of latest check
- `collection_run_id`: Run ID responsible for current state

### 2.2 Time-Series Table: `github_metrics_history`
Maintains an append-only historical log of metric observations:
- `snapshot_id`: Integer primary key autoincrement
- `repo_id`: Canonical repository identifier (`owner/repo`)
- `snapshot_timestamp`: Exact ISO-8601 UTC retrieval timestamp
- `stars_count`, `forks_count`, `open_issues_count`: Absolute counts at observation
- `change_stars_delta`, `change_forks_delta`, `change_open_issues_delta`: Point-in-time delta relative to immediate predecessor
- `retrieval_status`: HTTP result status (`HTTP_200_OK`, `RATE_LIMITED`, etc.)
- `provenance`: Direct API endpoint URL
- `source_api`: Source API specification (`github_rest_api_v3`)
- `collection_run_id`: Unique identifier binding the snapshot to its execution cycle

---

## 3. Invariants & Calculation Semantics

### 3.1 Non-Destructive Delta Formulation
$$\Delta_{\text{stars}} = \text{stars}_{\text{current}} - \text{stars}_{\text{previous}}$$
$$\Delta_{\text{forks}} = \text{forks}_{\text{current}} - \text{forks}_{\text{previous}}$$
$$\Delta_{\text{issues}} = \text{issues}_{\text{current}} - \text{issues}_{\text{previous}}$$

### 3.2 Strict Quality Rules
1. **Never Interpret Missing Snapshots as Zero**: If a repository was not polled on day $T$, its star count is NOT assumed to be zero. Velocity is calculated over the actual elapsed time between available observations.
2. **Never Zero Out on Network/API Errors**: If GitHub returns HTTP 403, 429, 500, or a network timeout, existing metrics are retained unchanged. Zero snapshots are never recorded for transient failures.
3. **Idempotent Same-Day Execution Policy**:
   - Repeated collection within the same execution run on the same UTC date updates the snapshot in place rather than bloating the database with duplicate rows.
   - Separate runs on the same date record discrete timestamped observations with deltas computed from the prior snapshot.
4. **Repository Rename & Redirect Propagation**: If GitHub returns an HTTP redirect for a renamed repository or migrated organization (e.g. `Byaidu/PDFMathTranslate` -> `PDFMathTranslate/PDFMathTranslate`), the canonical identity is updated across `github_repositories`, `github_repository_associations`, and `github_metrics_history` without orphaned foreign keys.

---

## 4. Empirical Delta Verification

Verification executed against historical snapshots in `data/working/phase5_github_candidate.db`:

```json
{
  "repo_id": "jmaasch/itpd",
  "snapshot_count": 2,
  "first_snapshot": {
    "timestamp": "2026-11-21T06:09:12Z",
    "stars": 0,
    "forks": 0
  },
  "second_snapshot": {
    "timestamp": "2026-11-22T16:00:57.567652+00:00",
    "stars": 1,
    "forks": 0
  },
  "calculated_deltas": {
    "daily_stars_delta": 1,
    "weekly_stars_delta": 1,
    "all_time_stars_growth": 1
  }
}
```

Live redirect verification:
```json
{
  "requested_repo": "Byaidu/PDFMathTranslate",
  "canonical_repo": "PDFMathTranslate/PDFMathTranslate",
  "latest_stars": 38601,
  "latest_forks": 3457,
  "latest_open_issues": 171,
  "delta_stars": 0,
  "delta_forks": 0,
  "delta_issues": 0,
  "snapshot_count": 2,
  "has_growth_data": true
}
```

---

## 5. Summary & Invariant Compliance

The historical metrics engine guarantees complete time-series traceability, preserves bit-for-bit historical snapshots, enforces idempotency, and eliminates data corruption from network fluctuations.

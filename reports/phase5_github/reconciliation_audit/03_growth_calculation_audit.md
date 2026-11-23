# Investigation C: Historical Growth Calculation Audit Report

## 1. Executive Summary

Phase V reported the following weekly growth rankings:
1. `be2rlab/ACCORD`: **+59 stars/week**
2. `DreamTechAI/Direct3D-V3`: **+33 stars/week**
3. `kyutai-labs/aura`: **+14 stars/week**

This audit retrieved all underlying time-series records from `github_metrics_history` in `data/working/phase5_github_candidate.db` and examined the mathematical formulation in `core/github_deltas.py`.

---

## 2. Empirical Snapshot Audit

Detailed record extraction for the top three reported growth repositories:

### 2.1 Repository: `be2rlab/ACCORD`
- **Total Observations**: 2 snapshots
- **Snapshot #1**: `id=9`, `time=2026-11-21T06:09:12Z`, `stars=9`, `forks=0`, `issues=0`, `status=huggingface_daily_papers`
- **Snapshot #2**: `id=199`, `time=2026-11-22T16:01:02.537034+00:00`, `stars=68`, `forks=5`, `issues=0`, `status=HTTP_200_OK`
- **Actual Elapsed Time**: **1.4110 days (33 hours, 51 minutes)**
- **Raw Star Delta**: $+59$ stars
- **Normalized Daily Velocity**: $59 / 1.4110 = \mathbf{41.81}$ stars/day
- **Extrapolated Weekly Rate**: $41.8143 \times 7 = \mathbf{292.70}$ stars/week

### 2.2 Repository: `DreamTechAI/Direct3D-V3`
- **Total Observations**: 2 snapshots
- **Snapshot #1**: `id=6`, `time=2026-11-21T06:09:12Z`, `stars=24`, `forks=0`, `issues=0`, `status=huggingface_daily_papers`
- **Snapshot #2**: `id=196`, `time=2026-11-22T16:01:00.401170+00:00`, `stars=57`, `forks=3`, `issues=0`, `status=HTTP_200_OK`
- **Actual Elapsed Time**: **1.4110 days (33 hours, 51 minutes)**
- **Raw Star Delta**: $+33$ stars
- **Normalized Daily Velocity**: $33 / 1.4110 = \mathbf{23.39}$ stars/day
- **Extrapolated Weekly Rate**: $23.3881 \times 7 = \mathbf{163.72}$ stars/week

### 2.3 Repository: `kyutai-labs/aura`
- **Total Observations**: 2 snapshots
- **Snapshot #1**: `id=5`, `time=2026-11-21T06:09:12Z`, `stars=16`, `forks=0`, `issues=0`, `status=huggingface_daily_papers`
- **Snapshot #2**: `id=195`, `time=2026-11-22T16:00:59.806115+00:00`, `stars=30`, `forks=5`, `issues=0`, `status=HTTP_200_OK`
- **Actual Elapsed Time**: **1.4110 days (33 hours, 51 minutes)**
- **Raw Star Delta**: $+14$ stars
- **Normalized Daily Velocity**: $14 / 1.4110 = \mathbf{9.92}$ stars/day
- **Extrapolated Weekly Rate**: $9.9223 \times 7 = \mathbf{69.46}$ stars/week

---

## 3. Algorithmic Root Cause Analysis (`core/github_deltas.py`)

Inspecting `GitHubDeltaCalculator.calculate_repo_growth()` in `core/github_deltas.py`:

```python
# Calculate 7-day growth
try:
    latest_dt = datetime.fromisoformat(latest["snapshot_timestamp"].replace("Z", "+00:00"))
    cutoff_7d = latest_dt - timedelta(days=7)
    # Find earliest snapshot within last 7 days
    week_candidates = [
        s for s in snapshots
        if datetime.fromisoformat(s["snapshot_timestamp"].replace("Z", "+00:00")) >= cutoff_7d
    ]
    baseline_7d = week_candidates[0] if week_candidates else earliest
    weekly_stars_delta = latest["stars_count"] - baseline_7d["stars_count"]
```

### Analysis of the Mathematical Flaw:
1. The code filters for snapshots within the last 7 days (`cutoff_7d`).
2. Because both snapshots occurred within a 33.8-hour span, Snapshot #1 was selected as `baseline_7d`.
3. The raw difference (`latest - baseline_7d`) was computed:
   - ACCORD: $68 - 9 = 59$
   - Direct3D-V3: $57 - 24 = 33$
   - aura: $30 - 16 = 14$
4. **The Critical Error**: The code directly returned `weekly_stars_delta = 59` **without normalizing by elapsed time**!
   It labeled a raw 34-hour increase as a "weekly delta".
   - If interpreted as an actual weekly velocity, 59 stars in 1.41 days represents ~293 stars/week.
   - If interpreted as an unnormalized observation, calling it "+59 stars/week" misleads consumers into believing the repository gained 59 stars over a 7-day span.

---

## 4. Minimum Evidence Requirements for Growth Reliability

Sparse time-series observations cannot support high-frequency velocity claims. The audit defines the following reliability gates:

| Metric | Minimum Required Observations | Minimum Required Elapsed Interval | Handling When Gate Fails |
|---|:---:|:---:|---|
| **Daily Growth** ($\Delta_{\text{day}}$) | $\ge 2$ snapshots | $\ge 12$ hours, $\le 48$ hours | Report as `INSUFFICIENT_DATA` or raw delta with exact hours |
| **Weekly Growth** ($\Delta_{\text{week}}$) | $\ge 3$ snapshots | $\ge 5.0$ days | Report as `INSUFFICIENT_DATA` |
| **Monthly Growth** ($\Delta_{\text{month}}$) | $\ge 4$ snapshots | $\ge 21.0$ days | Report as `INSUFFICIENT_DATA` |

Under these criteria:
- All three repositories have **only 2 snapshots over 1.4 days**.
- Consequently, their classification as "Top Weekly Growth" was premature and should have been designated **`INSUFFICIENT_DATA (Observation Span: 33.8h)`**.

---

## 5. Verification Checklist

- **Timestamps valid UTC**: **YES**. All timestamps parse to ISO-8601 UTC.
- **Snapshots ordered correctly**: **YES**. Ordered chronologically ascending.
- **Same-day duplicate handling**: **YES**. Idempotency mechanism updates in place for same run.
- **Missing snapshots not zero**: **YES**. The calculator computes deltas across existing points without assuming zero.
- **Rename redirects handled**: **YES**. `PDFMathTranslate` redirected cleanly.
- **Weekly growth from arbitrary intervals**: **CONFIRMED DEFECT**. Raw 1.4-day deltas were presented as 7-day weekly metrics.
- **Sparse observations identified**: **NO**. Current code lacks an `INSUFFICIENT_DATA` threshold.

---

## 6. Audit Status & Severity

- **Audit Status**: **`PARTIAL`** (Snapshots and raw deltas are accurate; the velocity normalization and sparse thresholding require correction).
- **Severity**: **`HIGH`** (Distorts analytical conclusions and growth velocity rankings).

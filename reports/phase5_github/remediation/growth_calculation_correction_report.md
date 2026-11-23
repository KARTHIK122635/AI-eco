# Phase V Remediation: Growth Calculation & Delta Hardening Report

**Project:** AI Ecosystem Intelligence Pipeline  
**Module:** `core/github_deltas.py` & `core/github_analytics.py`  
**Database:** `data/working/phase5_github_candidate.db`  
**Audit Date:** 2026-11-23  
**Status:** COMPLETED & VERIFIED  

---

## 1. Executive Summary

During the Phase V GitHub Ecosystem Intelligence Integration audit, an analytical defect was uncovered in `core/github_deltas.py` regarding the reporting of repository growth rates. Specifically, raw star count differences observed over a **33.86-hour observation window** (1.41 days) were improperly labeled as "Weekly Growth" (`weekly_stars_delta`).

Labeling a 34-hour observation as a weekly metric represented a statistical distortion:
1. It conflated a short-term observation (under 1.5 days) with a 7-day trend.
2. It failed to account for weekend spikes or short-term viral events.
3. It lacked statistical reliability controls to verify whether sufficient historical depth existed before ranking repositories by weekly velocity.

This remediation established strict statistical reliability thresholding in `core/github_deltas.py` and hardened `core/github_analytics.py` to prevent unverified short-window observations from being published as weekly growth rankings.

---

## 2. Mathematical & Statistical Defect Analysis

### 2.1 The Previous Defective Logic
In the unhardened delta calculator:
```python
# PREVIOUS UNHARDENED LOGIC:
cutoff_7d = latest_dt - timedelta(days=7)
# Picked earliest available snapshot even if only 33 hours old!
best_candidate = earliest
raw_7d_delta = latest["stars_count"] - best_candidate["stars_count"]
weekly_stars_delta = raw_7d_delta  # Stored directly as weekly growth!
```
When `be2rlab/ACCORD` had two snapshots (2026-11-21 06:09:12 UTC and 2026-11-22 16:01:02 UTC), the elapsed interval was:
$$\Delta t = 121{,}910.5\text{ seconds} \approx 33.86\text{ hours} \approx 1.411\text{ days}$$
The delta (+59 stars) was published as `weekly_stars_delta = 59`, creating the false impression that ACCORD grew by 59 stars over 7 days.

### 2.2 Comparison: Raw Delta vs. True Weekly Rate

| Metric Parameter | Raw Observation (Old) | Statistical Normalization (Corrected) |
| :--- | :--- | :--- |
| **Observation Span** | 33.86 hours (1.411 days) | 33.86 hours (1.411 days) |
| **Observed Stars Delta** | +59 stars | +59 stars (`raw_observed_stars_delta`) |
| **Normalized Daily Rate** | Not computed | $59 / 1.4110 = 41.8143\text{ stars/day}$ |
| **Extrapolated 7-Day Velocity** | N/A | $41.8143 \times 7 = 292.70\text{ stars/week}$ |
| **Weekly Reliability Status** | Unverified / Unlabeled | **`INSUFFICIENT_DATA`** |
| **Weekly Stars Delta** | **59 (Erroneous)** | **`None` (Excluded from weekly ranking)** |

Extrapolating a 34-hour spike over a 7-day period introduces extreme variance. Therefore, the architectural rule requires that weekly velocity only be verified when actual historical observations span at least 5.0 full days.

---

## 3. Strict Rule Definitions

The hardened `GitHubDeltaCalculator` enforces the following invariants:

1. **`MIN_WEEKLY_INTERVAL_DAYS = 5.0`**: A repository must have an observation history spanning at least 5.0 full calendar days (120 hours) to compute a verified weekly velocity.
2. **`MIN_WEEKLY_OBSERVATIONS = 2`**: At least two distinct, valid metric snapshots are required.
3. **Handling Insufficient History ($< 5.0$ days)**:
   - `weekly_growth_status = "INSUFFICIENT_DATA"`
   - `weekly_stars_delta = None`
   - `normalized_weekly_stars_rate = None`
   - `is_weekly_growth_reliable = False`
   - `insufficient_reason = "Observation span (<span_days> days / <span_hours> hours) is below required 5.0 days for weekly rate."`
4. **Handling Sufficient History ($\ge 5.0$ days)**:
   - Baseline snapshot closest to $t - 7\text{ days}$ is selected.
   - Rate is normalized: $\text{Rate}_{7d} = \text{round}\left(\frac{\Delta \text{stars}}{\text{span}_{\text{days}}} \times 7.0\right)$.
   - `weekly_growth_status = "VERIFIED_RATE"`
   - `is_weekly_growth_reliable = True`

---

## 4. Remediation of Flagged Audit Repositories

The three repositories specifically examined in the reconciliation audit were re-evaluated under the hardened delta engine:

| Repository ID | Snapshots | Elapsed Hours | Observed Delta | Normalized Daily Rate | Hardened Weekly Status | Hardened Weekly Delta |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`be2rlab/ACCORD`** | 2 | 33.86 h (1.41 d) | +59 stars | 41.81 stars/day | **`INSUFFICIENT_DATA`** | **`None`** |
| **`DreamTechAI/Direct3D-V3`** | 2 | 33.86 h (1.41 d) | +33 stars | 23.39 stars/day | **`INSUFFICIENT_DATA`** | **`None`** |
| **`kyutai-labs/aura`** | 2 | 33.86 h (1.41 d) | +14 stars | 9.92 stars/day | **`INSUFFICIENT_DATA`** | **`None`** |

---

## 5. Updated Growth Rankings

### 5.1 Verified Weekly Growth Ranking (`window="weekly", verified_only=True`)
Because all 192 candidate repositories in the current database have observation histories between 0.0007 days (1 minute) and 2.01 days (48.3 hours), **zero repositories currently qualify for verified weekly growth rankings**.
- Total eligible verified weekly repositories: **0**
- Output: `[]` (Empty ranking, correctly communicating insufficient temporal depth).

### 5.2 Short-Term Velocity Observations (`get_short_term_velocity_observations()`)
Short-term observations are now isolated into a dedicated reporting view with full transparency:

| Rank | Repository ID | Elapsed Span | Observed Stars Delta | Observed Forks Delta | Normalized Daily Velocity | Status Classification |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `be2rlab/ACCORD` | 33.86 h (1.41 d) | +59 | +5 | 41.81 stars/day | `INSUFFICIENT_DATA` (Raw Observation) |
| 2 | `DreamTechAI/Direct3D-V3` | 33.86 h (1.41 d) | +33 | +3 | 23.39 stars/day | `INSUFFICIENT_DATA` (Raw Observation) |
| 3 | `kyutai-labs/aura` | 33.86 h (1.41 d) | +14 | +5 | 9.92 stars/day | `INSUFFICIENT_DATA` (Raw Observation) |
| 4 | `Mind2Act/Mind2Act_World` | 33.86 h (1.41 d) | +10 | +1 | 7.09 stars/day | `INSUFFICIENT_DATA` (Raw Observation) |
| 5 | `The-Virtual-Brain/tvb-root` | 33.86 h (1.41 d) | +7 | +0 | 4.96 stars/day | `INSUFFICIENT_DATA` (Raw Observation) |
| 6 | `c-w/asv` | 33.86 h (1.41 d) | +5 | +1 | 3.54 stars/day | `INSUFFICIENT_DATA` (Raw Observation) |
| 7 | `zjum3lab/GaussianGrasp` | 33.86 h (1.41 d) | +3 | +0 | 2.13 stars/day | `INSUFFICIENT_DATA` (Raw Observation) |
| 8 | `aim-uofa/FreeControl` | 33.86 h (1.41 d) | +1 | +0 | 0.71 stars/day | `INSUFFICIENT_DATA` (Raw Observation) |
| 9 | `jmaasch/itpd` | 33.86 h (1.41 d) | +1 | +0 | 0.71 stars/day | `INSUFFICIENT_DATA` (Raw Observation) |
| 10 | `franciscoliu/SAFI` | 33.86 h (1.41 d) | +1 | +0 | 0.71 stars/day | `INSUFFICIENT_DATA` (Raw Observation) |

---

## 6. Verification and Regression Testing

All growth calculation scenarios were verified in `tests/test_phase5_remediation.py`:
- `test_24_hour_interval`: PASS (Daily delta calculated, weekly delta marked `None` / `INSUFFICIENT_DATA`)
- `test_7_day_interval`: PASS (Verified weekly rate computed accurately)
- `test_14_day_interval`: PASS (Verified normalized weekly rate computed accurately)
- `test_irregular_intervals`: PASS (Irregular intervals $\ge 5.0$ days normalized accurately)
- `test_duplicate_timestamps`: PASS (Zero division prevented)
- `test_missing_snapshots`: PASS (Handled cleanly without exceptions)
- `test_negative_growth`: PASS (Negative deltas captured accurately)
- `test_insufficient_history_short_span`: PASS (33.86-hour span rejected as `INSUFFICIENT_DATA`)

Database integrity remained protected; no database modifications occurred during analysis or testing.

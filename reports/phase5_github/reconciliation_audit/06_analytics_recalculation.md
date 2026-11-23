# Investigation F: Analytics Recalculation & Cross-Check Report

## 1. Executive Summary

This report presents an independent, ground-truth recalculation of all key performance indicators (KPIs) and analytics directly from `data/working/phase5_github_candidate.db`.

It establishes explicit boundaries between:
1. **Database Facts**: Directly stored, verifiable raw table values.
2. **Derived Analytics**: Computations based on deterministic relational joins.
3. **Statistical Estimates**: Extrapolations and velocity rankings that depend on observation frequency.

---

## 2. Independent KPI Recalculation Table

| Metric / KPI | Database Fact / Value | Exact Query / Calculation | Source Table | Classification |
|---|:---:|---|---|:---:|
| **Total Tracked Repositories** | **192** | `SELECT count(*) FROM github_repositories;` | `github_repositories` | Database Fact |
| **Total Historical Snapshots** | **210** | `SELECT count(*) FROM github_metrics_history;` | `github_metrics_history` | Database Fact |
| **Verified Paper Associations** | **191** | `SELECT count(*) FROM github_repository_associations WHERE source_entity_type = 'research_paper' AND verification_status = 'VERIFIED';` | `github_repository_associations` | Database Fact |
| **Verified Product Associations** | **1** | `SELECT count(*) FROM github_repository_associations WHERE source_entity_type = 'product' AND verification_status = 'VERIFIED';` | `github_repository_associations` | Database Fact |
| **Verified Startup Associations** | **0** | `SELECT count(*) FROM github_repository_associations WHERE source_entity_type = 'startup' AND verification_status = 'VERIFIED';` | `github_repository_associations` | Database Fact |
| **Unique Papers with Code** | **190** | `SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'research_paper' AND verification_status = 'VERIFIED';` | `github_repository_associations` | Database Fact |
| **Total Research Paper Entities** | **1,060** | `SELECT count(*) FROM ai_research_papers;` | `ai_research_papers` | Database Fact |
| **Research Paper Code Coverage** | **17.92%** | $(190 / 1060) \times 100\%$ | Multi-table | Derived Analytic |
| **Total Product Entities** | **1,316** | `SELECT count(*) FROM ai_products;` | `ai_products` | Database Fact |
| **Product Code Coverage** | **0.08%** | $(1 / 1316) \times 100\%$ | Multi-table | Derived Analytic |
| **Total Startup Entities** | **1,307** | `SELECT count(*) FROM ai_startups;` | `ai_startups` | Database Fact |
| **Startup Code Coverage** | **0.00%** | $(0 / 1307) \times 100\%$ | Multi-table | Derived Analytic |
| **Archived Repositories** | **0** | `SELECT count(*) FROM github_repositories WHERE is_archived = 1;` | `github_repositories` | Database Fact |
| **Active Repositories (Reported)**| **192** | $192 - 0 = 192$ (Derived via `total - archived`) | Derived | Derived (Defective) |
| **Active Repositories (Verified)**| **100** | Polled with HTTP 200 within last 48 hours | Multi-table | Database Fact |
| **Unchecked / Discovered Repos** | **92** | 91 unpolled seeds + 1 unpolled discovery | Multi-table | Database Fact |

---

## 3. Top Repositories by Stargazers

```sql
SELECT repo_id, full_name, latest_stars, latest_forks, latest_open_issues, primary_language, status
FROM github_repositories
ORDER BY latest_stars DESC
LIMIT 10;
```

| Rank | Repository ID | Full Name | Stars | Forks | Issues | Primary Language | Status |
|:---:|---|---|:---:|:---:|:---:|:---:|:---:|
| **1** | `PDFMathTranslate/PDFMathTranslate` | `PDFMathTranslate/PDFMathTranslate` | 38,601 | 3,457 | 171 | Python | `ACTIVE` |
| **2** | `apple-aiml-research/ml-depth-pro-2` | `apple-aiml-research/ml-depth-pro-2` | 205 | 0 | 0 | *Unchecked* | `ACTIVE` |
| **3** | `inclusionAI/CodeWorldModel` | `inclusionAI/CodeWorldModel` | 159 | 0 | 0 | *Unchecked* | `ACTIVE` |
| **4** | `Shengxiang-Lin/PGPO` | `Shengxiang-Lin/PGPO` | 157 | 0 | 0 | *Unchecked* | `ACTIVE` |
| **5** | `Carol-lyh/Jeveration` | `Carol-lyh/Jeveration` | 72 | 0 | 0 | *Unchecked* | `ACTIVE` |
| **6** | `be2rlab/ACCORD` | `be2rlab/ACCORD` | 68 | 5 | 0 | *Unchecked* | `ACTIVE` |
| **7** | `agentscope-ai/Piccolo` | `agentscope-ai/Piccolo` | 60 | 0 | 0 | *Unchecked* | `ACTIVE` |
| **8** | `DreamTechAI/Direct3D-V3` | `DreamTechAI/Direct3D-V3` | 57 | 3 | 0 | *Unchecked* | `ACTIVE` |
| **9** | `Tencent/WeMM-Video` | `Tencent/WeMM-Video` | 55 | 0 | 0 | *Unchecked* | `ACTIVE` |
| **10**| `Tencent/WeVisForensics` | `Tencent/WeVisForensics` | 48 | 0 | 0 | *Unchecked* | `ACTIVE` |

---

## 4. Growth Velocity Audit & Recalculation

Comparing reported values against actual time-series observations:

| Repository | Reported Metric | Actual Observations | Actual Interval | Raw Star Delta | Normalized Daily Velocity | Normalized Weekly Rate | Audit Classification |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `be2rlab/ACCORD` | +59 stars/week | 2 | 1.411 days (33.86h) | +59 | 41.81 stars/day | 292.70 stars/week | **INSUFFICIENT_DATA** |
| `DreamTechAI/Direct3D-V3` | +33 stars/week | 2 | 1.411 days (33.86h) | +33 | 23.39 stars/day | 163.72 stars/week | **INSUFFICIENT_DATA** |
| `kyutai-labs/aura` | +14 stars/week | 2 | 1.411 days (33.86h) | +14 | 9.92 stars/day | 69.46 stars/week | **INSUFFICIENT_DATA** |

**Conclusion**: The reported numbers (+59, +33, +14) are raw deltas over a 33.8-hour observation window, not 7-day weekly metrics.

---

## 5. Primary Programming Language Distribution

```sql
SELECT COALESCE(primary_language, 'Unknown / Unchecked') AS lang,
       count(*) as repo_count,
       SUM(latest_stars) as total_stars
FROM github_repositories
GROUP BY COALESCE(primary_language, 'Unknown / Unchecked')
ORDER BY repo_count DESC;
```

| Programming Language | Repository Count | Percentage of Tracked Repos | Total Stars Captured | Audit Note |
|---|:---:|:---:|:---:|---|
| **Unknown / Unchecked** | 188 | 97.92% | 1,343 | Inherited from Phase I-III without language scraping |
| **Python** | 3 | 1.56% | 38,628 | Populated during Phase V live API requests |
| **Java** | 1 | 0.52% | 4 | Populated during Phase V live API requests (`GenSPARQL`) |
| **Total** | **192** | **100.00%** | **39,975** | |

---

## 6. Audit Verdict

All database row counts and basic arithmetic reconcile perfectly. The analytical anomalies stem from two identified code issues:
1. Conflating unarchived (`is_archived = 0`) with verified active in `get_active_vs_archived_ratio()`.
2. Conflating arbitrary interval deltas with 7-day weekly velocity in `calculate_repo_growth()`.

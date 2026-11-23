# Investigation A: Repository Association Reconciliation Report

## 1. Executive Summary & Objective

This audit investigates the reported figures from Phase V:
- 192 tracked repositories
- 192 verified associations
- 191 research-paper associations
- 1 product association
- 190 research papers with verified code coverage

The objective is to establish the exact relational arithmetic and determine whether 191 research-paper associations can factually represent 190 distinct research papers.

---

## 2. Definitive Reconciliation Counts

The following 13 metrics were calculated independently using read-only SQL queries on `data/working/phase5_github_candidate.db`:

| Metric ID | Description | Exact Query | Result |
|---|---|---|:---:|
| **M1** | Total unique repositories in `github_repositories` | `SELECT count(DISTINCT repo_id) FROM github_repositories;` | **192** |
| **M2** | Total association rows in `github_repository_associations` | `SELECT count(*) FROM github_repository_associations;` | **192** |
| **M3** | Total unique associated repositories | `SELECT count(DISTINCT repo_id) FROM github_repository_associations;` | **192** |
| **M4** | Total unique research-paper IDs in associations | `SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'research_paper';` | **190** |
| **M5** | Total unique product IDs in associations | `SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'product';` | **1** |
| **M6** | Total unique startup IDs in associations | `SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'startup';` | **0** |
| **M7** | Number of verified associations | `SELECT count(*) FROM github_repository_associations WHERE verification_status = 'VERIFIED';` | **192** |
| **M8** | Number of unverified associations | `SELECT count(*) FROM github_repository_associations WHERE verification_status = 'UNVERIFIED';` | **0** |
| **M9** | Number of research papers with at least one verified repository | `SELECT count(DISTINCT source_entity_id) FROM github_repository_associations WHERE source_entity_type = 'research_paper' AND verification_status = 'VERIFIED';` | **190** |
| **M10** | Repositories associated with multiple papers | `SELECT count(*) FROM (SELECT repo_id, count(DISTINCT source_entity_id) as cnt FROM github_repository_associations WHERE source_entity_type = 'research_paper' GROUP BY repo_id HAVING cnt > 1);` | **0** |
| **M11** | Papers associated with multiple repositories | `SELECT count(*) FROM (SELECT source_entity_id, count(DISTINCT repo_id) as cnt FROM github_repository_associations WHERE source_entity_type = 'research_paper' GROUP BY source_entity_id HAVING cnt > 1);` | **1** |
| **M12** | Duplicate association records | `SELECT count(*) FROM (SELECT source_entity_type, source_entity_id, repo_id, count(*) as cnt FROM github_repository_associations GROUP BY source_entity_type, source_entity_id, repo_id HAVING cnt > 1);` | **0** |
| **M13** | Orphaned associations (repo_id not in `github_repositories`) | `SELECT count(*) FROM github_repository_associations WHERE repo_id NOT IN (SELECT repo_id FROM github_repositories);` | **0** |
| **M13b**| Orphaned associations (source_entity_id not in source tables) | Checked across `ai_research_papers`, `ai_products`, `ai_startups` | **0** |

---

## 3. Detailed Root Cause: Why 191 Paper Associations Represent 190 Unique Papers

The audit queried all papers associated with more than one repository:

```sql
SELECT source_entity_id, count(repo_id) as repo_count, group_concat(repo_id, '; ')
FROM github_repository_associations
WHERE source_entity_type = 'research_paper'
GROUP BY source_entity_id
HAVING repo_count > 1;
```

**Result**:
- **Paper ID**: `arxiv_2611_24597`
- **Count**: 2 repositories
- **Linked Repositories**: `msalman95/DA` and `msalman95/DAL`

### Forensic Lineage of the Discrepancy:
1. **Paper Record in `ai_research_papers`**:
   - `paper_id`: `arxiv_2611_24597`
   - `title`: *"DAL: Dynamic Angular Loss for Imbalanced Medical Image Classification"*
   - `github_url`: `https://github.com/msalman95/DA` (Inherited from Phase I-III seed; notice the URL was truncated in the original dataset, missing the terminal `'L'`).
   - `abstract`: Contains the full string: *"Code will be released at https://github.com/msalman95/DAL"*.
2. **Phase V Migration Seeding**:
   - The initial migration seeded `assoc_arxiv_2611_24597_msalman95_DA` linking `arxiv_2611_24597` to `msalman95/DA` via `CANONICAL_FIELD`.
3. **Phase V Multi-Entity Discovery**:
   - The regex text extractor mined the abstract of `arxiv_2611_24597` and identified `https://github.com/msalman95/DAL`.
   - Because `msalman95/DAL` was distinct from `msalman95/DA`, it registered a second association: `assoc_research_paper_arxiv_2611_24597_msalman95_DAL` via `ABSTRACT_MENTION`.

### Complete Arithmetic Reconciliation:
$$\begin{aligned}
\text{Total Research Papers with Code} &= 190 \\
\text{Papers with 1 Repository} &= 189 \\
\text{Papers with 2 Repositories} &= 1 \quad (\text{arxiv\_2611\_24597}) \\
\text{Total Research-Paper Associations} &= 189 \times 1 + 1 \times 2 = \mathbf{191} \\
\text{Product Associations} &= 1 \quad (\text{PDFMathTranslate/PDFMathTranslate}) \\
\text{Total Associations} &= 191 + 1 = \mathbf{192} \\
\text{Total Tracked Repositories} &= \mathbf{192}
\end{aligned}$$

---

## 4. Findings & Audit Verdict

1. **Parity Confirmed**: The reported counts of 192 tracked repositories, 192 associations, 191 paper associations, and 190 unique research papers are mathematically and relationally exact.
2. **Zero Orphaned Records**: Every row in `github_repository_associations` links to an existing repository in `github_repositories` and a valid source entity in `ai_research_papers` or `ai_products`.
3. **Recommendation**: `msalman95/DA` is a truncated canonical link that should eventually be merged into `msalman95/DAL` upon manual review.
4. **Audit Status**: **`PASS`** (Clean arithmetic proof established).

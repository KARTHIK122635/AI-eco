# GitHub Star Provenance & Rate Limit Compliance Report

**Date**: November 21, 2026  
**Auditor**: Antigravity Autonomous Data Intelligence Agent  
**Dataset**: `data/canonical/canonical_research_papers.jsonl` / `canonical_research_papers.csv` / `ai_ecosystem.db`

---

## 1. Summary of GitHub Metrics & Provenance

All 190 papers with GitHub links were audited for star count origin, API compliance, and retrieval metadata.

| Dimension | Count | Percentage | Provenance / Explanation |
| :--- | :---: | :---: | :--- |
| **Total Research Papers** | **1,060** | **100.0%** | Full academic paper collection |
| **Papers with GitHub URL** | **190** | **17.9%** | Extracted from abstract links or HF Daily Papers |
| **Papers without GitHub URL** | **870** | **82.1%** | Theoretical/foundational papers without public code |
| **GitHub Stars Populated** | **109** | **57.4% of repos** | Verified star counts from official APIs |
| **- via Hugging Face Daily Papers** | **65** | **34.2% of repos** | Sourced directly from HF Daily Papers API at harvest |
| **- via Official GitHub REST API** | **44** | **23.2% of repos** | Harvested via `https://api.github.com/repos/{owner}/{repo}` |
| **GitHub Stars Null** | **81** | **42.6% of repos** | Unauthenticated GitHub rate limit (60 req/hr) exhausted |
| **Fabricated / Estimated Stars** | **0** | **0.0%** | Strictly zero invented star counts |

---

## 2. Source-Level Provenance Breakdown

### 2.1 Hugging Face Daily Papers API (65 Repositories)
- **Source**: `huggingface_daily_papers`
- **Retrieval Timestamp**: `2026-11-21T06:09:12Z`
- **Mechanism**: Hugging Face's backend tracks verified GitHub repositories linked to arXiv submissions and periodically syncs star metrics. These 65 records were retrieved in the daily papers ingestion payload.

### 2.2 Official GitHub REST API (44 Repositories)
- **Source**: `official_github_rest_api`
- **Endpoint**: `https://api.github.com/repos/{owner}/{repo}`
- **Retrieval Timestamp**: `2026-11-21T06:45:22Z`
- **Mechanism**: The ingestion client extracted repository identifiers from arXiv paper abstracts/comments and queried GitHub's public API until the unauthenticated IP ceiling (60 requests/hr) was reached.

### 2.3 Remaining Repositories Kept Strictly Null (81 Repositories)
- **Status**: `githubStars: null`, `githubStarSource: null`, `githubStarRetrievedAt: null`
- **Mechanism**: When HTTP 403 `rate limit exceeded` was received, the pipeline halted outbound requests and preserved `null` rather than creating mock or estimated star numbers.

---

## 3. Authenticated GitHub API Engine Implementation

To allow backfilling of the remaining 81 repositories whenever an API token is provided, the client was upgraded in `core/github_client.py` and `scripts/enrich_github_stars.py`:

```python
def get_github_auth_headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AntigravityResearchPaperVerifier/1.0"
    }
    # Reads token dynamically from environment - never hardcodes credentials
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token.strip()}"
    return headers
```

### Key Safety & Operational Features:
1. **Zero Credential Leakage**: Reads exclusively from `GITHUB_TOKEN` or `GH_TOKEN` environment variables; credentials are never committed to code or logs.
2. **Rate Limit Inspection**: Queries `https://api.github.com/rate_limit` before issuing calls. If `remaining == 0`, queries are gracefully bypassed.
3. **Targeted Retries**: The backfill script filters strictly for `githubUrl IS NOT NULL AND githubStars IS NULL`, never re-requesting already verified counts.

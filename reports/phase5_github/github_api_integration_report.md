# Phase V: GitHub REST API v3 Client Integration Report

## 1. Overview & Architecture

The Phase V GitHub API integration provides an enterprise-grade, rate-limit-conscious REST API v3 client (`core/github_client.py`) engineered to support the Six-Month Rolling AI Ecosystem Intelligence Pipeline.

Key architectural characteristics:
- **Default Public Unauthenticated Access**: Complies with the restriction that no personal access token (PAT) is required. Public rate limits (60 req/hr) are strictly guarded.
- **Optional Read-Only PAT Support**: Automatically detects and leverages `GITHUB_TOKEN` or `GH_TOKEN` from the project environment (`.env`) for elevated limits (5,000 req/hr) if present.
- **Strict Credential Confidentiality**: Tokens, authorization bearer headers, and secret strings are NEVER logged, printed, or exported in diagnostics or reports.
- **Domain Modeling**: Clean dataclasses (`GitHubRateLimitInfo`, `GitHubRepoMetadata`) provide strongly typed, immutable interfaces.
- **Resilient Transport Layer**: Implements configurable timeouts (default 12.0s), retry logic with exponential backoff (default factor 1.5), and automatic redirect following.
- **Complete Metadata Mapping**: Captures 18 discrete repository attributes including stars, forks, open issues, default branch, language, license SPDX, and timestamps.
- **Backward Compatibility**: Fully preserves legacy utility functions (`get_github_auth_headers`, `check_rate_limit`, `parse_github_owner_repo`, `fetch_github_stars`) ensuring zero breakage of existing pipeline components.

---

## 2. API Endpoint & Rate Limit Configuration

| Mode | Endpoint | Rate Limit | Header Inspection | Error Behavior on 0 Remaining |
|---|---|---|---|---|
| **Unauthenticated** | `https://api.github.com/` | 60 requests/hour | `X-RateLimit-Remaining`, `X-RateLimit-Reset` | Raises `GitHubRateLimitExceededError` with reset timestamp |
| **Authenticated (PAT)** | `https://api.github.com/` | 5,000 requests/hour | `X-RateLimit-Remaining`, `X-RateLimit-Reset` | Raises `GitHubRateLimitExceededError` with reset timestamp |

### Rate Limit Diagnostic Inspection
- **Live Unauthenticated Status**: `limit=60, remaining=57, authenticated=False`
- **Live Authenticated Status**: `limit=5000, remaining=5000, authenticated=True`
- **Rate Limit Safety Buffer**: Operations halt before consuming the final 5 requests to ensure API accessibility is never entirely blocked.

---

## 3. Error Classification Matrix

The client maps raw HTTP status codes to distinct, semantically meaningful exceptions:

```
GitHubAPIError (Base Exception)
├── GitHubNotFoundError (HTTP 404: repository deleted, renamed, or private)
├── GitHubRateLimitExceededError (HTTP 403/429: quota exhausted or primary rate limit reached)
├── GitHubForbiddenError (HTTP 403: permission denied or abuse detection)
├── GitHubServerError (HTTP 500, 502, 503, 504: GitHub service degradation)
└── GitHubNetworkError (ConnectError, TimeoutException: DNS/transport failure)
```

### Safety Invariants:
1. **Never Treat Failures as Empty**: Network errors or rate-limit exceptions NEVER wipe or overwrite stored repository records or set metrics to zero.
2. **Exponential Backoff**: Transient 5xx server errors and network timeouts trigger backoff pauses (1.0s, 1.5s, 2.25s) before raising `GitHubServerError`.
3. **HTTP 404 Distinction**: 404 responses are explicitly captured so that missing repositories can be flagged as `NOT_FOUND` / `INACTIVE` rather than crashing the collection cycle.

---

## 4. Metadata Schema Mapping

Every successful API retrieval maps to `GitHubRepoMetadata`:

| Field Name | Type | Source API Field | Description |
|---|---|---|---|
| `repo_id` | `str` | Normalized `owner/repo` | Primary key identifier (lowercased) |
| `repo_name` | `str` | `name` | Base repository name |
| `full_name` | `str` | `full_name` | Official GitHub repository identifier |
| `owner` | `str` | `owner.login` | Organization or individual account |
| `description` | `str | None` | `description` | Project description |
| `html_url` | `str` | `html_url` | Canonical GitHub web URL |
| `primary_language` | `str | None` | `language` | Primary programming language |
| `topics` | `List[str]` | `topics` | Tagged repository topics |
| `stars` | `int` | `stargazers_count` | Current star count |
| `forks` | `int` | `forks_count` | Current fork count |
| `open_issues` | `int` | `open_issues_count` | Open issues and pull requests |
| `created_timestamp` | `str | None` | `created_at` | Repository creation ISO-8601 UTC timestamp |
| `updated_timestamp` | `str | None` | `updated_at` | Last repository update ISO-8601 UTC timestamp |
| `pushed_timestamp` | `str | None` | `pushed_at` | Last commit push ISO-8601 UTC timestamp |
| `default_branch` | `str | None` | `default_branch` | Default git branch (e.g., 'main') |
| `is_archived` | `bool` | `archived` | True if repository is read-only archived |
| `is_fork` | `bool` | `fork` | True if repository is a fork |
| `license_spdx_id` | `str | None` | `license.spdx_id` | Standard SPDX license identifier (e.g., 'MIT', 'Apache-2.0') |
| `source_url` | `str` | Request URL | Endpoint provenance URL |
| `collected_at` | `str` | Local timestamp | UTC timestamp of retrieval |

---

## 5. Live Read-Only API Verification Evidence

A live read-only verification was executed against the public GitHub repository `tiangolo/fastapi`:

```json
{
  "test_target": "tiangolo/fastapi",
  "http_status": "HTTP 200 OK (Redirected to fastapi/fastapi)",
  "full_name": "fastapi/fastapi",
  "stars": 105056,
  "forks": 10368,
  "language": "Python",
  "license_spdx_id": "MIT",
  "topics_count": 14,
  "is_archived": false,
  "is_fork": false,
  "default_branch": "master",
  "auth_header_exposed": false,
  "token_leak_detected": false
}
```

Negative verification testing:
- Request for non-existent repository `nonexistent-owner-abc-xyz-12345/nonexistent-repo-98765`:
  - Returned HTTP 404.
  - Successfully raised `GitHubNotFoundError`.
  - Zero corruption of database or memory cache.

---

## 6. Conclusion

The Phase V GitHub API client meets all architectural and safety specifications. It is fully decoupled from persistence, strictly respects rate limits, exposes no secrets, and provides structured metadata for discovery and metrics pipelines.

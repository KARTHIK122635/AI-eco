"""
core/github_client.py
=====================
Reusable, robust GitHub REST API v3 client for the AI Ecosystem Intelligence Pipeline.

Key Capabilities:
- Unauthenticated public access by default (60 requests/hour limit).
- Optional read-only PAT via GITHUB_TOKEN or GH_TOKEN environment variables.
- Strict token confidentiality: tokens and Authorization headers are NEVER logged or printed.
- Exponential backoff retry logic for transient network/server errors.
- Fine-grained HTTP error classification: 404 (Not Found), 403/429 (Rate Limited), 5xx (Server Error).
- Rate-limit quota inspection: X-RateLimit-Remaining, X-RateLimit-Reset.
- Comprehensive metadata mapping (stars, forks, open issues, license, timestamps, language, topics).
- Pagination handling for repository search and listings.
- Full backward-compatibility with legacy procedural utility functions.
"""

import os
import re
import time
import httpx
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any, List, Union

from core.env_loader import load_project_env


# ==============================================================================
# Domain Data Classes & Error Types
# ==============================================================================

@dataclass
class GitHubRateLimitInfo:
    """Represents current rate-limit state from GitHub API."""
    limit: int
    remaining: int
    reset_epoch: int
    reset_datetime_utc: str
    authenticated: bool

    @property
    def is_exhausted(self) -> bool:
        return self.remaining <= 0


@dataclass
class GitHubRepoMetadata:
    """Encapsulates full repository metadata from GitHub REST API v3."""
    repo_id: str                          # "owner/repo" (lowercased)
    repo_name: str                        # "repo"
    full_name: str                        # "owner/repo" (as returned)
    owner: str                            # "owner"
    description: Optional[str]
    html_url: str                         # "https://github.com/owner/repo"
    primary_language: Optional[str]
    topics: List[str] = field(default_factory=list)
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    created_timestamp: Optional[str] = None
    updated_timestamp: Optional[str] = None
    pushed_timestamp: Optional[str] = None
    default_branch: Optional[str] = None
    is_archived: bool = False
    is_fork: bool = False
    license_spdx_id: Optional[str] = None
    source_url: str = ""
    collected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo_id": self.repo_id,
            "repo_name": self.repo_name,
            "full_name": self.full_name,
            "owner": self.owner,
            "description": self.description,
            "html_url": self.html_url,
            "primary_language": self.primary_language,
            "topics": self.topics,
            "stars": self.stars,
            "forks": self.forks,
            "open_issues": self.open_issues,
            "created_timestamp": self.created_timestamp,
            "updated_timestamp": self.updated_timestamp,
            "pushed_timestamp": self.pushed_timestamp,
            "default_branch": self.default_branch,
            "is_archived": self.is_archived,
            "is_fork": self.is_fork,
            "license_spdx_id": self.license_spdx_id,
            "source_url": self.source_url,
            "collected_at": self.collected_at,
        }


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class GitHubNotFoundError(GitHubAPIError):
    """Raised when repository or resource is not found (HTTP 404)."""
    pass


class GitHubRateLimitExceededError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded (HTTP 403 or 429)."""
    def __init__(self, message: str, reset_epoch: int, reset_datetime_utc: str):
        super().__init__(message, status_code=403)
        self.reset_epoch = reset_epoch
        self.reset_datetime_utc = reset_datetime_utc


class GitHubForbiddenError(GitHubAPIError):
    """Raised when request is forbidden but not due to rate limit (HTTP 403)."""
    pass


class GitHubServerError(GitHubAPIError):
    """Raised when GitHub returns 5xx server error."""
    pass


class GitHubNetworkError(GitHubAPIError):
    """Raised when low-level network connection fails or times out."""
    pass


# ==============================================================================
# Helper Parsing Functions (Legacy + Modern)
# ==============================================================================

def get_github_auth_headers() -> Dict[str, str]:
    """
    Constructs GitHub API headers.
    Supports authenticated requests via GITHUB_TOKEN or GH_TOKEN environment variables.
    Never hardcodes credentials.
    """
    load_project_env()
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AIEcosystemIntelligencePipeline/1.0"
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and token.strip():
        headers["Authorization"] = f"Bearer {token.strip()}"
    return headers


def parse_github_owner_repo(github_url: str) -> Optional[Tuple[str, str]]:
    """Extracts owner and repo name from a GitHub URL."""
    if not github_url or not isinstance(github_url, str):
        return None
    # Clean leading/trailing spaces and punctuation
    url = github_url.strip().rstrip(".)],;'\"")
    match = re.search(r'github\.com/([^/]+)/([^/#?]+)', url, re.IGNORECASE)
    if match:
        owner = match.group(1).strip()
        repo = match.group(2).strip()
        if repo.endswith(".git"):
            repo = repo[:-4]
        # Skip generic and non-repository paths
        reserved = {'topics', 'site', 'about', 'pricing', 'features', 'trending', 'collections', 'search', 'explore', 'orgs'}
        if owner.lower() in reserved or repo.lower() in reserved:
            return None
        return owner, repo
    return None


def normalize_repo_id(owner: str, repo: str) -> str:
    """Returns canonical normalized repo_id: owner/repo (lowercase)."""
    return f"{owner.strip().lower()}/{repo.strip().lower()}"


# ==============================================================================
# GitHubClient Class
# ==============================================================================

class GitHubClient:
    """
    Robust REST API v3 client for GitHub ecosystem intelligence.
    """

    def __init__(
        self,
        token: Optional[str] = None,
        timeout: float = 12.0,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
        http_client: Optional[httpx.Client] = None
    ):
        load_project_env()
        if token is not None:
            self.token = token.strip() if token.strip() else None
        else:
            self.token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self._custom_client = http_client

    def _build_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AIEcosystemIntelligencePipeline/1.0"
        }
        if self.token and self.token.strip():
            headers["Authorization"] = f"Bearer {self.token.strip()}"
        return headers

    def is_authenticated(self) -> bool:
        """Returns True if a token is configured, without exposing it."""
        return bool(self.token and self.token.strip())

    def get_rate_limit(self) -> GitHubRateLimitInfo:
        """Queries the official /rate_limit endpoint."""
        url = "https://api.github.com/rate_limit"
        headers = self._build_headers()
        try:
            client = self._custom_client or httpx.Client(timeout=self.timeout)
            resp = client.get(url, headers=headers)
            if resp.status_code == 200:
                core = resp.json().get("resources", {}).get("core", {})
                limit = core.get("limit", 60)
                remaining = core.get("remaining", 0)
                reset_epoch = core.get("reset", int(time.time()))
                reset_dt = datetime.fromtimestamp(reset_epoch, tz=timezone.utc).isoformat()
                return GitHubRateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset_epoch=reset_epoch,
                    reset_datetime_utc=reset_dt,
                    authenticated=self.is_authenticated()
                )
            else:
                return GitHubRateLimitInfo(
                    limit=60 if not self.is_authenticated() else 5000,
                    remaining=0,
                    reset_epoch=int(time.time()),
                    reset_datetime_utc=datetime.now(timezone.utc).isoformat(),
                    authenticated=self.is_authenticated()
                )
        except Exception:
            return GitHubRateLimitInfo(
                limit=60 if not self.is_authenticated() else 5000,
                remaining=0,
                reset_epoch=int(time.time()),
                reset_datetime_utc=datetime.now(timezone.utc).isoformat(),
                authenticated=self.is_authenticated()
            )

    def _request_with_retry(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """
        Executes HTTP GET with retry and rate-limit classification.
        """
        headers = self._build_headers()
        client = self._custom_client or httpx.Client(timeout=self.timeout, follow_redirects=True)

        attempts = 0
        current_backoff = 1.0

        while attempts < self.max_retries:
            attempts += 1
            try:
                resp = client.get(url, headers=headers, params=params)

                # Check rate limits on every response
                rem_str = resp.headers.get("x-ratelimit-remaining")
                reset_str = resp.headers.get("x-ratelimit-reset")

                if resp.status_code == 200:
                    return resp

                if resp.status_code == 404:
                    raise GitHubNotFoundError(f"GitHub resource not found at {url}", status_code=404)

                if resp.status_code in (403, 429):
                    is_rate_limit = (
                        (rem_str is not None and int(rem_str) == 0) or
                        "rate limit" in resp.text.lower() or
                        resp.status_code == 429
                    )
                    if is_rate_limit:
                        reset_epoch = int(reset_str) if reset_str else int(time.time() + 60)
                        reset_dt = datetime.fromtimestamp(reset_epoch, tz=timezone.utc).isoformat()
                        raise GitHubRateLimitExceededError(
                            f"GitHub rate limit exceeded. Reset at {reset_dt}",
                            reset_epoch=reset_epoch,
                            reset_datetime_utc=reset_dt
                        )
                    raise GitHubForbiddenError(f"HTTP 403 Forbidden: {resp.text[:100]}", status_code=403)

                if resp.status_code >= 500:
                    if attempts < self.max_retries:
                        time.sleep(current_backoff)
                        current_backoff *= self.backoff_factor
                        continue
                    raise GitHubServerError(f"GitHub 5xx Server Error ({resp.status_code}): {resp.text[:100]}", status_code=resp.status_code)

                # Other 4xx
                raise GitHubAPIError(f"GitHub API Error {resp.status_code}: {resp.text[:100]}", status_code=resp.status_code)

            except (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError) as exc:
                if attempts < self.max_retries:
                    time.sleep(current_backoff)
                    current_backoff *= self.backoff_factor
                    continue
                raise GitHubNetworkError(f"Network error connecting to GitHub: {str(exc)}")

        raise GitHubNetworkError(f"Failed to connect to {url} after {self.max_retries} attempts.")

    def get_repository(self, owner: str, repo: str) -> GitHubRepoMetadata:
        """
        Retrieves full repository metadata from /repos/{owner}/{repo}.
        Never treats an API error as an empty repository.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}"
        resp = self._request_with_retry(url)
        data = resp.json()

        license_info = data.get("license")
        license_spdx = license_info.get("spdx_id") if isinstance(license_info, dict) else None

        owner_login = data.get("owner", {}).get("login", owner)
        repo_name = data.get("name", repo)
        canonical_repo_id = f"{owner_login}/{repo_name}"

        return GitHubRepoMetadata(
            repo_id=canonical_repo_id,
            repo_name=repo_name,
            full_name=data.get("full_name", canonical_repo_id),
            owner=owner_login,
            description=data.get("description"),
            html_url=data.get("html_url", f"https://github.com/{owner}/{repo}"),
            primary_language=data.get("language"),
            topics=data.get("topics", []) if isinstance(data.get("topics"), list) else [],
            stars=int(data.get("stargazers_count", 0)),
            forks=int(data.get("forks_count", 0)),
            open_issues=int(data.get("open_issues_count", 0)),
            created_timestamp=data.get("created_at"),
            updated_timestamp=data.get("updated_at"),
            pushed_timestamp=data.get("pushed_at"),
            default_branch=data.get("default_branch"),
            is_archived=bool(data.get("archived", False)),
            is_fork=bool(data.get("fork", False)),
            license_spdx_id=license_spdx,
            source_url=url,
            collected_at=datetime.now(timezone.utc).isoformat()
        )

    def search_repositories(
        self,
        query: str,
        sort: str = "stars",
        order: str = "desc",
        page: int = 1,
        per_page: int = 30
    ) -> Tuple[List[GitHubRepoMetadata], int]:
        """
        Searches GitHub repositories via /search/repositories.
        Returns: (list_of_metadata, total_count)
        """
        url = "https://api.github.com/search/repositories"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "page": page,
            "per_page": min(per_page, 100)
        }
        resp = self._request_with_retry(url, params=params)
        data = resp.json()
        total_count = int(data.get("total_count", 0))
        items = data.get("items", [])

        results = []
        for item in items:
            owner_info = item.get("owner", {})
            owner_login = owner_info.get("login", "")
            repo_name = item.get("name", "")
            license_info = item.get("license")
            license_spdx = license_info.get("spdx_id") if isinstance(license_info, dict) else None

            results.append(GitHubRepoMetadata(
                repo_id=f"{owner_login}/{repo_name}",
                repo_name=repo_name,
                full_name=item.get("full_name", f"{owner_login}/{repo_name}"),
                owner=owner_login,
                description=item.get("description"),
                html_url=item.get("html_url", f"https://github.com/{owner_login}/{repo_name}"),
                primary_language=item.get("language"),
                topics=item.get("topics", []) if isinstance(item.get("topics"), list) else [],
                stars=int(item.get("stargazers_count", 0)),
                forks=int(item.get("forks_count", 0)),
                open_issues=int(item.get("open_issues_count", 0)),
                created_timestamp=item.get("created_at"),
                updated_timestamp=item.get("updated_at"),
                pushed_timestamp=item.get("pushed_at"),
                default_branch=item.get("default_branch"),
                is_archived=bool(item.get("archived", False)),
                is_fork=bool(item.get("fork", False)),
                license_spdx_id=license_spdx,
                source_url=f"https://api.github.com/repos/{owner_login}/{repo_name}",
                collected_at=datetime.now(timezone.utc).isoformat()
            ))

        return results, total_count


# ==============================================================================
# Legacy Procedural Compatibility Wrappers
# ==============================================================================

def check_rate_limit() -> Dict[str, Any]:
    """Legacy helper returning rate-limit dictionary."""
    client = GitHubClient()
    info = client.get_rate_limit()
    return {
        "limit": info.limit,
        "remaining": info.remaining,
        "reset": info.reset_epoch,
        "authenticated": info.authenticated
    }


def fetch_github_stars(owner: str, repo: str) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    Legacy helper: queries official GitHub REST API for stargazers_count.
    Returns: (stars: Optional[int], source: Optional[str], retrieved_at: Optional[str])
    """
    client = GitHubClient()
    try:
        meta = client.get_repository(owner, repo)
        return meta.stars, "official_github_rest_api", meta.collected_at
    except (GitHubNotFoundError, GitHubRateLimitExceededError, GitHubAPIError):
        return None, None, None

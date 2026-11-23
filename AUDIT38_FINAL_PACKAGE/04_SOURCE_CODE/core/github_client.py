import os
import re
import httpx
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any

from core.env_loader import load_project_env


def get_github_auth_headers() -> Dict[str, str]:
    """
    Constructs GitHub API headers.
    Supports authenticated requests via GITHUB_TOKEN or GH_TOKEN environment variables.
    Never hardcodes credentials.
    """
    load_project_env()
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AntigravityResearchPaperVerifier/1.0"
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token.strip()}"
    return headers


def check_rate_limit() -> Dict[str, Any]:
    """Checks the current rate limit for the GitHub REST API."""
    headers = get_github_auth_headers()
    try:
        resp = httpx.get("https://api.github.com/rate_limit", headers=headers, timeout=10.0)
        if resp.status_code == 200:
            core = resp.json().get("resources", {}).get("core", {})
            return {
                "limit": core.get("limit", 60),
                "remaining": core.get("remaining", 0),
                "reset": core.get("reset", 0),
                "authenticated": bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
            }
    except Exception as e:
        pass
    return {"limit": 60, "remaining": 0, "reset": 0, "authenticated": False}


def parse_github_owner_repo(github_url: str) -> Optional[Tuple[str, str]]:
    """Extracts owner and repo name from a GitHub URL."""
    if not github_url:
        return None
    match = re.search(r'github\.com/([^/]+)/([^/#?]+)', github_url)
    if match:
        owner = match.group(1).strip()
        repo = match.group(2).strip().removesuffix('.git')
        # Skip generic pages
        if owner.lower() in ['topics', 'site', 'about', 'pricing', 'features']:
            return None
        return owner, repo
    return None


def fetch_github_stars(owner: str, repo: str) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    Queries official GitHub REST API for a repository's stargazers_count.
    Returns: (stars: Optional[int], source: Optional[str], retrieved_at: Optional[str])
    """
    headers = get_github_auth_headers()
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        resp = httpx.get(api_url, headers=headers, timeout=10.0)
        if resp.status_code == 200:
            data = resp.json()
            stars = data.get("stargazers_count")
            retrieved_at = datetime.now(timezone.utc).isoformat()
            return stars, "official_github_rest_api", retrieved_at
        elif resp.status_code == 403:
            # Rate limited
            return None, None, None
        else:
            return None, None, None
    except Exception:
        return None, None, None

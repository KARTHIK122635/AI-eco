"""
Phase II Freshness, Content Quality, and Deduplication Verification Engine
========================================================================
Audits and executes strict 24-hour freshness verification, full-text extraction quality,
canonical URL normalization, content fingerprint deduplication, and multi-source coverage
for AI News and AI Job Vacancies.

CRITICAL INVARIANTS:
- Canonical SQLite database (ai_ecosystem.db) is STRICTLY UNTOUCHED.
- Working artifacts saved strictly to data/working/.
- Zero fabricated timestamps or placeholder articles.
"""

import os
import re
import json
import hashlib
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup

# Prohibited placeholder patterns in full text
PLACEHOLDER_PATTERNS = [
    r'enable javascript',
    r'please enable cookies',
    r'access denied',
    r'403 forbidden',
    r'404 not found',
    r'sign in to continue',
    r'subscribe to read',
    r'lorem ipsum',
    r'click here to view',
    r'loading\.{3,}',
]


def parse_datetime_utc(raw_val: Any) -> Optional[datetime]:
    """
    Parses various date formats (ISO 8601, RFC 2822, UNIX epoch) into UTC datetime.
    Never invents or fabricates dates. Returns None on parse failure.
    """
    if not raw_val:
        return None

    if isinstance(raw_val, datetime):
        if raw_val.tzinfo is None:
            return raw_val.replace(tzinfo=timezone.utc)
        return raw_val.astimezone(timezone.utc)

    val_str = str(raw_val).strip()

    # UNIX timestamp (integer / float)
    if val_str.isdigit():
        try:
            ts = int(val_str)
            # Handle milliseconds
            if ts > 1e11:
                ts = ts / 1000.0
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except Exception:
            pass

    # ISO 8601 with Z or offset
    try:
        clean_iso = val_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_iso)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass

    # RFC 2822 (standard email / RSS pubDate)
    try:
        dt = parsedate_to_datetime(val_str)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass

    return None


def evaluate_freshness(
    published_dt: Optional[datetime],
    reference_dt: Optional[datetime] = None,
    fresh_window_hours: float = 24.0,
) -> Dict[str, Any]:
    """
    Strictly categorizes publication freshness against a reference UTC timestamp.
    Zero fabricated timestamps permitted.
    """
    ref = reference_dt or datetime.now(timezone.utc)

    if not published_dt:
        return {
            "status": "MISSING_DATE",
            "age_hours": None,
            "is_fresh_24h": False,
            "classification": "UNVERIFIABLE",
            "rationale": "Missing or unparseable publication timestamp."
        }

    age_seconds = (ref - published_dt).total_seconds()
    age_hours = age_seconds / 3600.0

    if age_hours < -0.1:  # Allow 6 minutes clock skew
        return {
            "status": "FUTURE_TIMESTAMP_ANOMALY",
            "age_hours": round(age_hours, 2),
            "is_fresh_24h": False,
            "classification": "ANOMALY",
            "rationale": f"Publication timestamp is {abs(age_hours):.1f} hours in the future."
        }
    elif age_hours <= fresh_window_hours:
        return {
            "status": "FRESH_24H",
            "age_hours": round(age_hours, 2),
            "is_fresh_24h": True,
            "classification": "FRESH",
            "rationale": f"Published within the last {fresh_window_hours:.0f} hours ({age_hours:.1f} hours old)."
        }
    elif age_hours <= 168.0:
        return {
            "status": "RECENT_7D",
            "age_hours": round(age_hours, 2),
            "is_fresh_24h": False,
            "classification": "RECENT",
            "rationale": f"Published within past week ({age_hours/24.0:.1f} days old)."
        }
    else:
        return {
            "status": "HISTORICAL_STALE",
            "age_hours": round(age_hours, 2),
            "is_fresh_24h": False,
            "classification": "STALE",
            "rationale": f"Published more than 7 days ago ({age_hours/24.0:.1f} days old)."
        }


def canonicalize_url(url: str) -> str:
    """
    Normalizes URLs for robust deduplication:
    - Strips tracking parameters (utm_*, ref, gclid, etc.)
    - Removes fragments (#section)
    - Normalizes scheme to lowercase https
    - Strips trailing slash
    """
    if not url:
        return ""
    try:
        p = urlparse(url.strip())
        scheme = p.scheme.lower() or "https"
        netloc = p.netloc.lower().rstrip(":80").rstrip(":443")
        path = p.path.rstrip("/")

        clean_queries = []
        if p.query:
            for q in p.query.split("&"):
                k = q.split("=")[0].lower()
                if not any(k.startswith(pfx) for pfx in ["utm_", "ref", "fbclid", "gclid", "source", "mc_"]):
                    clean_queries.append(q)
        query = "&".join(sorted(clean_queries))

        return urlunparse((scheme, netloc, path, "", query, ""))
    except Exception:
        return url.strip()


def compute_content_fingerprint(text: str) -> str:
    """Computes deterministic SHA-256 fingerprint from normalized alphanumeric text."""
    if not text:
        return ""
    norm = re.sub(r'[^a-zA-Z0-9]+', ' ', text.lower()).strip()
    return hashlib.sha256(norm.encode('utf-8')).hexdigest()


def validate_content_quality(text: Optional[str], min_length: int = 50) -> Tuple[bool, str]:
    """
    Validates text quality:
    - Checks length
    - Detects raw unrendered HTML
    - Flags placeholder error pages
    """
    if not text or len(text.strip()) < min_length:
        return False, f"Content length ({len(text.strip()) if text else 0}) below minimum threshold ({min_length})."

    t_lower = text.lower()
    for pat in PLACEHOLDER_PATTERNS:
        if re.search(pat, t_lower):
            return False, f"Detected invalid placeholder/gatekeeper phrase matching '{pat}'."

    if re.search(r'<(?:html|head|body|script|style|div|p)\b[^>]*>', text, re.IGNORECASE):
        return False, "Detected unrendered raw HTML tags in extracted content body."

    return True, "Content quality validated."


class DeduplicationRegistry:
    """Tracks unique URLs, content hashes, and entity keys to eliminate duplicates."""

    def __init__(self):
        self.canonical_urls: Set[str] = set()
        self.content_hashes: Set[str] = set()
        self.entity_keys: Set[str] = set()
        self.duplicates_prevented: int = 0
        self.duplicate_log: List[Dict[str, Any]] = []

    def check_and_register(
        self,
        record_id: str,
        raw_url: str,
        title: str,
        content: str,
        entity_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Returns (is_unique, reason). If not unique, records deduplication reason.
        """
        c_url = canonicalize_url(raw_url)
        c_hash = compute_content_fingerprint(content or title)
        e_key = f"{(entity_name or '').strip().lower()}:::{title.strip().lower()}"

        if c_url and c_url in self.canonical_urls:
            self.duplicates_prevented += 1
            reason = f"Duplicate canonical URL: {c_url}"
            self.duplicate_log.append({"record_id": record_id, "type": "URL_COLLISION", "value": c_url})
            return False, reason

        if c_hash and c_hash in self.content_hashes:
            self.duplicates_prevented += 1
            reason = f"Duplicate content fingerprint: {c_hash[:16]}..."
            self.duplicate_log.append({"record_id": record_id, "type": "CONTENT_COLLISION", "value": c_hash})
            return False, reason

        if e_key and e_key in self.entity_keys:
            self.duplicates_prevented += 1
            reason = f"Duplicate entity-title pairing: {e_key}"
            self.duplicate_log.append({"record_id": record_id, "type": "ENTITY_TITLE_COLLISION", "value": e_key})
            return False, reason

        if c_url:
            self.canonical_urls.add(c_url)
        if c_hash:
            self.content_hashes.add(c_hash)
        if e_key:
            self.entity_keys.add(e_key)

        return True, "UNIQUE"

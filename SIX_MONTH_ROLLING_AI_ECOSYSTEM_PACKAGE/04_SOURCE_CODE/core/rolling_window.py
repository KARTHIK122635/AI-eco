"""
Dynamic Six-Month Rolling Window & Freshness Classification Engine
==================================================================
Calculates the dynamic six-month collection window relative to execution UTC time.
Strictly classifies records into 6 mutual freshness tiers:
1. FRESH_24H: Published within the last 24 hours
2. RECENT_7D: Published within 24 hours to 7 days
3. HISTORICAL_6M: Published between 7 days and 6 calendar months ago (within active rolling window)
4. OUTSIDE_WINDOW: Published more than 6 calendar months ago (preserved in archive, excluded from active view)
5. MISSING_DATE: Missing or unparseable publication date (zero synthetic dates fabricated)
6. FUTURE_TIMESTAMP_ANOMALY: Published in the future (> 0.1 hours clock skew, rejected)

CRITICAL INVARIANTS:
- Does NOT hardcode May 22, 2026 as a permanent start date.
- Window moves forward dynamically on every execution.
- Distinguishes collection timestamps (collected_at) from publication timestamps (published_at/posted_at).
"""

import re
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from typing import Any, Dict, Optional, Tuple


def compute_rolling_window(
    ref_time: Optional[datetime] = None,
    months: int = 6
) -> Tuple[datetime, datetime]:
    """
    Computes the dynamic [start_date, end_date] UTC window for rolling interval.
    Uses calendar month arithmetic (approx 184 days for 6 months).
    """
    now = ref_time or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    else:
        now = now.astimezone(timezone.utc)

    # Calculate 6 calendar months back accurately
    year = now.year
    month = now.month - months
    day = now.day

    while month <= 0:
        month += 12
        year -= 1

    # Clamp day for shorter months (e.g. Feb, Apr, etc.)
    max_days = [31, 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28,
                31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
    clamped_day = min(day, max_days)

    start_date = datetime(year, month, clamped_day, 0, 0, 0, tzinfo=timezone.utc)
    end_date = now

    return start_date, end_date


def parse_publication_timestamp(raw_val: Any) -> Optional[datetime]:
    """
    Parses various timestamp formats (ISO 8601, RFC 2822, UNIX epoch) into UTC datetime.
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
            if ts > 1e11:  # Milliseconds
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

    # YYYY-MM-DD or YYYY-MM
    try:
        m = re.match(r'^(\d{4})-(\d{2})(?:-(\d{2}))?', val_str)
        if m:
            y = int(m.group(1))
            mo = int(m.group(2))
            d = int(m.group(3)) if m.group(3) else 1
            return datetime(y, mo, d, 0, 0, 0, tzinfo=timezone.utc)
    except Exception:
        pass

    return None


def classify_freshness(
    published_dt: Optional[datetime],
    ref_time: Optional[datetime] = None,
    window_start: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Strictly categorizes publication freshness into the 6 mandated tiers:
    - FRESH_24H
    - RECENT_7D
    - HISTORICAL_6M
    - OUTSIDE_WINDOW
    - MISSING_DATE
    - FUTURE_TIMESTAMP_ANOMALY
    """
    now = ref_time or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    start_bound = window_start
    if not start_bound:
        start_bound, _ = compute_rolling_window(now, months=6)

    if not published_dt:
        return {
            "status": "MISSING_DATE",
            "age_hours": None,
            "in_rolling_window": False,
            "is_fresh_24h": False,
            "rationale": "Missing or unparseable publication timestamp."
        }

    age_seconds = (now - published_dt).total_seconds()
    age_hours = age_seconds / 3600.0

    # Future timestamp check (> 0.1h in the future)
    if age_hours < -0.1:
        return {
            "status": "FUTURE_TIMESTAMP_ANOMALY",
            "age_hours": round(age_hours, 2),
            "in_rolling_window": False,
            "is_fresh_24h": False,
            "rationale": f"Publication timestamp is {abs(age_hours):.2f} hours in the future."
        }

    # 24H Freshness
    if age_hours <= 24.0:
        return {
            "status": "FRESH_24H",
            "age_hours": round(age_hours, 2),
            "in_rolling_window": True,
            "is_fresh_24h": True,
            "rationale": f"Genuinely published within last 24 hours ({age_hours:.1f}h ago)."
        }

    # Recent 7D
    if age_hours <= 168.0:
        return {
            "status": "RECENT_7D",
            "age_hours": round(age_hours, 2),
            "in_rolling_window": True,
            "is_fresh_24h": False,
            "rationale": f"Published within last 7 days ({age_hours/24.0:.1f} days ago)."
        }

    # Within 6M Rolling Window
    if published_dt >= start_bound:
        return {
            "status": "HISTORICAL_6M",
            "age_hours": round(age_hours, 2),
            "in_rolling_window": True,
            "is_fresh_24h": False,
            "rationale": f"Published within 6-month rolling window ({age_hours/24.0:.1f} days ago)."
        }

    # Older than 6M Rolling Window
    return {
        "status": "OUTSIDE_WINDOW",
        "age_hours": round(age_hours, 2),
        "in_rolling_window": False,
        "is_fresh_24h": False,
        "rationale": f"Published prior to rolling window ({age_hours/24.0:.1f} days ago). Preserved in archive."
    }

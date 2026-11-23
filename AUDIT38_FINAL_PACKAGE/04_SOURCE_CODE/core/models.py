from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
import re


def normalize_string(val: Optional[str]) -> str:
    """Helper to normalize text for deduplication matching."""
    if not val:
        return ""
    # Strip whitespace, lowercase, remove punctuation
    clean = re.sub(r'[^\w\s]', '', val.lower())
    return " ".join(clean.split())


@dataclass
class StartupProductRecord:
    company_name: str
    original_source_url: str
    source_directory: str
    product_name: Optional[str] = None
    description: Optional[str] = None
    employee_count: Optional[Union[int, str]] = None
    pricing_model: Optional[str] = None
    company_website: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    discovered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    def deduplication_key(self) -> str:
        """
        Generate a unique deduplication fingerprint.
        Prioritizes company_name + product_name (if present).
        """
        norm_company = normalize_string(self.company_name)
        norm_product = normalize_string(self.product_name)
        if norm_product and norm_product != norm_company:
            return f"{norm_company}::{norm_product}"
        return norm_company

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SourceAssessment:
    source_name: str
    directory_url: str
    accessible: bool
    status_code: Optional[int]
    collection_method: str
    available_fields: List[str]
    missing_fields: List[str]
    rate_limits_info: str
    robots_txt_status: str
    bot_protection_detected: bool
    notes_and_alternatives: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

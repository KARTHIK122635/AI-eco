import re
from typing import Set, Dict, Optional
from core.models import StartupProductRecord, normalize_string


class Deduplicator:
    """
    In-memory and persistent tracker to avoid duplicate companies and products.
    Deduplicates based on normalized company name, product name, and canonical URLs.
    """
    def __init__(self):
        self._seen_keys: Set[str] = set()
        self._seen_urls: Set[str] = set()
        self._records_by_key: Dict[str, StartupProductRecord] = {}

    def is_duplicate(self, record: StartupProductRecord) -> bool:
        key = record.deduplication_key()
        norm_url = record.original_source_url.strip().lower().rstrip('/')
        if key in self._seen_keys or norm_url in self._seen_urls:
            return True
        return False

    def add(self, record: StartupProductRecord) -> bool:
        """
        Attempts to add record. If duplicate, returns False.
        If new, registers it and returns True.
        Can enrich existing record if new record provides missing data.
        """
        key = record.deduplication_key()
        norm_url = record.original_source_url.strip().lower().rstrip('/')

        if key in self._seen_keys:
            # Check if we can enrich missing fields (e.g. employee count or pricing model)
            existing = self._records_by_key.get(key)
            if existing:
                self._enrich(existing, record)
            return False

        if norm_url in self._seen_urls:
            return False

        self._seen_keys.add(key)
        self._seen_urls.add(norm_url)
        self._records_by_key[key] = record
        return True

    def _enrich(self, existing: StartupProductRecord, incoming: StartupProductRecord):
        """Enrich existing record with non-null incoming fields."""
        if not existing.description and incoming.description:
            existing.description = incoming.description
        if not existing.employee_count and incoming.employee_count:
            existing.employee_count = incoming.employee_count
        if not existing.pricing_model and incoming.pricing_model:
            existing.pricing_model = incoming.pricing_model
        if not existing.company_website and incoming.company_website:
            existing.company_website = incoming.company_website
        if incoming.categories:
            combined = set(existing.categories + incoming.categories)
            existing.categories = list(combined)

    def count(self) -> int:
        return len(self._seen_keys)

    def get_all(self):
        return list(self._records_by_key.values())

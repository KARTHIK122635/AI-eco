import re
from typing import Dict, List, Optional
from core.schemas import AIStartup, AIProduct


def normalize_entity_name(name: str) -> str:
    """Canonical normalization of company and product names for robust entity resolution."""
    if not name:
        return ""
    # Lowercase
    s = name.lower().strip()
    # Remove corporate designators
    s = re.sub(r'\b(inc|llc|corp|ltd|co|corporation|technologies|company)\b', '', s)
    # Remove special punctuation
    s = re.sub(r'[^\w\s]', '', s)
    return " ".join(s.split())


class EntityResolver:
    """
    Resolves, links, and merges startups and products across multiple heterogeneous sources.
    Maintains clean separation between organizations (startups) and deliverables (products).
    """
    def __init__(self):
        self.startups_by_key: Dict[str, AIStartup] = {}
        self.products_by_key: Dict[str, AIProduct] = {}

    def register_startup(self, startup: AIStartup) -> bool:
        """
        Adds or merges a startup entity. Returns True if newly added, False if merged/enriched.
        """
        key = normalize_entity_name(startup.name)
        if not key:
            return False

        if key in self.startups_by_key:
            existing = self.startups_by_key[key]
            # Merge provenance
            for src in startup.provenance_sources:
                if src not in existing.provenance_sources:
                    existing.provenance_sources.append(src)
            # Enrich missing fields
            if not existing.description and startup.description:
                existing.description = startup.description
            if not existing.employee_count and startup.employee_count:
                existing.employee_count = startup.employee_count
            if not existing.pricing_model and startup.pricing_model:
                existing.pricing_model = startup.pricing_model
            if not existing.website and startup.website:
                existing.website = startup.website
            if not existing.headquarters and startup.headquarters:
                existing.headquarters = startup.headquarters
            if not existing.batch_or_founded and startup.batch_or_founded:
                existing.batch_or_founded = startup.batch_or_founded
            # Merge AI evidence
            combined_evidence = set(existing.ai_evidence + startup.ai_evidence)
            existing.ai_evidence = list(combined_evidence)
            return False

        self.startups_by_key[key] = startup
        return True

    def register_product(self, product: AIProduct) -> bool:
        """
        Adds or merges a product entity. Returns True if newly added, False if duplicate.
        """
        # Product key is normalized developer/company + normalized product name
        dev_key = normalize_entity_name(product.developer_or_company)
        prod_key = normalize_entity_name(product.name)
        full_key = f"{dev_key}::{prod_key}" if dev_key else prod_key

        if full_key in self.products_by_key:
            return False

        # Link to startup if matching developer is registered
        if dev_key in self.startups_by_key:
            product.developer_startup_id = self.startups_by_key[dev_key].startup_id

        self.products_by_key[full_key] = product
        return True

    def get_startups(self) -> List[AIStartup]:
        return list(self.startups_by_key.values())

    def get_products(self) -> List[AIProduct]:
        return list(self.products_by_key.values())

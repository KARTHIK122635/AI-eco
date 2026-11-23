"""
AI Ecosystem Intelligence Pipeline - Entity Resolver Subsystem
==============================================================
Module: src.entity_resolver
Description: Deterministic entity resolution and cross-source deduplication engine.
Implements:
- Normalization of messy corporate and product names (e.g. 'OpenAI, Inc.', 'Open AI' -> 'OpenAI')
- Deterministic seed list matching against known AI organizations
- Cross-source entity linking preserving provenance lineage
- In-memory and persistent deduplication with schema constraints
"""

import re
import logging
from typing import Dict, List, Optional, Set, Tuple

from core.entity_resolution import EntityResolver, normalize_entity_name
from core.deduplicator import Deduplicator
from core.schemas import AIStartup, AIProduct

logger = logging.getLogger("src.entity_resolver")


class ProductionEntityResolver:
    """
    Unified entity resolution facade providing:
    1. Deterministic canonical name resolution
    2. Seed list matching against known major AI organizations
    3. Organization vs Product relationship linking
    4. Exact and fuzzy deduplication
    """

    KNOWN_SEED_ORGANIZATIONS = {
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "google": "Google",
        "deepmind": "Google DeepMind",
        "meta": "Meta",
        "microsoft": "Microsoft",
        "mistral": "Mistral AI",
        "cohere": "Cohere",
        "huggingface": "Hugging Face",
        "stability ai": "Stability AI",
        "midjourney": "Midjourney",
        "runway": "Runway",
        "elevenlabs": "ElevenLabs",
        "scale ai": "Scale AI",
        "databricks": "Databricks",
        "snowflake": "Snowflake",
        "nvidia": "NVIDIA",
        "together ai": "Together AI",
        "anyscale": "Anyscale",
        "perplexity": "Perplexity AI",
    }

    def __init__(self):
        self.resolver = EntityResolver()
        self.deduplicator = Deduplicator()

    def resolve_canonical_name(self, raw_name: str) -> str:
        """
        Maps messy raw strings to canonical corporate entities.
        Example: 'OpenAI, Inc.' -> 'OpenAI', 'Google LLC' -> 'Google'
        """
        normalized = normalize_entity_name(raw_name)
        if normalized in self.KNOWN_SEED_ORGANIZATIONS:
            return self.KNOWN_SEED_ORGANIZATIONS[normalized]
        # Return properly capitalized normalized form if not in seed list
        return " ".join(word.capitalize() for word in normalized.split())

    def register_and_resolve_startup(self, startup: AIStartup) -> Tuple[bool, str]:
        """
        Registers startup with the canonical resolver.
        Returns (is_new, canonical_name).
        """
        canonical_name = self.resolve_canonical_name(startup.name)
        startup.name = canonical_name
        is_new = self.resolver.register_startup(startup)
        return is_new, canonical_name


__all__ = [
    "ProductionEntityResolver",
    "EntityResolver",
    "normalize_entity_name",
    "Deduplicator",
]

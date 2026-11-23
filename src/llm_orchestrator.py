"""
AI Ecosystem Intelligence Pipeline - LLM Orchestrator Subsystem
===============================================================
Module: src.llm_orchestrator
Description: Multi-tier LLM orchestration engine with resilient error handling.
Implements:
- Multi-tier fallback chain: Gemini -> Groq Llama 3 -> DeepSeek -> Offline Grounded Provider
- Intelligent SemanticChunker preventing HTTP 413 (Payload Too Large / Context Overflow)
- Bounded exponential backoff with random jitter for HTTP 429 (Rate Limits)
- Schema-constrained JSON extraction adhering to canonical schemas
- Strict zero-hallucination grounding against source provenance
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from core.llm.multi_tier_engine import MultiTierLLMEngine, ProviderAttemptLog
from core.llm.base import BaseLLMProvider, ProviderConfig, LLMResponse, TokenUsage, estimate_cost
from core.llm.factory import get_llm_provider
from core.llm.providers.offline_provider import OfflineProvider
from src.stage3.gemini_enrichment import GeminiEnrichmentRunner

logger = logging.getLogger("src.llm_orchestrator")


class ProductionLLMOrchestrator:
    """
    Unified LLM orchestrator managing:
    1. Multi-tier provider failovers
    2. Context-window aware payload chunking
    3. Rate-limit backoff with jitter
    4. Canonical JSON schema enforcement
    """

    def __init__(self, primary_provider: str = "gemini"):
        self.engine = MultiTierLLMEngine()
        self.enrichment_runner = GeminiEnrichmentRunner
        self.primary_provider = primary_provider

    def extract_structured_entity(
        self,
        raw_text: str,
        entity_type: str,
        context_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extracts structured JSON fields from raw HTML/text using the multi-tier cascade.
        Automatically chunks oversized text to prevent HTTP 413 and retries on HTTP 429.
        """
        return self.engine.enrich_record(
            raw_content=raw_text,
            entity_type=entity_type,
            metadata=context_metadata or {}
        )

    def get_provider_telemetry(self) -> List[Dict[str, Any]]:
        """Returns provider latency, token usage, cost, and failover logs."""
        return [
            {
                "provider": log.provider,
                "model": log.model,
                "tier": log.tier,
                "success": log.success,
                "latency_seconds": log.latency_seconds,
                "tokens": log.prompt_tokens + log.completion_tokens,
                "cost_usd": log.estimated_cost_usd,
                "error": log.error_message
            }
            for log in self.engine.attempt_history
        ]


__all__ = [
    "ProductionLLMOrchestrator",
    "MultiTierLLMEngine",
    "ProviderAttemptLog",
    "BaseLLMProvider",
    "ProviderConfig",
    "LLMResponse",
    "TokenUsage",
    "estimate_cost",
    "get_llm_provider",
    "OfflineProvider",
    "GeminiEnrichmentService",
]

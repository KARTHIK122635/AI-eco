"""
AI Ecosystem Intelligence Pipeline - Source Package (`src`)
============================================================
Core modules for assessment submission:
- `src.crawler`: High-concurrency async crawling and freshness ingestion
- `src.llm_orchestrator`: Resilient multi-tier LLM cascade with backoff and chunking
- `src.entity_resolver`: Deterministic entity resolution and deduplication
"""

# Lazy / safe imports
def get_crawler():
    from src.crawler import ProductionCrawler
    return ProductionCrawler()

def get_llm_orchestrator():
    from src.llm_orchestrator import ProductionLLMOrchestrator
    return ProductionLLMOrchestrator()

def get_entity_resolver():
    from src.entity_resolver import ProductionEntityResolver
    return ProductionEntityResolver()

__all__ = [
    "get_crawler",
    "get_llm_orchestrator",
    "get_entity_resolver",
]

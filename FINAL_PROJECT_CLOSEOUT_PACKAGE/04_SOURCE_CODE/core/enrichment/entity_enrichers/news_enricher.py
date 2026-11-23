"""
Entity enricher for AI News.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - News Source Content Validation (summary and article_summary) and Multi-Table Persistence
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from core.llm.base import BaseLLMProvider
from core.enrichment.schemas import (
    EnrichmentResult,
    ValidationStatus,
    NEWS_ENRICHMENT_SCHEMA,
    compute_source_version,
    compute_canonical_source_version
)
from core.enrichment.validator import EvidenceValidator


class NewsEnricher:
    """
    Enriches AI News records with article summaries, AI topics, mentioned companies,
    categories, and key developments.
    STRICT RULE: Never generate an article summary or summary from a headline alone.
    Requires minimum source content (>= 50 chars).
    """
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def enrich_record(self, record: Dict[str, Any]) -> List[EnrichmentResult]:
        news_id = record.get("news_id") or record.get("id") or "unknown"
        title = record.get("title") or "Unknown Headline"
        article_url = record.get("article_url") or ""
        content = record.get("content", "") or ""
        existing_summary = record.get("summary", "") or ""
        now_iso = datetime.now(timezone.utc).isoformat()

        is_heuristic = self.provider.name in ("offline", "heuristic")

        # Strict Rule Check: If content is missing or trivial (< 50 chars), refuse to fabricate summary
        if not content or len(content.strip()) < 50:
            source_version = compute_canonical_source_version("news", record)
            results: List[EnrichmentResult] = []
            if not existing_summary:
                # Return INSUFFICIENT_EVIDENCE result for summary
                res = EnrichmentResult(
                    attempt_id=str(uuid.uuid4()),
                    record_id=str(news_id),
                    entity_type="news",
                    field_name="summary",
                    original_value=existing_summary,
                    enriched_value=None,
                    source_url=article_url,
                    evidence="",
                    source_version=source_version,
                    confidence_score=0.0,
                    enrichment_method="heuristic_extraction" if is_heuristic else f"llm_{self.provider.name}",
                    provider=self.provider.name,
                    model=self.provider.model,
                    enriched_at=now_iso,
                    validation_status=ValidationStatus.INSUFFICIENT_EVIDENCE.value,
                    validation_rationale="News Rule Violation: Cannot generate an article summary from a headline alone or without access to sufficient source text (>= 50 chars)."
                )
                results.append(res)
            return results

        source_text = f"Title: {title}\nArticle Content: {content}"
        source_version = compute_canonical_source_version("news", record)

        prompt = f"""You are a precise AI journalism analyst.
Analyze the following AI news article strictly grounded in the provided source text.
Do not hallucinate facts or developments. If information is not in the text, omit it.

Source Content:
{source_text}

Extract according to schema:
- article_summary: concise, grounded summary of the actual article text
- ai_topic: specific AI topic (e.g. GPU Infrastructure, Model Release, Safety Regulation)
- companies_or_models_mentioned: list of organizations, labs, or AI models mentioned
- news_category: category classification
- key_developments: bullet points of specific events or findings reported
- evidence: exact verbatim sentence from text supporting the extraction
- confidence_score: between 0.0 and 1.0 based on clarity of evidence
"""
        extracted = self.provider.extract_structured(
            prompt=prompt,
            schema=NEWS_ENRICHMENT_SCHEMA,
            system_prompt="Extract factual information strictly grounded in the article text. Never invent news."
        )

        results: List[EnrichmentResult] = []
        evidence = extracted.get("evidence", "") or ""
        confidence = float(extracted.get("confidence_score", 0.75))

        fields_to_check = [
            ("summary", "article_summary"),
            ("ai_topic", "ai_topic"),
            ("related_companies", "companies_or_models_mentioned"),
            ("category", "news_category"),
            ("key_developments", "key_developments")
        ]

        for db_field, ext_key in fields_to_check:
            orig_val = record.get(db_field)
            new_val = extracted.get(ext_key)
            
            if (orig_val is None or orig_val == "" or orig_val == []) and new_val:
                attempt_id = str(uuid.uuid4())
                
                if is_heuristic:
                    if db_field in ("category", "ai_topic"):
                        method = "heuristic_classification"
                    else:
                        method = "heuristic_extraction"
                else:
                    method = f"llm_{self.provider.name}"

                res = EnrichmentResult(
                    attempt_id=attempt_id,
                    record_id=str(news_id),
                    entity_type="news",
                    field_name=db_field,
                    original_value=orig_val,
                    enriched_value=new_val,
                    source_url=article_url,
                    evidence=evidence,
                    source_version=source_version,
                    confidence_score=confidence,
                    enrichment_method=method,
                    provider=self.provider.name,
                    model=self.provider.model,
                    enriched_at=now_iso,
                    validation_status=ValidationStatus.NEEDS_REVIEW.value,
                    validation_rationale=""
                )
                status, rationale = EvidenceValidator.validate_enrichment(res, source_text)
                res.validation_status = status.value
                res.validation_rationale = rationale
                results.append(res)

        return results

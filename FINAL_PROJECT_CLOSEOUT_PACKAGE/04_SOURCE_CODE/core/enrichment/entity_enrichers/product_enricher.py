"""
Entity enricher for AI Products.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - Accurate Heuristic Attribution, Sentence Evidence, and Source Versioning
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from core.llm.base import BaseLLMProvider
from core.enrichment.schemas import (
    EnrichmentResult,
    ValidationStatus,
    PRODUCT_ENRICHMENT_SCHEMA,
    compute_source_version,
    compute_canonical_source_version
)
from core.enrichment.validator import EvidenceValidator


class ProductEnricher:
    """
    Enriches AI Product records with grounded descriptions, product categories,
    main capabilities, and supported technologies based on source evidence.
    """
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def enrich_record(self, record: Dict[str, Any]) -> List[EnrichmentResult]:
        product_id = record.get("product_id") or record.get("id") or "unknown"
        name = record.get("entity_name") or record.get("product_name") or record.get("name") or "Unknown Product"
        source_url = record.get("original_source_url") or record.get("product_url") or record.get("url") or ""
        desc = record.get("description", "") or ""
        features = record.get("features", "") or ""
        source_text = f"Product Name: {name}\nExisting Description: {desc}\nFeatures: {features}"
        source_version = compute_canonical_source_version("product", record)

        prompt = f"""You are a precise AI product analyst.
Extract structured information about the AI product '{name}' strictly grounded in the provided source text.
Do not hallucinate capabilities or technologies. If information is not in the text, omit it.

Source Content:
{source_text}

Extract according to schema:
- product_description: concise summary of what the product does
- product_category: product category classification
- main_capabilities: list of key features or capabilities
- supported_technologies: list of technologies, frameworks, or models supported
- developer_or_company: creator organization if mentioned
- official_product_url: official URL if mentioned
- evidence: exact verbatim sentence from text supporting the extraction
- confidence_score: between 0.0 and 1.0 based on clarity of evidence
"""
        extracted = self.provider.extract_structured(
            prompt=prompt,
            schema=PRODUCT_ENRICHMENT_SCHEMA,
            system_prompt="Extract factual information strictly grounded in the product text. Never invent features."
        )

        results: List[EnrichmentResult] = []
        now_iso = datetime.now(timezone.utc).isoformat()
        evidence = extracted.get("evidence", "") or ""
        confidence = float(extracted.get("confidence_score", 0.75))

        fields_to_check = [
            ("description", "product_description"),
            ("category", "product_category"),
            ("main_capabilities", "main_capabilities"),
            ("supported_technologies", "supported_technologies")
        ]

        is_heuristic = self.provider.name in ("offline", "heuristic")

        for db_field, ext_key in fields_to_check:
            orig_val = record.get(db_field)
            new_val = extracted.get(ext_key)
            
            if (orig_val is None or orig_val == "" or orig_val == []) and new_val:
                attempt_id = str(uuid.uuid4())
                
                if is_heuristic:
                    if db_field == "category":
                        method = "heuristic_classification"
                    else:
                        method = "heuristic_extraction"
                else:
                    method = f"llm_{self.provider.name}"

                res = EnrichmentResult(
                    attempt_id=attempt_id,
                    record_id=str(product_id),
                    entity_type="product",
                    field_name=db_field,
                    original_value=orig_val,
                    enriched_value=new_val,
                    source_url=source_url,
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

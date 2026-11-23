"""
Entity enricher for AI Startups.
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
    STARTUP_ENRICHMENT_SCHEMA,
    compute_source_version,
    compute_canonical_source_version
)
from core.enrichment.validator import EvidenceValidator


class StartupEnricher:
    """
    Enriches AI Startup records with grounded descriptions, AI specialization,
    technologies, and products/services based on source evidence.
    """
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def enrich_record(self, record: Dict[str, Any]) -> List[EnrichmentResult]:
        startup_id = record.get("startup_id") or record.get("id") or "unknown"
        name = record.get("entity_name") or record.get("name") or "Unknown Company"
        source_url = record.get("primary_source_url") or record.get("website") or ""
        
        # Build source context
        desc = record.get("description", "") or ""
        focus = record.get("ai_focus_area", "") or ""
        ev = record.get("ai_evidence", "") or ""
        source_text = f"Company Name: {name}\nAI Focus: {focus}\nExisting Description: {desc}\nEvidence: {ev}"
        source_version = compute_canonical_source_version("startup", record)

        prompt = f"""You are a precise data extraction specialist.
Extract structured information about the AI startup '{name}' strictly grounded in the provided source text.
Do not hallucinate facts. If a field is not supported by the text, omit it or leave it empty.

Source Content:
{source_text}

Extract according to schema:
- company_description: concise summary
- industry: primary sector
- ai_specialization: specific AI subfield (e.g. LLMs, Computer Vision, Agents, Robotics)
- products_and_services: list of products or services offered
- technologies: list of specific technologies, frameworks, or models used
- evidence: exact verbatim sentence from text supporting the extraction
- confidence_score: between 0.0 and 1.0 based on clarity of evidence
"""
        extracted = self.provider.extract_structured(
            prompt=prompt,
            schema=STARTUP_ENRICHMENT_SCHEMA,
            system_prompt="Extract factual information strictly grounded in the text. Never invent facts."
        )

        results: List[EnrichmentResult] = []
        now_iso = datetime.now(timezone.utc).isoformat()
        evidence = extracted.get("evidence", "") or ""
        confidence = float(extracted.get("confidence_score", 0.75))

        fields_to_check = [
            ("description", "company_description"),
            ("ai_specialization", "ai_specialization"),
            ("technologies", "technologies"),
            ("products_and_services", "products_and_services"),
            ("industry", "industry")
        ]

        is_heuristic = self.provider.name in ("offline", "heuristic")

        for db_field, ext_key in fields_to_check:
            orig_val = record.get(db_field)
            new_val = extracted.get(ext_key)
            
            if (orig_val is None or orig_val == "" or orig_val == []) and new_val:
                attempt_id = str(uuid.uuid4())
                
                if is_heuristic:
                    if db_field in ("ai_specialization", "industry"):
                        method = "heuristic_classification"
                    else:
                        method = "heuristic_extraction"
                else:
                    method = f"llm_{self.provider.name}"

                res = EnrichmentResult(
                    attempt_id=attempt_id,
                    record_id=str(startup_id),
                    entity_type="startup",
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

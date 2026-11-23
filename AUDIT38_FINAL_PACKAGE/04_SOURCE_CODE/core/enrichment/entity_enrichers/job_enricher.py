"""
Entity enricher for AI Jobs.
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
    JOB_ENRICHMENT_SCHEMA,
    compute_source_version,
    compute_canonical_source_version
)
from core.enrichment.validator import (
    EvidenceValidator,
    RETAINED_15_REVIEW_JOB_IDS,
    PROTECTED_JOB_FIELDS
)


class JobEnricher:
    """
    Enriches AI Job records with required skills, preferred skills, technologies,
    and role specializations extracted from job descriptions.
    STRICT RULES:
    1. Do not modify verified compensation, vacancy status, descriptions, URLs, or evidence.
    2. Preserve the 15 REQUIRES_REVIEW boundary classification records intact.
    3. Ground all skills and technologies in verbatim evidence.
    """
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def enrich_record(self, record: Dict[str, Any]) -> List[EnrichmentResult]:
        job_id = record.get("job_id") or record.get("jobId") or "unknown"
        title = record.get("job_title") or record.get("jobTitle") or "Unknown Job"
        company = record.get("company_name") or record.get("companyName") or "Unknown Company"
        app_url = record.get("application_url") or record.get("applicationUrl") or ""
        desc = record.get("job_description") or record.get("jobDescription") or ""

        # Build complete source context
        source_text = f"Job Title: {title}\nCompany: {company}\nDescription:\n{desc}"
        source_version = compute_canonical_source_version("job", record)

        prompt = f"""You are a precise technical talent and skills analyst.
Extract skills and technical requirements for the role '{title}' at '{company}' strictly grounded in the provided job description.
Do not hallucinate skills not mentioned in the text.

Source Content:
{source_text[:3500]}

Extract according to schema:
- role_specialization: specific technical niche or focus
- required_skills: list of mandatory technical skills, tools, or languages mentioned
- preferred_skills: list of nice-to-have or preferred qualifications mentioned
- technologies: list of specific programming languages, frameworks, and infrastructure tools mentioned
- evidence: exact verbatim sentence from description supporting the skills
- confidence_score: between 0.0 and 1.0 based on clarity of text
"""
        extracted = self.provider.extract_structured(
            prompt=prompt,
            schema=JOB_ENRICHMENT_SCHEMA,
            system_prompt="Extract technical skills strictly grounded in the job description. Never invent skills."
        )

        results: List[EnrichmentResult] = []
        now_iso = datetime.now(timezone.utc).isoformat()
        evidence = extracted.get("evidence", "") or ""
        confidence = float(extracted.get("confidence_score", 0.75))

        fields_to_check = [
            ("required_skills", "required_skills"),
            ("preferred_skills", "preferred_skills"),
            ("technologies", "technologies"),
            ("role_specialization", "role_specialization")
        ]

        is_heuristic = self.provider.name in ("offline", "heuristic")

        for db_field, ext_key in fields_to_check:
            orig_val = record.get(db_field)
            if orig_val is None:
                camel_map = {
                    "required_skills": "requiredSkills",
                    "preferred_skills": "preferredSkills",
                    "role_specialization": "roleSpecialization"
                }
                if db_field in camel_map:
                    orig_val = record.get(camel_map[db_field])

            new_val = extracted.get(ext_key)

            # Strict canonical job protections
            if db_field in PROTECTED_JOB_FIELDS:
                continue

            # Enrich only if original is missing/empty and new value is present
            if (orig_val is None or orig_val == "" or orig_val == [] or orig_val == "[]") and new_val:
                attempt_id = str(uuid.uuid4())
                
                # Accurate method naming
                if is_heuristic:
                    if db_field == "role_specialization":
                        method = "heuristic_classification"
                    else:
                        method = "heuristic_extraction"
                else:
                    method = f"llm_{self.provider.name}"

                res = EnrichmentResult(
                    attempt_id=attempt_id,
                    record_id=str(job_id),
                    entity_type="job",
                    field_name=db_field,
                    original_value=orig_val,
                    enriched_value=new_val,
                    source_url=app_url,
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

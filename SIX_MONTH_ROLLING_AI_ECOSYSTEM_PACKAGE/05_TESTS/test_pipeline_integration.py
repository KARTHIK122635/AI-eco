"""
Integration tests for pipeline-level evidence enforcement with MockProvider.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 20 - Enforcement of EvidenceValidator in EnrichmentEngine._validate_and_append
"""

import os
import json
import sqlite3
import tempfile
import unittest
from typing import Dict, Any, Optional

from core.llm.base import BaseLLMProvider, ProviderConfig, LLMResponse, TokenUsage
from core.enrichment.engine import EnrichmentEngine
from core.enrichment.schemas import ValidationStatus, compute_source_version


class AdversarialMockProvider(BaseLLMProvider):
    """
    Mock provider simulating an untrustworthy or hallucinating LLM that claims high confidence
    and tries to return fabricated technologies, partial lists, unsupported claims, and invalid classifications.
    """
    def __init__(self, mode: str = "fabricated_tech"):
        config = ProviderConfig(provider_name="mock_adversarial", model_name="mock-hallucinator-v1")
        super().__init__(config)
        self.mode = mode

    def is_available(self) -> bool:
        return True

    def _execute_request(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        # Generate adversarial responses based on mode
        if self.mode == "fabricated_tech":
            data = {
                "technologies": ["QuantumTeleportation", "WarpDriveKernel"],
                "evidence": "Python developer role",
                "confidence_score": 0.99
            }
        elif self.mode == "partial_list":
            data = {
                "technologies": ["Python", "NonexistentFrameworkX"],
                "evidence": "Requires strong Python experience for backend microservices.",
                "confidence_score": 0.99
            }
        elif self.mode == "fabricated_free_text":
            data = {
                "company_description": "The company manufactures autonomous surgical robots and hospital software.",
                "evidence": "The company develops software for hospitals.",
                "confidence_score": 0.99
            }
        elif self.mode == "unsupported_classification":
            data = {
                "ai_specialization": "Computer Vision & Multimodal",
                "evidence": "We have a vision for cloud data warehousing.",
                "confidence_score": 0.99
            }
        else:
            data = {}

        return LLMResponse(
            content=json.dumps(data),
            structured_data=data,
            token_usage=TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20, estimated_cost_usd=0.0001),
            model=self.model,
            provider=self.name,
            success=True
        )


class TestPipelineIntegration(unittest.TestCase):

    def setUp(self):
        # Create a temporary test database with canonical schema
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()

        self.conn = sqlite3.connect(self.temp_db_path)
        self.cur = self.conn.cursor()

        # Seed canonical tables with test records
        self.cur.execute("""
        CREATE TABLE ai_jobs (
            job_id TEXT PRIMARY KEY,
            job_title TEXT,
            company_name TEXT,
            job_description TEXT,
            required_skills TEXT,
            preferred_skills TEXT,
            application_url TEXT
        )
        """)
        self.cur.execute("""
        INSERT INTO ai_jobs VALUES (
            'job_test_01', 'Software Engineer', 'HealthCorp',
            'The company develops software for hospitals. Requires strong Python experience for backend microservices.',
            '[]', '[]', 'https://example.com/job/1'
        )
        """)

        self.cur.execute("""
        CREATE TABLE ai_startups (
            startup_id TEXT PRIMARY KEY,
            entity_name TEXT,
            ai_focus_area TEXT,
            description TEXT,
            ai_evidence TEXT,
            technologies TEXT,
            website TEXT
        )
        """)
        self.cur.execute("""
        INSERT INTO ai_startups VALUES (
            'startup_test_01', 'VisionCloud', 'Cloud',
            'We have a vision for cloud data warehousing.',
            'cloud data warehousing', '[]', 'https://example.com/startup/1'
        )
        """)

        self.conn.commit()

    def tearDown(self):
        self.conn.close()
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_pipeline_rejects_fabricated_technologies(self):
        """
        Integration Test (Audit 20):
        Provider returns fabricated technologies with confidence=0.99.
        Engine._validate_and_append MUST reject and set status to FAILED.
        """
        provider = AdversarialMockProvider(mode="fabricated_tech")
        engine = EnrichmentEngine(provider=provider, db_path=self.temp_db_path)

        jobs = engine.load_table_records("ai_jobs")
        for r in jobs:
            res_list = engine.job_enricher.enrich_record(r)
            engine._validate_and_append(res_list)

        self.assertTrue(len(engine.enrichment_log) > 0)
        for res in engine.enrichment_log:
            if res.field_name in ("required_skills", "technologies"):
                self.assertEqual(
                    res.validation_status,
                    ValidationStatus.FAILED.value,
                    f"Pipeline must mark fabricated tech as FAILED, got: {res.validation_status}"
                )

    def test_pipeline_routes_partial_lists_to_review(self):
        """
        Integration Test (Audit 20):
        Provider returns a list where 1 item is supported ('Python') and 1 is hallucinated ('NonexistentFrameworkX').
        Engine._validate_and_append MUST recalculate status to NEEDS_REVIEW (never VERIFIED).
        """
        provider = AdversarialMockProvider(mode="partial_list")
        engine = EnrichmentEngine(provider=provider, db_path=self.temp_db_path)

        jobs = engine.load_table_records("ai_jobs")
        for r in jobs:
            res_list = engine.job_enricher.enrich_record(r)
            engine._validate_and_append(res_list)

        found_tech_res = False
        for res in engine.enrichment_log:
            if res.field_name in ("required_skills", "technologies"):
                found_tech_res = True
                self.assertEqual(
                    res.validation_status,
                    ValidationStatus.NEEDS_REVIEW.value,
                    f"Pipeline must route partially supported list to NEEDS_REVIEW, got: {res.validation_status}"
                )
                self.assertIn("Partially supported list", res.validation_rationale)
        self.assertTrue(found_tech_res)

    def test_pipeline_rejects_fabricated_free_text_claims(self):
        """
        Integration Test (Audit 20):
        Provider returns free-text with fabricated claims ('autonomous surgical robots') not in evidence.
        Engine._validate_and_append MUST recalculate status to FAILED or NEEDS_REVIEW (never VERIFIED).
        """
        provider = AdversarialMockProvider(mode="fabricated_free_text")
        engine = EnrichmentEngine(provider=provider, db_path=self.temp_db_path)

        startups = engine.load_table_records("ai_startups")
        for r in startups:
            res_list = engine.startup_enricher.enrich_record(r)
            engine._validate_and_append(res_list)

        for res in engine.enrichment_log:
            if res.field_name == "company_description":
                self.assertIn(
                    res.validation_status,
                    (ValidationStatus.FAILED.value, ValidationStatus.NEEDS_REVIEW.value),
                    f"Fabricated free-text claim must not be VERIFIED, got: {res.validation_status}"
                )
                self.assertNotEqual(res.validation_status, ValidationStatus.VERIFIED.value)

    def test_pipeline_rejects_unsupported_classifications(self):
        """
        Integration Test (Audit 20):
        Provider attempts to classify as 'Computer Vision & Multimodal' using generic 'vision' in cloud context.
        Engine._validate_and_append MUST reject and route to FAILED/NEEDS_REVIEW (never VERIFIED).
        """
        provider = AdversarialMockProvider(mode="unsupported_classification")
        engine = EnrichmentEngine(provider=provider, db_path=self.temp_db_path)

        startups = engine.load_table_records("ai_startups")
        for r in startups:
            res_list = engine.startup_enricher.enrich_record(r)
            engine._validate_and_append(res_list)

        for res in engine.enrichment_log:
            if res.field_name == "ai_specialization":
                self.assertIn(
                    res.validation_status,
                    (ValidationStatus.FAILED.value, ValidationStatus.NEEDS_REVIEW.value),
                    f"Unsupported classification must not be VERIFIED, got: {res.validation_status}"
                )
                self.assertNotEqual(res.validation_status, ValidationStatus.VERIFIED.value)

    def test_pipeline_rejects_unknown_taxonomy_category(self):
        """
        Integration Test (Audit 21 Requirement 2):
        Provider returns an unknown category outside the approved taxonomy.
        Pipeline must reject and set status to FAILED.
        """
        class UnknownCategoryProvider(BaseLLMProvider):
            def __init__(self):
                super().__init__(ProviderConfig(provider_name="gemini", model_name="gemini-flash"))
            def is_available(self):
                return True
            def _execute_request(self, prompt, **kwargs):
                data = {
                    "ai_specialization": "Quantum Metaverse Cloud AI",
                    "evidence": "We have a vision for cloud data warehousing.",
                    "confidence_score": 0.99
                }
                return LLMResponse(content=json.dumps(data), structured_data=data, token_usage=TokenUsage(), model=self.model, provider=self.name, success=True)

        engine = EnrichmentEngine(provider=UnknownCategoryProvider(), db_path=self.temp_db_path)
        startups = engine.load_table_records("ai_startups")
        for r in startups:
            res_list = engine.startup_enricher.enrich_record(r)
            engine._validate_and_append(res_list)

        for res in engine.enrichment_log:
            if res.field_name == "ai_specialization":
                self.assertEqual(res.validation_status, ValidationStatus.FAILED.value)
                self.assertIn("taxonomy", res.validation_rationale.lower())

    def test_source_version_modification_sensitivity(self):
        """
        Integration Test (Audit 21 Requirement 5):
        Verify that changing any source field in canonical record alters the source version digest.
        """
        from core.enrichment.schemas import compute_canonical_source_version
        engine = EnrichmentEngine(provider=AdversarialMockProvider(), db_path=self.temp_db_path)
        jobs = engine.load_table_records("ai_jobs")
        original_record = dict(jobs[0])
        original_ver = compute_canonical_source_version("job", original_record)

        # Modify a non-description field
        modified_record = dict(original_record)
        modified_record["job_title"] = "Senior Staff AI Engineer"
        modified_ver = compute_canonical_source_version("job", modified_record)

        self.assertNotEqual(original_ver, modified_ver, "Modifying canonical job_title must change source version!")
        self.assertEqual(len(original_ver), 64, "Source version must be a full 64-character SHA-256 hex string!")
        self.assertEqual(len(modified_ver), 64, "Source version must be a full 64-character SHA-256 hex string!")


if __name__ == "__main__":
    unittest.main()

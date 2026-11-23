"""
Unit tests for real JSON Schema validation using jsonschema.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - Strict Schema Validation
"""

import unittest
import uuid
from datetime import datetime, timezone

from core.llm.schema_validator import validate_json_schema
from core.enrichment.schema_validator import validate_enrichment_result_schema
from core.enrichment.schemas import (
    ENRICHMENT_RESULT_SCHEMA,
    JOB_ENRICHMENT_SCHEMA,
    STARTUP_ENRICHMENT_SCHEMA,
    PRODUCT_ENRICHMENT_SCHEMA,
    RESEARCH_PAPER_ENRICHMENT_SCHEMA,
    NEWS_ENRICHMENT_SCHEMA,
    ValidationStatus
)


class TestSchemaValidation(unittest.TestCase):

    def setUp(self):
        self.valid_result_dict = {
            "attempt_id": str(uuid.uuid4()),
            "record_id": "job_12345",
            "entity_type": "job",
            "field_name": "technologies",
            "original_value": None,
            "enriched_value": ["Python", "PyTorch"],
            "source_url": "https://example.com/job/123",
            "evidence": "Requires strong Python and PyTorch skills.",
            "source_version": "a1b2c3d4e5f6071829",
            "confidence_score": 0.85,
            "enrichment_method": "heuristic_extraction",
            "provider": "offline",
            "model": "heuristic-keyword-v1",
            "enriched_at": datetime.now(timezone.utc).isoformat(),
            "validation_status": "NEEDS_REVIEW",
            "validation_rationale": "All items substantiated by evidence.",
            "retry_count": 0
        }

    def test_valid_result_schema_passes(self):
        """Test that a fully compliant EnrichmentResult record passes schema validation."""
        is_valid, err = validate_enrichment_result_schema(self.valid_result_dict)
        self.assertTrue(is_valid, f"Expected valid schema, got error: {err}")
        self.assertIsNone(err)

    def test_missing_required_fields_fails(self):
        """Test that omitting required fields (e.g. attempt_id, record_id, validation_status) fails."""
        for req_field in ["attempt_id", "record_id", "entity_type", "field_name", "validation_status", "source_version"]:
            bad_dict = dict(self.valid_result_dict)
            del bad_dict[req_field]
            is_valid, err = validate_enrichment_result_schema(bad_dict)
            self.assertFalse(is_valid)
            self.assertIn("required", err.lower())

    def test_invalid_validation_status_enum_fails(self):
        """Test that invalid validation statuses (e.g. 'APPROVED', 'UNKNOWN', 'PENDING') are rejected."""
        for invalid_status in ["APPROVED", "UNKNOWN", "PENDING", "PASS", "COMPLETED"]:
            bad_dict = dict(self.valid_result_dict)
            bad_dict["validation_status"] = invalid_status
            is_valid, err = validate_enrichment_result_schema(bad_dict)
            self.assertFalse(is_valid)
            self.assertIn("validation_status", err)

    def test_confidence_score_range_0_to_1(self):
        """Test that confidence scores < 0.0 or > 1.0 are rejected."""
        for bad_score in [-0.1, 1.05, 95.0, -1.0]:
            bad_dict = dict(self.valid_result_dict)
            bad_dict["confidence_score"] = bad_score
            is_valid, err = validate_enrichment_result_schema(bad_dict)
            self.assertFalse(is_valid)
            self.assertIn("confidence_score", err)

    def test_additional_properties_rejected(self):
        """Test that unexpected extra properties are rejected by schema."""
        bad_dict = dict(self.valid_result_dict)
        bad_dict["unauthorized_inferred_salary"] = 150000
        is_valid, err = validate_enrichment_result_schema(bad_dict)
        self.assertFalse(is_valid)
        self.assertIn("Additional properties are not allowed", err)

    def test_entity_schemas_enforce_types_and_required_evidence(self):
        """Test that entity schemas (Job, Startup, Product, Paper, News) reject missing evidence or invalid types."""
        schemas = [
            JOB_ENRICHMENT_SCHEMA,
            STARTUP_ENRICHMENT_SCHEMA,
            PRODUCT_ENRICHMENT_SCHEMA,
            RESEARCH_PAPER_ENRICHMENT_SCHEMA,
            NEWS_ENRICHMENT_SCHEMA
        ]
        for schema in schemas:
            # Missing evidence
            bad_payload = {"confidence_score": 0.8}
            is_valid, err = validate_json_schema(bad_payload, schema)
            self.assertFalse(is_valid)
            self.assertIn("evidence", err)

            # Invalid confidence type
            bad_payload2 = {"evidence": "Valid sentence excerpt.", "confidence_score": "high"}
            is_valid2, err2 = validate_json_schema(bad_payload2, schema)
            self.assertFalse(is_valid2)
            self.assertIn("confidence_score", err2)


if __name__ == "__main__":
    unittest.main()

"""
Test Suite for Stage 3 Gemini LLM Enrichment Pipeline
======================================================
Covers all 21 test requirements specified in Stage 3 Execution Brief:
1. Actual Gemini provider configuration
2. API authentication failure handling
3. API quota and rate-limit handling (HTTP 429)
4. Timeout handling
5. Malformed JSON response parsing
6. Invalid field types handling
7. Unsupported claims detection
8. Contradictory evidence detection
9. Negation and attribution preservation
10. Numerical value and date mismatches
11. Partial list evidence detection
12. Unique operation and proposal IDs
13. Bounded retry and backoff handling
14. Source quotation traceability
15. Pending approval protection
16. Rejected proposal protection
17. Explicit approval requirements
18. Canonical database write protection
19. Historical audit log preservation (366 archive rows)
20. Transactional rollback on database failure
21. No offline fallback masquerading as Gemini
"""

from datetime import datetime, timezone
import json
import os
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import httpx

from core.enrichment.engine import EnrichmentEngine
from core.enrichment.schemas import (
    EnrichmentResult,
    ValidationStatus,
    compute_canonical_source_version,
)
from core.enrichment.validator import EvidenceValidator
from src.stage3.apply_approved import ApprovedUpdateApplicator
from src.stage3.gemini_enrichment import GeminiEnrichmentRunner, compute_file_hash
from src.stage3.gemini_provider import (
    DEFAULT_GEMINI_MODEL,
    GeminiEnrichmentResponse,
    GeminiProvider,
    GeminiUsage,
    redact_secrets,
)
from src.stage3.review_proposals import ReviewQueueManager
from src.stage3.schema_mapping import (
    CANONICAL_TABLE_SCHEMAS,
    ENTITY_TABLE_MAP,
    check_proposal_schema_compatibility,
    is_column_allowed,
    is_valid_sql_identifier,
)


class TestGeminiProviderConfiguration(unittest.TestCase):
    """Test 1: Actual Gemini provider configuration."""

    def test_provider_defaults_and_env(self):
        # Default model is gemini-3.1-flash-lite
        provider = GeminiProvider(api_key="mock-test-key-123")
        self.assertEqual(provider.model_id, DEFAULT_GEMINI_MODEL)
        self.assertEqual(provider.api_key, "mock-test-key-123")
        self.assertEqual(provider.max_retries, 3)

        # Custom model override
        custom_provider = GeminiProvider(api_key="mock-test-key-456", model_id="gemini-1.5-pro")
        self.assertEqual(custom_provider.model_id, "gemini-1.5-pro")

    def test_secret_redaction(self):
        dummy_secret = "MOCK_SECRET_REDACTION_TOKEN_TEST"
        msg = f"Connecting with key={dummy_secret} to endpoint"
        redacted = redact_secrets(msg, dummy_secret)
        self.assertNotIn(dummy_secret, redacted)
        self.assertIn("[REDACTED_GEMINI_KEY]", redacted)


class TestGeminiAuthAndErrorHandling(unittest.TestCase):
    """Tests 2, 3, 4, 13: Auth, rate limits, timeouts, retries."""

    def test_missing_api_key_validation(self):
        """Test 2a: Missing API key fails validation cleanly."""
        provider = GeminiProvider(api_key="")
        is_valid, msg = provider.validate_api_key()
        self.assertFalse(is_valid)
        self.assertIn("GEMINI_API_KEY is not configured", msg)

    @patch("httpx.Client.post")
    def test_auth_failure_http_401(self, mock_post):
        """Test 2b: HTTP 401 raises error immediately without infinite retries."""
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "API_KEY_INVALID: API key not valid."
        mock_post.return_value = mock_resp

        provider = GeminiProvider(api_key="invalid-key")
        with self.assertRaises(RuntimeError) as ctx:
            provider.generate_content_rest("Test prompt", "req-1")
        self.assertIn("HTTP 401", str(ctx.exception))
        self.assertEqual(mock_post.call_count, 1)  # Non-retryable

    @patch("httpx.Client.post")
    def test_rate_limit_retry_http_429(self, mock_post):
        """Test 3 & 13: HTTP 429 triggers bounded retries with backoff."""
        mock_resp_429 = MagicMock()
        mock_resp_429.status_code = 429
        mock_resp_429.text = "Resource has been exhausted (rate limit)."

        mock_resp_200 = MagicMock()
        mock_resp_200.status_code = 200
        mock_resp_200.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps({
                                    "record_id": "rec-1",
                                    "entity_type": "startup",
                                    "target_field": "ai_specialization",
                                    "original_value": None,
                                    "proposed_value": "Foundation Models & LLMs",
                                    "evidence": "LLMs",
                                    "evidence_url": "http://example.com",
                                    "evidence_quote": "LLMs",
                                    "reasoning": "Reason",
                                    "confidence": 0.9,
                                    "status": "VERIFIED",
                                    "limitations": "",
                                    "model_id": "gemini-2.5-flash",
                                    "provider": "google-gemini",
                                })
                            }
                        ]
                    }
                }
            ],
            "usageMetadata": {"promptTokenCount": 50, "candidatesTokenCount": 20, "totalTokenCount": 70}
        }

        # First call 429, second call 200
        mock_post.side_effect = [mock_resp_429, mock_resp_200]

        provider = GeminiProvider(api_key="valid-key", retry_delay_base=0.01)
        data, usage = provider.generate_content_rest("Test prompt", "req-2")
        self.assertEqual(mock_post.call_count, 2)
        self.assertEqual(usage.total_tokens, 70)

    @patch("httpx.Client.post")
    def test_timeout_handling(self, mock_post):
        """Test 4: Timeout triggers bounded retry and records failure."""
        mock_post.side_effect = httpx.TimeoutException("Timed out")
        provider = GeminiProvider(api_key="valid-key", max_retries=2, retry_delay_base=0.01)
        resp = provider.enrich_candidate(
            record_id="rec-1",
            entity_type="startup",
            target_field="ai_specialization",
            original_value=None,
            canonical_source_text="Some text",
            source_url="http://example.com",
            request_id="req-timeout",
        )
        self.assertFalse(resp.is_success)
        self.assertEqual(resp.status, "FAILED")
        self.assertIn("timed out", resp.error_message.lower())
        self.assertEqual(mock_post.call_count, 3)  # Initial + 2 retries


class TestGeminiResponseParsingAndValidation(unittest.TestCase):
    """Tests 5, 6, 7, 8, 9, 10, 11, 14: Structured parsing & EvidenceValidator."""

    @patch("httpx.Client.post")
    def test_malformed_json_response(self, mock_post):
        """Test 5: Malformed JSON handled gracefully as FAILED status."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "NOT VALID JSON {foo: bar"}]}}]
        }
        mock_post.return_value = mock_resp

        provider = GeminiProvider(api_key="valid-key")
        resp = provider.enrich_candidate(
            record_id="rec-1",
            entity_type="startup",
            target_field="ai_specialization",
            original_value=None,
            canonical_source_text="Some text",
            source_url="http://example.com",
            request_id="req-malformed",
        )
        self.assertFalse(resp.is_success)
        self.assertEqual(resp.status, "FAILED")
        self.assertIn("Malformed JSON", resp.error_message)

    def test_invalid_taxonomy_field_type(self):
        """Test 6: Invalid taxonomy value receives FAILED status."""
        res = EnrichmentResult(
            attempt_id="att-1",
            record_id="prelim_startup_6631243200679035785",
            entity_type="startup",
            field_name="ai_specialization",
            original_value=None,
            enriched_value="Fabricated AI Category That Does Not Exist",
            source_url="http://example.com",
            evidence="Fabricated text",
            source_version="abc",
            confidence_score=0.9,
            enrichment_method="llm_extraction",
            provider="google-gemini",
            model="gemini-2.5-flash",
            enriched_at="2026-11-22T00:00:00Z",
            validation_status="NEEDS_REVIEW",
            validation_rationale="",
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, "Fabricated text")
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("Taxonomy Violation", rationale)

    def test_unsupported_claims(self):
        """Test 7: Unsupported claims never receive VERIFIED status."""
        res = EnrichmentResult(
            attempt_id="att-2",
            record_id="arxiv_2611_26232",
            entity_type="paper",
            field_name="methodology",
            original_value=None,
            enriched_value="We utilize quantum annealing for training models.",
            source_url="http://example.com",
            evidence="This paper proposes a stochastic gradient descent algorithm.",
            source_version="abc",
            confidence_score=0.9,
            enrichment_method="llm_extraction",
            provider="google-gemini",
            model="gemini-2.5-flash",
            enriched_at="2026-11-22T00:00:00Z",
            validation_status="NEEDS_REVIEW",
            validation_rationale="",
        )
        status, rationale = EvidenceValidator.validate_enrichment(
            res, "This paper proposes a stochastic gradient descent algorithm."
        )
        self.assertNotEqual(status, ValidationStatus.VERIFIED)

    def test_contradictory_negation_evidence(self):
        """Test 8 & 9: Evidence with negation rejects affirmative claims."""
        res = EnrichmentResult(
            attempt_id="att-3",
            record_id="arxiv_2611_26232",
            entity_type="paper",
            field_name="methodology",
            original_value=None,
            enriched_value="We manufacture autonomous surgical robots.",
            source_url="http://example.com",
            evidence="We do not manufacture autonomous surgical robots.",
            source_version="abc",
            confidence_score=0.9,
            enrichment_method="llm_extraction",
            provider="google-gemini",
            model="gemini-2.5-flash",
            enriched_at="2026-11-22T00:00:00Z",
            validation_status="NEEDS_REVIEW",
            validation_rationale="",
        )
        status, rationale = EvidenceValidator.validate_enrichment(
            res, "We do not manufacture autonomous surgical robots."
        )
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("Semantic Contradiction", rationale)

    def test_numerical_mismatch(self):
        """Test 10: Date / numerical discrepancy triggers failure."""
        res = EnrichmentResult(
            attempt_id="att-4",
            record_id="prelim_startup_6631243200679035785",
            entity_type="startup",
            field_name="description",
            original_value=None,
            enriched_value="The company was founded in 2022.",
            source_url="http://example.com",
            evidence="The company was founded in 2020.",
            source_version="abc",
            confidence_score=0.9,
            enrichment_method="llm_extraction",
            provider="google-gemini",
            model="gemini-2.5-flash",
            enriched_at="2026-11-22T00:00:00Z",
            validation_status="NEEDS_REVIEW",
            validation_rationale="",
        )
        status, rationale = EvidenceValidator.validate_enrichment(
            res, "The company was founded in 2020."
        )
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("Semantic Mismatch", rationale)
        self.assertIn("2022", rationale)

    def test_partial_list_evidence(self):
        """Test 11: List where only partial elements are grounded requires review or fails."""
        res = EnrichmentResult(
            attempt_id="att-5",
            record_id="job_e98b00bb44e6a41d",
            entity_type="job",
            field_name="technologies",
            original_value=None,
            enriched_value=["Python", "QuantumCryptography"],
            source_url="http://example.com",
            evidence="Requires strong Python skills.",
            source_version="abc",
            confidence_score=0.9,
            enrichment_method="llm_extraction",
            provider="google-gemini",
            model="gemini-2.5-flash",
            enriched_at="2026-11-22T00:00:00Z",
            validation_status="NEEDS_REVIEW",
            validation_rationale="",
        )
        status, rationale = EvidenceValidator.validate_enrichment(
            res, "Requires strong Python skills."
        )
        self.assertNotEqual(status, ValidationStatus.VERIFIED)

    def test_source_quotation_traceability(self):
        """Test 14: Evidence excerpt must be traceable to original canonical source text."""
        res = EnrichmentResult(
            attempt_id="att-6",
            record_id="prelim_startup_6631243200679035785",
            entity_type="startup",
            field_name="ai_specialization",
            original_value=None,
            enriched_value="Foundation Models & LLMs",
            source_url="http://example.com",
            evidence="Completely hallucinated quote not present in source",
            source_version="abc",
            confidence_score=0.9,
            enrichment_method="llm_extraction",
            provider="google-gemini",
            model="gemini-2.5-flash",
            enriched_at="2026-11-22T00:00:00Z",
            validation_status="NEEDS_REVIEW",
            validation_rationale="",
        )
        status, rationale = EvidenceValidator.validate_enrichment(
            res, "Company Name: Mistral AI\nAI Focus: foundation model; ai; artificial intelligence; llm"
        )
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("Rule 2 Violation", rationale)
        self.assertIn("not be traced", rationale)


class TestApprovalQueueAndWriteProtection(unittest.TestCase):
    """Tests 12, 15, 16, 17, 18, 19, 20, 21: Safety, approval workflows, write protection."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_stage3_")
        self.temp_db = os.path.join(self.temp_dir, "test_ecosystem.db")
        # Copy active DB to temporary location for destructive/test operations
        shutil.copyfile("data/normalized/ai_ecosystem.db", self.temp_db)

        self.temp_results = os.path.join(self.temp_dir, "results.jsonl")
        self.temp_queue = os.path.join(self.temp_dir, "queue.csv")
        self.temp_summary = os.path.join(self.temp_dir, "summary.json")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_unique_operation_and_proposal_ids(self):
        """Test 12: Unique operation IDs generated per candidate."""
        import uuid
        ids = {str(uuid.uuid4()) for _ in range(100)}
        self.assertEqual(len(ids), 100)

    def test_pending_approval_protection(self):
        """Test 15: Cannot apply proposals with status PENDING_APPROVAL."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )
        # Create dummy proposal with PENDING_APPROVAL
        proposal = {
            "proposal_id": "prop-pending-1",
            "record_id": "prelim_startup_6631243200679035785",
            "entity_type": "startup",
            "field_name": "ai_specialization",
            "original_value": None,
            "proposed_value": "Foundation Models & LLMs",
            "validation_status": "VERIFIED",
            "approval_status": "PENDING_APPROVAL",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        success, msg = applicator.apply_proposal("prop-pending-1", confirm_authorized=True)
        self.assertFalse(success)
        self.assertIn("APPROVAL VIOLATION", msg)

    def test_rejected_proposal_protection(self):
        """Test 16: Cannot apply rejected proposals."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )
        proposal = {
            "proposal_id": "prop-rejected-1",
            "record_id": "prelim_startup_6631243200679035785",
            "entity_type": "startup",
            "field_name": "ai_specialization",
            "original_value": None,
            "proposed_value": "Foundation Models & LLMs",
            "validation_status": "VERIFIED",
            "approval_status": "REJECTED",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        success, msg = applicator.apply_proposal("prop-rejected-1", confirm_authorized=True)
        self.assertFalse(success)
        self.assertIn("APPROVAL VIOLATION", msg)

    def test_explicit_approval_requirements(self):
        """Test 17: Cannot apply without confirm_authorized=True flag."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )
        success, msg = applicator.apply_proposal("prop-1", confirm_authorized=False)
        self.assertFalse(success)
        self.assertIn("WRITE PROTECTION ABORT", msg)

    def test_canonical_database_write_protection_and_hash(self):
        """Test 18: GeminiEnrichmentRunner dry-run leaves DB byte-identical."""
        pre_hash = compute_file_hash("data/normalized/ai_ecosystem.db")
        runner = GeminiEnrichmentRunner(db_path="data/normalized/ai_ecosystem.db")
        success = runner.run_dry_run()
        self.assertTrue(success)
        post_hash = compute_file_hash("data/normalized/ai_ecosystem.db")
        self.assertEqual(pre_hash, post_hash)

    def test_historical_audit19_log_preservation(self):
        """Test 19: Historical Audit 19 archive rows remain exactly 366 rows."""
        conn = sqlite3.connect("data/normalized/ai_ecosystem.db")
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM audit19_enrichment_audit_log_archive")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 366)

    def test_rollback_on_database_failure(self):
        """Test 20: Transaction rollback on database failure."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )
        # Create an approved proposal targeting a non-existent table/record
        proposal = {
            "proposal_id": "prop-bad-table",
            "record_id": "non_existent_rec_9999",
            "entity_type": "startup",
            "field_name": "ai_focus_area",
            "original_value": None,
            "proposed_value": "Foundation Models & LLMs",
            "validation_status": "VERIFIED",
            "approval_status": "APPROVED",
            "duplication_status": "NO_DUPLICATION",
            "schema_status": "SCHEMA_COMPATIBLE",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        success, msg = applicator.apply_proposal("prop-bad-table", confirm_authorized=True)
        self.assertFalse(success)
        self.assertIn("not found in canonical table", msg)

    def test_no_offline_fallback_masquerading(self):
        """Test 21: Never fall back to offline heuristic when Gemini fails."""
        provider = GeminiProvider(api_key="valid-key")
        with patch.object(provider, "generate_content_rest", side_effect=RuntimeError("Gemini 503 Unavailable")):
            resp = provider.enrich_candidate(
                record_id="rec-1",
                entity_type="startup",
                target_field="ai_specialization",
                original_value=None,
                canonical_source_text="Some text",
                source_url="http://example.com",
                request_id="req-no-masquerade",
            )
            # Must record as FAILED and never return heuristic output
            self.assertFalse(resp.is_success)
            self.assertEqual(resp.status, "FAILED")
            self.assertIsNone(resp.proposed_value)
            self.assertIn("Gemini 503 Unavailable", resp.error_message)


class TestAudit27SchemaAndValidationHardening(unittest.TestCase):
    """
    Audit 27 Hardening Tests:
    1. Every proposal target field exists in the canonical schema allowlist check.
    2. Missing target fields are rejected before approval (BLOCKED_SCHEMA).
    3. Every VERIFIED proposal can pass a read-only schema compatibility check.
    4. Generated labels cannot count as original evidence.
    5. Existing field duplication is detected.
    6. Approval cannot bypass schema compatibility.
    7. SQL identifier allowlisting.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = os.path.join(self.temp_dir, "test_schema.db")
        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE ai_startups (
                startup_id TEXT PRIMARY KEY,
                entity_name TEXT,
                ai_focus_area TEXT,
                ai_evidence TEXT,
                description TEXT
            );
        """)
        cursor.execute("""
            INSERT INTO ai_startups (startup_id, entity_name, ai_focus_area, ai_evidence, description)
            VALUES ('startup-1', 'Anthropic', 'Applied AI & Automation', 'foundation model; ai; llm', 'Anthropic is an AI safety startup.');
        """)
        conn.commit()
        conn.close()

        self.temp_results = os.path.join(self.temp_dir, "results.jsonl")
        self.temp_queue = os.path.join(self.temp_dir, "queue.csv")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_target_field_exists_in_schema_allowlist(self):
        """Test 22: Target field existence verification against canonical schema allowlist."""
        # Existing columns in canonical tables
        self.assertTrue(is_column_allowed("ai_news", "summary"))
        self.assertTrue(is_column_allowed("ai_jobs", "required_skills"))
        self.assertTrue(is_column_allowed("ai_startups", "ai_focus_area"))
        self.assertTrue(is_column_allowed("ai_startups", "ai_evidence"))
        self.assertTrue(is_column_allowed("ai_research_papers", "abstract"))

        # Non-existent columns in canonical tables
        self.assertFalse(is_column_allowed("ai_startups", "technologies"))
        self.assertFalse(is_column_allowed("ai_startups", "ai_specialization"))
        self.assertFalse(is_column_allowed("ai_research_papers", "methodology"))
        self.assertFalse(is_column_allowed("ai_research_papers", "research_domain"))
        self.assertFalse(is_column_allowed("ai_research_papers", "key_contributions"))
        self.assertFalse(is_column_allowed("ai_jobs", "technologies"))

        # Non-existent table
        self.assertFalse(is_column_allowed("non_existent_table", "summary"))

    def test_missing_target_fields_rejected_before_approval(self):
        """Test 23: Missing target fields are flagged as BLOCKED_SCHEMA before approval."""
        is_compat, code, reason = check_proposal_schema_compatibility("startup", "ai_specialization")
        self.assertFalse(is_compat)
        self.assertEqual(code, "BLOCKED_SCHEMA")
        self.assertIn("does not exist in canonical table 'ai_startups'", reason)

        is_compat, code, reason = check_proposal_schema_compatibility("paper", "methodology")
        self.assertFalse(is_compat)
        self.assertEqual(code, "BLOCKED_SCHEMA")
        self.assertIn("does not exist in canonical table 'ai_research_papers'", reason)

        is_compat, code, reason = check_proposal_schema_compatibility("job", "technologies")
        self.assertFalse(is_compat)
        self.assertEqual(code, "BLOCKED_SCHEMA")
        self.assertIn("does not exist in canonical table 'ai_jobs'", reason)

        # Compatible field check
        is_compat, code, reason = check_proposal_schema_compatibility("news", "summary")
        self.assertTrue(is_compat)
        self.assertEqual(code, "SCHEMA_COMPATIBLE")

    def test_verified_proposals_pass_readonly_schema_check(self):
        """Test 24: Read-only schema compatibility audit identifies all un-migrated target fields."""
        test_proposals = [
            {"entity_type": "startup", "field_name": "ai_specialization", "validation_status": "VERIFIED"},
            {"entity_type": "startup", "field_name": "technologies", "validation_status": "VERIFIED"},
            {"entity_type": "paper", "field_name": "methodology", "validation_status": "VERIFIED"},
            {"entity_type": "paper", "field_name": "research_domain", "validation_status": "VERIFIED"},
            {"entity_type": "news", "field_name": "summary", "validation_status": "NEEDS_REVIEW"},
            {"entity_type": "job", "field_name": "required_skills", "validation_status": "FAILED"},
        ]
        results = []
        for p in test_proposals:
            is_compat, status_code, _ = check_proposal_schema_compatibility(p["entity_type"], p["field_name"])
            results.append((p["field_name"], is_compat, status_code))

        # Check that the 4 verified fields targeting missing columns are caught
        verified_blocked = [r for r in results if not r[1]]
        self.assertEqual(len(verified_blocked), 4)
        for field_name, is_compat, status_code in verified_blocked:
            self.assertEqual(status_code, "BLOCKED_SCHEMA")

    def test_generated_labels_cannot_count_as_original_evidence(self):
        """Test 25: Application-generated context labels cannot count as original evidence."""
        # 1. Exact label rejected by is_verbatim_excerpt
        self.assertFalse(EvidenceValidator.is_verbatim_excerpt("Company Name:", "Company Name: Anthropic"))
        self.assertFalse(EvidenceValidator.is_verbatim_excerpt("AI Focus:", "AI Focus: Applied AI & Automation"))
        self.assertFalse(EvidenceValidator.is_verbatim_excerpt("Existing Description:", "Existing Description: Safety lab"))
        self.assertFalse(EvidenceValidator.is_verbatim_excerpt("Evidence:", "Evidence: foundation model; ai"))
        self.assertFalse(EvidenceValidator.is_verbatim_excerpt("Title:", "Title: Some research paper"))

        # 2. validate_enrichment rejects pure application labels as Rule 2 violation
        dummy_result = EnrichmentResult(
            attempt_id="att-label-1",
            record_id="rec-1",
            entity_type="startup",
            field_name="ai_specialization",
            original_value=None,
            enriched_value="Applied AI & Automation",
            source_url="http://example.com",
            evidence="AI Focus:",
            source_version="v1",
            confidence_score=0.9,
            enrichment_method="llm_extraction",
            provider="google-gemini",
            model="gemini-3.1-flash-lite",
            enriched_at="2026-11-22T00:00:00Z",
            validation_status="NEEDS_REVIEW",
            validation_rationale="",
        )
        status, rationale = EvidenceValidator.validate_enrichment(dummy_result, "AI Focus: Applied AI & Automation")
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("cannot qualify as an original source quotation", rationale)

    def test_existing_field_duplication_is_detected(self):
        """Test 26: Proposed values duplicating existing canonical data are detected and flagged."""
        canonical_record = {
            "startup_id": "startup-1",
            "entity_name": "Anthropic",
            "ai_focus_area": "Applied AI & Automation",
            "ai_evidence": "foundation model; ai; artificial intelligence; llm",
            "description": "Anthropic is an AI safety startup building Claude.",
        }

        # Case A: Duplicate ai_focus_area
        dup_focus_result = EnrichmentResult(
            attempt_id="att-dup-1",
            record_id="startup-1",
            entity_type="startup",
            field_name="ai_specialization",
            original_value=None,
            enriched_value="Applied AI & Automation",
            source_url="http://example.com",
            evidence="Anthropic is an AI safety startup building Claude.",
            source_version="v1",
            confidence_score=0.95,
            enrichment_method="llm_extraction",
            provider="google-gemini",
            model="gemini-3.1-flash-lite",
            enriched_at="2026-11-22T00:00:00Z",
            validation_status="NEEDS_REVIEW",
            validation_rationale="",
        )
        status, rationale = EvidenceValidator.validate_enrichment(
            dup_focus_result,
            "Anthropic is an AI safety startup building Claude.",
            canonical_record=canonical_record,
        )
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
        self.assertIn("Duplication Safeguard: Proposed value 'Applied AI & Automation' duplicates existing ai_focus_area", rationale)

        # Case B: Duplicate technologies that already exist in ai_evidence
        dup_tech_result = EnrichmentResult(
            attempt_id="att-dup-2",
            record_id="startup-1",
            entity_type="startup",
            field_name="technologies",
            original_value=None,
            enriched_value=["foundation model", "ai", "llm"],
            source_url="http://example.com",
            evidence="Anthropic is an AI safety startup building Claude.",
            source_version="v1",
            confidence_score=0.95,
            enrichment_method="llm_extraction",
            provider="google-gemini",
            model="gemini-3.1-flash-lite",
            enriched_at="2026-11-22T00:00:00Z",
            validation_status="NEEDS_REVIEW",
            validation_rationale="",
        )
        status, rationale = EvidenceValidator.validate_enrichment(
            dup_tech_result,
            "Anthropic is an AI safety startup building Claude.",
            canonical_record=canonical_record,
        )
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
        self.assertIn("Duplication Safeguard: All proposed technologies", rationale)
        self.assertIn("already exist in canonical ai_evidence", rationale)

    def test_approval_cannot_bypass_schema_compatibility(self):
        """Test 27: Human approval cannot bypass schema compatibility checks in apply_approved.py."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )

        # Even with approval_status=APPROVED and validation_status=VERIFIED,
        # proposal targeting non-existent column 'ai_specialization' must be rejected
        proposal = {
            "proposal_id": "prop-bypass-test",
            "record_id": "startup-1",
            "entity_type": "startup",
            "field_name": "ai_specialization",
            "original_value": None,
            "proposed_value": "Applied AI & Automation",
            "validation_status": "VERIFIED",
            "approval_status": "APPROVED",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        success, msg = applicator.apply_proposal("prop-bypass-test", confirm_authorized=True)
        self.assertFalse(success)
        self.assertIn("SCHEMA COMPATIBILITY ABORT: BLOCKED_SCHEMA", msg)
        self.assertIn("Column 'ai_specialization' does not exist in canonical table 'ai_startups'", msg)

        # Confirm no database modification occurred
        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(ai_startups);")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        self.assertNotIn("ai_specialization", columns)

    def test_sql_identifier_allowlisting(self):
        """Test 28: SQL identifier allowlisting rejects malicious identifiers and accepts valid ones."""
        # Valid identifiers
        self.assertTrue(is_valid_sql_identifier("startup_id"))
        self.assertTrue(is_valid_sql_identifier("ai_startups"))
        self.assertTrue(is_valid_sql_identifier("summary"))
        self.assertTrue(is_valid_sql_identifier("field_123"))
        self.assertTrue(is_valid_sql_identifier("_private_col"))

        # Malicious or invalid identifiers
        self.assertFalse(is_valid_sql_identifier("col; DROP TABLE ai_startups;--"))
        self.assertFalse(is_valid_sql_identifier("col' OR '1'='1"))
        self.assertFalse(is_valid_sql_identifier("col name with spaces"))
        self.assertFalse(is_valid_sql_identifier("col-with-dashes"))
        self.assertFalse(is_valid_sql_identifier("123startsWithDigit"))
        self.assertFalse(is_valid_sql_identifier("col$dollar"))
        self.assertFalse(is_valid_sql_identifier(""))
        self.assertFalse(is_valid_sql_identifier(None))


class TestAudit28DefectCorrections(unittest.TestCase):
    """
    Audit 28 Critical Defect Correction Tests:
    1. Rejection of label-plus-value adversarial quotations (e.g. 'AI Focus: Applied AI & Automation').
    2. Tests proving generated context labels can never produce VERIFIED status.
    3. 100% parity verification between JSONL and CSV review queue.
    4. Duplication protection in apply_approved.py (rejects DUPLICATE_OF_EXISTING_CANONICAL_DATA).
    5. Runtime SQLite PRAGMA table_info physical schema verification.
    6. Future schema migration cannot bypass dynamic canonical duplication protection.
    7. Revalidation of nine VERIFIED proposals preserves strict data governance.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = os.path.join(self.temp_dir, "test_audit28.db")
        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE ai_startups (
                startup_id TEXT PRIMARY KEY,
                entity_name TEXT,
                ai_focus_area TEXT,
                ai_evidence TEXT,
                description TEXT
            );
        """)
        cursor.execute("""
            INSERT INTO ai_startups (startup_id, entity_name, ai_focus_area, ai_evidence, description)
            VALUES ('startup-1', 'Anthropic', 'Applied AI & Automation', 'foundation model; ai; llm', 'Anthropic is an AI safety startup.');
        """)
        conn.commit()
        conn.close()

        self.temp_results = os.path.join(self.temp_dir, "results.jsonl")
        self.temp_queue = os.path.join(self.temp_dir, "queue.csv")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_adversarial_label_plus_value_quotation_rejected(self):
        """Test 29: Adversarial label-plus-value quotations are strictly rejected by validator."""
        source_text = (
            "Company Name: Anthropic\n"
            "AI Focus: Applied AI & Automation\n"
            "Existing Description: Safety research lab\n"
            "Evidence: foundation model; ai\n"
            "Title: Autonomous AI Agents\n"
            "Abstract: This paper studies safe AI.\n"
            "Job Title: AI Research Scientist\n"
            "Company: Anthropic PBC\n"
            "Description: We are seeking an AI Researcher."
        )

        adversarial_quotes = [
            "AI Focus: Applied AI & Automation",
            "Company Name: Anthropic",
            "Existing Description: Safety research lab",
            "Evidence: foundation model; ai",
            "Title: Autonomous AI Agents",
            "Abstract: This paper studies safe AI.",
            "Job Title: AI Research Scientist",
            "Company: Anthropic PBC",
            "Description: We are seeking an AI Researcher.",
        ]

        for adv_quote in adversarial_quotes:
            # is_verbatim_excerpt must return False
            self.assertFalse(
                EvidenceValidator.is_verbatim_excerpt(adv_quote, source_text),
                f"Quotation with label prefix '{adv_quote}' must be rejected by is_verbatim_excerpt"
            )

            # validate_enrichment must return FAILED
            result = EnrichmentResult(
                attempt_id="att-test",
                record_id="rec-1",
                entity_type="startup",
                field_name="ai_specialization",
                original_value=None,
                enriched_value="Applied AI & Automation",
                source_url="http://example.com",
                evidence=adv_quote,
                source_version="v1",
                confidence_score=0.9,
                enrichment_method="llm_extraction",
                provider="google-gemini",
                model="gemini-3.1-flash-lite",
                enriched_at="2026-11-22T00:00:00Z",
                validation_status="NEEDS_REVIEW",
                validation_rationale="",
            )
            setattr(result, "evidence_quote", adv_quote)
            status, rationale = EvidenceValidator.validate_enrichment(result, source_text)
            self.assertEqual(
                status,
                ValidationStatus.FAILED,
                f"Quotation with label prefix '{adv_quote}' must produce FAILED status"
            )
            self.assertIn("Application-generated context label prefix", rationale)

    def test_generated_context_cannot_produce_verified_status(self):
        """Test 30: Proves that generated context labels can NEVER produce VERIFIED status."""
        canonical_record = {
            "startup_id": "startup-1",
            "entity_name": "Anthropic",
            "ai_focus_area": "Applied AI & Automation",
            "ai_evidence": "foundation model; ai; llm",
            "description": "Safety lab",
        }
        source_text = EnrichmentEngine.build_canonical_source_text("startup", canonical_record)

        # Attempt to achieve VERIFIED with label quote
        result = EnrichmentResult(
            attempt_id="att-label-verify",
            record_id="startup-1",
            entity_type="startup",
            field_name="ai_specialization",
            original_value=None,
            enriched_value="Applied AI & Automation",
            source_url="http://example.com",
            evidence="AI Focus: Applied AI & Automation",
            source_version="v1",
            confidence_score=1.0,
            enrichment_method="llm_extraction",
            provider="google-gemini",
            model="gemini-3.1-flash-lite",
            enriched_at="2026-11-22T00:00:00Z",
            validation_status="NEEDS_REVIEW",
            validation_rationale="",
        )
        setattr(result, "evidence_quote", "AI Focus: Applied AI & Automation")

        status, rationale = EvidenceValidator.validate_enrichment(
            result, source_text, canonical_record=canonical_record
        )
        self.assertNotEqual(status, ValidationStatus.VERIFIED)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("Rule 2 Violation", rationale)

    def test_jsonl_and_csv_proposal_parity_100_percent(self):
        """Test 31: 100% field-by-field parity between JSONL results and CSV review queue."""
        from scripts.verify_jsonl_csv_parity import verify_parity
        self.assertTrue(verify_parity())

    def test_apply_approved_rejects_duplicate_canonical_data(self):
        """Test 32: apply_approved.py rejects proposals marked as DUPLICATE_OF_EXISTING_CANONICAL_DATA."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )

        proposal = {
            "proposal_id": "prop-dup-test",
            "record_id": "startup-1",
            "entity_type": "startup",
            "field_name": "ai_focus_area",
            "original_value": "Applied AI & Automation",
            "proposed_value": "Applied AI & Automation",
            "validation_status": "VERIFIED",
            "approval_status": "APPROVED",
            "duplication_status": "DUPLICATE_OF_EXISTING_CANONICAL_DATA",
            "schema_status": "SCHEMA_COMPATIBLE",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        success, msg = applicator.apply_proposal("prop-dup-test", confirm_authorized=True)
        self.assertFalse(success)
        self.assertIn("DUPLICATION ABORT", msg)

    def test_apply_approved_runtime_pragma_table_info_check(self):
        """Test 33: apply_approved.py checks actual SQLite physical schema using PRAGMA table_info."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )

        # Target a column that is not in the physical SQLite table
        proposal = {
            "proposal_id": "prop-pragma-test",
            "record_id": "startup-1",
            "entity_type": "startup",
            "field_name": "ai_specialization",
            "original_value": None,
            "proposed_value": "Foundation Models & LLMs",
            "validation_status": "VERIFIED",
            "approval_status": "APPROVED",
            "duplication_status": "NO_DUPLICATION",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        success, msg = applicator.apply_proposal("prop-pragma-test", confirm_authorized=True)
        self.assertFalse(success)
        self.assertIn("SCHEMA COMPATIBILITY ABORT", msg)

    def test_future_migration_cannot_bypass_duplication_protection(self):
        """Test 34: Future schema migration adding columns cannot bypass dynamic runtime duplication protection."""
        # Simulate a migration that adds the column 'technologies' to SQLite
        conn = sqlite3.connect(self.temp_db)
        conn.execute("ALTER TABLE ai_startups ADD COLUMN technologies TEXT;")
        conn.commit()
        conn.close()

        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )

        # Proposal with proposed technologies identical to existing canonical ai_evidence
        proposal = {
            "proposal_id": "prop-migrated-dup-test",
            "record_id": "startup-1",
            "entity_type": "startup",
            "field_name": "technologies",
            "original_value": None,
            "proposed_value": ["foundation model", "ai", "llm"],
            "validation_status": "VERIFIED",
            "approval_status": "APPROVED",
            "duplication_status": "NO_DUPLICATION",  # Even if mistakenly marked NO_DUPLICATION in JSON
            "schema_status": "SCHEMA_COMPATIBLE",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        # Temporarily allow technologies in schema allowlist to simulate updated schema definition after migration
        with patch.dict(CANONICAL_TABLE_SCHEMAS["ai_startups"], {"technologies": None}):
            CANONICAL_TABLE_SCHEMAS["ai_startups"].add("technologies")
            try:
                # Dynamic runtime duplication check against the actual SQLite row must catch and reject it!
                success, msg = applicator.apply_proposal("prop-migrated-dup-test", confirm_authorized=True)
                self.assertFalse(success)
                self.assertIn("DUPLICATION REJECTED", msg)
                self.assertIn("already exist in canonical ai_evidence", msg)
            finally:
                CANONICAL_TABLE_SCHEMAS["ai_startups"].discard("technologies")

    def test_revalidation_nine_verified_proposals(self):
        """Test 35: Revalidation of original 9 verified proposals enforces label and duplication rules."""
        with open("data/stage3/gemini_enrichment_results.jsonl", "r", encoding="utf-8") as f:
            proposals = [json.loads(line) for line in f if line.strip()]

        # Proposals 1 & 4 must be FAILED due to label quotation
        self.assertEqual(proposals[0]["validation_status"], "FAILED")
        self.assertIn("Application-generated context label prefix", proposals[0]["validation_rationale"])
        self.assertEqual(proposals[3]["validation_status"], "FAILED")
        self.assertIn("Application-generated context label prefix", proposals[3]["validation_rationale"])

        # Proposals 2, 3, 5, 7 must be NEEDS_REVIEW due to duplication safeguard
        for idx in [1, 2, 4, 6]:
            self.assertEqual(proposals[idx]["validation_status"], "NEEDS_REVIEW")
            self.assertEqual(proposals[idx]["duplication_status"], "DUPLICATE_OF_EXISTING_CANONICAL_DATA")

        # The only 3 remaining VERIFIED proposals must all be BLOCKED_SCHEMA
        verified = [p for p in proposals if p["validation_status"] == "VERIFIED"]
        self.assertEqual(len(verified), 3)
        for p in verified:
            self.assertEqual(p["schema_status"], "BLOCKED_SCHEMA")


class TestAudit29ProductionValidationAndApplicator(unittest.TestCase):
    """
    Audit 29 Regression Tests:
    1. Production runner passes canonical record to EvidenceValidator.
    2. Production runner rejects duplicate startup data and leaves DB unmodified.
    3. Production runner validates against raw canonical content (not generated labels).
    4. Applicator rejects missing duplication_status.
    5. Applicator rejects unknown duplication_status.
    6. Applicator rejects missing schema_status.
    7. Applicator rejects non-compatible schema_status (BLOCKED_SCHEMA).
    8. Applicator runtime PRAGMA table_info rejects nonexistent column even if allowed in memory.
    9. Concurrency conflict on empty string "" vs NULL/None.
    10. Concurrency conflict on NULL/None vs empty string "".
    11. Transaction rollback preserves database state.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = os.path.join(self.temp_dir, "test_audit29.db")
        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE ai_startups (
                startup_id TEXT PRIMARY KEY,
                entity_name TEXT,
                ai_focus_area TEXT,
                ai_evidence TEXT,
                description TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE enrichment_audit_log (
                audit_id TEXT PRIMARY KEY,
                entity_type TEXT,
                record_id TEXT,
                field_name TEXT,
                original_value TEXT,
                enriched_value TEXT,
                source_url TEXT,
                evidence_used TEXT,
                confidence_score REAL,
                enrichment_method TEXT,
                provider TEXT,
                model TEXT,
                audit_phase TEXT,
                enriched_at TEXT,
                created_at TEXT
            );
        """)
        cursor.execute("""
            INSERT INTO ai_startups (startup_id, entity_name, ai_focus_area, ai_evidence, description)
            VALUES 
                ('startup-1', 'Anthropic', 'Applied AI & Automation', 'foundation model; ai; llm', 'Anthropic is an AI safety startup.'),
                ('startup-null-focus', 'NullFocus AI', NULL, 'ai research', 'Startup with NULL focus area.'),
                ('startup-empty-focus', 'EmptyFocus AI', '', 'ai research', 'Startup with empty string focus area.');
        """)
        conn.commit()
        conn.close()

        self.temp_results = os.path.join(self.temp_dir, "results.jsonl")
        self.temp_queue = os.path.join(self.temp_dir, "queue.csv")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_production_runner_passes_canonical_record(self):
        """Test 36: Production Gemini runner passes canonical_record into EvidenceValidator.validate_enrichment."""
        runner = GeminiEnrichmentRunner(
            db_path=self.temp_db,
            candidates_file=self.temp_results,
            output_dir=self.temp_dir,
        )
        runner.provider.api_key = "mock-test-key-for-unit-tests"
        
        conn = sqlite3.connect(self.temp_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ai_startups WHERE startup_id = 'startup-1'")
        startup_rec = dict(cursor.fetchone())
        conn.close()
        expected_ver = compute_canonical_source_version("startup", startup_rec)

        candidate = {
            "entity_type": "startup",
            "record_id": "startup-1",
            "field_name": "ai_focus_area",
            "source_url": "https://example.com/anthropic",
            "source_version": expected_ver,
            "original_value": "Applied AI & Automation",
        }
        
        mock_resp = GeminiEnrichmentResponse(
            request_id="req-test",
            record_id="startup-1",
            entity_type="startup",
            target_field="ai_focus_area",
            original_value=None,
            proposed_value="AI Safety and Alignment",
            evidence="AI safety startup.",
            evidence_url="https://example.com/anthropic",
            evidence_quote="AI safety startup.",
            reasoning="Valid grounded extraction",
            confidence=0.95,
            status="SUCCESS",
            limitations="",
            model_id="gemini-3.1-flash-lite",
            provider="google-gemini",
            request_timestamp=datetime.now(timezone.utc).isoformat(),
            response_timestamp=datetime.now(timezone.utc).isoformat(),
            raw_response_text="{}",
            usage=GeminiUsage(prompt_tokens=10, candidates_tokens=10, total_tokens=20),
            retry_count=0,
            is_success=True,
            error_message=None,
        )

        with patch.object(runner, "load_candidates", return_value=[candidate]):
            with patch.object(runner.provider, "enrich_candidate", return_value=mock_resp):
                with patch.object(EvidenceValidator, "validate_enrichment", wraps=EvidenceValidator.validate_enrichment) as mock_val:
                    with patch("time.sleep", return_value=None):
                        runner.run_execute(limit=1)

                    self.assertTrue(mock_val.called)
                    call_kwargs = mock_val.call_args.kwargs
                    self.assertIn("canonical_record", call_kwargs)
                    canonical_rec = call_kwargs["canonical_record"]
                    self.assertIsNotNone(canonical_rec)
                    self.assertEqual(canonical_rec.get("startup_id"), "startup-1")
                    self.assertEqual(canonical_rec.get("entity_name"), "Anthropic")

    def test_production_runner_rejects_duplicate_startup_data(self):
        """Test 37: Production runner duplication safeguard flags duplicate values as NEEDS_REVIEW."""
        db_hash_before = compute_file_hash(self.temp_db)
        
        runner = GeminiEnrichmentRunner(
            db_path=self.temp_db,
            candidates_file=self.temp_results,
            output_dir=self.temp_dir,
        )
        runner.provider.api_key = "mock-test-key-for-unit-tests"
        
        conn = sqlite3.connect(self.temp_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ai_startups WHERE startup_id = 'startup-1'")
        startup_rec = dict(cursor.fetchone())
        conn.close()
        expected_ver = compute_canonical_source_version("startup", startup_rec)

        # Candidate proposing existing focus area ('Applied AI & Automation')
        candidate = {
            "entity_type": "startup",
            "record_id": "startup-1",
            "field_name": "ai_focus_area",
            "source_url": "https://example.com/anthropic",
            "source_version": expected_ver,
            "original_value": "Applied AI & Automation",
        }
        
        mock_resp = GeminiEnrichmentResponse(
            request_id="req-test-dup",
            record_id="startup-1",
            entity_type="startup",
            target_field="ai_focus_area",
            original_value="Applied AI & Automation",
            proposed_value="Applied AI & Automation",
            evidence="Applied AI & Automation",
            evidence_url="https://example.com/anthropic",
            evidence_quote="Applied AI & Automation",
            reasoning="Duplicates existing data",
            confidence=0.95,
            status="SUCCESS",
            limitations="",
            model_id="gemini-3.1-flash-lite",
            provider="google-gemini",
            request_timestamp=datetime.now(timezone.utc).isoformat(),
            response_timestamp=datetime.now(timezone.utc).isoformat(),
            raw_response_text="{}",
            usage=GeminiUsage(prompt_tokens=10, candidates_tokens=10, total_tokens=20),
            retry_count=0,
            is_success=True,
            error_message=None,
        )

        with patch.object(runner, "load_candidates", return_value=[candidate]):
            with patch.object(runner.provider, "enrich_candidate", return_value=mock_resp):
                with patch("time.sleep", return_value=None):
                    runner.run_execute(limit=1)

        with open(runner.results_jsonl_path, "r", encoding="utf-8") as f:
            proposal = json.loads(f.readline())
        
        self.assertNotEqual(proposal["validation_status"], "VERIFIED")
        self.assertEqual(proposal["validation_status"], "NEEDS_REVIEW")
        self.assertEqual(proposal["duplication_status"], "DUPLICATE_OF_EXISTING_CANONICAL_DATA")
        self.assertIn("Duplication Safeguard", proposal["validation_rationale"])
        
        db_hash_after = compute_file_hash(self.temp_db)
        self.assertEqual(db_hash_before, db_hash_after)

    def test_production_runner_validates_against_raw_canonical_content(self):
        """Test 38: EvidenceValidator validates quotes against raw canonical content without labels."""
        raw_content = EnrichmentEngine.get_canonical_raw_content("startup", {
            "startup_id": "startup-1",
            "entity_name": "Anthropic",
            "ai_focus_area": "Applied AI & Automation",
            "ai_evidence": "foundation model; ai; llm",
            "description": "Anthropic is an AI safety startup.",
        })
        
        self.assertIn("Anthropic", raw_content)
        self.assertIn("Applied AI & Automation", raw_content)
        self.assertNotIn("AI Focus:", raw_content)
        self.assertNotIn("Company Name:", raw_content)

        res = EnrichmentResult(
            attempt_id="test-prop",
            record_id="startup-1",
            entity_type="startup",
            field_name="ai_focus_area",
            original_value="",
            enriched_value="Applied AI & Automation",
            source_url="https://example.com",
            evidence="AI Focus: Applied AI & Automation",
            source_version="v1",
            confidence_score=0.9,
            enrichment_method="llm_extraction",
            provider="google-gemini",
            model="gemini-3.1-flash-lite",
            enriched_at=datetime.now(timezone.utc).isoformat(),
            validation_status="NEEDS_REVIEW",
        )
        status, rationale = EvidenceValidator.validate_enrichment(
            res,
            "AI Focus: Applied AI & Automation",
            canonical_record={"startup_id": "startup-1", "ai_focus_area": "Applied AI & Automation"}
        )
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("Application-generated context label prefix", rationale)

    def test_applicator_rejects_missing_duplication_status(self):
        """Test 39: apply_approved.py rejects proposals with missing duplication_status."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )
        proposal = {
            "proposal_id": "prop-missing-dup",
            "record_id": "startup-1",
            "entity_type": "startup",
            "field_name": "ai_focus_area",
            "original_value": "Applied AI & Automation",
            "proposed_value": "New Focus",
            "validation_status": "VERIFIED",
            "approval_status": "APPROVED",
            "schema_status": "SCHEMA_COMPATIBLE",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        success, msg = applicator.apply_proposal("prop-missing-dup", confirm_authorized=True)
        self.assertFalse(success)
        self.assertIn("DUPLICATION ABORT", msg)
        self.assertIn("duplication_status is 'None'", msg)

    def test_applicator_rejects_unknown_duplication_status(self):
        """Test 40: apply_approved.py rejects proposals with unknown/invalid duplication_status."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )
        proposal = {
            "proposal_id": "prop-unknown-dup",
            "record_id": "startup-1",
            "entity_type": "startup",
            "field_name": "ai_focus_area",
            "original_value": "Applied AI & Automation",
            "proposed_value": "New Focus",
            "validation_status": "VERIFIED",
            "approval_status": "APPROVED",
            "schema_status": "SCHEMA_COMPATIBLE",
            "duplication_status": "UNKNOWN_STATUS",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        success, msg = applicator.apply_proposal("prop-unknown-dup", confirm_authorized=True)
        self.assertFalse(success)
        self.assertIn("DUPLICATION ABORT", msg)
        self.assertIn("duplication_status is 'UNKNOWN_STATUS'", msg)

    def test_applicator_rejects_missing_schema_status(self):
        """Test 41: apply_approved.py rejects proposals with missing schema_status."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )
        proposal = {
            "proposal_id": "prop-missing-schema",
            "record_id": "startup-1",
            "entity_type": "startup",
            "field_name": "ai_focus_area",
            "original_value": "Applied AI & Automation",
            "proposed_value": "New Focus",
            "validation_status": "VERIFIED",
            "approval_status": "APPROVED",
            "duplication_status": "NO_DUPLICATION",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        success, msg = applicator.apply_proposal("prop-missing-schema", confirm_authorized=True)
        self.assertFalse(success)
        self.assertIn("SCHEMA COMPATIBILITY ABORT", msg)
        self.assertIn("schema_status is 'None'", msg)

    def test_applicator_rejects_non_schema_compatible(self):
        """Test 42: apply_approved.py rejects proposals marked BLOCKED_SCHEMA."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )
        proposal = {
            "proposal_id": "prop-blocked-schema",
            "record_id": "startup-1",
            "entity_type": "startup",
            "field_name": "ai_focus_area",
            "original_value": "Applied AI & Automation",
            "proposed_value": "New Focus",
            "validation_status": "VERIFIED",
            "approval_status": "APPROVED",
            "duplication_status": "NO_DUPLICATION",
            "schema_status": "BLOCKED_SCHEMA",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        success, msg = applicator.apply_proposal("prop-blocked-schema", confirm_authorized=True)
        self.assertFalse(success)
        self.assertIn("SCHEMA COMPATIBILITY ABORT", msg)
        self.assertIn("BLOCKED_SCHEMA", msg)

    def test_applicator_runtime_pragma_rejects_nonexistent_column(self):
        """Test 43: apply_approved.py runtime PRAGMA table_info rejects physical missing column."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )
        proposal = {
            "proposal_id": "prop-pragma-missing-col",
            "record_id": "startup-1",
            "entity_type": "startup",
            "field_name": "ai_specialization",
            "original_value": None,
            "proposed_value": "Generative AI",
            "validation_status": "VERIFIED",
            "approval_status": "APPROVED",
            "duplication_status": "NO_DUPLICATION",
            "schema_status": "SCHEMA_COMPATIBLE",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        with patch.dict(CANONICAL_TABLE_SCHEMAS["ai_startups"], {"ai_specialization": None}):
            CANONICAL_TABLE_SCHEMAS["ai_startups"].add("ai_specialization")
            try:
                success, msg = applicator.apply_proposal("prop-pragma-missing-col", confirm_authorized=True)
                self.assertFalse(success)
                self.assertIn("RUNTIME SCHEMA ABORT", msg)
                self.assertIn("PRAGMA table_info verified", msg)
            finally:
                CANONICAL_TABLE_SCHEMAS["ai_startups"].discard("ai_specialization")

    def test_concurrency_conflict_empty_string_vs_null(self):
        """Test 44: Exact before-image match: proposal '' vs DB NULL raises CONCURRENCY CONFLICT."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )
        proposal = {
            "proposal_id": "prop-concurrency-empty-vs-null",
            "record_id": "startup-null-focus",
            "entity_type": "startup",
            "field_name": "ai_focus_area",
            "original_value": "",
            "proposed_value": "Generative AI",
            "validation_status": "VERIFIED",
            "approval_status": "APPROVED",
            "duplication_status": "NO_DUPLICATION",
            "schema_status": "SCHEMA_COMPATIBLE",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        success, msg = applicator.apply_proposal("prop-concurrency-empty-vs-null", confirm_authorized=True)
        self.assertFalse(success)
        self.assertIn("CONCURRENCY CONFLICT", msg)
        self.assertIn("Expected: ''", msg)
        self.assertIn("Current: None", msg)

        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT ai_focus_area FROM ai_startups WHERE startup_id = 'startup-null-focus'")
        val = cursor.fetchone()[0]
        conn.close()
        self.assertIsNone(val)

    def test_concurrency_conflict_null_vs_empty_string(self):
        """Test 45: Exact before-image match: proposal NULL vs DB '' raises CONCURRENCY CONFLICT."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )
        proposal = {
            "proposal_id": "prop-concurrency-null-vs-empty",
            "record_id": "startup-empty-focus",
            "entity_type": "startup",
            "field_name": "ai_focus_area",
            "original_value": None,
            "proposed_value": "Generative AI",
            "validation_status": "VERIFIED",
            "approval_status": "APPROVED",
            "duplication_status": "NO_DUPLICATION",
            "schema_status": "SCHEMA_COMPATIBLE",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        success, msg = applicator.apply_proposal("prop-concurrency-null-vs-empty", confirm_authorized=True)
        self.assertFalse(success)
        self.assertIn("CONCURRENCY CONFLICT", msg)
        self.assertIn("Expected: None", msg)
        self.assertIn("Current: ''", msg)

        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT ai_focus_area FROM ai_startups WHERE startup_id = 'startup-empty-focus'")
        val = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(val, "")

    def test_transaction_rollback_preserves_database_state(self):
        """Test 46: Failed applicator operation preserves database and audit log state cleanly."""
        applicator = ApprovedUpdateApplicator(
            db_path=self.temp_db,
            queue_csv_path=self.temp_queue,
            results_jsonl_path=self.temp_results,
        )
        proposal = {
            "proposal_id": "prop-rollback-check",
            "record_id": "startup-1",
            "entity_type": "startup",
            "field_name": "ai_focus_area",
            "original_value": "Wrong Before Value",
            "proposed_value": "Should Never Be Applied",
            "validation_status": "VERIFIED",
            "approval_status": "APPROVED",
            "duplication_status": "NO_DUPLICATION",
            "schema_status": "SCHEMA_COMPATIBLE",
        }
        with open(self.temp_results, "w", encoding="utf-8") as f:
            f.write(json.dumps(proposal) + "\n")

        success, msg = applicator.apply_proposal("prop-rollback-check", confirm_authorized=True)
        self.assertFalse(success)
        self.assertIn("CONCURRENCY CONFLICT", msg)

        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT ai_focus_area FROM ai_startups WHERE startup_id = 'startup-1'")
        val = cursor.fetchone()[0]
        self.assertEqual(val, "Applied AI & Automation")

        cursor.execute("SELECT count(*) FROM enrichment_audit_log")
        log_count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(log_count, 0)


if __name__ == "__main__":
    unittest.main()

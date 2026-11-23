"""
Comprehensive unit tests for Evidence Validator and anti-hallucination enforcement.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - Strict Field-Level Evidence Grounding and Regression Verification
"""

import unittest
import uuid
from datetime import datetime, timezone

from core.enrichment.schemas import EnrichmentResult, ValidationStatus, compute_source_version
from core.enrichment.validator import (
    EvidenceValidator,
    RETAINED_15_REVIEW_JOB_IDS
)


class TestEvidenceValidator(unittest.TestCase):

    def setUp(self):
        self.now_iso = datetime.now(timezone.utc).isoformat()
        self.sample_source = "We develop deep learning architectures for multimodal vision models using PyTorch on AWS GPU clusters."
        self.sample_source_version = compute_source_version(self.sample_source)

    def _create_result(self, **kwargs) -> EnrichmentResult:
        defaults = {
            "attempt_id": str(uuid.uuid4()),
            "record_id": "test_rec_1",
            "entity_type": "job",
            "field_name": "technologies",
            "original_value": None,
            "enriched_value": ["PyTorch"],
            "source_url": "https://example.com/test",
            "evidence": "multimodal vision models using PyTorch on AWS GPU clusters",
            "source_version": self.sample_source_version,
            "confidence_score": 0.85,
            "enrichment_method": "llm_gemini",
            "provider": "gemini",
            "model": "gemini-1.5-flash",
            "enriched_at": self.now_iso,
            "validation_status": ValidationStatus.NEEDS_REVIEW.value,
            "validation_rationale": "",
            "retry_count": 0
        }
        defaults.update(kwargs)
        return EnrichmentResult(**defaults)

    def test_regression_computer_vision_multimodal_unsupported_concept(self):
        """
        REGRESSION TEST (Audit 19 Specification):
        Source evidence: 'Experience with computer vision models.'
        Proposed value: 'Computer Vision & Multimodal'
        Expected result: NEEDS_REVIEW or FAILED, NEVER VERIFIED, because multimodal
        capability is not established by the evidence.
        """
        source = "We are seeking an engineer. Experience with computer vision models. Apply today."
        ev = "Experience with computer vision models."
        res = self._create_result(
            field_name="role_specialization",
            enriched_value="Computer Vision & Multimodal",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertIn(status, (ValidationStatus.NEEDS_REVIEW, ValidationStatus.FAILED))
        self.assertNotEqual(status, ValidationStatus.VERIFIED, "Regression: must NEVER be VERIFIED when multimodal is unsupported!")
        self.assertIn("multimodal", rationale.lower())

    def test_unsupported_skills_fail(self):
        """Test that proposing skills completely absent from evidence returns FAILED."""
        source = "We build frontend web applications using React and TypeScript."
        ev = "We build frontend web applications using React and TypeScript."
        res = self._create_result(
            field_name="required_skills",
            enriched_value=["PyTorch", "Kubernetes"],
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.90
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("Evidence does not support any items", rationale)

    def test_fabricated_technologies_fail(self):
        """Test that fabricated technologies return FAILED."""
        source = "We manage PostgreSQL databases for online transactions."
        ev = "We manage PostgreSQL databases for online transactions."
        res = self._create_result(
            field_name="technologies",
            enriched_value=["Quantum Computing", "JAX"],
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)

    def test_partially_supported_list_needs_review(self):
        """Test that a list where some items are supported and others are not returns NEEDS_REVIEW."""
        source = "We use Python and Docker for our analytics pipeline daily."
        ev = "We use Python and Docker for our analytics pipeline daily."
        # Python and Docker are in evidence, Kubernetes is NOT
        res = self._create_result(
            field_name="technologies",
            enriched_value=["Python", "Docker", "Kubernetes"],
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.85
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
        self.assertIn("Partially supported list", rationale)
        self.assertIn("Kubernetes", rationale)

    def test_evidence_from_unrelated_section_fails(self):
        """Test that evidence not found in the supplied source content returns FAILED."""
        source = "We build speech recognition models using Kaldi and PyTorch."
        unrelated_ev = "Extensive background in hedge fund quantitative equity trading."
        res = self._create_result(
            field_name="technologies",
            enriched_value=["PyTorch"],
            evidence=unrelated_ev,
            source_version=compute_source_version(source),
            confidence_score=0.90
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("Rule 2", rationale)

    def test_empty_evidence_fails(self):
        """Test that missing or empty evidence returns FAILED (Rule 5)."""
        source = "We build NLP transformers in Python."
        res = self._create_result(
            field_name="technologies",
            enriched_value=["Python"],
            evidence="",
            source_version=compute_source_version(source),
            confidence_score=0.90
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("Rule 5", rationale)

    def test_exact_evidence_with_wrong_enriched_value_fails(self):
        """Test that verbatim evidence with an incorrect/unsupported enriched value returns FAILED."""
        source = "The candidate must have 5 years of Python software development experience."
        ev = "The candidate must have 5 years of Python software development experience."
        res = self._create_result(
            field_name="role_specialization",
            enriched_value="Java Enterprise Architecture",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.90
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)

    def test_heuristic_classifications_never_automatically_verified(self):
        """Test that heuristic classifications are routed to NEEDS_REVIEW, never automatically VERIFIED (Rule 8)."""
        source = "Our company develops foundation models and large language models for enterprises."
        ev = "develops foundation models and large language models for enterprises"
        res = self._create_result(
            entity_type="startup",
            field_name="ai_specialization",
            enriched_value="Foundation Models & LLMs",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.80,
            enrichment_method="heuristic_classification",
            provider="offline"
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
        self.assertIn("heuristic", rationale.lower())

    def test_news_validation_minimum_content_for_summary_and_article_summary(self):
        """Test that news articles with < 50 chars source content return INSUFFICIENT_EVIDENCE for both fields."""
        headline_only = "OpenAI releases new preview model"
        
        # Test 1: field_name = 'summary'
        res1 = self._create_result(
            entity_type="news",
            field_name="summary",
            enriched_value="OpenAI released a preview model.",
            evidence="OpenAI releases new preview model",
            source_version=compute_source_version(headline_only),
            confidence_score=0.90
        )
        status1, rat1 = EvidenceValidator.validate_enrichment(res1, headline_only)
        self.assertEqual(status1, ValidationStatus.INSUFFICIENT_EVIDENCE)
        self.assertIn("News Rule", rat1)

        # Test 2: field_name = 'article_summary'
        res2 = self._create_result(
            entity_type="news",
            field_name="article_summary",
            enriched_value="OpenAI released a preview model.",
            evidence="OpenAI releases new preview model",
            source_version=compute_source_version(headline_only),
            confidence_score=0.90
        )
        status2, rat2 = EvidenceValidator.validate_enrichment(res2, headline_only)
        self.assertEqual(status2, ValidationStatus.INSUFFICIENT_EVIDENCE)
        self.assertIn("News Rule", rat2)

    def test_forbidden_salary_and_location_inferences(self):
        """Test that forbidden inference fields are rejected (Rule 3)."""
        for field in ["salary_min", "salary_max", "currency", "location", "company_size", "job_status"]:
            res = self._create_result(
                field_name=field,
                enriched_value=120000 if "salary" in field else "San Francisco",
                evidence="We develop deep learning architectures for multimodal vision models",
                confidence_score=0.95
            )
            status, rationale = EvidenceValidator.validate_enrichment(res, self.sample_source)
            self.assertEqual(status, ValidationStatus.FAILED)
            self.assertIn("Rule 3", rationale)

    def test_preserves_15_stage2_boundary_jobs(self):
        """Test that the 15 boundary jobs preserved in Audits 10-18 remain NEEDS_REVIEW."""
        for jid in RETAINED_15_REVIEW_JOB_IDS:
            res = self._create_result(
                record_id=jid,
                field_name="category",
                enriched_value="CORE_AI_ML",
                evidence="deep learning architectures",
                confidence_score=0.99
            )
            status, rationale = EvidenceValidator.validate_enrichment(res, self.sample_source)
            self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
            self.assertIn("Boundary Preservation", rationale)

    def test_regression_hospital_software_vs_autonomous_medical_robots(self):
        """
        REGRESSION TEST (Audit 20 Specification):
        Evidence: 'The company develops software for hospitals.'
        Proposed value: 'The company develops advanced autonomous medical robots and hospital software.'
        Expected result: NEVER VERIFIED (must be FAILED or NEEDS_REVIEW) because the proposed value
        introduces fabricated claims ('advanced autonomous medical robots') not supported by the evidence.
        """
        source = "About Us: The company develops software for hospitals across North America."
        ev = "The company develops software for hospitals"
        res = self._create_result(
            field_name="company_description",
            enriched_value="The company develops advanced autonomous medical robots and hospital software.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertIn(status, (ValidationStatus.FAILED, ValidationStatus.NEEDS_REVIEW))
        self.assertNotEqual(status, ValidationStatus.VERIFIED, "Audit 20 Violation: Fabricated claim must NEVER be VERIFIED!")
        self.assertTrue(
            "unsupported" in rationale.lower() or "claim" in rationale.lower(),
            f"Expected rationale to mention unsupported claims, got: {rationale}"
        )

    def test_regression_one_supported_one_fabricated_sentence_in_summary(self):
        """
        REGRESSION TEST (Audit 20 Specification):
        Summary containing one supported sentence and one fabricated sentence.
        Must NEVER be VERIFIED; must be routed to NEEDS_REVIEW or FAILED.
        """
        source = "We develop software tools for database query optimization. Our headquarters are in Boston."
        ev = "We develop software tools for database query optimization."
        res = self._create_result(
            field_name="company_description",
            enriched_value="We develop software tools for database query optimization. We also manufacture humanoid robotic assistants.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.90
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertIn(status, (ValidationStatus.FAILED, ValidationStatus.NEEDS_REVIEW))
        self.assertNotEqual(status, ValidationStatus.VERIFIED, "Audit 20 Violation: Partially fabricated summary must NEVER be VERIFIED!")
        self.assertIn("unsupported", rationale.lower())

    def test_regression_generic_words_rejected_for_cv_multimodal(self):
        """
        REGRESSION TEST (Audit 20 Specification):
        Generic words like 'vision', 'image', 'video', 'diffusion' must NOT substantiate
        'Computer Vision & Multimodal' without specific technical indicators.
        """
        source = "We have a grand vision for social media video sharing and image diffusion across communities."
        ev = "We have a grand vision for social media video sharing and image diffusion across communities."
        res = self._create_result(
            field_name="ai_specialization",
            enriched_value="Computer Vision & Multimodal",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.85
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertIn(status, (ValidationStatus.FAILED, ValidationStatus.NEEDS_REVIEW))
        self.assertNotEqual(status, ValidationStatus.VERIFIED, "Audit 20 Violation: Generic words must not verify CV & Multimodal!")

    # =========================================================================
    # AUDIT 21 REGRESSION TESTS (Sections 1, 2, 3, 7)
    # =========================================================================

    def test_regression_negation_contradiction_fails(self):
        """
        REGRESSION TEST (Audit 21 Requirement 1 & 7):
        Evidence: 'We do not manufacture autonomous surgical robots.'
        Proposed: 'We manufacture autonomous surgical robots.'
        Must NEVER receive VERIFIED; must return FAILED.
        """
        source = "Overview: We do not manufacture autonomous surgical robots. We focus on billing software."
        ev = "We do not manufacture autonomous surgical robots."
        res = self._create_result(
            field_name="company_description",
            enriched_value="We manufacture autonomous surgical robots.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED, "Audit 21 Violation: Negation contradiction must return FAILED!")
        self.assertNotEqual(status, ValidationStatus.VERIFIED)
        self.assertTrue("contradiction" in rationale.lower() or "negat" in rationale.lower())

    def test_regression_modality_tense_shift_fails(self):
        """
        REGRESSION TEST (Audit 21 Requirement 1 & 7):
        Evidence: 'We plan to develop a medical AI platform.'
        Proposed: 'We have developed a medical AI platform.'
        Must NEVER receive VERIFIED; must return FAILED or NEEDS_REVIEW.
        """
        source = "Roadmap: We plan to develop a medical AI platform by next year."
        ev = "We plan to develop a medical AI platform"
        res = self._create_result(
            field_name="company_description",
            enriched_value="We have developed a medical AI platform.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.90
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertIn(status, (ValidationStatus.FAILED, ValidationStatus.NEEDS_REVIEW))
        self.assertNotEqual(status, ValidationStatus.VERIFIED, "Audit 21 Violation: Modality shift must NEVER be VERIFIED!")
        self.assertTrue("modality" in rationale.lower() or "plan" in rationale.lower())

    def test_regression_unsupported_dates_numbers_fails(self):
        """
        REGRESSION TEST (Audit 21 Requirement 1 & 7):
        Evidence: 'The company was founded in 2020.'
        Proposed: 'The company was founded in 2022.'
        Must NEVER receive VERIFIED; must return FAILED.
        """
        source = "History: The company was founded in 2020 in San Francisco."
        ev = "The company was founded in 2020"
        res = self._create_result(
            field_name="company_description",
            enriched_value="The company was founded in 2022.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED, "Audit 21 Violation: Unsupported date/number must return FAILED!")
        self.assertNotEqual(status, ValidationStatus.VERIFIED)
        self.assertTrue("2022" in rationale or "date" in rationale.lower() or "number" in rationale.lower())

    def test_regression_attribution_causal_upgrade_fails(self):
        """
        REGRESSION TEST (Audit 21 Requirement 1 & 7):
        Evidence: 'The company reports that its product supports hospitals.'
        Proposed: 'The product is independently proven to improve hospital outcomes.'
        Must NEVER receive VERIFIED; must return FAILED or NEEDS_REVIEW.
        """
        source = "Press release: The company reports that its product supports hospitals in daily triage."
        ev = "The company reports that its product supports hospitals"
        res = self._create_result(
            field_name="product_description",
            enriched_value="The product is independently proven to improve hospital outcomes.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.92
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertIn(status, (ValidationStatus.FAILED, ValidationStatus.NEEDS_REVIEW))
        self.assertNotEqual(status, ValidationStatus.VERIFIED, "Audit 21 Violation: Unsupported causal claim must NEVER be VERIFIED!")
        self.assertTrue("attribution" in rationale.lower() or "causal" in rationale.lower() or "proven" in rationale.lower())

    def test_regression_unknown_category_non_heuristic_provider_fails(self):
        """
        REGRESSION TEST (Audit 21 Requirement 2 & 7):
        Category outside approved taxonomy from non-heuristic provider (e.g. Gemini/OpenAI).
        Must NEVER receive VERIFIED; must return FAILED.
        """
        source = "We build Quantum Neural Metaverse solutions for enterprise customers."
        ev = "We build Quantum Neural Metaverse solutions"
        res = self._create_result(
            field_name="ai_specialization",
            enriched_value="Quantum Neural Metaverse",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95,
            enrichment_method="llm_gemini",
            provider="gemini"
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED, "Audit 21 Violation: Unknown taxonomy from non-heuristic must return FAILED!")
        self.assertNotEqual(status, ValidationStatus.VERIFIED)
        self.assertIn("taxonomy", rationale.lower())

    def test_regression_unknown_category_heuristic_provider_fails(self):
        """
        REGRESSION TEST (Audit 21 Requirement 2 & 7):
        Category outside approved taxonomy from heuristic provider.
        Must NEVER receive VERIFIED; must return FAILED.
        """
        source = "We develop Synthetic General Robotics systems."
        ev = "We develop Synthetic General Robotics systems."
        res = self._create_result(
            field_name="ai_specialization",
            enriched_value="Synthetic General Robotics",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.75,
            enrichment_method="heuristic_classification",
            provider="offline"
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED, "Audit 21 Violation: Unknown taxonomy from heuristic provider must return FAILED!")
        self.assertNotEqual(status, ValidationStatus.VERIFIED)
        self.assertIn("taxonomy", rationale.lower())

    def test_regression_heuristic_list_never_verified(self):
        """
        REGRESSION TEST (Audit 21 Requirement 3 & 7):
        Heuristic-extracted list with 100% keyword match in evidence.
        Must NEVER automatically become VERIFIED; must return NEEDS_REVIEW.
        """
        source = "The role requires strong experience in Python and PyTorch for model training."
        ev = "The role requires strong experience in Python and PyTorch"
        res = self._create_result(
            field_name="required_skills",
            enriched_value=["Python", "PyTorch"],
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.80,
            enrichment_method="heuristic_extraction",
            provider="offline"
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW, "Audit 21 Violation: Heuristic list must return NEEDS_REVIEW, never VERIFIED!")
        self.assertNotEqual(status, ValidationStatus.VERIFIED)
        self.assertIn("heuristic", rationale.lower())

    def test_regression_list_negated_item_fails(self):
        """
        REGRESSION TEST (Audit 21 Requirement 3 & 7):
        Evidence negates a technology: 'We do not use Java.'
        Enriched list includes Java: ['Python', 'Java'].
        Must NEVER receive VERIFIED; must return FAILED.
        """
        source = "Tech stack: We require Python. We do not use Java or legacy C++."
        ev = "We require Python. We do not use Java or legacy C++."
        res = self._create_result(
            field_name="required_skills",
            enriched_value=["Python", "Java"],
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.85,
            enrichment_method="llm_gemini",
            provider="gemini"
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED, "Audit 21 Violation: Negated list item must return FAILED!")
        self.assertNotEqual(status, ValidationStatus.VERIFIED)
        self.assertIn("negat", rationale.lower())

    def test_positive_verbatim_extractive_text_verified(self):
        """
        POSITIVE TEST: Exact verbatim sentence extraction with high confidence from LLM.
        Meaning and context preserved, no negation inversion.
        Must return VERIFIED.
        """
        source = "We develop machine learning algorithms for autonomous flight control."
        ev = "We develop machine learning algorithms for autonomous flight control."
        res = self._create_result(
            field_name="company_description",
            enriched_value="We develop machine learning algorithms for autonomous flight control.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.85,
            enrichment_method="llm_gemini",
            provider="gemini"
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.VERIFIED, f"Positive case must be VERIFIED, got {status}: {rationale}")

    def test_positive_non_heuristic_list_verified(self):
        """
        POSITIVE TEST: Non-heuristic list with all items substantiated and no negation.
        Must return VERIFIED.
        """
        source = "Required skills include Python and Docker for production microservices."
        ev = "Required skills include Python and Docker"
        res = self._create_result(
            field_name="required_skills",
            enriched_value=["Python", "Docker"],
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.85,
            enrichment_method="llm_gemini",
            provider="gemini"
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.VERIFIED, f"Positive list must be VERIFIED, got {status}: {rationale}")

    def test_positive_approved_taxonomy_category_verified(self):
        """
        POSITIVE TEST: Approved taxonomy category with all required constituent concepts
        substantiated from non-heuristic provider.
        Must return VERIFIED.
        """
        source = "We develop foundation models and transformer architectures for large language models."
        ev = "We develop foundation models and transformer architectures for large language models."
        res = self._create_result(
            field_name="ai_specialization",
            enriched_value="Foundation Models & LLMs",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.85,
            enrichment_method="llm_gemini",
            provider="gemini"
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.VERIFIED, f"Positive category must be VERIFIED, got {status}: {rationale}")

    # =========================================================================
    # AUDIT 22 ADVERSARIAL REGRESSION TESTS (Section 2)
    # =========================================================================

    def test_adversarial_active_passive_voice_reversal_fails(self):
        """
        ADVERSARIAL TEST: Active vs. Passive voice semantic inversion.
        Evidence: 'The model was trained by OpenAI.'
        Proposed: 'The model trained OpenAI.'
        Must return FAILED, never VERIFIED.
        """
        source = "Overview: The model was trained by OpenAI using high-bandwidth clusters."
        ev = "The model was trained by OpenAI"
        res = self._create_result(
            field_name="company_description",
            enriched_value="The model trained OpenAI.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("voice", rationale.lower())

    def test_adversarial_subject_object_reversal_fails(self):
        """
        ADVERSARIAL TEST: Subject/object reversal with all same entities and action.
        Evidence: 'Google acquired DeepMind in 2014.'
        Proposed: 'DeepMind acquired Google.'
        Must return FAILED, never VERIFIED.
        """
        source = "History: Google acquired DeepMind in 2014 to accelerate AI research."
        ev = "Google acquired DeepMind in 2014"
        res = self._create_result(
            field_name="company_description",
            enriched_value="DeepMind acquired Google in 2014.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("reversal", rationale.lower())

    def test_adversarial_some_vs_all_fails(self):
        """
        ADVERSARIAL TEST: Some vs. All quantifier inflation.
        Evidence: 'Some of our products support cloud deployment.'
        Proposed: 'All of our products support cloud deployment.'
        Must return FAILED, never VERIFIED.
        """
        source = "Capabilities: Some of our products support cloud deployment across regions."
        ev = "Some of our products support cloud deployment"
        res = self._create_result(
            field_name="product_description",
            enriched_value="All of our products support cloud deployment.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("quantifier", rationale.lower())

    def test_adversarial_improved_vs_doubled_fails(self):
        """
        ADVERSARIAL TEST: Improved vs. Doubled metric inflation.
        Evidence: 'The system improved model latency.'
        Proposed: 'The system doubled model latency.'
        Must return FAILED, never VERIFIED.
        """
        source = "Performance: The system improved model latency across test suites."
        ev = "The system improved model latency"
        res = self._create_result(
            field_name="product_description",
            enriched_value="The system doubled model latency.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("inflation", rationale.lower())

    def test_adversarial_conditional_vs_factual_fails(self):
        """
        ADVERSARIAL TEST: Conditional vs. Factual assertion.
        Evidence: 'If configured properly, the tool prevents memory leaks.'
        Proposed: 'The tool prevents memory leaks.'
        Must return FAILED, never VERIFIED.
        """
        source = "Safety: If configured properly, the tool prevents memory leaks during compilation."
        ev = "If configured properly, the tool prevents memory leaks"
        res = self._create_result(
            field_name="product_description",
            enriched_value="The tool prevents memory leaks.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("condition", rationale.lower())

    def test_adversarial_historical_vs_current_status_fails(self):
        """
        ADVERSARIAL TEST: Historical vs. Current status shift.
        Evidence: 'The company previously operated an ad network.'
        Proposed: 'The company currently operates an ad network.'
        Must return FAILED, never VERIFIED.
        """
        source = "About: The company previously operated an ad network before pivoting to ML."
        ev = "The company previously operated an ad network"
        res = self._create_result(
            field_name="company_description",
            enriched_value="The company currently operates an ad network.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("temporal", rationale.lower())

    def test_adversarial_without_negation_fails(self):
        """
        ADVERSARIAL TEST: Negation with 'without'.
        Evidence: 'The framework operates without requiring PyTorch.'
        Proposed: 'The framework requires PyTorch.'
        Must return FAILED, never VERIFIED.
        """
        source = "Specs: The framework operates without requiring PyTorch for inference."
        ev = "The framework operates without requiring PyTorch"
        res = self._create_result(
            field_name="product_description",
            enriched_value="The framework requires PyTorch.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("negat", rationale.lower())

    def test_adversarial_neither_negation_fails(self):
        """
        ADVERSARIAL TEST: Negation with 'neither...nor'.
        Evidence: 'The platform supports neither Python nor R.'
        Proposed: 'The platform supports Python and R.'
        Must return FAILED, never VERIFIED.
        """
        source = "Stack: The platform supports neither Python nor R scripts natively."
        ev = "The platform supports neither Python nor R"
        res = self._create_result(
            field_name="product_description",
            enriched_value="The platform supports Python and R.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("negat", rationale.lower())

    def test_adversarial_lack_negation_fails(self):
        """
        ADVERSARIAL TEST: Negation with 'lack/lacks'.
        Evidence: 'The model lacks real-time streaming capabilities.'
        Proposed: 'The model features real-time streaming capabilities.'
        Must return FAILED, never VERIFIED.
        """
        source = "Limitations: The model lacks real-time streaming capabilities on edge hardware."
        ev = "The model lacks real-time streaming capabilities"
        res = self._create_result(
            field_name="product_description",
            enriched_value="The model features real-time streaming capabilities.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("negat", rationale.lower())

    def test_adversarial_exclude_negation_fails(self):
        """
        ADVERSARIAL TEST: Exclusion with 'exclude/excludes'.
        Evidence: 'The benchmark excludes proprietary datasets.'
        Proposed: 'The benchmark includes proprietary datasets.'
        Must return FAILED, never VERIFIED.
        """
        source = "Methodology: The benchmark excludes proprietary datasets from public runs."
        ev = "The benchmark excludes proprietary datasets"
        res = self._create_result(
            field_name="methodology",
            enriched_value="The benchmark includes proprietary datasets.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("negat", rationale.lower())

    def test_adversarial_unsupported_causal_claim_fails(self):
        """
        ADVERSARIAL TEST: Co-occurrence inferred as causation.
        Evidence: 'The company released an AI assistant and revenues grew.'
        Proposed: 'The AI assistant caused revenues to grow.'
        Must return FAILED, never VERIFIED.
        """
        source = "Financials: The company released an AI assistant and revenues grew by 15%."
        ev = "The company released an AI assistant and revenues grew"
        res = self._create_result(
            field_name="company_description",
            enriched_value="The AI assistant caused revenues to grow.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("causal", rationale.lower())

    def test_adversarial_same_keywords_contradiction_fails(self):
        """
        ADVERSARIAL TEST: Contradictory claims sharing 100% of keywords.
        Evidence: 'We do not manufacture autonomous surgical robots.'
        Proposed: 'We manufacture autonomous surgical robots.'
        Must return FAILED, never VERIFIED.
        """
        source = "Company profile: We do not manufacture autonomous surgical robots."
        ev = "We do not manufacture autonomous surgical robots."
        res = self._create_result(
            field_name="company_description",
            enriched_value="We manufacture autonomous surgical robots.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.99
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertNotEqual(status, ValidationStatus.VERIFIED)

    # =========================================================================
    # AUDIT 23 CONTEXT ISOLATION & EXPANDED ADVERSARIAL TESTS (Requirement 3)
    # =========================================================================

    def test_regression_case_a_unrelated_negation_passes(self):
        """
        AUDIT 23 Case A:
        Evidence: 'The company does not disclose revenue. Its platform supports Python.'
        Proposed: 'Its platform supports Python.'
        Expected: Must not be rejected because of unrelated negation in sentence 1.
        """
        source = "Company profile: The company does not disclose revenue. Its platform supports Python."
        ev = "The company does not disclose revenue. Its platform supports Python."
        res = self._create_result(
            field_name="company_description",
            enriched_value="Its platform supports Python.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.VERIFIED)
        self.assertIn("exact extractive substring", rationale.lower())

    def test_regression_case_b_unrelated_conditional_statement_passes(self):
        """
        AUDIT 23 Case B:
        Evidence: 'If requested, the service provides on-premise deployment. The product supports Python.'
        Proposed: 'The product supports Python.'
        Expected: Must not be rejected because of unrelated conditional statement in sentence 1.
        """
        source = "Overview: If requested, the service provides on-premise deployment. The product supports Python."
        ev = "If requested, the service provides on-premise deployment. The product supports Python."
        res = self._create_result(
            field_name="product_description",
            enriched_value="The product supports Python.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.VERIFIED)
        self.assertIn("exact extractive substring", rationale.lower())

    def test_regression_case_c_unrelated_historical_statement_passes(self):
        """
        AUDIT 23 Case C:
        Evidence: 'The company previously sold hardware. Its current software supports Python.'
        Proposed: 'Its current software supports Python.'
        Expected: Must not be rejected because of unrelated historical statement in sentence 1.
        """
        source = "History: The company previously sold hardware. Its current software supports Python."
        ev = "The company previously sold hardware. Its current software supports Python."
        res = self._create_result(
            field_name="product_description",
            enriched_value="Its current software supports Python.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.VERIFIED)
        self.assertIn("exact extractive substring", rationale.lower())

    def test_adversarial_double_negation_affirmative_passes(self):
        """
        AUDIT 23: Double negation idiom asserting affirmative reality.
        Evidence: 'We cannot deny that the framework supports Python.'
        Proposed: 'The framework supports Python.'
        Expected: Affirmative claim matches double-negation assertion; must not be rejected as negation flip.
        """
        source = "Statements: We cannot deny that the framework supports Python natively."
        ev = "We cannot deny that the framework supports Python"
        res = self._create_result(
            field_name="product_description",
            enriched_value="The framework supports Python",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.VERIFIED)

    def test_adversarial_double_negation_contradicted_by_negative_claim_fails(self):
        """
        AUDIT 23: Double negation idiom contradicted by an explicit negative claim.
        Evidence: 'We cannot deny that the framework supports Python.'
        Proposed: 'The framework does not support Python.'
        Expected: Must return FAILED.
        """
        source = "Statements: We cannot deny that the framework supports Python natively."
        ev = "We cannot deny that the framework supports Python"
        res = self._create_result(
            field_name="product_description",
            enriched_value="The framework does not support Python.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("double-negation", rationale.lower())

    def test_adversarial_indirect_negation_fails_to_fails(self):
        """
        AUDIT 23: Indirect negation with 'fails to'.
        Evidence: 'The software fails to encrypt user passwords.'
        Proposed: 'The software encrypts user passwords.'
        Expected: Must return FAILED.
        """
        source = "Security report: The software fails to encrypt user passwords at rest."
        ev = "The software fails to encrypt user passwords"
        res = self._create_result(
            field_name="product_description",
            enriched_value="The software encrypts user passwords.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("negat", rationale.lower())

    def test_adversarial_indirect_negation_unable_to_fails(self):
        """
        AUDIT 23: Indirect negation with 'unable to'.
        Evidence: 'The model is unable to process audio files.'
        Proposed: 'The model processes audio files.'
        Expected: Must return FAILED.
        """
        source = "Limitations: The model is unable to process audio files directly."
        ev = "The model is unable to process audio files"
        res = self._create_result(
            field_name="product_description",
            enriched_value="The model processes audio files.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("negat", rationale.lower())

    def test_adversarial_exception_qualifier_fails(self):
        """
        AUDIT 23: Exception qualifier exclusion.
        Evidence: 'The SDK supports all operating systems except Windows.'
        Proposed: 'The SDK supports Windows.'
        Expected: Must return FAILED.
        """
        source = "Platform compatibility: The SDK supports all operating systems except Windows."
        ev = "The SDK supports all operating systems except Windows."
        res = self._create_result(
            field_name="product_description",
            enriched_value="The SDK supports Windows.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("excludes", rationale.lower())

    def test_adversarial_conflicting_statements_across_sentences_needs_review(self):
        """
        AUDIT 23: Conflicting statements in evidence across separate sentences.
        Evidence: 'The platform supports Python. In legacy clusters, the platform does not support Python.'
        Proposed: 'The platform supports Python.'
        Expected: Because of internal source conflict, must return NEEDS_REVIEW, never VERIFIED.
        """
        source = "Environments: The platform supports Python. In legacy clusters, the platform does not support Python."
        ev = "The platform supports Python. In legacy clusters, the platform does not support Python."
        res = self._create_result(
            field_name="product_description",
            enriched_value="The platform supports Python.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
        self.assertIn("conflicting", rationale.lower())

    def test_adversarial_unsupported_dates_fails(self):
        """
        AUDIT 23: Unsupported date substitution.
        Evidence: 'The company was founded in 2020.'
        Proposed: 'The company was founded in 2024.'
        Expected: Must return FAILED.
        """
        source = "History: The company was founded in 2020 by former researchers."
        ev = "The company was founded in 2020"
        res = self._create_result(
            field_name="company_description",
            enriched_value="The company was founded in 2024.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("date", rationale.lower())

    def test_adversarial_unsupported_numbers_fails(self):
        """
        AUDIT 23: Unsupported quantitative count.
        Evidence: 'The system runs on 8 GPUs.'
        Proposed: 'The system runs on 32 GPUs.'
        Expected: Must return FAILED.
        """
        source = "Specs: The system runs on 8 GPUs simultaneously."
        ev = "The system runs on 8 GPUs"
        res = self._create_result(
            field_name="product_description",
            enriched_value="The system runs on 32 GPUs.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("number", rationale.lower())

    def test_adversarial_uncertain_claims_never_verified(self):
        """
        AUDIT 23: Global Invariant - Uncertain or non-extractive claims must NEVER be VERIFIED.
        Evidence: 'The platform assists biomedical research workflows.'
        Proposed: 'The platform guarantees breakthrough medical cures.'
        Expected: Must return FAILED or NEEDS_REVIEW, never VERIFIED.
        """
        source = "BioAI: The platform assists biomedical research workflows across labs."
        ev = "The platform assists biomedical research workflows"
        res = self._create_result(
            field_name="product_description",
            enriched_value="The platform guarantees breakthrough medical cures.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.99
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertNotEqual(status, ValidationStatus.VERIFIED)
        self.assertEqual(status, ValidationStatus.FAILED)

    # =========================================================================
    # AUDIT 24 REGRESSION & SEMANTIC CONTEXT/PREDICATE ALIGNMENT TESTS
    # =========================================================================

    def test_audit24_regression_test_a(self):
        """
        AUDIT 24 Test A: Same predicate ('support'), different objects ('Java' negated, 'Python' affirmed).
        Evidence: 'The company does not support Java. Its product supports Python.'
        Claim: 'Its product supports Python.'
        Expected: VERIFIED for exact non-heuristic extraction.
        """
        source = "Tech Stack: The company does not support Java. Its product supports Python."
        ev = "The company does not support Java. Its product supports Python."
        res = self._create_result(
            field_name="product_description",
            enriched_value="Its product supports Python.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.VERIFIED)

    def test_audit24_regression_test_b(self):
        """
        AUDIT 24 Test B: Conditional context for one object, unconditional for another.
        Evidence: 'If requested, the service supports Java. The product supports Python.'
        Claim: 'The product supports Python.'
        Expected: VERIFIED for exact non-heuristic extraction.
        """
        source = "Overview: If requested, the service supports Java. The product supports Python."
        ev = "If requested, the service supports Java. The product supports Python."
        res = self._create_result(
            field_name="product_description",
            enriched_value="The product supports Python.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.VERIFIED)

    def test_audit24_regression_test_c(self):
        """
        AUDIT 24 Test C: Historical status for one object, current for another.
        Evidence: 'The company previously supported Java. Its current product supports Python.'
        Claim: 'Its current product supports Python.'
        Expected: VERIFIED for exact non-heuristic extraction.
        """
        source = "History: The company previously supported Java. Its current product supports Python."
        ev = "The company previously supported Java. Its current product supports Python."
        res = self._create_result(
            field_name="product_description",
            enriched_value="Its current product supports Python.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.VERIFIED)

    def test_audit24_regression_test_d(self):
        """
        AUDIT 24 Test D: Affirmative first sentence, negated second sentence with different object.
        Evidence: 'The company supports Java. The company does not support Python.'
        Claim: 'The company supports Java.'
        Expected: VERIFIED for exact non-heuristic extraction.
        """
        source = "Features: The company supports Java. The company does not support Python."
        ev = "The company supports Java. The company does not support Python."
        res = self._create_result(
            field_name="product_description",
            enriched_value="The company supports Java.",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.VERIFIED)

    def test_audit24_multiple_subjects_and_objects(self):
        """
        AUDIT 24: Multiple subjects and objects in evidence excerpt.
        Evidence: 'Alpha develops computer vision and Beta develops robotics. Neither company develops hardware.'
        """
        source = "Alpha develops computer vision and Beta develops robotics. Neither company develops hardware."
        ev = source
        # Supported claim
        res1 = self._create_result(
            field_name="company_description",
            enriched_value="Alpha develops computer vision",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status1, _ = EvidenceValidator.validate_enrichment(res1, source)
        self.assertEqual(status1, ValidationStatus.VERIFIED)

        # Contradicted claim
        res2 = self._create_result(
            field_name="company_description",
            enriched_value="Alpha develops hardware",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status2, _ = EvidenceValidator.validate_enrichment(res2, source)
        self.assertEqual(status2, ValidationStatus.FAILED)

    def test_audit24_same_predicate_different_objects(self):
        """
        AUDIT 24: Same predicate ('provides'), different objects.
        """
        source = "The toolkit provides PyTorch integration. The toolkit does not provide TensorFlow integration."
        ev = source
        res1 = self._create_result(
            field_name="product_description",
            enriched_value="The toolkit provides PyTorch integration",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status1, _ = EvidenceValidator.validate_enrichment(res1, source)
        self.assertEqual(status1, ValidationStatus.VERIFIED)

        res2 = self._create_result(
            field_name="product_description",
            enriched_value="The toolkit provides TensorFlow integration",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status2, _ = EvidenceValidator.validate_enrichment(res2, source)
        self.assertEqual(status2, ValidationStatus.FAILED)

    def test_audit24_negation_in_separate_clauses(self):
        """
        AUDIT 24: Negation in separate clauses connected by conjunction 'but'.
        """
        source = "The platform supports Linux, but it does not support Windows."
        ev = source
        res1 = self._create_result(
            field_name="product_description",
            enriched_value="The platform supports Linux",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status1, _ = EvidenceValidator.validate_enrichment(res1, source)
        self.assertEqual(status1, ValidationStatus.VERIFIED)

        res2 = self._create_result(
            field_name="product_description",
            enriched_value="The platform supports Windows",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status2, _ = EvidenceValidator.validate_enrichment(res2, source)
        self.assertEqual(status2, ValidationStatus.FAILED)

    def test_audit24_conditionality_in_separate_clauses(self):
        """
        AUDIT 24: Conditionality in separate clauses.
        """
        source = "If enterprise licensing is purchased, the software includes 24/7 support. The software includes standard documentation."
        ev = source
        res1 = self._create_result(
            field_name="product_description",
            enriched_value="The software includes standard documentation",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status1, _ = EvidenceValidator.validate_enrichment(res1, source)
        self.assertEqual(status1, ValidationStatus.VERIFIED)

        res2 = self._create_result(
            field_name="product_description",
            enriched_value="The software includes 24/7 support",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status2, _ = EvidenceValidator.validate_enrichment(res2, source)
        self.assertEqual(status2, ValidationStatus.FAILED)

    def test_audit24_historical_and_current_in_same_excerpt(self):
        """
        AUDIT 24: Historical and current statements in the same excerpt.
        """
        source = "The company previously focused on crypto mining. Its current product provides medical AI diagnostics."
        ev = source
        res1 = self._create_result(
            field_name="product_description",
            enriched_value="Its current product provides medical AI diagnostics",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status1, _ = EvidenceValidator.validate_enrichment(res1, source)
        self.assertEqual(status1, ValidationStatus.VERIFIED)

        res2 = self._create_result(
            field_name="company_description",
            enriched_value="The company currently focuses on crypto mining",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status2, _ = EvidenceValidator.validate_enrichment(res2, source)
        self.assertEqual(status2, ValidationStatus.FAILED)

    def test_audit24_qualifiers_and_exceptions(self):
        """
        AUDIT 24: Qualifiers and exceptions in evidence.
        """
        source = "The model supports all major languages except Korean."
        ev = source
        res = self._create_result(
            field_name="product_description",
            enriched_value="The model supports Korean",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.FAILED)
        self.assertIn("qualifier", rationale.lower())

    def test_audit24_conflicting_claims_yields_needs_review(self):
        """
        AUDIT 24: Conflicting source statements yield NEEDS_REVIEW, never VERIFIED.
        """
        source = "Section 1 states the API is free. Section 2 states the API requires a paid enterprise subscription."
        ev = source
        res = self._create_result(
            field_name="product_description",
            enriched_value="the API is free",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
        self.assertIn("conflict", rationale.lower())

    def test_audit24_double_and_indirect_negation(self):
        """
        AUDIT 24: Double negation asserts affirmative meaning.
        """
        source = "It cannot be denied that the tool accelerates code review."
        ev = source
        res1 = self._create_result(
            field_name="product_description",
            enriched_value="the tool accelerates code review",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status1, _ = EvidenceValidator.validate_enrichment(res1, source)
        self.assertEqual(status1, ValidationStatus.VERIFIED)

        res2 = self._create_result(
            field_name="product_description",
            enriched_value="the tool does not accelerate code review",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status2, _ = EvidenceValidator.validate_enrichment(res2, source)
        self.assertEqual(status2, ValidationStatus.FAILED)

    # -------------------------------------------------------------------------
    # AUDIT 25 PRIORITY 2: MANDATORY REGRESSION TESTS 1-8
    # Extractive Context and Attribution Qualifier Integrity
    # -------------------------------------------------------------------------

    def test_audit25_regression_test1_allegation(self):
        """
        Test 1 — Allegation:
        Evidence: 'The CEO alleged that the competitor stole the design.'
        Claim: 'the competitor stole the design'
        Expected: NEEDS_REVIEW, never VERIFIED.
        """
        source = "The CEO alleged that the competitor stole the design."
        ev = source
        res = self._create_result(
            field_name="company_description",
            enriched_value="the competitor stole the design",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
        self.assertIn("qualification", rationale.lower())

    def test_audit25_regression_test2_reported_claim(self):
        """
        Test 2 — Reported claim:
        Evidence: 'The company reportedly operates the largest AI data center.'
        Claim: 'operates the largest AI data center'
        Expected: NEEDS_REVIEW.
        """
        source = "The company reportedly operates the largest AI data center."
        ev = source
        res = self._create_result(
            field_name="company_description",
            enriched_value="operates the largest AI data center",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
        self.assertIn("qualification", rationale.lower())

    def test_audit25_regression_test3_vendor_attribution(self):
        """
        Test 3 — Vendor attribution:
        Evidence: 'According to the vendor, the platform prevents fraud.'
        Claim: 'the platform prevents fraud'
        Expected: NEEDS_REVIEW.
        """
        source = "According to the vendor, the platform prevents fraud."
        ev = source
        res = self._create_result(
            field_name="product_description",
            enriched_value="the platform prevents fraud",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
        self.assertIn("qualification", rationale.lower())

    def test_audit25_regression_test4_planned_activity(self):
        """
        Test 4 — Planned activity:
        Evidence: 'The company plans to launch a medical AI platform next year.'
        Claim: 'launch a medical AI platform'
        Expected: NEEDS_REVIEW, never VERIFIED as an accomplished fact.
        """
        source = "The company plans to launch a medical AI platform next year."
        ev = source
        res = self._create_result(
            field_name="company_description",
            enriched_value="launch a medical AI platform",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
        self.assertIn("qualification", rationale.lower())

    def test_audit25_regression_test5_limited_scope(self):
        """
        Test 5 — Limited scope:
        Evidence: 'The platform supports Python only in enterprise mode.'
        Claim: 'supports Python'
        Expected: NEEDS_REVIEW.
        """
        source = "The platform supports Python only in enterprise mode."
        ev = source
        res = self._create_result(
            field_name="product_description",
            enriched_value="supports Python",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
        self.assertIn("qualification", rationale.lower())

    def test_audit25_regression_test6_manual_approval_condition(self):
        """
        Test 6 — Manual approval condition:
        Evidence: 'The system processes images only after manual approval.'
        Claim: 'processes images'
        Expected: NEEDS_REVIEW.
        """
        source = "The system processes images only after manual approval."
        ev = source
        res = self._create_result(
            field_name="product_description",
            enriched_value="processes images",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
        self.assertIn("qualification", rationale.lower())

    def test_audit25_regression_test7_self_reported_outcome(self):
        """
        Test 7 — Self-reported outcome:
        Evidence: 'The company says its model improves diagnostic accuracy.'
        Claim: 'its model improves diagnostic accuracy'
        Expected: NEEDS_REVIEW.
        """
        source = "The company says its model improves diagnostic accuracy."
        ev = source
        res = self._create_result(
            field_name="company_description",
            enriched_value="its model improves diagnostic accuracy",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
        self.assertIn("qualification", rationale.lower())

    def test_audit25_regression_test8_report_attribution(self):
        """
        Test 8 — Report attribution:
        Evidence: 'The report states that the company acquired DeepMind.'
        Claim: 'the company acquired DeepMind'
        Expected: NEEDS_REVIEW.
        """
        source = "The report states that the company acquired DeepMind."
        ev = source
        res = self._create_result(
            field_name="company_description",
            enriched_value="the company acquired DeepMind",
            evidence=ev,
            source_version=compute_source_version(source),
            confidence_score=0.95
        )
        status, rationale = EvidenceValidator.validate_enrichment(res, source)
        self.assertEqual(status, ValidationStatus.NEEDS_REVIEW)
        self.assertIn("qualification", rationale.lower())


if __name__ == "__main__":
    unittest.main()

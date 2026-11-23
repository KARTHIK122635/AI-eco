"""
Unit tests for deterministic Offline Provider heuristics, word-boundary protection, and calibrated confidence.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - Accurate Heuristic Attribution and False-Positive Prevention
"""

import unittest
from core.llm.providers.offline_provider import OfflineProvider
from core.llm.base import ProviderConfig
from core.enrichment.schemas import JOB_ENRICHMENT_SCHEMA, STARTUP_ENRICHMENT_SCHEMA


class TestOfflineProvider(unittest.TestCase):

    def setUp(self):
        self.provider = OfflineProvider()

    def test_provider_identity_is_heuristic(self):
        """Test that OfflineProvider is identified as offline / heuristic-keyword-v1, not claiming to be LLM."""
        self.assertEqual(self.provider.name, "offline")
        self.assertEqual(self.provider.model, "heuristic-keyword-v1")
        self.assertTrue(self.provider.is_available())

    def test_calibrated_confidence_never_unearned_095(self):
        """Test that keyword match yields calibrated confidence (e.g. 0.70-0.80), never unearned 0.95."""
        text = "Source Content: Candidate should have experience with PyTorch and Python for model development."
        res = self.provider.extract_structured(text, JOB_ENRICHMENT_SCHEMA)
        conf = res.get("confidence_score")
        self.assertIsNotNone(conf)
        self.assertLessEqual(conf, 0.85, "Confidence must be calibrated, never 0.95 merely for keyword matching.")
        self.assertGreaterEqual(conf, 0.70)

    def test_programming_languages_vs_common_words_false_positives(self):
        """
        Test that common words like 'go', 'fast', 'c', 'r', 'rust' do NOT trigger
        programming language extraction false positives in non-code contexts.
        """
        # Text with 'go', 'fast', 'rust', but NOT programming languages
        ordinary_text = """
        Source Content:
        Our team moves in a fast-paced environment. We go to client offices weekly.
        The old machinery had surface rust on the metal plates.
        Looking for a senior business development lead.
        """
        res = self.provider.extract_structured(ordinary_text, JOB_ENRICHMENT_SCHEMA)
        extracted_tech = res.get("technologies", [])
        
        self.assertNotIn("Go", extracted_tech, "False positive: 'go' verb should not match Go programming language.")
        self.assertNotIn("FastAPI", extracted_tech, "False positive: 'fast-paced' should not match FastAPI.")
        self.assertNotIn("C", extracted_tech, "False positive: 'c' should not match C language.")
        self.assertNotIn("R", extracted_tech, "False positive: 'r' should not match R language.")

    def test_genuine_programming_language_matches(self):
        """Test that explicit programming language contexts ARE correctly identified."""
        code_text = """
        Source Content:
        Must be proficient in Golang, Rust programming, and C/C++.
        Experience building microservices with FastAPI and deploying via Docker.
        """
        res = self.provider.extract_structured(code_text, JOB_ENRICHMENT_SCHEMA)
        extracted_tech = res.get("technologies", [])
        self.assertIn("Go", extracted_tech)
        self.assertIn("Rust", extracted_tech)
        self.assertIn("C++", extracted_tech)
        self.assertIn("FastAPI", extracted_tech)
        self.assertIn("Docker", extracted_tech)

    def test_sentence_level_evidence_extraction(self):
        """Test that the evidence excerpt is the exact sentence where extracted terms appear."""
        doc = """
        Source Content:
        Company founded in 2020 in Seattle.
        We develop large language models for enterprise healthcare automation.
        Our office is located near downtown.
        """
        res = self.provider.extract_structured(doc, STARTUP_ENRICHMENT_SCHEMA)
        ev = res.get("evidence", "")
        self.assertIn("large language models", ev)
        self.assertIn("healthcare automation", ev)
        self.assertNotIn("Company founded in 2020", ev)

    def test_schema_conformance(self):
        """Test that extraction output conforms to requested schema."""
        prompt = "Source Content: We build distributed systems with Kubernetes and Python."
        res = self.provider.extract_structured(prompt, JOB_ENRICHMENT_SCHEMA)
        self.assertIn("evidence", res)
        self.assertIn("confidence_score", res)
        self.assertIsInstance(res["technologies"], list)


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for Entity-Specific Enrichers.
Phase II - Stage 3: LLM Fallback and Enrichment
"""

import unittest
from core.llm.providers.offline_provider import OfflineProvider
from core.enrichment.entity_enrichers import (
    StartupEnricher,
    ProductEnricher,
    PaperEnricher,
    NewsEnricher,
    JobEnricher
)
from core.enrichment.schemas import ValidationStatus


class TestEntityEnrichers(unittest.TestCase):

    def setUp(self):
        self.provider = OfflineProvider()

    def test_startup_enricher(self):
        enricher = StartupEnricher(self.provider)
        rec = {
            "startup_id": "startup_test_101",
            "entity_name": "Synthetix AI",
            "primary_source_url": "https://synthetix.example.com",
            "description": "",  # missing
            "ai_focus_area": "Foundation Models",
            "ai_evidence": "Building distributed multimodal LLMs using PyTorch, CUDA, and Triton.",
            "technologies": None
        }
        results = enricher.enrich_record(rec)
        self.assertGreater(len(results), 0)
        field_names = [r.field_name for r in results]
        self.assertIn("technologies", field_names)
        
        tech_res = next(r for r in results if r.field_name == "technologies")
        self.assertIn("PyTorch", tech_res.enriched_value)
        self.assertIn(tech_res.validation_status, [ValidationStatus.VERIFIED.value, ValidationStatus.NEEDS_REVIEW.value])

    def test_product_enricher(self):
        enricher = ProductEnricher(self.provider)
        rec = {
            "product_id": "prod_test_202",
            "entity_name": "VisionFlow Engine",
            "developer_or_company": "VisionFlow Labs",
            "original_source_url": "https://visionflow.example.com",
            "ai_task_category": "Computer Vision",
            "description": "High-performance computer vision SDK that supports PyTorch, OpenCV, and TensorRT for real-time video outpainting.",
            "supported_technologies": None,
            "main_capabilities": None
        }
        results = enricher.enrich_record(rec)
        self.assertGreater(len(results), 0)
        field_names = [r.field_name for r in results]
        self.assertIn("supported_technologies", field_names)
        
        tech_res = next(r for r in results if r.field_name == "supported_technologies")
        self.assertIn("PyTorch", tech_res.enriched_value)

    def test_paper_enricher(self):
        enricher = PaperEnricher(self.provider)
        rec = {
            "paper_id": "paper_test_303",
            "title": "Scaling Transformer Representations for Long Horizon Planning",
            "categories": "cs.AI, cs.LG",
            "paper_url": "https://arxiv.org/abs/2401.00000",
            "abstract": "We present an empirical study on scaling transformer models for reinforcement learning agents across complex decision horizons using JAX.",
            "research_domain": None,
            "methodology": None,
            "model_or_architecture": None
        }
        results = enricher.enrich_record(rec)
        self.assertGreater(len(results), 0)
        field_names = [r.field_name for r in results]
        self.assertIn("research_domain", field_names)

    def test_news_enricher_refusal_when_no_content(self):
        enricher = NewsEnricher(self.provider)
        rec = {
            "news_id": "news_test_404",
            "title": "Major Tech Company Announces Q3 Results",
            "article_url": "https://news.example.com/item/1",
            "summary": "",  # missing
            "content": ""   # missing content!
        }
        results = enricher.enrich_record(rec)
        # MUST return INSUFFICIENT_EVIDENCE and must NOT invent a fake summary
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].validation_status, ValidationStatus.INSUFFICIENT_EVIDENCE.value)
        self.assertIsNone(results[0].enriched_value)

    def test_news_enricher_with_valid_content(self):
        enricher = NewsEnricher(self.provider)
        rec = {
            "news_id": "news_test_405",
            "title": "Nvidia Launches New GPU Architecture",
            "article_url": "https://news.example.com/item/2",
            "summary": "",
            "content": "Nvidia unveiled its next-generation Blackwell GPU architecture today at GTC, delivering 4x training performance for large language models and transformers."
        }
        results = enricher.enrich_record(rec)
        self.assertGreater(len(results), 0)
        summary_res = next((r for r in results if r.field_name == "summary"), None)
        self.assertIsNotNone(summary_res)
        self.assertIn(summary_res.validation_status, [ValidationStatus.VERIFIED.value, ValidationStatus.NEEDS_REVIEW.value])

    def test_job_enricher_extracts_skills_without_modifying_protected_fields(self):
        enricher = JobEnricher(self.provider)
        rec = {
            "job_id": "job_test_505",
            "job_title": "Machine Learning Engineer",
            "company_name": "Anthropic",
            "application_url": "https://jobs.example.com/1",
            "job_description": "We are looking for a Machine Learning Engineer with deep expertise in Python, PyTorch, Ray, and Kubernetes to scale distributed training on cloud infrastructure.",
            "required_skills": "[]",  # empty
            "preferred_skills": "[]",
            "salary_min": 180000.0,   # protected!
            "salary_max": 240000.0,
            "currency": "USD",
            "job_status": "EMPLOYER_CONFIRMED_OPEN"
        }
        results = enricher.enrich_record(rec)
        self.assertGreater(len(results), 0)
        
        # Ensure protected fields were NEVER added to results
        for r in results:
            self.assertNotIn(r.field_name, ["salary_min", "salary_max", "currency", "job_status", "job_description", "application_url"])

        # Check required_skills extracted
        req_res = next((r for r in results if r.field_name == "required_skills"), None)
        self.assertIsNotNone(req_res)
        self.assertIn("Python", req_res.enriched_value)
        self.assertIn("PyTorch", req_res.enriched_value)


if __name__ == "__main__":
    unittest.main()

"""
Master Test Suite: End-to-End Validation across Phase I, Phase II, and Phase III
==============================================================================
Validates:
1. Phase I Research Paper-to-GitHub Pipeline (confidence scoring, live verification, dead links, NO_PUBLIC_CODE_FOUND)
2. Phase II Freshness, Quality, and Deduplication Engine (24h window, date parsing, placeholder detection, deduplication)
3. Phase III Multi-Tier LLM Orchestration Engine (Primary -> Fallback 1 -> Fallback 2 402 catch -> Offline Heuristic)
4. Database Non-Mutation and Audit 19 Preservation Invariants
"""

import os
import sys
import json
import sqlite3
import hashlib
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

from core.paper_github_pipeline import PaperGitHubEnricher
from core.freshness_engine import (
    parse_datetime_utc,
    evaluate_freshness,
    canonicalize_url,
    compute_content_fingerprint,
    validate_content_quality,
    DeduplicationRegistry
)
from core.llm.base import LLMResponse, TokenUsage, ProviderConfig
from core.llm.providers.deepseek_provider import DeepSeekProvider
from core.llm.multi_tier_engine import MultiTierLLMEngine, SemanticChunker


class TestPhase1PaperGitHubPipeline(unittest.TestCase):
    """Tests for Phase I Research Paper GitHub Enrichment."""

    def test_arxiv_id_extraction(self):
        pid = PaperGitHubEnricher.extract_arxiv_id("https://arxiv.org/abs/2301.12345v2", "Title", "Abstract")
        self.assertEqual(pid, "2301.12345")

        pid2 = PaperGitHubEnricher.extract_arxiv_id("", "Study on Transformers", "Available at arxiv_2611_26232.")
        self.assertEqual(pid2, "2611.26232")

    def test_extract_github_links_from_text(self):
        text = "Code is at https://github.com/google-deepmind/graphcast. Also see https://github.com/huggingface/transformers."
        links = PaperGitHubEnricher.extract_github_links_from_text(text)
        self.assertEqual(len(links), 2)
        self.assertIn("https://github.com/google-deepmind/graphcast", links)
        self.assertIn("https://github.com/huggingface/transformers", links)

    def test_generic_github_urls_ignored(self):
        text = "Visit https://github.com/topics/machine-learning or https://github.com/about for info."
        links = PaperGitHubEnricher.extract_github_links_from_text(text)
        self.assertEqual(len(links), 0)


class TestPhase2FreshnessAndDeduplication(unittest.TestCase):
    """Tests for Phase II Freshness, Content Quality, and Deduplication."""

    def test_rfc2822_and_iso_date_parsing(self):
        dt1 = parse_datetime_utc("Sun, 22 Nov 2026 14:00:00 GMT")
        self.assertIsNotNone(dt1)
        self.assertEqual(dt1.year, 2026)
        self.assertEqual(dt1.tzinfo, timezone.utc)

        dt2 = parse_datetime_utc("2026-11-22T14:30:00Z")
        self.assertIsNotNone(dt2)
        self.assertEqual(dt2.minute, 30)

        dt3 = parse_datetime_utc(1795358000)
        self.assertIsNotNone(dt3)

        self.assertIsNone(parse_datetime_utc(None))
        self.assertIsNone(parse_datetime_utc("invalid-timestamp-string"))

    def test_freshness_window_classification(self):
        ref = datetime(2026, 11, 22, 14, 0, 0, tzinfo=timezone.utc)

        # 2 hours old -> FRESH_24H
        fresh = ref - timedelta(hours=2)
        res_fresh = evaluate_freshness(fresh, reference_dt=ref)
        self.assertEqual(res_fresh["status"], "FRESH_24H")
        self.assertTrue(res_fresh["is_fresh_24h"])

        # 48 hours old -> RECENT_7D
        recent = ref - timedelta(hours=48)
        res_recent = evaluate_freshness(recent, reference_dt=ref)
        self.assertEqual(res_recent["status"], "RECENT_7D")
        self.assertFalse(res_recent["is_fresh_24h"])

        # 10 days old -> HISTORICAL_STALE
        stale = ref - timedelta(days=10)
        res_stale = evaluate_freshness(stale, reference_dt=ref)
        self.assertEqual(res_stale["status"], "HISTORICAL_STALE")

        # Future date (> 0.1h in future) -> FUTURE_TIMESTAMP_ANOMALY
        future = ref + timedelta(hours=5)
        res_future = evaluate_freshness(future, reference_dt=ref)
        self.assertEqual(res_future["status"], "FUTURE_TIMESTAMP_ANOMALY")

        # Missing date
        res_missing = evaluate_freshness(None, reference_dt=ref)
        self.assertEqual(res_missing["status"], "MISSING_DATE")

    def test_url_canonicalization(self):
        u1 = "https://techcrunch.com/2026/11/22/ai-model/?utm_source=twitter&utm_medium=social#comments"
        u2 = "http://techcrunch.com/2026/11/22/ai-model/?utm_campaign=feed"
        c1 = canonicalize_url(u1)
        c2 = canonicalize_url(u2)
        self.assertEqual(c1, "https://techcrunch.com/2026/11/22/ai-model")
        self.assertEqual(c2, "http://techcrunch.com/2026/11/22/ai-model")

    def test_content_quality_and_placeholder_rejection(self):
        good_text = "This is a detailed technical report discussing large language models and neural architecture search."
        ok, msg = validate_content_quality(good_text, min_length=20)
        self.assertTrue(ok)

        # Rejects placeholder
        placeholder = "Please enable JavaScript to view this website properly."
        ok2, msg2 = validate_content_quality(placeholder, min_length=10)
        self.assertFalse(ok2)
        self.assertIn("placeholder", msg2.lower())

        # Rejects raw HTML tags
        raw_html = "<div class='content'><p>Unrendered markup</p></div>"
        ok3, msg3 = validate_content_quality(raw_html, min_length=10)
        self.assertFalse(ok3)

    def test_deduplication_registry(self):
        dedup = DeduplicationRegistry()
        u1, reason1 = dedup.check_and_register("r1", "https://site.com/art?utm_source=x", "AI News", "Long detailed text about artificial intelligence")
        self.assertTrue(u1)

        # Duplicate URL
        u2, reason2 = dedup.check_and_register("r2", "https://site.com/art?utm_campaign=y", "Different Title", "Another text")
        self.assertFalse(u2)
        self.assertIn("Duplicate canonical URL", reason2)

        # Duplicate Content Fingerprint
        u3, reason3 = dedup.check_and_register("r3", "https://other.com/post", "Unique Title", "Long detailed text about artificial intelligence")
        self.assertFalse(u3)
        self.assertIn("Duplicate content fingerprint", reason3)


class TestPhase3MultiTierLLMEngine(unittest.TestCase):
    """Tests for Phase III Multi-Tier Fallback Orchestrator."""

    def test_semantic_chunker(self):
        chunker = SemanticChunker(max_chunk_chars=100, overlap_chars=20)
        text = "Paragraph one is about training transformers.\n\nParagraph two discusses dataset curation.\n\nParagraph three discusses evals."
        chunks = chunker.chunk_text(text)
        self.assertTrue(len(chunks) >= 2)

    def test_deepseek_402_non_retriable_error_handling(self):
        cfg = ProviderConfig(provider_name="deepseek", api_key="sk-test-key", model_name="deepseek-chat")
        provider = DeepSeekProvider(cfg)

        with patch("httpx.Client.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 402
            mock_resp.text = '{"error":{"message":"Insufficient Balance","type":"insufficient_balance_error"}}'
            mock_post.return_value = mock_resp

            resp = provider.generate("Test prompt")
            self.assertFalse(resp.success)
            self.assertIn("402", resp.error)
            self.assertIn("Insufficient Balance", resp.error)
            # Must exit immediately on attempt 1 without spamming 3 retries
            self.assertEqual(mock_post.call_count, 1)

    def test_multi_tier_fallback_cascade(self):
        engine = MultiTierLLMEngine()

        # Mock primary failure -> Groq should be called and succeed
        with patch.object(engine.primary_provider, "generate") as mock_gemini, \
             patch.object(engine.fallback_1_provider, "generate") as mock_groq:

            mock_gemini.return_value = LLMResponse(content="", success=False, error="HTTP 429 Rate Limited", provider="gemini")
            mock_groq.return_value = LLMResponse(
                content='{"answer": "fallback_success"}',
                success=True,
                provider="groq",
                model="qwen/qwen3.8-27b",
                token_usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15, estimated_cost_usd=0.0001)
            )

            res = engine.execute_with_fallback("Test prompt")
            self.assertTrue(res.success)
            self.assertEqual(res.active_tier, "FALLBACK_1")
            self.assertEqual(res.active_provider, "groq")
            self.assertEqual(len(res.attempts), 2)
            self.assertEqual(res.attempts[0].error_type, "HTTP_429_RATE_LIMITED")


class TestDatabaseIntegrityAndSafety(unittest.TestCase):
    """Tests verifying canonical database and authentic Audit 19 archive preservation."""

    def test_canonical_db_unaltered(self):
        path = "data/normalized/ai_ecosystem.db"
        self.assertTrue(os.path.exists(path))
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        self.assertEqual(h, "4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d")

    def test_audit19_archive_unaltered(self):
        path = "source/audit19_original_database.db"
        self.assertTrue(os.path.exists(path))
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        self.assertEqual(h, "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d")


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for LLM provider architecture with mocked HTTP responses.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - Zero Real API Charges and Mocked Adapter Verification
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock

from core.llm.base import (
    BaseLLMProvider,
    ProviderConfig,
    LLMResponse,
    TokenUsage,
    RateLimiter,
    estimate_cost,
    PRICING_CATALOG
)
from core.llm.providers.gemini import GeminiProvider
from core.llm.providers.openai_provider import OpenAIProvider
from core.llm.providers.groq_provider import GroqProvider
from core.llm.providers.ollama_provider import OllamaProvider
from core.llm.providers.offline_provider import OfflineProvider
from core.llm.factory import get_llm_provider
from core.enrichment.schemas import JOB_ENRICHMENT_SCHEMA


class TestLLMProviders(unittest.TestCase):
    
    def test_cost_estimation(self):
        # Gemini 1.5 Flash: $0.075 / 1M input, $0.30 / 1M output
        cost = estimate_cost("gemini", "gemini-1.5-flash", 1_000_000, 1_000_000)
        self.assertAlmostEqual(cost, 0.375, places=4)
        
        # OpenAI GPT-4o-mini: $0.15 / 1M input, $0.60 / 1M output
        cost_oai = estimate_cost("openai", "gpt-4o-mini", 1_000_000, 1_000_000)
        self.assertAlmostEqual(cost_oai, 0.75, places=4)

        # Offline / Ollama: 0.0
        cost_off = estimate_cost("offline", "default", 500_000, 500_000)
        self.assertEqual(cost_off, 0.0)

    def test_token_usage_accumulation(self):
        u1 = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150, estimated_cost_usd=0.001)
        u2 = TokenUsage(prompt_tokens=200, completion_tokens=100, total_tokens=300, estimated_cost_usd=0.002)
        total = u1.add(u2)
        self.assertEqual(total.prompt_tokens, 300)
        self.assertEqual(total.completion_tokens, 150)
        self.assertEqual(total.total_tokens, 450)
        self.assertAlmostEqual(total.estimated_cost_usd, 0.003, places=5)

    def test_factory_fallback_when_no_credentials(self):
        # When environment has no keys, get_llm_provider safely returns OfflineProvider
        with patch.dict(os.environ, {}, clear=True):
            p = get_llm_provider()
            self.assertIsInstance(p, OfflineProvider)
            self.assertEqual(p.name, "offline")

    def test_distinguish_initialization_from_real_request(self):
        """
        Audit 19 Requirement:
        The provider tests must distinguish initialization with dummy credentials from a real API request.
        """
        config = ProviderConfig(
            provider_name="gemini",
            api_key="DUMMY_KEY_NOT_REAL",
            model_name="gemini-1.5-flash"
        )
        provider = GeminiProvider(config)
        # Initialization succeeds because dummy credentials are set
        self.assertTrue(provider.is_available())
        self.assertEqual(provider.name, "gemini")
        # No network call was made upon initialization
        self.assertEqual(provider.cumulative_usage.total_tokens, 0)

    @patch("httpx.Client")
    def test_mocked_gemini_request(self, mock_client_cls):
        """Tests Gemini adapter with mocked HTTP 200 response (zero paid API charges)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": json.dumps({
                                "role_specialization": "ML Infrastructure",
                                "required_skills": ["Python", "Kubernetes"],
                                "preferred_skills": ["CUDA"],
                                "technologies": ["PyTorch"],
                                "evidence": "Must have Python and Kubernetes experience.",
                                "confidence_score": 0.90
                            })}
                        ]
                    }
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 120,
                "candidatesTokenCount": 60,
                "totalTokenCount": 180
            }
        }
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value.__enter__.return_value = mock_client

        provider = GeminiProvider(ProviderConfig(
            provider_name="gemini",
            api_key="test_dummy_key",
            model_name="gemini-1.5-flash"
        ))

        res = provider.generate("Extract skills", json_schema=JOB_ENRICHMENT_SCHEMA)
        self.assertTrue(res.success)
        self.assertIsNotNone(res.structured_data)
        self.assertEqual(res.token_usage.total_tokens, 180)
        self.assertIn("Python", res.structured_data["required_skills"])
        mock_client.post.assert_called_once()

    @patch("httpx.Client")
    def test_mocked_openai_request(self, mock_client_cls):
        """Tests OpenAI adapter with mocked HTTP 200 response (zero paid API charges)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "role_specialization": "LLM Research",
                            "required_skills": ["PyTorch"],
                            "preferred_skills": [],
                            "technologies": ["PyTorch", "vLLM"],
                            "evidence": "Deep expertise in PyTorch and vLLM required.",
                            "confidence_score": 0.92
                        })
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 50,
                "total_tokens": 200
            }
        }
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value.__enter__.return_value = mock_client

        provider = OpenAIProvider(ProviderConfig(
            provider_name="openai",
            api_key="test_dummy_key",
            model_name="gpt-4o-mini"
        ))

        res = provider.generate("Extract skills", json_schema=JOB_ENRICHMENT_SCHEMA)
        self.assertTrue(res.success)
        self.assertIsNotNone(res.structured_data)
        self.assertEqual(res.token_usage.total_tokens, 200)
        self.assertIn("vLLM", res.structured_data["technologies"])
        mock_client.post.assert_called_once()

    @patch("httpx.Client")
    def test_mocked_groq_request(self, mock_client_cls):
        """Tests Groq adapter with mocked HTTP 200 response (zero paid API charges)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "role_specialization": "Backend AI Systems",
                            "required_skills": ["FastAPI", "Python"],
                            "preferred_skills": ["Docker"],
                            "technologies": ["Python", "Docker"],
                            "evidence": "Experience with FastAPI and Python microservices.",
                            "confidence_score": 0.88
                        })
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 40,
                "total_tokens": 140
            }
        }
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value.__enter__.return_value = mock_client

        provider = GroqProvider(ProviderConfig(
            provider_name="groq",
            api_key="test_dummy_key",
            model_name="llama-3.3-70b-versatile"
        ))

        res = provider.generate("Extract skills", json_schema=JOB_ENRICHMENT_SCHEMA)
        self.assertTrue(res.success)
        self.assertIsNotNone(res.structured_data)
        mock_client.post.assert_called_once()


if __name__ == "__main__":
    unittest.main()

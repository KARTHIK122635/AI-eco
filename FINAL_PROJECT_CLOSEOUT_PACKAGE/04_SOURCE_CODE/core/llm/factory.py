"""
LLM Provider Factory with environment-variable resolution and graceful offline fallback.
Phase II - Stage 3: LLM Fallback and Enrichment
"""

import os
import logging
from typing import Optional, Dict, Any

from core.llm.base import BaseLLMProvider, ProviderConfig
from core.llm.providers.gemini import GeminiProvider
from core.llm.providers.openai_provider import OpenAIProvider
from core.llm.providers.groq_provider import GroqProvider
from core.llm.providers.deepseek_provider import DeepSeekProvider
from core.llm.providers.ollama_provider import OllamaProvider
from core.llm.providers.offline_provider import OfflineProvider
from core.env_loader import load_project_env

load_project_env()

logger = logging.getLogger("LLMFactory")


def get_llm_provider(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 2048,
    timeout_seconds: float = 30.0,
    max_retries: int = 3,
    rate_limit_rpm: Optional[int] = 60
) -> BaseLLMProvider:
    """
    Instantiates an LLM provider adapter using environment variables and explicit overrides.
    Falls back gracefully to OfflineProvider if no valid provider credentials exist.
    """
    chosen = provider_name or os.environ.get("LLM_PROVIDER", "").strip().lower()

    # 1. Google Gemini
    if chosen == "gemini" or (not chosen and os.environ.get("GEMINI_API_KEY")):
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if key:
            model = model_name or os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")
            config = ProviderConfig(
                provider_name="gemini",
                api_key=key,
                model_name=model,
                base_url=base_url or os.environ.get("GEMINI_BASE_URL"),
                temperature=temperature,
                max_tokens=max_tokens,
                timeout_seconds=timeout_seconds,
                max_retries=max_retries,
                rate_limit_rpm=rate_limit_rpm
            )
            logger.info(f"Initialized Gemini provider with model '{model}'")
            return GeminiProvider(config)
        elif chosen == "gemini":
            logger.warning("Gemini provider requested but GEMINI_API_KEY is not set. Falling back to offline provider.")

    # 2. OpenAI
    if chosen == "openai" or (not chosen and os.environ.get("OPENAI_API_KEY")):
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if key:
            model = model_name or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
            config = ProviderConfig(
                provider_name="openai",
                api_key=key,
                model_name=model,
                base_url=base_url or os.environ.get("OPENAI_BASE_URL"),
                temperature=temperature,
                max_tokens=max_tokens,
                timeout_seconds=timeout_seconds,
                max_retries=max_retries,
                rate_limit_rpm=rate_limit_rpm
            )
            logger.info(f"Initialized OpenAI provider with model '{model}'")
            return OpenAIProvider(config)
        elif chosen == "openai":
            logger.warning("OpenAI provider requested but OPENAI_API_KEY is not set. Falling back to offline provider.")

    # 3. Groq
    if chosen == "groq" or (not chosen and os.environ.get("GROQ_API_KEY")):
        key = api_key or os.environ.get("GROQ_API_KEY")
        if key:
            model = model_name or os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")
            config = ProviderConfig(
                provider_name="groq",
                api_key=key,
                model_name=model,
                base_url=base_url or os.environ.get("GROQ_BASE_URL"),
                temperature=temperature,
                max_tokens=max_tokens,
                timeout_seconds=timeout_seconds,
                max_retries=max_retries,
                rate_limit_rpm=rate_limit_rpm
            )
            logger.info(f"Initialized Groq provider with model '{model}'")
            return GroqProvider(config)
        elif chosen == "groq":
            logger.warning("Groq provider requested but GROQ_API_KEY is not set. Falling back to offline provider.")

    # 4. DeepSeek
    if chosen == "deepseek" or (not chosen and os.environ.get("DEEPSEEK_API_KEY")):
        key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if key:
            model = model_name or os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
            config = ProviderConfig(
                provider_name="deepseek",
                api_key=key,
                model_name=model,
                base_url=base_url or os.environ.get("DEEPSEEK_BASE_URL"),
                temperature=temperature,
                max_tokens=max_tokens,
                timeout_seconds=timeout_seconds,
                max_retries=max_retries,
                rate_limit_rpm=rate_limit_rpm
            )
            logger.info(f"Initialized DeepSeek provider with model '{model}'")
            return DeepSeekProvider(config)
        elif chosen == "deepseek":
            logger.warning("DeepSeek provider requested but DEEPSEEK_API_KEY is not set. Falling back to offline provider.")

    # 5. Ollama (local)
    if chosen == "ollama":
        model = model_name or os.environ.get("OLLAMA_MODEL", "llama3")
        ollama_url = base_url or os.environ.get("OLLAMA_HOST") or os.environ.get("OLLAMA_BASE_URL") or "http://localhost:11434"
        config = ProviderConfig(
            provider_name="ollama",
            model_name=model,
            base_url=ollama_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            rate_limit_rpm=rate_limit_rpm
        )
        provider = OllamaProvider(config)
        if provider.is_available():
            logger.info(f"Initialized Ollama provider with model '{model}' at '{ollama_url}'")
            return provider
        else:
            logger.warning("Ollama daemon is unreachable. Falling back to offline provider.")

    # 5. Default / Offline Fallback Provider
    logger.info("Initializing offline heuristic provider (no remote credentials required).")
    config = ProviderConfig(
        provider_name="offline",
        model_name=model_name or "heuristic-grounded-v1",
        temperature=0.0,
        max_tokens=max_tokens,
        rate_limit_rpm=None
    )
    return OfflineProvider(config)

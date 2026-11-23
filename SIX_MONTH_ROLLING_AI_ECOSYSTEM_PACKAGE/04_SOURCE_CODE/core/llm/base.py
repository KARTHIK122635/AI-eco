"""
Base LLM Provider abstractions, schemas, retry logic, rate limiting, and cost estimation.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - Strict Schema Validation & Token Tracking
"""

import time
import json
import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union

from core.llm.schema_validator import validate_json_schema

logger = logging.getLogger("LLMProvider")

# Estimated cost per 1M tokens (USD) as of late 2024 / 2025
PRICING_CATALOG = {
    "gemini": {
        "gemini-3.1-flash-lite": {"input_per_m": 0.075, "output_per_m": 0.30},
        "gemini-3.8-flash": {"input_per_m": 0.075, "output_per_m": 0.30},
        "gemini-2.5-flash": {"input_per_m": 0.075, "output_per_m": 0.30},
        "gemini-1.5-flash": {"input_per_m": 0.075, "output_per_m": 0.30},
        "gemini-2.0-flash": {"input_per_m": 0.10, "output_per_m": 0.40},
        "gemini-1.5-pro": {"input_per_m": 1.25, "output_per_m": 5.00},
        "default": {"input_per_m": 0.075, "output_per_m": 0.30}
    },
    "openai": {
        "gpt-4o-mini": {"input_per_m": 0.15, "output_per_m": 0.60},
        "gpt-4o": {"input_per_m": 2.50, "output_per_m": 10.00},
        "default": {"input_per_m": 0.15, "output_per_m": 0.60}
    },
    "groq": {
        "qwen/qwen3.8-27b": {"input_per_m": 0.20, "output_per_m": 0.20},
        "openai/gpt-oss-20b": {"input_per_m": 0.15, "output_per_m": 0.15},
        "llama-3.3-70b-versatile": {"input_per_m": 0.59, "output_per_m": 0.79},
        "llama-3.1-8b-instant": {"input_per_m": 0.05, "output_per_m": 0.08},
        "mixtral-8x7b-32768": {"input_per_m": 0.24, "output_per_m": 0.24},
        "default": {"input_per_m": 0.20, "output_per_m": 0.20}
    },
    "deepseek": {
        "deepseek-chat": {"input_per_m": 0.14, "output_per_m": 0.28},
        "deepseek-reasoner": {"input_per_m": 0.55, "output_per_m": 2.19},
        "default": {"input_per_m": 0.14, "output_per_m": 0.28}
    },
    "ollama": {
        "default": {"input_per_m": 0.0, "output_per_m": 0.0}
    },
    "offline": {
        "default": {"input_per_m": 0.0, "output_per_m": 0.0}
    }
}


@dataclass
class TokenUsage:
    """Tracks token consumption and estimated costs."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def add(self, other: 'TokenUsage') -> 'TokenUsage':
        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
            estimated_cost_usd=round(self.estimated_cost_usd + other.estimated_cost_usd, 6)
        )


@dataclass
class ProviderConfig:
    """Configuration container for LLM providers."""
    provider_name: str
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    base_url: Optional[str] = None
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_delay_base: float = 1.0
    rate_limit_rpm: Optional[int] = 60
    temperature: float = 0.1  # Low temperature for factual extraction
    max_tokens: int = 2048


@dataclass
class LLMResponse:
    """Unified response object returned by all provider adapters."""
    content: str
    structured_data: Optional[Dict[str, Any]] = None
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    model: str = "unknown"
    provider: str = "unknown"
    latency_seconds: float = 0.0
    success: bool = True
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    raw_error_code: Optional[int] = None


class RateLimiter:
    """Simple rate limiter based on requests-per-minute (RPM)."""
    def __init__(self, rpm: Optional[int] = 60):
        self.rpm = rpm
        self.interval = 60.0 / rpm if (rpm and rpm > 0) else 0.0
        self.last_call_time = 0.0

    def acquire(self):
        if self.interval <= 0.0:
            return
        now = time.time()
        elapsed = now - self.last_call_time
        if elapsed < self.interval:
            sleep_duration = self.interval - elapsed
            time.sleep(sleep_duration)
        self.last_call_time = time.time()


def estimate_cost(provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Computes estimated cost in USD based on provider and model rates."""
    provider_rates = PRICING_CATALOG.get(provider.lower(), PRICING_CATALOG.get("offline", {}))
    model_rates = provider_rates.get(model.lower(), provider_rates.get("default", {"input_per_m": 0.0, "output_per_m": 0.0}))
    
    cost = (prompt_tokens / 1_000_000.0) * model_rates["input_per_m"] + \
           (completion_tokens / 1_000_000.0) * model_rates["output_per_m"]
    return round(cost, 6)


class BaseLLMProvider(ABC):
    """
    Abstract common interface for all LLM provider adapters.
    Implements retry with exponential backoff, rate limiting, and token tracking.
    """
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.rate_limiter = RateLimiter(rpm=config.rate_limit_rpm)
        self.cumulative_usage = TokenUsage()

    @property
    def name(self) -> str:
        return self.config.provider_name

    @property
    def model(self) -> str:
        return self.config.model_name or "default"

    def is_available(self) -> bool:
        """Checks if the provider is properly configured and available for use."""
        if self.name in ["ollama", "offline"]:
            return True
        return bool(self.config.api_key and self.config.api_key.strip())

    @abstractmethod
    def _execute_request(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Provider-specific low-level request execution."""
        pass

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """
        Executes generation with automatic rate limiting and exponential backoff retry.
        """
        if not self.is_available():
            return LLMResponse(
                content="",
                success=False,
                error=f"Provider '{self.name}' is not configured (missing API key or endpoint).",
                provider=self.name,
                model=self.model
            )

        max_retries = max(1, self.config.max_retries)
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                self.rate_limiter.acquire()
                start_time = time.time()
                
                response = self._execute_request(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    json_schema=json_schema,
                    temperature=temperature if temperature is not None else self.config.temperature,
                    max_tokens=max_tokens if max_tokens is not None else self.config.max_tokens
                )
                response.latency_seconds = round(time.time() - start_time, 3)
                
                # Accumulate usage
                if response.success and response.token_usage:
                    self.cumulative_usage = self.cumulative_usage.add(response.token_usage)
                
                if response.success:
                    return response
                
                last_error = response.error or "Unknown provider failure"
                logger.warning(f"Provider {self.name} attempt {attempt}/{max_retries} failed: {last_error}")

                # Non-retriable error fast exit (401 Auth, 402 Insufficient Balance, 404 Model Not Found)
                is_non_retriable = (
                    response.raw_error_code in (401, 402, 404) or
                    (response.raw_response and response.raw_response.get("status_code") in (401, 402, 404)) or
                    any(term in last_error.lower() for term in [
                        "insufficient balance", "payment required", "invalid api key",
                        "unauthorized", "not found", "no longer available"
                    ])
                )
                if is_non_retriable:
                    logger.info(f"Non-retriable error for provider '{self.name}'. Immediate fallback recommended.")
                    return response

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Provider {self.name} attempt {attempt}/{max_retries} encountered exception: {e}")

            if attempt < max_retries:
                # Exponential backoff with jitter
                delay = (self.config.retry_delay_base * (2 ** (attempt - 1))) + random.uniform(0.1, 0.5)
                time.sleep(delay)

        return LLMResponse(
            content="",
            success=False,
            error=f"Provider '{self.name}' failed after {max_retries} attempts. Last error: {last_error}",
            provider=self.name,
            model=self.model
        )

    def extract_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        Executes structured extraction, enforces JSON Schema validation,
        and logs and rejects invalid responses.
        """
        resp = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            json_schema=schema,
            temperature=temperature
        )
        parsed_data = None
        if resp.success and resp.structured_data:
            parsed_data = resp.structured_data
        elif resp.success and resp.content:
            try:
                text = resp.content.strip()
                if text.startswith("```json"):
                    text = text[7:]
                elif text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                parsed_data = json.loads(text.strip())
            except Exception as e:
                logger.warning(f"Failed to parse JSON from {self.name} response: {e}")
                return {}

        if parsed_data is not None:
            is_valid, err_msg = validate_json_schema(parsed_data, schema)
            if not is_valid:
                logger.warning(f"Structured response rejected by JSON Schema validator: {err_msg}")
                return {}
            return parsed_data

        return {}

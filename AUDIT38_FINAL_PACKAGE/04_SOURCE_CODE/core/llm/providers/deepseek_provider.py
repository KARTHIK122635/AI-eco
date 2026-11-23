"""
DeepSeek LLM Provider adapter via REST API (OpenAI-compatible).
Phase II - Stage 3: LLM Multi-Tier Fallback Engine
Explicit error handling for HTTP 402 Insufficient Balance, HTTP 429 Rate Limits, and Schema Validation.
"""

import json
import logging
from typing import Dict, Any, Optional
import httpx

from core.llm.base import BaseLLMProvider, ProviderConfig, LLMResponse, TokenUsage, estimate_cost
from core.llm.schema_validator import validate_json_schema

logger = logging.getLogger("DeepSeekProvider")

DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"


class DeepSeekProvider(BaseLLMProvider):
    """
    Adapter for DeepSeek Cloud API (OpenAI-compatible /chat/completions).
    Handles balance status, token usage accounting, and strict schema validation.
    """

    def __init__(self, config: ProviderConfig):
        if not config.model_name:
            config.model_name = DEFAULT_DEEPSEEK_MODEL
        super().__init__(config)
        self.base_url = (config.base_url or "https://api.deepseek.com").rstrip("/")

    def _execute_request(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.config.max_tokens
        }

        if json_schema:
            payload["response_format"] = {"type": "json_object"}

        try:
            with httpx.Client(timeout=self.config.timeout_seconds) as client:
                res = client.post(url, json=payload, headers=headers)

            if res.status_code == 402:
                err_msg = f"DeepSeek HTTP 402 Insufficient Balance: {res.text[:300]}"
                logger.warning(f"DeepSeek account balance exhausted: {res.text[:150]}")
                return LLMResponse(
                    content="",
                    success=False,
                    error=err_msg,
                    provider=self.name,
                    model=self.model,
                    raw_response={"status_code": 402, "error_type": "INSUFFICIENT_BALANCE"}
                )

            if res.status_code == 429:
                err_msg = f"DeepSeek HTTP 429 Rate Limited: {res.text[:300]}"
                return LLMResponse(
                    content="",
                    success=False,
                    error=err_msg,
                    provider=self.name,
                    model=self.model,
                    raw_response={"status_code": 429, "error_type": "RATE_LIMITED"}
                )

            if res.status_code != 200:
                err_msg = f"DeepSeek API returned HTTP {res.status_code}: {res.text[:300]}"
                return LLMResponse(
                    content="",
                    success=False,
                    error=err_msg,
                    provider=self.name,
                    model=self.model,
                    raw_response={"status_code": res.status_code, "error_type": "API_ERROR"}
                )

            data = res.json()
            choices = data.get("choices", [])
            if not choices:
                return LLMResponse(content="", success=False, error="No choices returned by DeepSeek", provider=self.name, model=self.model)

            message = choices[0].get("message", {})
            text_content = message.get("content", "").strip()

            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

            # DeepSeek Pricing: ~$0.14 / 1M prompt, ~$0.28 / 1M completion (deepseek-chat)
            estimated_usd = (prompt_tokens * 0.14 + completion_tokens * 0.28) / 1_000_000.0

            token_usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=estimated_usd
            )

            # Validate JSON Schema if requested
            if json_schema and text_content:
                try:
                    parsed_json = json.loads(text_content)
                    is_valid, validation_errors = validate_json_schema(parsed_json, json_schema)
                    if not is_valid:
                        return LLMResponse(
                            content=text_content,
                            success=False,
                            error=f"Schema validation failed: {validation_errors}",
                            provider=self.name,
                            model=self.model,
                            token_usage=token_usage,
                            raw_response=data
                        )
                except json.JSONDecodeError as jde:
                    return LLMResponse(
                        content=text_content,
                        success=False,
                        error=f"Failed to decode response as JSON: {jde}",
                        provider=self.name,
                        model=self.model,
                        token_usage=token_usage,
                        raw_response=data
                    )

            return LLMResponse(
                content=text_content,
                success=True,
                provider=self.name,
                model=self.model,
                token_usage=token_usage,
                raw_response=data
            )

        except Exception as e:
            logger.error(f"DeepSeek execution exception: {e}")
            return LLMResponse(
                content="",
                success=False,
                error=f"DeepSeek exception: {str(e)}",
                provider=self.name,
                model=self.model
            )

"""
OpenAI LLM Provider adapter via REST API.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - Strict JSON Schema Validation and Mock-Ready Testing
"""

import json
import logging
from typing import Dict, Any, Optional
import httpx

from core.llm.base import BaseLLMProvider, ProviderConfig, LLMResponse, TokenUsage, estimate_cost
from core.llm.schema_validator import validate_json_schema

logger = logging.getLogger("OpenAIProvider")

DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


class OpenAIProvider(BaseLLMProvider):
    """
    Adapter for OpenAI chat completions API.
    Supports JSON object mode, system instructions, token usage accounting, and schema enforcement.
    """
    def __init__(self, config: ProviderConfig):
        if not config.model_name:
            config.model_name = DEFAULT_OPENAI_MODEL
        super().__init__(config)
        self.base_url = config.base_url or "https://api.openai.com/v1"

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

            if res.status_code != 200:
                err_msg = f"OpenAI API returned HTTP {res.status_code}: {res.text[:300]}"
                return LLMResponse(content="", success=False, error=err_msg, provider=self.name, model=self.model)

            data = res.json()
            choices = data.get("choices", [])
            if not choices:
                return LLMResponse(content="", success=False, error="No choices returned by OpenAI", provider=self.name, model=self.model)

            message = choices[0].get("message", {})
            text_content = message.get("content", "").strip()

            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

            cost = estimate_cost(self.name, self.model, prompt_tokens, completion_tokens)
            token_usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=cost
            )

            structured = None
            if json_schema and text_content:
                c = text_content
                if c.startswith("```json"): c = c[7:]
                elif c.startswith("```"): c = c[3:]
                if c.endswith("```"): c = c[:-3]
                try:
                    structured = json.loads(c.strip())
                    is_valid, schema_err = validate_json_schema(structured, json_schema)
                    if not is_valid:
                        logger.warning(f"OpenAI response failed JSON Schema validation: {schema_err}")
                        return LLMResponse(
                            content=text_content,
                            structured_data=None,
                            token_usage=token_usage,
                            model=self.model,
                            provider=self.name,
                            success=False,
                            error=f"Schema validation failed: {schema_err}"
                        )
                except Exception as e:
                    logger.warning(f"JSON decode failed on OpenAI output: {e}")
                    return LLMResponse(
                        content=text_content,
                        structured_data=None,
                        token_usage=token_usage,
                        model=self.model,
                        provider=self.name,
                        success=False,
                        error=f"Invalid JSON returned: {e}"
                    )

            return LLMResponse(
                content=text_content,
                structured_data=structured,
                token_usage=token_usage,
                model=self.model,
                provider=self.name,
                success=True
            )

        except Exception as e:
            return LLMResponse(content="", success=False, error=str(e), provider=self.name, model=self.model)

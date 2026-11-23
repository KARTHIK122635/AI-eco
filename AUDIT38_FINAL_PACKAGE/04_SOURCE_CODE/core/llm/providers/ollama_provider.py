"""
Ollama Local LLM Provider adapter via REST API.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - Strict JSON Schema Validation and Mock-Ready Testing
"""

import json
import logging
from typing import Dict, Any, Optional
import httpx

from core.llm.base import BaseLLMProvider, ProviderConfig, LLMResponse, TokenUsage
from core.llm.schema_validator import validate_json_schema

logger = logging.getLogger("OllamaProvider")

DEFAULT_OLLAMA_MODEL = "llama3"


class OllamaProvider(BaseLLMProvider):
    """
    Adapter for locally hosted Ollama instance (`http://localhost:11434`).
    Zero cost, local privacy, schema-constrained JSON extraction, and schema enforcement.
    """
    def __init__(self, config: ProviderConfig):
        if not config.model_name:
            config.model_name = DEFAULT_OLLAMA_MODEL
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"

    def is_available(self) -> bool:
        # Check if local Ollama daemon is reachable
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def _execute_request(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        url = f"{self.base_url}/api/chat"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else self.config.temperature,
                "num_predict": max_tokens if max_tokens is not None else self.config.max_tokens
            }
        }

        if json_schema:
            payload["format"] = "json"

        try:
            with httpx.Client(timeout=self.config.timeout_seconds) as client:
                res = client.post(url, json=payload)

            if res.status_code != 200:
                return LLMResponse(content="", success=False, error=f"Ollama returned HTTP {res.status_code}: {res.text[:200]}", provider=self.name, model=self.model)

            data = res.json()
            message = data.get("message", {})
            text_content = message.get("content", "").strip()

            prompt_tokens = data.get("prompt_eval_count", 0)
            completion_tokens = data.get("eval_count", 0)
            token_usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                estimated_cost_usd=0.0
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
                        logger.warning(f"Ollama response failed JSON Schema validation: {schema_err}")
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
                    logger.warning(f"JSON decode failed on Ollama output: {e}")
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

"""
Google Gemini LLM Provider adapter via REST API.
Phase II - Stage 3: LLM Fallback and Enrichment
Audit 19 - Strict JSON Schema Validation and Mock-Ready Testing
"""

import json
import logging
from typing import Dict, Any, Optional
import httpx

from core.llm.base import BaseLLMProvider, ProviderConfig, LLMResponse, TokenUsage, estimate_cost
from core.llm.schema_validator import validate_json_schema

logger = logging.getLogger("GeminiProvider")

DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"


class GeminiProvider(BaseLLMProvider):
    """
    Adapter for Google Gemini using standard Google Generative Language REST API.
    Supports JSON mode, system instructions, token usage accounting, and schema enforcement.
    """
    def __init__(self, config: ProviderConfig):
        if not config.model_name:
            config.model_name = DEFAULT_GEMINI_MODEL
        super().__init__(config)
        self.base_url = config.base_url or "https://generativelanguage.googleapis.com/v1beta"

    def _execute_request(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.config.api_key}"
        
        contents = []
        if prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })

        generation_config: Dict[str, Any] = {
            "temperature": temperature if temperature is not None else self.config.temperature,
            "maxOutputTokens": max_tokens if max_tokens is not None else self.config.max_tokens
        }

        if json_schema:
            generation_config["responseMimeType"] = "application/json"

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": generation_config
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        try:
            with httpx.Client(timeout=self.config.timeout_seconds) as client:
                res = client.post(url, json=payload, headers={"Content-Type": "application/json"})
            
            if res.status_code != 200:
                err_msg = f"Gemini API returned HTTP {res.status_code}: {res.text[:300]}"
                return LLMResponse(content="", success=False, error=err_msg, provider=self.name, model=self.model)

            data = res.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return LLMResponse(content="", success=False, error="No candidates returned by Gemini", provider=self.name, model=self.model)

            candidate = candidates[0]
            parts = candidate.get("content", {}).get("parts", [])
            text_content = "".join(p.get("text", "") for p in parts).strip()

            # Token usage
            usage_meta = data.get("usageMetadata", {})
            prompt_tokens = usage_meta.get("promptTokenCount", 0)
            completion_tokens = usage_meta.get("candidatesTokenCount", 0)
            total_tokens = usage_meta.get("totalTokenCount", prompt_tokens + completion_tokens)
            
            cost = estimate_cost(self.name, self.model, prompt_tokens, completion_tokens)
            token_usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=cost
            )

            # Try structured parse and validate if requested
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
                        logger.warning(f"Gemini response failed JSON Schema validation: {schema_err}")
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
                    logger.warning(f"JSON decode failed on Gemini output: {e}")
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

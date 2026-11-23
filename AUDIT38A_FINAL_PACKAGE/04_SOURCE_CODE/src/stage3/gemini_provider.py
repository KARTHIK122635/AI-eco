"""
Gemini Provider for Stage 3 LLM Enrichment
===========================================
Official Google Gemini API integration with:
- Google Generative Language v1beta REST API client (robust pure-Python HTTP with httpx)
- SDK fallback/compatibility
- Structured JSON response parsing
- Strict system prompt enforcement
- Bounded retries with exponential backoff (3 attempts)
- Token tracking and cost accounting via usageMetadata
- Secret redaction in all logs, outputs, and exception messages
- Zero silent fallbacks to offline heuristic
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx

logger = logging.getLogger("stage3.gemini_provider")

# Official default model
DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"

# System instruction mandated by Stage 3 Execution Brief
STRICT_SYSTEM_INSTRUCTION = (
    "You are an evidence-grounded data enrichment assistant. "
    "Use only the supplied source evidence. Do not use unsupported assumptions "
    "or general knowledge to fill factual gaps. Preserve the meaning and scope of "
    "the original record. If evidence is insufficient, contradictory, outdated or "
    "ambiguous, return an appropriate review status. Never fabricate facts, URLs, "
    "dates, numerical values, citations or company information."
)

# Gemini Pricing (per 1,000,000 tokens)
PRICING_PER_MILLION = {
    "gemini-3.1-flash-lite": {
        "prompt": 0.075,
        "completion": 0.30,
    },
    "gemini-3.8-flash": {
        "prompt": 0.075,
        "completion": 0.30,
    },
    "gemini-2.5-flash": {
        "prompt": 0.075,
        "completion": 0.30,
    },
    "gemini-1.5-flash": {
        "prompt": 0.075,
        "completion": 0.30,
    },
    "gemini-1.5-pro": {
        "prompt": 1.25,
        "completion": 5.00,
    },
    "default": {
        "prompt": 0.075,
        "completion": 0.30,
    }
}


def load_env_file(env_path: str = ".env") -> Dict[str, str]:
    """Simple, pure-Python .env file loader."""
    env_vars = {}
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        env_vars[k] = v
        except Exception as e:
            logger.warning(f"Failed to read {env_path}: {e}")
    return env_vars


def redact_secrets(text: str, secret: Optional[str] = None) -> str:
    """Redacts API keys and sensitive tokens from strings."""
    if not text:
        return ""
    text_str = str(text)
    if secret and secret in text_str:
        text_str = text_str.replace(secret, "[REDACTED_GEMINI_KEY]")
    # Redact any generic key-like patterns in URLs or query strings
    text_str = re.sub(r'key=[A-Za-z0-9_\-]{10,}', 'key=[REDACTED_GEMINI_KEY]', text_str)
    text_str = re.sub(r'AIza[0-9A-Za-z-_]{35}', '[REDACTED_GEMINI_KEY]', text_str)
    return text_str


@dataclass
class GeminiUsage:
    """Token usage and cost accounting."""
    prompt_tokens: int = 0
    candidates_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "candidates_tokens": self.candidates_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": round(self.estimated_cost_usd, 6),
        }


@dataclass
class GeminiEnrichmentResponse:
    """Structured response from Gemini API enrichment call."""
    request_id: str
    record_id: str
    entity_type: str
    target_field: str
    original_value: Any
    proposed_value: Any
    evidence: str
    evidence_url: str
    evidence_quote: str
    reasoning: str
    confidence: float
    status: str
    limitations: str
    model_id: str
    provider: str
    request_timestamp: str
    response_timestamp: str
    raw_response_text: str
    usage: GeminiUsage = field(default_factory=GeminiUsage)
    retry_count: int = 0
    is_success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "record_id": self.record_id,
            "entity_type": self.entity_type,
            "target_field": self.target_field,
            "original_value": self.original_value,
            "proposed_value": self.proposed_value,
            "evidence": self.evidence,
            "evidence_url": self.evidence_url,
            "evidence_quote": self.evidence_quote,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "status": self.status,
            "limitations": self.limitations,
            "model_id": self.model_id,
            "provider": self.provider,
            "request_timestamp": self.request_timestamp,
            "response_timestamp": self.response_timestamp,
            "usage": self.usage.to_dict(),
            "retry_count": self.retry_count,
            "is_success": self.is_success,
            "error_message": self.error_message,
        }


class GeminiProvider:
    """
    Official Google Gemini API Client for Stage 3 Enrichment.
    Uses official Google Generative Language v1beta endpoint with JSON mode.
    """

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_id: Optional[str] = None,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        retry_delay_base: float = 1.0,
    ):
        # Resolve API key
        if api_key is None:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                env_file_vars = load_env_file()
                api_key = env_file_vars.get("GEMINI_API_KEY")

        self.api_key = api_key
        self.model_id = (
            model_id
            or os.environ.get("GEMINI_MODEL")
            or load_env_file().get("GEMINI_MODEL")
            or DEFAULT_GEMINI_MODEL
        )
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_delay_base = retry_delay_base

        # Total cumulative usage for this provider instance
        self.total_usage = GeminiUsage()
        self.call_history: List[Dict[str, Any]] = []

    def validate_api_key(self) -> Tuple[bool, str]:
        """Validates that API key is set and non-empty."""
        if not self.api_key or self.api_key.strip() == "" or self.api_key == "your_api_key_here":
            return False, (
                "GEMINI_API_KEY is not configured. Please set the GEMINI_API_KEY environment "
                "variable or add it to .env. Example: GEMINI_API_KEY=AIzaSy..."
            )
        return True, "API key configured."

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculates estimated USD cost based on token counts."""
        pricing = PRICING_PER_MILLION.get(self.model_id, PRICING_PER_MILLION["default"])
        prompt_cost = (prompt_tokens / 1_000_000.0) * pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000.0) * pricing["completion"]
        return prompt_cost + completion_cost

    def build_prompt(
        self,
        record_id: str,
        entity_type: str,
        target_field: str,
        original_value: Any,
        canonical_source_text: str,
        source_url: str,
        field_type_hint: str = "string",
    ) -> str:
        """Constructs an evidence-grounded prompt for the Gemini model."""
        prompt = f"""You are evaluating a candidate record for Stage 3 data enrichment.

RECORD CONTEXT:
- Record ID: {record_id}
- Entity Type: {entity_type}
- Target Field: {target_field}
- Expected Data Type: {field_type_hint}
- Original Field Value: {json.dumps(original_value)}
- Source URL: {source_url}

CANONICAL SOURCE TEXT (Ground Truth Evidence):
\"\"\"
{canonical_source_text}
\"\"\"

ENRICHMENT INSTRUCTIONS:
1. Examine the CANONICAL SOURCE TEXT carefully.
2. Determine if there is direct, verifiable evidence in the text to enrich or update the target field '{target_field}'.
3. If target field is a list (e.g., technologies, skills, contributions), provide a JSON list of verified items. All items MUST be explicitly supported in the text.
4. If target field is a string, provide a concise, factual string directly grounded in the text.
5. If the source text contains contradictory, ambiguous, or insufficient information, set status to 'NEEDS_REVIEW' or 'INSUFFICIENT_EVIDENCE' and do NOT invent values.
6. Extract a verbatim quote from the canonical source text in 'evidence_quote' that directly supports your proposed value.
7. Set status to one of: 'VERIFIED', 'NEEDS_REVIEW', 'INSUFFICIENT_EVIDENCE', 'FAILED'.
8. Provide your reasoning and identify any limitations in the evidence.

Return ONLY a valid JSON object with the following exact keys:
{{
  "record_id": "{record_id}",
  "entity_type": "{entity_type}",
  "target_field": "{target_field}",
  "original_value": {json.dumps(original_value)},
  "proposed_value": <enriched value: string, list of strings, or null>,
  "evidence": "<summary of facts observed in evidence>",
  "evidence_url": "{source_url}",
  "evidence_quote": "<verbatim excerpt from source text supporting the proposed value>",
  "reasoning": "<explanation of how the evidence supports the proposed value>",
  "confidence": <float between 0.0 and 1.0>,
  "status": "<VERIFIED | NEEDS_REVIEW | INSUFFICIENT_EVIDENCE | FAILED>",
  "limitations": "<any uncertainties, ambiguities, or gaps in the evidence>",
  "model_id": "{self.model_id}",
  "provider": "google-gemini"
}}
"""
        return prompt

    def generate_content_rest(
        self,
        prompt: str,
        request_id: str,
    ) -> Tuple[Dict[str, Any], GeminiUsage]:
        """
        Calls official Google Generative Language v1beta generateContent REST API.
        Includes bounded retries with exponential backoff.
        """
        is_valid, msg = self.validate_api_key()
        if not is_valid:
            raise ValueError(msg)

        url = f"{self.BASE_URL}/models/{self.model_id}:generateContent?key={self.api_key}"

        payload = {
            "system_instruction": {
                "parts": [{"text": STRICT_SYSTEM_INSTRUCTION}]
            },
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.0,
                "responseMimeType": "application/json",
            }
        }

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    resp = client.post(
                        url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    )

                    if resp.status_code == 200:
                        data = resp.json()
                        usage = GeminiUsage()
                        if "usageMetadata" in data:
                            u_meta = data["usageMetadata"]
                            usage.prompt_tokens = u_meta.get("promptTokenCount", 0)
                            usage.candidates_tokens = u_meta.get("candidatesTokenCount", 0)
                            usage.total_tokens = u_meta.get("totalTokenCount", 0)
                            usage.estimated_cost_usd = self.calculate_cost(
                                usage.prompt_tokens, usage.candidates_tokens
                            )
                        return data, usage

                    # Handle HTTP Errors
                    status = resp.status_code
                    resp_text = redact_secrets(resp.text, self.api_key)

                    # Non-retryable errors
                    if status in (400, 401, 403, 404):
                        raise RuntimeError(
                            f"Gemini API Client Error (HTTP {status}): {resp_text}"
                        )

                    # Retryable errors (429, 500, 503, 504)
                    if status in (429, 500, 502, 503, 504):
                        last_error = RuntimeError(
                            f"Gemini API Transient Error (HTTP {status}): {resp_text}"
                        )
                        if attempt < self.max_retries:
                            if status == 429:
                                match = re.search(r'retryDelay["\']?\s*:\s*["\']?(\d+)', resp_text)
                                if match and self.retry_delay_base >= 1.0:
                                    delay = min(float(match.group(1)) + 2.0, 65.0)
                                elif self.retry_delay_base < 1.0:
                                    delay = self.retry_delay_base * (2 ** attempt)
                                else:
                                    delay = max(5.0 * (2 ** attempt), 10.0)
                            else:
                                delay = self.retry_delay_base * (2 ** attempt)
                            logger.warning(
                                f"Attempt {attempt + 1} failed with HTTP {status}. "
                                f"Retrying in {delay:.1f}s..."
                            )
                            time.sleep(delay)
                            continue
                        else:
                            raise last_error

                    # Other status codes
                    raise RuntimeError(
                        f"Gemini API Unexpected Response (HTTP {status}): {resp_text}"
                    )

            except httpx.TimeoutException as e:
                last_error = TimeoutError(f"Gemini API request timed out after {self.timeout_seconds}s")
                if attempt < self.max_retries:
                    delay = self.retry_delay_base * (2 ** attempt)
                    logger.warning(f"Timeout on attempt {attempt + 1}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    raise last_error

            except httpx.RequestError as e:
                safe_err = redact_secrets(str(e), self.api_key)
                last_error = RuntimeError(f"Network error contacting Gemini API: {safe_err}")
                if attempt < self.max_retries:
                    delay = self.retry_delay_base * (2 ** attempt)
                    logger.warning(f"Network error on attempt {attempt + 1}: {safe_err}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    raise last_error

        raise last_error or RuntimeError("Unknown Gemini API error")

    def enrich_candidate(
        self,
        record_id: str,
        entity_type: str,
        target_field: str,
        original_value: Any,
        canonical_source_text: str,
        source_url: str,
        request_id: str,
        field_type_hint: str = "string",
    ) -> GeminiEnrichmentResponse:
        """
        Executes Gemini enrichment for a single candidate record.
        Parses structured JSON response and records usage/costs.
        Never falls back to offline heuristic on failure.
        """
        req_ts = datetime.now(timezone.utc).isoformat()
        prompt = self.build_prompt(
            record_id=record_id,
            entity_type=entity_type,
            target_field=target_field,
            original_value=original_value,
            canonical_source_text=canonical_source_text,
            source_url=source_url,
            field_type_hint=field_type_hint,
        )

        try:
            raw_data, usage = self.generate_content_rest(prompt, request_id)
            resp_ts = datetime.now(timezone.utc).isoformat()

            # Update instance cumulative usage
            self.total_usage.prompt_tokens += usage.prompt_tokens
            self.total_usage.candidates_tokens += usage.candidates_tokens
            self.total_usage.total_tokens += usage.total_tokens
            self.total_usage.estimated_cost_usd += usage.estimated_cost_usd

            # Extract generated content text
            candidates = raw_data.get("candidates", [])
            if not candidates:
                raise ValueError("Gemini API returned 0 candidates in response")

            part_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if not part_text:
                raise ValueError("Gemini API candidate content part text is empty")

            # Parse JSON
            try:
                parsed = json.loads(part_text)
            except json.JSONDecodeError as jde:
                # Try to locate JSON substring if model wrapped in markdown fences
                match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", part_text, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(1))
                else:
                    raise ValueError(f"Malformed JSON returned by Gemini: {jde} -- raw text: {part_text[:200]}")

            # Extract fields with safe defaults
            proposed_val = parsed.get("proposed_value")
            ev_summary = parsed.get("evidence", "")
            ev_quote = parsed.get("evidence_quote", "")
            ev_url = parsed.get("evidence_url", source_url)
            reasoning = parsed.get("reasoning", "")
            confidence = float(parsed.get("confidence", 0.5))
            status = parsed.get("status", "NEEDS_REVIEW")
            limitations = parsed.get("limitations", "")

            # Ensure status is one of allowed statuses
            valid_statuses = {"VERIFIED", "NEEDS_REVIEW", "INSUFFICIENT_EVIDENCE", "FAILED"}
            if status not in valid_statuses:
                status = "NEEDS_REVIEW"

            enrichment_resp = GeminiEnrichmentResponse(
                request_id=request_id,
                record_id=record_id,
                entity_type=entity_type,
                target_field=target_field,
                original_value=original_value,
                proposed_value=proposed_val,
                evidence=ev_summary,
                evidence_url=ev_url,
                evidence_quote=ev_quote,
                reasoning=reasoning,
                confidence=confidence,
                status=status,
                limitations=limitations,
                model_id=self.model_id,
                provider="google-gemini",
                request_timestamp=req_ts,
                response_timestamp=resp_ts,
                raw_response_text=part_text,
                usage=usage,
                is_success=True,
            )
            self.call_history.append(enrichment_resp.to_dict())
            return enrichment_resp

        except Exception as e:
            resp_ts = datetime.now(timezone.utc).isoformat()
            safe_error = redact_secrets(str(e), self.api_key)
            logger.error(f"Gemini enrichment failed for {record_id} ({target_field}): {safe_error}")

            fail_resp = GeminiEnrichmentResponse(
                request_id=request_id,
                record_id=record_id,
                entity_type=entity_type,
                target_field=target_field,
                original_value=original_value,
                proposed_value=None,
                evidence="",
                evidence_url=source_url,
                evidence_quote="",
                reasoning=f"API call failed: {safe_error}",
                confidence=0.0,
                status="FAILED",
                limitations=f"Exception during Gemini API execution: {safe_error}",
                model_id=self.model_id,
                provider="google-gemini",
                request_timestamp=req_ts,
                response_timestamp=resp_ts,
                raw_response_text="",
                usage=GeminiUsage(),
                is_success=False,
                error_message=safe_error,
            )
            self.call_history.append(fail_resp.to_dict())
            return fail_resp

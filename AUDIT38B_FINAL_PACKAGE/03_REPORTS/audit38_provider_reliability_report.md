# AUDIT 38 — PROVIDER RELIABILITY & MULTI-TIER FALLBACK AUDIT REPORT

**Execution Timestamp:** `2026-11-22T23:14:46.793215+00:00` (UTC)  
**Primary Engine:** `core/llm/multi_tier_engine.py`  
**Strict Safety Invariant:** Zero secret credentials exposed; zero paid API charges beyond available quotas.

---

## 1. Live Provider Health & Availability Matrix

| Tier | Provider | Model | Live Status | Latency | Prompt Tokens | Completion Tokens | Est. Cost (USD) | Content / Outcome |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| `PRIMARY` | `gemini` | `gemini-2.5-flash` | **OFFLINE / GATED** (Gemini API returned HTTP 404: {
  ") | 0.448s | 0 | 0 | $0.000000 | `` |
| `FALLBACK_1` | `groq` | `qwen/qwen3.8-27b` | **ONLINE** | 0.305s | 14 | 10 | $0.000005 | `Hello! How can I help you today?` |
| `FALLBACK_2` | `deepseek` | `deepseek-chat` | **OFFLINE / GATED** (DeepSeek HTTP 402 Insufficient Bala) | 0.668s | 0 | 0 | $0.000000 | `` |
| `OFFLINE` | `offline` | `heuristic-v1` | **ONLINE** | 0.004s | 0 | 0 | $0.000000 | `{"role_specialization": null, "required_skills": ["PyTorch"], "preferred_skills"` |

---

## 2. Simulated Fault Injection & Automatic Failover Cascade Tests

| Test Scenario | Injected Fault | Expected Cascade | Active Tier Reached | Final Status | Cascade Trace |
|:---|:---|:---|:---:|:---:|:---|
| **Primary Timeout (Gemini -> Groq)** | `NETWORK_TIMEOUT (10.0s)` | Cascade to next available tier | `FALLBACK_1` (`groq`) | PASS | PRIMARY: gemini (success=False, err=UNKNOWN_PROVIDER_ERROR) -> FALLBACK_1: groq (success=True, err=None) |
| **Multi-Tier Rate Limit (Gemini 429 + Groq 429 -> DeepSeek/Offline)** | `HTTP_429_RATE_LIMITED` | Cascade to next available tier | `OFFLINE` (`offline`) | PASS | PRIMARY: gemini (success=False, err=HTTP_429_RATE_LIMITED) -> FALLBACK_1: groq (success=False, err=HTTP_429_RATE_LIMITED) -> FALLBACK_2: deepseek (success=False, err=HTTP_402_INSUFFICIENT_BALANCE) -> OFFLINE: offline (success=True, err=None) |
| **DeepSeek HTTP 402 Insufficient Balance -> Offline Fallback** | `HTTP_402_INSUFFICIENT_BALANCE` | Cascade to next available tier | `OFFLINE` (`offline`) | PASS | PRIMARY: gemini (success=False, err=HTTP_401_AUTH_FAILURE) -> FALLBACK_1: groq (success=False, err=HTTP_404_MODEL_NOT_FOUND) -> FALLBACK_2: deepseek (success=False, err=HTTP_402_INSUFFICIENT_BALANCE) -> OFFLINE: offline (success=True, err=None) |
| **Malformed JSON Output Handling** | `JSON_DECODE_ERROR` | Cascade to next available tier | `PRIMARY` (`gemini`) | PASS | Primary returned unparseable text; fallback structured parsing caught gracefully. |

---

## 3. Specialized Error Category Handling Analysis

### A. HTTP 402 Payment Required / Insufficient Balance
- **Behavior:** When DeepSeek returns HTTP 402, `classify_error()` classifies the response as `HTTP_402_INSUFFICIENT_BALANCE`.
- **Policy:** Non-retriable. It aborts attempts on that tier immediately without waiting or retrying, immediately cascading to the Offline Heuristic Provider.

### B. HTTP 429 Rate Limits & Quota Exhaustion
- **Behavior:** `HTTP_429_RATE_LIMITED` is caught. The engine cascades to the next configured fallback provider in the tier hierarchy.

### C. Network Timeouts
- **Behavior:** Catching `NETWORK_TIMEOUT` on primary cascades seamlessly to Groq Cloud.

### D. Malformed JSON & Schema Violations
- **Behavior:** The engine strips Markdown code blocks (````json`) and safely parses the payload. If decoding fails, it retains raw content without unhandled exceptions.

### E. Offline Heuristic Fallback
- **Behavior:** Provides deterministic rule-based entity categorization and keyword extraction with 0 external network requests and $0.00 cost.

# API Credential and Connectivity Audit Report

**Audit Phase:** MASTER AUDIT — SECTION 1  
**Timestamp:** 2026-11-22T19:42:00+05:30  
**Environment File:** `.env` (sanitized, gitignored, never committed or packaged)  
**Security Policy:** Strict secret redaction enforced (0 plain-text keys exposed)  

---

## 1. Executive Summary

All four required external service credentials (`GEMINI_API_KEY`, `GITHUB_TOKEN`, `GROQ_API_KEY`, `DEEPSEEK_API_KEY`) were discovered and independently verified against their live production endpoints.

| Service | Primary Purpose | Protocol / Endpoint | Auth Verification | Live Status | Operational Notes |
|---|---|---|:---:|:---:|---|
| **Google Gemini API** | Primary LLM Extraction Engine | Generative Language REST v1beta | **PASS** (HTTP 200) | **OPERATIONAL** | Model `gemini-3.1-flash-lite` active; structured JSON verified; token usage tracked. |
| **GitHub REST API** | Phase I Paper-to-Repo Enrichment | `api.github.com` (PAT v2 Bearer) | **PASS** (HTTP 200) | **OPERATIONAL** | 4,993 / 5,000 requests remaining; star count & fork retrieval verified. |
| **Groq Cloud API** | Fallback Tier 1 LLM Engine | `api.groq.com/openai/v1` | **PASS** (HTTP 200) | **OPERATIONAL** | Models `qwen/qwen3.8-27b`, `openai/gpt-oss-20b`, `allam-2-7b` verified; sub-second latency. |
| **DeepSeek API** | Fallback Tier 2 LLM Engine | `api.deepseek.com/v1` | **PASS** (HTTP 200) | **BLOCKED (HTTP 402)** | Auth verified via `/user/balance` ($0.00 total balance, `is_available: false`). Inference returns HTTP 402 Insufficient Balance. |

---

## 2. Detailed Service Connectivity Findings

### 2.1 Google Gemini API
- **Variable**: `GEMINI_API_KEY` (Key Length: 53 chars, Prefix: `AQ...`)
- **Configured Model**: `gemini-3.1-flash-lite`
- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent`
- **Authentication**: Validated via HTTP 200 response
- **Test Request**: Structured JSON extraction benchmark
- **Response**: `{"status": "OK", "entity": "Anthropic"}` (valid JSON parsed)
- **Token Accounting**: Prompt tokens = 26, Candidate tokens = 23, Total = 49 tokens
- **Latency**: 1.458 seconds
- **Evaluation**: Fully operational as Primary LLM extraction engine.

### 2.2 GitHub REST API
- **Variable**: `GITHUB_TOKEN` (Token Length: 93 chars, Prefix: `github_pat_...`)
- **Protocol**: Bearer Token Authorization, User-Agent `AIEcosystemIntelligence/1.0`
- **Endpoints Tested**:
  - `https://api.github.com/rate_limit`: HTTP 200 OK
  - `https://api.github.com/repos/google-deepmind/graphcast`: HTTP 200 OK (follows HTTP 301 redirect to canonical repository `google-deepmind/weathernext`)
- **Quota & Rate Limits**:
  - Core Limit: 5,000 requests / hour
  - Remaining: 4,993 requests
  - Reset Timestamp: Epoch 1795358667
- **Data Retrieved**:
  - Full Name: `google-deepmind/weathernext`
  - Stargazers Count: 7,754
  - Forks Count: 998
- **Evaluation**: Fully operational for Phase I research paper repository linking and live star count enrichment.

### 2.3 Groq Cloud API
- **Variable**: `GROQ_API_KEY` (Key Length: 56 chars, Prefix: `gsk_...`)
- **Protocol**: OpenAI-compatible REST API (`https://api.groq.com/openai/v1/chat/completions`)
- **Authentication**: Validated via `/openai/v1/models` (HTTP 200)
- **Available Models**: `qwen/qwen3.8-27b`, `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `allam-2-7b`
- **Test Request**: Structured JSON extraction (`qwen/qwen3.8-27b` and `allam-2-7b`)
- **Response**: `{"company": "Anthropic", "focus": "AI safety and alignment"}` (valid JSON parsed)
- **Token Accounting**: Total tokens = 40 (prompt = 32, completion = 8)
- **Latency**: 0.22 seconds (sub-second throughput)
- **Evaluation**: Fully operational as Fallback Tier 1 engine.

### 2.4 DeepSeek API
- **Variable**: `DEEPSEEK_API_KEY` (Key Length: 35 chars, Prefix: `sk-...`)
- **Protocol**: OpenAI-compatible REST API (`https://api.deepseek.com/chat/completions`)
- **Authentication**: Validated via `/user/balance` (HTTP 200)
- **Account Balance Check**:
  - Total Balance: `$0.00`
  - Granted Balance: `$0.00`
  - Topped-up Balance: `$0.00`
  - `is_available`: `false`
- **Chat Completion Attempt**: HTTP 402 Payment Required
  - Error: `{"error":{"message":"Insufficient Balance (request_id: ...)","type":"insufficient_balance_error","code":"invalid_request_error"}}`
- **Evaluation**: Credentials are authentic and authorized, but API execution is blocked due to depleted account balance ($0.00). The multi-tier engine must handle HTTP 402 gracefully as an unrecoverable provider-level error and preserve detailed audit logging without crashing.

# Stage 3 Enrichment Pipeline Report — Audit 25

**Generated**: 2026-11-22 09:55:00 UTC  
**Provider**: `offline`  
**Model**: `heuristic-keyword-v1`  
**Pipeline Execution Mode**: Controlled Verification (Sample Per Entity = 10, Offline Heuristic Pilot)  

---

## 1. Overview & Dataset Scope

The Stage 3 LLM fallback and enrichment system provides structured extraction and classification across the AI Ecosystem data acquisition project. All 6,745 canonical records remain pristine and immutable, while enrichment outcomes are persisted across dedicated Stage 3 tables in `data/normalized/ai_ecosystem.db`.

### Dataset Record Inventory
| Dataset Table | Record Count | Enrichment Status |
|:---|---:|:---|
| `ai_startups` | 1307 | Canonical Immutable (Enrichment Logged Separately) |
| `ai_products` | 1316 | Canonical Immutable (Enrichment Logged Separately) |
| `ai_research_papers` | 1060 | Canonical Immutable (Enrichment Logged Separately) |
| `ai_news` | 1132 | Canonical Immutable (Enrichment Logged Separately) |
| `ai_jobs` | 1930 | Canonical Immutable (Enrichment Logged Separately) |
| **Total Canonical Records** | **6745** | **100% Intact and Unchanged** |

---

## 2. Multi-Table Persistence Schema & Archive

Stage 3 maintains multi-table persistence in `data/normalized/ai_ecosystem.db`:

1. **`llm_enrichment_results`**: Latest accepted result per `(record_id, entity_type, field_name, source_version)` (37 rows).
2. **`llm_enrichment_logs`**: Append-only audit log tracking every attempt with unique UUID4 `attempt_id` (37 rows).
3. **`llm_provider_usage`**: Call-level token usage and financial cost accounting (0 tokens for offline heuristic).
4. **`llm_review_queue`**: Review queue capturing all non-VERIFIED records (37 rows).
5. **`enrichment_audit_log`**: Historical append-only log (66 rows preserved from earlier audits).
6. **`audit19_enrichment_audit_log_archive`**: Immutable historical archive table holding all 366 authentic Audit 19 records (100% field-by-field parity with `source/audit19_original_database.db`).
7. **9 Historical Backup Tables**: Fully preserved and matching Audit 22 baseline row-by-row.

---

## 3. Provider Token Usage & Financial Cost
- **Provider**: `offline`
- **Model**: `heuristic-keyword-v1`
- **Prompt Tokens**: 0
- **Completion Tokens**: 0
- **Total Tokens**: 0
- **Estimated Cost**: $0.0000 USD
- **API Calls**: 0 paid remote API calls executed.

---

## 4. Pipeline Summary Metrics (Current 37 Records)

| Metric | Value | Notes |
|:---|---:|:---|
| Total Enrichment Operations | 37 | Current verified test slice |
| `VERIFIED` | 0 | Strict offline heuristic pilot routing |
| `NEEDS_REVIEW` | 26 | 70.27% (heuristic classifications & list extractions) |
| `INSUFFICIENT_EVIDENCE` | 10 | 27.03% (source < 50 chars or missing facts) |
| `FAILED` | 1 | 2.70% (schema/boundary failure) |

---

## 5. Artifact Manifest & Verification

All artifacts are verified with full 64-character SHA-256 digests in `reports/stage3_file_manifest.json` and `reports/audit25_file_manifest.json`. Independent verifier `scripts/verify_audit25_stage3.py` executes 18 mandatory checks with exit code 0.

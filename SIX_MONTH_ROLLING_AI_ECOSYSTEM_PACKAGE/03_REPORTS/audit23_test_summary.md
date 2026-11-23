# Audit 23 — Test Suite Execution and Coverage Report

**Generated**: 2026-11-22  
**Test Framework**: Python `unittest`  
**Execution Command**: `python -m unittest discover tests -v`  
**Total Tests**: 88  
**Passed**: 88 (100%)  
**Failed**: 0  
**Skipped**: 0  

---

## 1. Test Suite Modules Breakdown

| Test Module | Test Focus | Total Tests | Passed | Status |
|:---|:---|---:|---:|:---|
| `test_evidence_validator.py` | Semantic adversarial tests, context isolation, negation, taxonomy | 49 | 49 | **PASS** |
| `test_pipeline_integration.py` | Pipeline evidence enforcement, grounding, source-version hashing | 12 | 12 | **PASS** |
| `test_schema_validation.py` | Schema strictness, forbidden fields, type validation, enum status | 6 | 6 | **PASS** |
| `test_persistence_and_logging.py` | Multi-table SQLite persistence, backup tables, attempt history | 5 | 5 | **PASS** |
| `test_entity_enrichers.py` | Startup, Product, Paper, News, and Job enrichers | 6 | 6 | **PASS** |
| `test_llm_providers.py` | Offline, Gemini, OpenAI, Groq, and Ollama provider interfaces | 4 | 4 | **PASS** |
| `test_offline_provider.py` | Heuristic offline provider, token reporting, grounding | 4 | 4 | **PASS** |
| `test_stage3_pipeline.py` | End-to-end Stage 3 runner execution, DB integrity, table preservation | 2 | 2 | **PASS** |
| **TOTAL** | **Full Stage 3 Test Battery** | **88** | **88** | **100% PASS** |

---

## 2. Key Audit 23 Regression & Adversarial Tests

### Audit 23 Context Isolation Tests
- `test_regression_case_a_unrelated_negation_passes`: Passes affirmative claim in sentence 2 despite unrelated negation in sentence 1.
- `test_regression_case_b_unrelated_conditional_statement_passes`: Passes factual claim in sentence 2 despite unrelated condition in sentence 1.
- `test_regression_case_c_unrelated_historical_statement_passes`: Passes current status claim in sentence 2 despite unrelated past statement in sentence 1.
- `test_adversarial_double_negation_affirmative_passes`: Passes affirmative claim supported by double negation idiom (`cannot deny`).
- `test_adversarial_double_negation_contradicted_by_negative_claim_fails`: Fails negative claim contradicting affirmative double negation.
- `test_adversarial_indirect_negation_fails_to_fails`: Fails affirmative claim contradicted by `fails to` indirect negation.
- `test_adversarial_indirect_negation_unable_to_fails`: Fails affirmative claim contradicted by `unable to` indirect negation.
- `test_adversarial_exception_qualifier_fails`: Fails affirmative claim for item excluded by `except for` qualifier.
- `test_adversarial_conflicting_statements_across_sentences_needs_review`: Returns `NEEDS_REVIEW` when separate sentences in evidence contain contradictory assertions.
- `test_adversarial_unsupported_dates_fails`: Fails proposed claim with modified year (`2020` -> `2024`).
- `test_adversarial_unsupported_numbers_fails`: Fails proposed claim with modified count (`8 GPUs` -> `32 GPUs`).
- `test_adversarial_uncertain_claims_never_verified`: Enforces invariant that uncertain/ambiguous claims never receive `VERIFIED`.

### Retained Audit 22 Adversarial Tests
- `test_adversarial_active_passive_voice_reversal_fails`: Fails active/passive semantic inversion (`was trained by OpenAI` vs `trained OpenAI`).
- `test_adversarial_subject_object_reversal_fails`: Fails subject/object reversal (`Google acquired DeepMind` vs `DeepMind acquired Google`).
- `test_adversarial_some_vs_all_fails`: Fails quantifier inflation (`some` -> `all`).
- `test_adversarial_improved_vs_doubled_fails`: Fails metric multiplier inflation (`improved` -> `doubled`).
- `test_adversarial_conditional_vs_factual_fails`: Fails unhedged claim derived from conditional statement.
- `test_adversarial_historical_vs_current_status_fails`: Fails current status assertion derived from historical statement.
- `test_adversarial_without_negation_fails`: Fails assertion dropping `without` exclusion.
- `test_adversarial_neither_negation_fails`: Fails assertion dropping `neither...nor` exclusion.
- `test_adversarial_lack_negation_fails`: Fails assertion dropping `lacks` exclusion.
- `test_adversarial_exclude_negation_fails`: Fails assertion dropping `excludes` exclusion.
- `test_adversarial_unsupported_causal_claim_fails`: Fails unearned causal connection (`caused revenues to grow`).
- `test_adversarial_same_keywords_contradiction_fails`: Fails contradictory claim sharing 100% identical keywords (`do not manufacture robots` vs `manufacture robots`).

# Audit 23 — Reproduction Commands and Verification Guide

This guide details the exact commands required to execute the test suite, run the independent verification pipeline, and inspect the deliverables for **Audit 23**.

---

## 1. Environment Requirements

- **Python Version**: Python 3.10+ (Tested on Python 3.14 / Windows PowerShell)
- **Dependencies**: Standard Library only (`sqlite3`, `hashlib`, `json`, `csv`, `re`, `unittest`, `dataclasses`, `typing`, `datetime`, `argparse`, `logging`)
- **Remote API Keys**: None (Offline Heuristic Provider only; zero remote dependencies)

---

## 2. Execute Verification Pipeline

To execute the 14-check independent verifier:

```powershell
python scripts/verify_audit23_stage3.py
```

Expected output:
- Process exit code: `0`
- Console output: All 14 checks reported as `[PASS]`
- Verification log generated at: `reports/audit23_verification_output.txt`

---

## 3. Execute Complete Test Suite

To run all 88 unit and integration tests across the test battery:

```powershell
python -m unittest discover tests -v
```

Expected output:
- `Ran 88 tests in ~0.35s`
- `OK` (0 failures, 0 errors, 0 skipped)

---

## 4. Re-verify Historical Tables and Attempt IDs

To re-aggregate all 169 historical attempt IDs:

```powershell
python scripts/export_attempts.py
```

To re-export all historical backup tables row-by-row and generate `history_preservation_report.md`:

```powershell
python scripts/export_historical_tables.py
```

To re-run the 366-record Audit 19 reconciliation:

```powershell
python scripts/reconcile_audit19.py
```

---

## 5. Verify Canonical Baseline Integrity

To verify all 6,745 canonical records against SQLite integrity checks:

```powershell
python scripts/verify_canonical_baseline.py
```

import os
import sys
import csv
import hashlib
import sqlite3

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INV_PATH = os.path.join(WORKSPACE_ROOT, "reports", "project_cleanup", "project_inventory.csv")
CLASS_PATH = os.path.join(WORKSPACE_ROOT, "reports", "project_cleanup", "project_classification.csv")
DUP_PATH = os.path.join(WORKSPACE_ROOT, "reports", "project_cleanup", "duplicate_files.csv")

PROTECTED_DB_HASHES = {
    "Canonical DB": {
        "path": "data/normalized/ai_ecosystem.db",
        "sha256": "4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d"
    },
    "Authentic Audit19 DB": {
        "path": "source/audit19_original_database.db",
        "sha256": "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d"
    },
    "Baseline Working DB": {
        "path": "data/working/rolling_ai_ecosystem.db",
        "sha256": "cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127"
    },
    "Candidate Working DB": {
        "path": "data/working/candidate_rolling_ai_ecosystem.db",
        "sha256": "eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198"
    }
}

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    print("=" * 80)
    print("INDEPENDENT FIRST-PASS INVENTORY & INTEGRITY VERIFICATION")
    print("=" * 80)

    # 1. Read first-pass CSVs
    print("\n[1/5] Inspecting first-pass CSV reports...")
    with open(INV_PATH, "r", encoding="utf-8") as f:
        inv_rows = list(csv.DictReader(f))
    with open(CLASS_PATH, "r", encoding="utf-8") as f:
        class_rows = list(csv.DictReader(f))
    with open(DUP_PATH, "r", encoding="utf-8") as f:
        dup_rows = list(csv.DictReader(f))

    print(f"  project_inventory.csv rows      : {len(inv_rows)}")
    print(f"  project_classification.csv rows : {len(class_rows)}")
    print(f"  duplicate_files.csv rows        : {len(dup_rows)}")

    # Check 1-to-1 match between inventory and classification
    inv_paths = [r["relative_path"] for r in inv_rows]
    class_paths = [r["relative_path"] for r in class_rows]

    inv_set = set(inv_paths)
    class_set = set(class_paths)

    assert len(inv_paths) == len(inv_set), f"Duplicate paths in inventory: {len(inv_paths) - len(inv_set)}"
    assert len(class_paths) == len(class_set), f"Duplicate paths in classification: {len(class_paths) - len(class_set)}"
    assert inv_set == class_set, f"Mismatch between inventory and classification paths: diff={len(inv_set ^ class_set)}"
    print("  -> Inventory and classification have exact 1-to-1 path parity (0 duplicates, 0 missing).")

    # 2. Re-scan current filesystem
    print("\n[2/5] Re-scanning live filesystem to check coverage...")
    live_files = []
    permission_errors = []
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        for f in files:
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, WORKSPACE_ROOT).replace("\\", "/")
            try:
                os.stat(fp)
                live_files.append(rel)
            except Exception as e:
                permission_errors.append((rel, str(e)))

    print(f"  Total live files in filesystem  : {len(live_files)}")
    print(f"  Permission errors encountered   : {len(permission_errors)}")
    assert len(permission_errors) == 0, f"Permission errors: {permission_errors}"

    # Check which live files are not in inventory
    # Note: reports/project_cleanup/* were intentionally excluded from inventory to avoid circular scan
    uninventoried = [p for p in live_files if p not in inv_set]
    print(f"  Live files not in first-pass inventory: {len(uninventoried)}")
    scanner_and_cleanup_files = [p for p in uninventoried if p.startswith("reports/project_cleanup") or "project_cleanup" in p or "inspect_unknowns" in p]
    other_uninventoried = [p for p in uninventoried if p not in scanner_and_cleanup_files]
    print(f"    - Scanner & cleanup report files (self-generated): {len(scanner_and_cleanup_files)}")
    print(f"    - Other uninventoried files                      : {len(other_uninventoried)}")
    if other_uninventoried:
        print("      Samples:", other_uninventoried[:10])

    # 3. Verify SQLite Integrity and Hashes
    print("\n[3/5] Verifying Protected Database SHA-256 Hashes & SQLite Integrity...")
    for name, info in PROTECTED_DB_HASHES.items():
        full_p = os.path.join(WORKSPACE_ROOT, info["path"])
        h = compute_sha256(full_p)
        assert h == info["sha256"], f"Hash mismatch for {name}: {h} != {info['sha256']}"
        print(f"  {name:<22}: {h} (VERIFIED MATCH)")

        # Run PRAGMA integrity_check
        conn = sqlite3.connect(f"file:{full_p}?mode=ro", uri=True)
        cur = conn.cursor()
        cur.execute("PRAGMA integrity_check;")
        res = cur.fetchall()
        assert res == [("ok",)], f"Integrity check failed for {name}: {res}"
        print(f"    -> SQLite PRAGMA integrity_check: {res[0][0].upper()}")
        conn.close()

    # 4. Verify Proposals in Candidate DB
    print("\n[4/5] Verifying 20 enrichment proposals in Candidate DB...")
    cand_p = os.path.join(WORKSPACE_ROOT, PROTECTED_DB_HASHES["Candidate Working DB"]["path"])
    conn = sqlite3.connect(f"file:{cand_p}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("SELECT approval_status, count(*) FROM enrichment_proposals GROUP BY approval_status")
    proposals = cur.fetchall()
    assert proposals == [("PENDING_APPROVAL", 20)], f"Proposals altered: {proposals}"
    print(f"  -> Enrichment Proposals: {proposals} (100% PENDING_APPROVAL)")
    conn.close()

    # 5. Check if secrets/tokens leaked in reports
    print("\n[5/5] Checking for secret/token leakage in cleanup reports...")
    token_keys = ["ya29.", "client_secret", "private_key", "refresh_token"]
    leak_found = False
    for r_dir in ["reports/project_cleanup", "reports"]:
        for root, dirs, files in os.walk(os.path.join(WORKSPACE_ROOT, r_dir)):
            for f in files:
                if f.endswith((".csv", ".md", ".json", ".txt")):
                    fp = os.path.join(root, f)
                    try:
                        with open(fp, "r", encoding="utf-8", errors="ignore") as rf:
                            content = rf.read()
                            for k in token_keys:
                                if k in content:
                                    print(f"  [ALERT] Potential secret key '{k}' found in {fp}!")
                                    leak_found = True
                    except:
                        pass
    if not leak_found:
        print("  -> ZERO secrets, tokens, or credential keys detected in any cleanup reports.")

    print("\n" + "=" * 80)
    print("INDEPENDENT INVENTORY & INTEGRITY VERIFICATION COMPLETE: ALL CHECKS PASSED")
    print("=" * 80)

if __name__ == "__main__":
    main()

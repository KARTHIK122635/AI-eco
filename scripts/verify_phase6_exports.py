import csv
import hashlib
import json
import os
import sqlite3

def run_export_verification():
    manifest_path = os.path.join("data", "exports", "phase6", "export_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    db_path = os.path.abspath(manifest["export_metadata"]["source_database_path"])
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cursor = conn.cursor()

    print("=== EXPORT VERIFICATION AUDIT ===")
    print(f"Manifest source DB: {db_path}")

    # 1. DB source table counts
    cursor.execute("SELECT COUNT(*) FROM github_repositories")
    db_repos_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM github_metrics_history")
    db_metrics_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM github_repository_associations")
    db_assocs_count = cursor.fetchone()[0]

    print(f"DB github_repositories: {db_repos_count}")
    print(f"DB github_metrics_history: {db_metrics_count}")
    print(f"DB github_repository_associations: {db_assocs_count}")

    # 2. Check each exported file
    formula_injection_violations = []
    none_string_violations = []

    for fname, meta in manifest["exported_files"].items():
        file_path = meta["path"]
        with open(file_path, "rb") as f:
            raw_bytes = f.read()
            computed_sha = hashlib.sha256(raw_bytes).hexdigest()

        expected_sha = meta["sha256"]
        assert computed_sha == expected_sha, f"Hash mismatch for {fname}: computed {computed_sha} != expected {expected_sha}"

        if fname.endswith(".csv"):
            with open(file_path, "r", encoding="utf-8") as f:
                reader = list(csv.reader(f))
                header = reader[0]
                rows = reader[1:]
                print(f"CSV {fname}: {len(rows)} data rows, {len(header)} columns. SHA256: {computed_sha[:16]}... OK")

                for r_idx, row in enumerate(rows):
                    for c_idx, val in enumerate(row):
                        if val.strip() in ["None", "null", "NULL"]:
                            none_string_violations.append((fname, r_idx, header[c_idx], val))
                        # Check unescaped formula triggers
                        if val and val[0] in ["=", "+", "-", "@"]:
                            formula_injection_violations.append((fname, r_idx, header[c_idx], val))

    print(f"Formula injection violations: {len(formula_injection_violations)}")
    print(f"Unsanitized None/null string violations: {len(none_string_violations)}")

    # 3. Aggregate totals reconciliation
    cursor.execute("SELECT SUM(latest_stars), SUM(latest_forks), SUM(latest_open_issues) FROM github_repositories")
    db_stars, db_forks, db_issues = cursor.fetchone()

    # Calculate from CSV
    repo_csv = os.path.join("data", "exports", "phase6", "github_repositories.csv")
    csv_stars = 0
    csv_forks = 0
    csv_issues = 0
    with open(repo_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            csv_stars += int(r["latest_stars"] or 0)
            csv_forks += int(r["latest_forks"] or 0)
            csv_issues += int(r["latest_open_issues"] or 0)

    print(f"Stars reconciliation: DB={db_stars}, CSV={csv_stars}, Match={db_stars == csv_stars}")
    print(f"Forks reconciliation: DB={db_forks}, CSV={csv_forks}, Match={db_forks == csv_forks}")
    print(f"Issues reconciliation: DB={db_issues}, CSV={csv_issues}, Match={db_issues == csv_issues}")

    conn.close()
    print("Verification completed successfully!")

if __name__ == "__main__":
    run_export_verification()

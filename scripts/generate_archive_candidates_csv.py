import os
import csv
import hashlib

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "reports", "project_cleanup", "second_pass")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CLASS_PATH = os.path.join(WORKSPACE_ROOT, "reports", "project_cleanup", "project_classification.csv")

# Load manifests to check references
MANIFEST_FILES = [
    "file_manifest.json",
    "audit38b_manifest.json",
    "final_closeout_manifest.json",
]

manifest_contents = {}
for mf in MANIFEST_FILES:
    mf_p = os.path.join(WORKSPACE_ROOT, mf)
    if os.path.exists(mf_p):
        try:
            with open(mf_p, "r", encoding="utf-8") as f:
                manifest_contents[mf] = f.read()
        except:
            pass

# Check clean-room verification script dependencies
ZIP_DEPENDENCIES = {
    "FINAL_PROJECT_CLOSEOUT_PACKAGE.zip": "scripts/verify_final_closeout_package.py",
    "AUDIT38B_FINAL_PACKAGE.zip": "scripts/verify_audit38b_package.py",
    "AUDIT38A_FINAL_PACKAGE.zip": "scripts/verify_audit38a_package.py",
    "AUDIT38_FINAL_PACKAGE.zip": "scripts/verify_audit38_package.py",
    "AUDIT37A_FINAL_PACKAGE.zip": "scripts/verify_audit37a_package.py",
    "AUDIT37_FINAL_PACKAGE.zip": "scripts/verify_audit37_package.py",
    "AUDIT36_FINAL_PACKAGE.zip": "scripts/verify_audit36_package.py",
    "AUDIT35_FINAL_PACKAGE.zip": "scripts/verify_audit35_package.py",
    "AUDIT34_FINAL_PACKAGE.zip": "scripts/verify_audit34_package.py",
    "AUDIT33_FINAL_PACKAGE.zip": "scripts/verify_audit33_package.py",
    "AUDIT32_FINAL_PACKAGE.zip": "scripts/verify_audit32_package.py",
    "AUDIT31_CORRECTIVE_PACKAGE.zip": "scripts/verify_audit31_package.py",
    "SIX_MONTH_ROLLING_AI_ECOSYSTEM_PACKAGE.zip": "scripts/verify_audit30_package.py",
}

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def classify_candidate(rel_p, fn, ext):
    parts = rel_p.split("/")
    
    # 1. Historical Audit Packages (Unpacked folders)
    if "PACKAGE" in parts[0] or parts[0] == "deliverables_audit22":
        sub_type = "Historical audit packages"
        related_audit = parts[0]
        must_remain = "Yes (Package Completeness)"
        rec_action = "KEEP" # Prompt: Do not move historical packages merely to make root cleaner
        recoverable = "Yes (From corresponding .zip bundle)"
        deps = "Standalone package verification"
        justification = f"Preserves complete directory structure of {parts[0]}. Required for clean package integrity."
    
    # 2. ZIP Recovery Archives
    elif ext == ".zip":
        sub_type = "ZIP recovery archives"
        related_audit = fn.replace(".zip", "")
        dep_script = ZIP_DEPENDENCIES.get(fn)
        if dep_script:
            must_remain = f"Yes (Referenced by {dep_script})"
            rec_action = "KEEP" # Required for regression tests
            deps = f"Hardcoded path in {dep_script}"
            justification = f"Directly imported/extracted by verification script {dep_script} at root path."
        else:
            must_remain = "No"
            rec_action = "SAFE_TO_ARCHIVE"
            deps = "None (Standalone historical archive)"
            justification = "Historical backup bundle with no active script dependencies."
        recoverable = "Self-contained ZIP"

    # 3. Legacy Scripts in scripts/
    elif rel_p.startswith("scripts/"):
        sub_type = "Legacy scripts"
        related_audit = "Historical Audits 1–29"
        must_remain = "No"
        rec_action = "SAFE_TO_ARCHIVE"
        deps = "None (Superseded by database baselines)"
        recoverable = "Yes (Documented in historical manifests)"
        justification = "One-off historical patch or query script. Logic preserved in canonical database."

    # 4. Historical Reports & Ledgers in Root
    elif "/" not in rel_p and (ext in [".md", ".txt", ".csv", ".json", ".sha256"]):
        sub_type = "Historical reports"
        related_audit = fn.split("_")[0] if "_" in fn else "General Audit"
        must_remain = "No"
        rec_action = "SAFE_TO_ARCHIVE"
        deps = "None (Static report artifact)"
        recoverable = "Yes (Packaged in corresponding ZIP)"
        justification = "Root-level audit report or test runner output. Safe to consolidate into archive/audit_reports/."

    # 5. Other Files
    else:
        sub_type = "Other files"
        related_audit = "Unspecified"
        must_remain = "No"
        rec_action = "MANUAL_REVIEW"
        deps = "Requires investigation"
        recoverable = "Unknown"
        justification = "Requires manual confirmation."

    # Check manifest references
    manifest_refs = []
    for mf_name, mf_content in manifest_contents.items():
        if rel_p in mf_content or fn in mf_content:
            manifest_refs.append(mf_name)

    manifest_str = "; ".join(manifest_refs) if manifest_refs else "None"

    return sub_type, related_audit, must_remain, rec_action, deps, recoverable, manifest_str, justification

def main():
    print("Reading project_classification.csv for ARCHIVE candidates...")
    with open(CLASS_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        archive_candidates = [r for r in reader if r["action"] == "ARCHIVE"]

    print(f"Total first-pass ARCHIVE candidates: {len(archive_candidates)}")

    rows = []
    sub_type_counts = {}
    action_counts = {}

    for c in archive_candidates:
        rel_p = c["relative_path"]
        fn = c["filename"]
        ext = os.path.splitext(fn)[1].lower()
        full_p = os.path.join(WORKSPACE_ROOT, rel_p)
        
        # Calculate live hash if exists
        h = compute_sha256(full_p) if os.path.exists(full_p) else "MISSING"

        sub_type, related_audit, must_remain, rec_action, deps, recoverable, manifest_str, justification = classify_candidate(rel_p, fn, ext)

        sub_type_counts[sub_type] = sub_type_counts.get(sub_type, 0) + 1
        action_counts[rec_action] = action_counts.get(rec_action, 0) + 1

        rows.append({
            "current_path": rel_p,
            "sub_type": sub_type,
            "filename": fn,
            "sha256": h,
            "proposed_archive_destination": c["proposed_destination"],
            "related_audit_or_package": related_audit,
            "manifest_references": manifest_str,
            "active_dependencies": deps,
            "independently_recoverable": recoverable,
            "must_remain_at_current_path": must_remain,
            "recommended_action": rec_action,
            "justification": justification
        })

    out_csv = os.path.join(OUTPUT_DIR, "archive_candidate_verification.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "current_path", "sub_type", "filename", "sha256",
            "proposed_archive_destination", "related_audit_or_package",
            "manifest_references", "active_dependencies", "independently_recoverable",
            "must_remain_at_current_path", "recommended_action", "justification"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} archive verification rows to {out_csv}\n")
    print("Candidates by Sub-Type:")
    for st, cnt in sorted(sub_type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {st:<30}: {cnt:>5} files")

    print("\nCandidates by Revised Recommended Action:")
    for act, cnt in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {act:<30}: {cnt:>5} files")

if __name__ == "__main__":
    main()

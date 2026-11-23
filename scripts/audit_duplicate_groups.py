import os
import csv
import hashlib
from collections import defaultdict

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "reports", "project_cleanup", "second_pass")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def get_package_name(path):
    parts = path.split("/")
    if len(parts) > 1 and ("PACKAGE" in parts[0] or parts[0] == "deliverables_audit22"):
        return parts[0]
    return "ROOT_OR_LOCAL"

def path_priority(p):
    if p.startswith("data/normalized/"): return 0
    if p.startswith("source/"): return 1
    if p.startswith("data/working/"): return 2
    if p.startswith("core/"): return 3
    if p.startswith("config/"): return 4
    if p.startswith("sources/"): return 5
    if p.startswith("src/"): return 6
    if p.startswith("scripts/"): return 7
    if p.startswith("reports/"): return 8
    if "PACKAGE" in p or "deliverables" in p: return 12
    return 10

def main():
    print("Scanning filesystem to identify and verify duplicate groups...")

    all_files = []
    files_by_hash = defaultdict(list)

    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        rel_dir = os.path.relpath(root, WORKSPACE_ROOT).replace("\\", "/")
        if rel_dir.startswith("reports/project_cleanup"):
            continue
        for f in files:
            fp = os.path.join(root, f)
            rel_p = os.path.relpath(fp, WORKSPACE_ROOT).replace("\\", "/")
            try:
                sz = os.path.getsize(fp)
                h = compute_sha256(fp)
                all_files.append((rel_p, sz, h))
                files_by_hash[h].append((rel_p, sz))
            except Exception as e:
                pass

    duplicate_groups = {h: paths for h, paths in files_by_hash.items() if len(paths) > 1}
    print(f"Total unique duplicate hashes: {len(duplicate_groups)}")

    csv_rows = []
    group_idx = 1

    package_distribution = defaultdict(int)

    for h, file_list in duplicate_groups.items():
        sorted_files = sorted(file_list, key=lambda x: path_priority(x[0]))
        canonical_p, canonical_sz = sorted_files[0]

        for dup_p, dup_sz in sorted_files[1:]:
            pkg = get_package_name(dup_p)
            package_distribution[pkg] += 1

            # Determine dependency status and recommended action
            if pkg != "ROOT_OR_LOCAL":
                dep_status = f"COMPONENT_OF_FROZEN_{pkg}"
                rec_action = "KEEP"  # Rule 8 & Prompt: Preserve package completeness
                justification = f"Preserves complete standalone directory structure of {pkg}. Removing would break frozen package completeness."
            else:
                dep_status = "LOCAL_REDUNDANCY"
                rec_action = "MANUAL_REVIEW"
                justification = f"Byte-identical duplicate of {canonical_p} in local project tree."

            csv_rows.append({
                "duplicate_group_id": f"DUP_GRP_{group_idx:04d}",
                "original_path": canonical_p,
                "duplicate_path": dup_p,
                "sha256": h,
                "package_name": pkg,
                "dependency_status": dep_status,
                "recommended_action": rec_action,
                "justification": justification
            })
        group_idx += 1

    out_csv = os.path.join(OUTPUT_DIR, "duplicate_group_verification.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "duplicate_group_id", "original_path", "duplicate_path", "sha256",
            "package_name", "dependency_status", "recommended_action", "justification"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"Wrote {len(csv_rows)} duplicate verification records to {out_csv}")
    print("\nDuplicate Instances by Historical Package:")
    for pkg, cnt in sorted(package_distribution.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pkg:<45}: {cnt:>5} duplicate instances")

if __name__ == "__main__":
    main()

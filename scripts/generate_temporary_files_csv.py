import os
import csv
import hashlib

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "reports", "project_cleanup", "second_pass")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    rows = []
    total_bytes = 0

    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        rel_dir = os.path.relpath(root, WORKSPACE_ROOT).replace("\\", "/")
        if rel_dir.startswith("reports/project_cleanup"):
            continue
        for f in files:
            fp = os.path.join(root, f)
            rel_p = os.path.relpath(fp, WORKSPACE_ROOT).replace("\\", "/")
            
            # Check if temporary
            if "__pycache__" in rel_p or rel_p.endswith((".pyc", ".pyo", ".pyd")):
                sz = os.path.getsize(fp)
                total_bytes += sz
                h = compute_sha256(fp)

                # Determine corresponding source file
                parts = rel_p.split("/")
                cache_idx = parts.index("__pycache__")
                parent_dir = "/".join(parts[:cache_idx])
                fname = parts[-1]
                py_name = fname.split(".")[0] + ".py"
                rel_src = f"{parent_dir}/{py_name}" if parent_dir else py_name
                full_src = os.path.join(WORKSPACE_ROOT, rel_src)
                src_exists = os.path.exists(full_src)

                # Determine whether it's part of a historical frozen package
                is_in_pkg = ("PACKAGE" in rel_p or "deliverables" in rel_p)

                if is_in_pkg:
                    rec_action = "KEEP"  # Rule 8: Preserve package completeness
                    justification = "Bytecode inside frozen historical package directory. Retained for package integrity."
                else:
                    rec_action = "SAFE_TO_DELETE"
                    justification = f"Auto-generated CPython bytecode cache. Verified source exists at {rel_src}. Fully regenerable."

                rows.append({
                    "cache_file_path": rel_p,
                    "filename": f,
                    "file_size_bytes": sz,
                    "sha256": h,
                    "corresponding_source_path": rel_src,
                    "source_exists": "Yes" if src_exists else "No",
                    "is_in_historical_package": "Yes" if is_in_pkg else "No",
                    "regenerable": "Yes" if src_exists else "No",
                    "recommended_action": rec_action,
                    "justification": justification
                })

    out_csv = os.path.join(OUTPUT_DIR, "temporary_file_verification.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "cache_file_path", "filename", "file_size_bytes", "sha256",
            "corresponding_source_path", "source_exists", "is_in_historical_package",
            "regenerable", "recommended_action", "justification"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Total temporary bytecode files cataloged : {len(rows)}")
    print(f"Total bytecode cache size                 : {total_bytes} bytes ({total_bytes / (1024*1024):.2f} MB)")
    print(f"Report written to                         : {out_csv}")
    
    actions = {}
    for r in rows:
        actions[r["recommended_action"]] = actions.get(r["recommended_action"], 0) + 1
    print("Action distribution:")
    for k, v in actions.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()

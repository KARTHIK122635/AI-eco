import os

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pyc_files = []
non_pyc_temps = []

for root, dirs, files in os.walk(WORKSPACE_ROOT):
    for f in files:
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, WORKSPACE_ROOT).replace("\\", "/")
        if "__pycache__" in rel or rel.endswith((".pyc", ".pyo", ".pyd")):
            pyc_files.append((rel, os.path.getsize(fp)))
        elif rel.endswith(".tmp") or f.startswith("~"):
            non_pyc_temps.append((rel, os.path.getsize(fp)))

print(f"Total .pyc / bytecode files : {len(pyc_files)}")
print(f"Total other temporary files : {len(non_pyc_temps)}")

total_pyc_bytes = sum(s for _, s in pyc_files)
print(f"Total bytecode cache size   : {total_pyc_bytes} bytes ({total_pyc_bytes / (1024*1024):.2f} MB)")

# Verify corresponding .py source exists for .pyc files
missing_sources = []
for rel, sz in pyc_files:
    # A .pyc in __pycache__/foo.cpython-314.pyc corresponds to foo.py in parent dir
    parts = rel.split("/")
    if "__pycache__" in parts:
        cache_idx = parts.index("__pycache__")
        parent_dir = "/".join(parts[:cache_idx])
        fname = parts[-1]
        py_name = fname.split(".")[0] + ".py"
        src_path = os.path.join(WORKSPACE_ROOT, parent_dir, py_name) if parent_dir else os.path.join(WORKSPACE_ROOT, py_name)
        if not os.path.exists(src_path):
            missing_sources.append((rel, src_path))

print(f"Bytecode files without corresponding .py source: {len(missing_sources)}")
if missing_sources:
    print("Samples:", missing_sources[:5])

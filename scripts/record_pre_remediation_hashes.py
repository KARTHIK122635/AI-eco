import hashlib

databases = {
    "Canonical DB": ("data/normalized/ai_ecosystem.db", "4949352d4f568f3f6128f398591cd8edac2eba45496c24535edb6c096398b95d"),
    "Authentic Audit19 DB": ("source/audit19_original_database.db", "1958c59f1a02e5a4bd274f114fdcfdd40942239f518eb662119962a263c84d4d"),
    "Baseline Working DB": ("data/working/rolling_ai_ecosystem.db", "cbc1814cf3c6546a4dfa1d2e731648aead070b133b38892ddd599a6e385c2127"),
    "Candidate Working DB": ("data/working/candidate_rolling_ai_ecosystem.db", "eca573b4a4f1c045f417883772308050418c2d471250be7fda6c68e1ec023198"),
    "Phase V Working DB": ("data/working/phase5_github_candidate.db", "dfa04c1b43204db50b998a34884a12ab7f48d9911dd0a3c07c3824a04711735a")
}

print("=" * 80)
print("PRE-REMEDIATION DATABASE HASH RECORDING")
print("=" * 80)

all_ok = True
for name, (path, expected) in databases.items():
    with open(path, "rb") as f:
        actual = hashlib.sha256(f.read()).hexdigest()
    match = (actual == expected)
    if not match:
        all_ok = False
    print(f"{name:25}: Match={str(match):5} | Actual={actual}")

print(f"\nAll 5 databases match expected hashes: {all_ok}")

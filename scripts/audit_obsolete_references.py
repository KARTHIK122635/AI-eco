import os
import ast
import re

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

obsolete_names = [
    "analyze_117_uncertain_details", "analyze_73_candidates", "analyze_ai_records",
    "analyze_all_155", "analyze_all_282", "analyze_and_resolve_52",
    "analyze_anthropic_responsibilities", "analyze_audit9_targets", "analyze_audit_categories",
    "analyze_candidate_sections", "analyze_canonical_schema", "analyze_history",
    "analyze_non_verbatim_sources", "apply_stage2_corrections_v10", "apply_stage2_corrections_v11",
    "apply_stage2_corrections_v12", "apply_stage2_corrections_v13", "apply_stage2_corrections_v14",
    "apply_stage2_corrections_v15", "apply_stage2_corrections_v3", "apply_stage2_corrections_v4",
    "apply_stage2_corrections_v5", "apply_stage2_corrections_v6", "apply_stage2_corrections_v7",
    "apply_stage2_corrections_v8", "apply_stage2_corrections_v9", "build_audit15_remediations",
    "compute_audit13_checksums", "compute_audit14_checksums", "compute_audit15_checksums",
    "design_audit13_fixes", "find_all_audit13_evidence_issues", "generate_audit10_independent_report",
    "generate_audit14_independent_report", "inspect_audit14_priorities", "inspect_audit15_cited",
    "scan_audit13_residuals_strict", "scan_audit15_candidates", "simulate_audit14_cleanup",
    "test_audit10_status_breakdown", "test_audit13_evidence_cleanup", "test_audit13_full_pipeline",
    "test_audit15_remediations", "verify_audit10_comprehensive", "verify_audit13_comprehensive",
    "verify_audit14_comprehensive", "verify_audit15_comprehensive"
]

references = {k: [] for k in obsolete_names}

for root, dirs, files in os.walk(WORKSPACE_ROOT):
    # skip package snapshots to see active references
    rel = os.path.relpath(root, WORKSPACE_ROOT).replace("\\", "/")
    for f in files:
        if f.endswith((".py", ".json", ".sh", ".ps1", ".bat", ".md")):
            fp = os.path.join(root, f)
            rel_f = os.path.relpath(fp, WORKSPACE_ROOT).replace("\\", "/")
            if rel_f.startswith("reports/project_cleanup"):
                continue
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as rf:
                    content = rf.read()
                    for name in obsolete_names:
                        if name in content and rel_f != f"scripts/{name}.py":
                            references[name].append(rel_f)
            except:
                pass

print("=== REFERENCES TO 47 OBSOLETE SCRIPTS ===")
for name in obsolete_names:
    refs = references[name]
    active_refs = [r for r in refs if not "PACKAGE" in r and not r.startswith("archive")]
    print(f"{name:<40}: {len(refs)} total refs, {len(active_refs)} in active repo")
    if active_refs:
        print(f"   Active refs: {active_refs[:5]}")

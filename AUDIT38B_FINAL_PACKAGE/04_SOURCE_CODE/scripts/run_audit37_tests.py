"""
Audit 37 Complete Test Suite Discovery and Execution Runner
===========================================================
Discovers all tests in tests/, captures clean stdout/stderr to
reports/audit37_test_runner_output.txt and audit37_test_runner_output.txt,
validates 100% pass rate, and itemizes exact per-module counts.
"""

import os
import sys
import shutil
import unittest
from datetime import datetime, timezone

WORKSPACE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
REPORTS_DIR = os.path.join(WORKSPACE_DIR, "reports")
OUTPUT_FILE = os.path.join(REPORTS_DIR, "audit37_test_runner_output.txt")
ROOT_OUTPUT_FILE = os.path.join(WORKSPACE_DIR, "audit37_test_runner_output.txt")


def run_tests():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.join(WORKSPACE_DIR, "tests"))

    # Compute per-module counts
    modules = {}
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            for sub in item:
                if isinstance(sub, unittest.TestSuite):
                    for case in sub:
                        mod = case.__class__.__module__
                        modules[mod] = modules.get(mod, 0) + 1
                else:
                    mod = sub.__class__.__module__
                    modules[mod] = modules.get(mod, 0) + 1
        else:
            mod = item.__class__.__module__
            modules[mod] = modules.get(mod, 0) + 1

    total_discovered = sum(modules.values())
    print(f"Discovered {total_discovered} tests across {len(modules)} test modules.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"================================================================================\n")
        f.write(f"   AUDIT 37 COMPLETE TEST SUITE DISCOVERY AND RUNNER VERIFICATION\n")
        f.write(f"   Timestamp: {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"   Total Discovered Tests: {total_discovered}\n")
        f.write(f"================================================================================\n\n")

        f.write("Discovered Test Modules Breakdown:\n")
        for mod, cnt in sorted(modules.items()):
            f.write(f"  - {mod}: {cnt} tests\n")
        f.write("\n" + "=" * 80 + "\n\n")

        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        result = runner.run(suite)

        f.write("\n" + "=" * 80 + "\n")
        f.write(f"Execution Summary:\n")
        f.write(f"  - Total Discovered: {total_discovered}\n")
        f.write(f"  - Total Run:        {result.testsRun}\n")
        f.write(f"  - Passed:           {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}\n")
        f.write(f"  - Failures:         {len(result.failures)}\n")
        f.write(f"  - Errors:           {len(result.errors)}\n")
        f.write(f"  - Skipped:          {len(result.skipped)}\n")
        f.write(f"  - Was Successful:   {result.wasSuccessful()}\n")
        f.write("=" * 80 + "\n")

    # Mirror to root directory
    shutil.copy2(OUTPUT_FILE, ROOT_OUTPUT_FILE)

    print(f"Executed {result.testsRun} tests. Failures: {len(result.failures)}, Errors: {len(result.errors)}, Skipped: {len(result.skipped)}")
    print(f"Output written cleanly to {OUTPUT_FILE} and {ROOT_OUTPUT_FILE}")
    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    run_tests()

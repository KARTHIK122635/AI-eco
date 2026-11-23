"""
Full Test Suite Runner for Audit 38
===================================
Discovers and executes all unit, integration, recovery, concurrency,
and database immutability tests across the entire repository.
Captures verbatim test-runner output to audit38_test_runner_output.txt.
"""

import os
import sys
import unittest
import io
from datetime import datetime, timezone

WORKSPACE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TESTS_DIR = os.path.join(WORKSPACE_DIR, "tests")
OUTPUT_PATH = os.path.join(WORKSPACE_DIR, "audit38_test_runner_output.txt")
REPORTS_OUTPUT_PATH = os.path.join(WORKSPACE_DIR, "reports", "audit38_test_runner_output.txt")

sys.path.insert(0, WORKSPACE_DIR)
sys.path.insert(0, os.path.join(WORKSPACE_DIR, "src"))


def run_all_tests():
    print("=" * 80)
    print("   DISCOVERING AND EXECUTING FULL AUDIT 38 REGRESSION TEST SUITE")
    print("=" * 80)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=TESTS_DIR, pattern="test_*.py")

    total_discovered = suite.countTestCases()
    print(f"Discovered {total_discovered} tests across all test modules in {TESTS_DIR}.\n")

    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)

    start_time = datetime.now(timezone.utc)
    result = runner.run(suite)
    end_time = datetime.now(timezone.utc)
    duration = (end_time - start_time).total_seconds()

    output_str = stream.getvalue()

    header = (
        f"================================================================================\n"
        f"   AUDIT 38 FULL REGRESSION TEST RUNNER REPORT\n"
        f"================================================================================\n"
        f"Execution Timestamp (UTC): {start_time.isoformat()}\n"
        f"Test Discovery Directory:  {TESTS_DIR}\n"
        f"Total Tests Discovered:    {total_discovered}\n"
        f"Total Tests Executed:      {result.testsRun}\n"
        f"Tests Passed:              {result.testsRun - len(result.failures) - len(result.errors)}\n"
        f"Failures:                  {len(result.failures)}\n"
        f"Errors:                    {len(result.errors)}\n"
        f"Skipped:                   {len(result.skipped)}\n"
        f"Execution Duration:        {duration:.2f} seconds\n"
        f"Overall Test Result:       {'SUCCESS (100% PASS)' if result.wasSuccessful() else 'FAILED'}\n"
        f"================================================================================\n\n"
    )

    full_output = header + output_str

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(full_output)

    os.makedirs(os.path.dirname(REPORTS_OUTPUT_PATH), exist_ok=True)
    with open(REPORTS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(full_output)

    print(header)
    print(f"Test output successfully saved to:\n  {OUTPUT_PATH}\n  {REPORTS_OUTPUT_PATH}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

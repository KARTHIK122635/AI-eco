import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import json
from core.engine import CrawlerEngine


async def main():
    engine = CrawlerEngine()
    print("=" * 70)
    print("RUNNING AUTOMATED ACCESSIBILITY & DATA FIELD TEST ON ALL SOURCES")
    print("=" * 70)
    assessments = await engine.test_all_sources()

    results = [a.to_dict() for a in assessments]
    with open("data/source_assessments.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 70)
    print("SOURCE ACCESSIBILITY & COMPLIANCE SUMMARY REPORT")
    print("=" * 70)
    for a in assessments:
        status_str = "ACCESSIBLE" if a.accessible else "RESTRICTED / BLOCKED"
        print(f"\n[Source: {a.source_name}] - {status_str}")
        print(f"  URL: {a.directory_url}")
        print(f"  Status Code: {a.status_code}")
        print(f"  Collection Method: {a.collection_method}")
        print(f"  Bot Protection / Cloudflare: {'YES' if a.bot_protection_detected else 'NO'}")
        print(f"  robots.txt: {a.robots_txt_status}")
        print(f"  Rate Limits & Terms: {a.rate_limits_info}")
        print(f"  Available Fields: {', '.join(a.available_fields)}")
        print(f"  Missing Fields: {', '.join(a.missing_fields)}")
        print(f"  Notes & Alternatives: {a.notes_and_alternatives}")
    print("\n" + "=" * 70)
    print("Report saved to data/source_assessments.json")


if __name__ == "__main__":
    asyncio.run(main())

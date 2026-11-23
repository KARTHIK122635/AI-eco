import argparse
import asyncio
import json
import logging
import sys
from core.engine import CrawlerEngine
from core.registry import SourceRegistry


def parse_args():
    parser = argparse.ArgumentParser(
        description="Startup and AI Product Data Discovery & Collection System"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test each registered source for accessibility, robots.txt, bot protections, and available fields."
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Run discovery and collection pipeline across enabled sources."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Number of records to collect per source (default: 25)."
    )
    parser.add_argument(
        "--sources",
        type=str,
        default="",
        help="Comma-separated list of specific source IDs to run (e.g. ycombinator,huggingface)."
    )
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="List all sources registered in the system."
    )
    return parser.parse_args()


async def main():
    args = parse_args()
    registry = SourceRegistry()
    engine = CrawlerEngine(registry=registry)

    if args.list_sources:
        print("Registered Sources in Registry:")
        for s in registry.list_available_sources():
            status = "ENABLED" if s.get("enabled") else "DISABLED"
            print(f"  [{s['id']}] {s['display_name']} ({status}) - {s['base_url']}")
            print(f"      {s['description']}")
        return

    if args.test:
        print("\n" + "=" * 70)
        print("RUNNING SOURCE ACCESSIBILITY & METADATA AUDIT")
        print("=" * 70)
        assessments = await engine.test_all_sources()
        for a in assessments:
            status = "ACCESSIBLE" if a.accessible else "RESTRICTED / BLOCKED"
            print(f"\n[{a.source_name}] -> {status}")
            print(f"  Base URL: {a.directory_url}")
            print(f"  Method: {a.collection_method}")
            print(f"  Cloudflare / Bot Defense: {'YES' if a.bot_protection_detected else 'NO'}")
            print(f"  robots.txt: {a.robots_txt_status}")
            print(f"  Rate Limits: {a.rate_limits_info}")
            print(f"  Available Fields: {', '.join(a.available_fields)}")
            print(f"  Missing Fields: {', '.join(a.missing_fields)}")
            print(f"  Notes & Alternatives: {a.notes_and_alternatives}")
        print("\nSaved full audit to data/source_assessments.json")
        return

    if args.ingest:
        print("\n" + "=" * 70)
        print(f"STARTING ASYNC DATA INGESTION (Target limit per source: {args.limit})")
        print("=" * 70)

        selected_sources = [s.strip() for s in args.sources.split(",") if s.strip()] if args.sources else None
        all_sources = registry.list_available_sources()

        summary = {}
        for s in all_sources:
            src_id = s["id"]
            if selected_sources and src_id not in selected_sources:
                continue
            if not selected_sources and not s.get("enabled", True):
                print(f"Skipping disabled source: {src_id}")
                continue

            print(f"\n--> Discovering records from {s['display_name']} ({src_id})...")
            res = await engine.ingest_source(src_id, limit=args.limit)
            summary[src_id] = res
            print(f"    Discovered: {res['discovered']} | Added: {res['added']} | Duplicates avoided: {res['duplicates']}")

        all_records = engine.deduplicator.get_all()
        engine.storage.export_csv(all_records)

        print("\n" + "=" * 70)
        print("COLLECTION RUN COMPLETED")
        print("=" * 70)
        print(f"Total Unique Startups & Products Ingested: {len(all_records)}")
        print(f"CSV Export:   {engine.storage.csv_path}")
        print(f"JSONL Export: {engine.storage.jsonl_path}")
        print(f"SQLite DB:    {engine.storage.db_path}")
        return

    # Default if no arguments: print help
    print("No action specified. Run with --test, --ingest, or --help.")


if __name__ == "__main__":
    asyncio.run(main())

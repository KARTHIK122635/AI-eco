import sqlite3
import httpx
import asyncio
from datetime import datetime, timezone

conn = sqlite3.connect('data/working/rolling_ai_ecosystem.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Update the 33 records first
c.execute("""
    UPDATE ai_jobs
    SET job_status = 'EMPLOYER_CONFIRMED_OPEN'
    WHERE job_status IS NULL AND source_name LIKE 'Greenhouse%'
""")
upd_gh = c.rowcount

c.execute("""
    UPDATE ai_jobs
    SET job_status = 'AGGREGATOR_LISTED',
        vacancy_status = 'SOURCE_LISTED'
    WHERE job_status IS NULL AND source_name LIKE '%API%'
""")
upd_api = c.rowcount

conn.commit()
print(f"Updated {upd_gh} Greenhouse records to EMPLOYER_CONFIRMED_OPEN.")
print(f"Updated {upd_api} Aggregator records to AGGREGATOR_LISTED and SOURCE_LISTED.")

# Verify zero nulls
c.execute("SELECT count(*) FROM ai_jobs WHERE job_status IS NULL")
print("Remaining NULL job_status:", c.fetchone()[0])

conn.close()

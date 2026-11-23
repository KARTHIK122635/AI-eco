import json
import sqlite3
import os

conn = sqlite3.connect('data/normalized/ai_ecosystem.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in c.fetchall()]
print('Tables in DB:', tables)
for t in tables:
    c.execute(f"SELECT count(*) FROM {t}")
    print(f'  {t}: {c.fetchone()[0]} rows')

c.execute("PRAGMA table_info(ai_jobs)")
cols = [r[1] for r in c.fetchall()]
print(f'ai_jobs columns ({len(cols)}): {cols}')

c.execute("SELECT category, count(*) FROM ai_jobs GROUP BY category ORDER BY count(*) DESC")
print('\nCategories in DB:')
for cat, cnt in c.fetchall():
    print(f'  {cat}: {cnt}')

c.execute("SELECT compensation_type, count(*) FROM ai_jobs GROUP BY compensation_type ORDER BY count(*) DESC")
print('\nCompensation types in DB:')
for comp, cnt in c.fetchall():
    print(f'  {comp}: {cnt}')

c.execute("SELECT vacancy_status, count(*) FROM ai_jobs GROUP BY vacancy_status ORDER BY count(*) DESC")
print('\nVacancy statuses in DB:')
for st, cnt in c.fetchall():
    print(f'  {st}: {cnt}')

c.execute("SELECT job_status, count(*) FROM ai_jobs GROUP BY job_status ORDER BY count(*) DESC")
print('\nJob statuses in DB:')
for st, cnt in c.fetchall():
    print(f'  {st}: {cnt}')

c.execute("SELECT count(*) FROM ai_jobs WHERE salary_min IS NOT NULL")
print(f'\nNon-null salary_min count: {c.fetchone()[0]}')

c.execute("SELECT count(*) FROM ai_jobs WHERE company_website IS NOT NULL AND company_website != ''")
print(f'Populated company_website count: {c.fetchone()[0]}')

c.execute("SELECT count(*) FROM ai_jobs WHERE preferred_skills IS NOT NULL AND preferred_skills != '[]'")
print(f'Populated preferred_skills count: {c.fetchone()[0]}')

conn.close()

if os.path.exists('data/destination_evidence_all.json'):
    with open('data/destination_evidence_all.json', 'r', encoding='utf-8') as f:
        ev = json.load(f)
    print(f'\nDestination evidence records: {len(ev)}')

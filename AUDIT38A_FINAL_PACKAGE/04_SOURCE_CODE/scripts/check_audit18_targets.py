import json
import csv
import sqlite3

target_ids = [
    'job_635816dfd21a2298',
    'job_58809b0308baf230',
    'job_4dbed03c7b9d1981',
    'job_675a85266ca800bd'
]

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jsonl_jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

with open('data/canonical/canonical_jobs.csv', 'r', encoding='utf-8') as f:
    csv_jobs = {row['jobId']: row for row in csv.DictReader(f)}

conn = sqlite3.connect('data/normalized/ai_ecosystem.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

for jid in target_ids:
    j = jsonl_jobs[jid]
    c = csv_jobs[jid]
    cur.execute('SELECT * FROM ai_jobs WHERE job_id = ?', (jid,))
    db_row = dict(cur.fetchone())
    
    print('='*60)
    print(f"Job ID: {jid} | {j['companyName']} - {j['jobTitle']}")
    print(f"JSONL: {j['provenance']}")
    print(f"CSV:   {c['provenance']}")
    print(f"DB:    {db_row['provenance']}")
    
    parsed_db = json.loads(db_row['provenance'])
    assert 'source' in parsed_db
    assert 'raw_compensation_disclosure' in parsed_db
    assert parsed_db['source'] == j['provenance']['source']
    assert parsed_db['raw_compensation_disclosure'] == j['provenance']['raw_compensation_disclosure']
    print('=> All fields confirmed present and identical!')

conn.close()

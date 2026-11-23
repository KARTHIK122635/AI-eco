import json
import re
import httpx

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

boards = {
    'Greenhouse: Anthropic': ('greenhouse', 'https://boards-api.greenhouse.io/v1/boards/anthropic/jobs'),
    'Greenhouse: CoreWeave': ('greenhouse', 'https://boards-api.greenhouse.io/v1/boards/coreweave/jobs'),
    'Greenhouse: Databricks': ('greenhouse', 'https://boards-api.greenhouse.io/v1/boards/databricks/jobs'),
    'Greenhouse: Scale AI': ('greenhouse', 'https://boards-api.greenhouse.io/v1/boards/scaleai/jobs'),
    'Greenhouse: Cresta': ('greenhouse', 'https://boards-api.greenhouse.io/v1/boards/cresta/jobs'),
    'Greenhouse: SambaNova Systems': ('greenhouse', 'https://boards-api.greenhouse.io/v1/boards/sambanovasystems/jobs'),
    'Greenhouse: Together AI': ('greenhouse', 'https://boards-api.greenhouse.io/v1/boards/togetherai/jobs'),
    'Greenhouse: Snorkel AI': ('greenhouse', 'https://boards-api.greenhouse.io/v1/boards/snorkelai/jobs'),
    'Greenhouse: Figure AI': ('greenhouse', 'https://boards-api.greenhouse.io/v1/boards/figure/jobs'),
    'Greenhouse: Labelbox': ('greenhouse', 'https://boards-api.greenhouse.io/v1/boards/labelbox/jobs'),
    'Greenhouse: Stability AI': ('greenhouse', 'https://boards-api.greenhouse.io/v1/boards/stabilityai/jobs'),
    'Lever: Palantir Technologies': ('lever', 'https://api.lever.co/v0/postings/palantir'),
    'Lever: Zilliz': ('lever', 'https://api.lever.co/v0/postings/zilliz'),
}

api_jobs_by_board = {}
with httpx.Client(timeout=15.0) as client:
    for s_name, (b_type, url) in boards.items():
        try:
            r = client.get(url)
            if b_type == 'greenhouse':
                data = r.json().get('jobs', [])
                id_map = {str(item['id']): item for item in data}
            else:
                data = r.json()
                id_map = {str(item['id']): item for item in data}
            api_jobs_by_board[s_name] = id_map
        except Exception as e:
            print(f"Error loading {s_name}: {e}")

matched_by_source = {}
total_by_source = {}

for j in jobs:
    s_name = j['sourceName']
    if s_name in api_jobs_by_board:
        total_by_source[s_name] = total_by_source.get(s_name, 0) + 1
        url = j['applicationUrl']
        
        # Extract requisition ID from url
        # Options: /jobs/([0-9]+), gh_jid=([0-9]+), ?([0-9]+)&, lever uuid
        m_gh_jid = re.search(r'gh_jid=([0-9]+)', url)
        m_gh_path = re.search(r'/jobs/([0-9]+)', url)
        m_gh_query = re.search(r'\?([0-9]{7,})', url)
        m_lev = re.search(r'/([a-f0-9\-]{20,})', url)
        
        req_id = None
        if m_gh_jid:
            req_id = m_gh_jid.group(1)
        elif m_gh_path:
            req_id = m_gh_path.group(1)
        elif m_gh_query:
            req_id = m_gh_query.group(1)
        elif m_lev:
            req_id = m_lev.group(1)
            
        board_data = api_jobs_by_board[s_name]
        if req_id and req_id in board_data:
            matched_by_source[s_name] = matched_by_source.get(s_name, 0) + 1

print("\nSource Matching Breakdown:")
for s_name in total_by_source:
    tot = total_by_source[s_name]
    mat = matched_by_source.get(s_name, 0)
    print(f"  {s_name:<32}: {mat:>4} / {tot:>4} matched in official ATS API ({mat/tot*100:.1f}%)")

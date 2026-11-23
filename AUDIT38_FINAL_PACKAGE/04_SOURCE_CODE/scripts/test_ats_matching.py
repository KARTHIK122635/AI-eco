import json
import re
import httpx

# 1. Load canonical jobs
with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f if line.strip()]

print(f"Total canonical jobs: {len(jobs)}")

# Group by source
sources = {}
for j in jobs:
    s = j['sourceName']
    sources[s] = sources.get(s, 0) + 1

for s, cnt in sources.items():
    print(f"  {s:<32}: {cnt}")

# Query all ATS APIs
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
                # map id as string
                id_map = {str(item['id']): item for item in data}
            else:
                data = r.json()
                id_map = {str(item['id']): item for item in data}
            api_jobs_by_board[s_name] = id_map
            print(f"Loaded {len(id_map)} active positions from {s_name} API")
        except Exception as e:
            print(f"Error loading {s_name}: {e}")

# Now match each job
matched = 0
not_matched = 0
match_details = []

for j in jobs:
    s_name = j['sourceName']
    if s_name in api_jobs_by_board:
        url = j['applicationUrl']
        # Extract requisition ID from url
        # e.g. https://job-boards.greenhouse.io/anthropic/jobs/5456619008 -> 5456619008
        # e.g. https://jobs.lever.co/palantir/5189eb86-50a4-44df-90a5-f489cbe9949d -> 5189eb86-50a4-44df-90a5-f489cbe9949d
        m_gh = re.search(r'/jobs/([0-9]+)', url)
        m_lev = re.search(r'/([a-f0-9\-]{20,})', url)
        
        req_id = None
        if m_gh:
            req_id = m_gh.group(1)
        elif m_lev:
            req_id = m_lev.group(1)
            
        board_data = api_jobs_by_board[s_name]
        if req_id and req_id in board_data:
            matched += 1
            match_details.append((j['jobId'], s_name, req_id, True, board_data[req_id].get('title', '')))
        else:
            not_matched += 1
            match_details.append((j['jobId'], s_name, req_id, False, 'NOT_IN_CURRENT_API'))

print(f"\nATS Matching Results:")
print(f"  Total ATS Jobs: {len(match_details)}")
print(f"  Matched in Live API: {matched}")
print(f"  Not Matched in Live API: {not_matched}")

import httpx

urls = [
    ('job_0c738ca8ba2349af', 'Palantir', 'https://jobs.lever.co/palantir/0a838e66-1ab0-4fc4-b4d3-4671c0352278/apply'),
    ('job_0c7e2e256cfb7dba', 'Palantir', 'https://jobs.lever.co/palantir/3531977a-9b2f-40a0-a486-4eeb38e75fc1/apply'),
    ('job_158e31214c4c0228', 'Palantir', 'https://jobs.lever.co/palantir/18d901fc-93bb-4d18-9f04-c72031e20d79/apply'),
    ('job_160616fb43936cab', 'Palantir', 'https://jobs.lever.co/palantir/dab396d4-2f14-4796-aac0-0d82883dccf0/apply'),
    ('job_16fc23a0faeead87', 'Palantir', 'https://jobs.lever.co/palantir/d7030550-f80f-422c-965f-3120db433dea/apply'),
    ('job_0c9a644f7ce24142', 'Zilliz', 'https://jobs.lever.co/zilliz/193ba194-6df6-4894-9f1b-05ace809c60a/apply'),
    ('job_42f62c099c1fde9e', 'Zilliz', 'https://jobs.lever.co/zilliz/5e73c85a-7acf-43f1-8936-68396bb74e82/apply'),
    ('job_7a2f4f5d6e716be5', 'Zilliz', 'https://jobs.lever.co/zilliz/02848077-ca83-461e-87cd-e8b95d7f0c51/apply'),
    ('job_201518350968ce4f', 'iMerit', 'https://remotive.com/remote-jobs/artificial-intelligence/ai-trainer-video-annotation-2091161')
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI-Vacancy-Audit/2.0'}

for jid, comp, url in urls:
    try:
        r = httpx.get(url, headers=headers, follow_redirects=True, timeout=12.0)
        t_start = r.text.find('<title>')
        t_end = r.text.find('</title>')
        title_str = r.text[t_start+7:t_end].strip() if t_start != -1 and t_end != -1 else 'No title'
        text_lower = r.text.lower()
        has_closed = any(c in text_lower for c in ['no longer available', 'job has expired', 'this posting is closed', 'closed', '404'])
        has_form = 'application' in text_lower and ('first_name' in text_lower or 'email' in text_lower or 'resume' in text_lower)
        print(f"[{jid}] ({comp}) HTTP {r.status_code}")
        print(f"    Final URL: {r.url}")
        print(f"    Title:     {title_str}")
        print(f"    Has Form:  {has_form} | Closed Signals: {has_closed}")
        print()
    except Exception as e:
        print(f"[{jid}] Error: {e}")

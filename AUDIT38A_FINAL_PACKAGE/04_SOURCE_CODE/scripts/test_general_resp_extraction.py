import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

resp_headers = [
    r'Key responsibilities',
    r'Responsibilities include',
    r'Responsibilities:',
    r'Responsibilities',
    r'What you\'ll do:',
    r'What you\'ll do',
    r'What you will do:',
    r'What you will do',
    r'Role Responsibilities',
    r'Duties and Responsibilities',
    r'Essential Duties',
    r'You will:',
    r'In this role you will'
]

end_headers = [
    r'You may be a good fit if you',
    r'What we\'re looking for',
    r'What you\'ll need',
    r'What you need to succeed',
    r'Qualifications',
    r'Minimum qualifications',
    r'Preferred qualifications',
    r'Requirements',
    r'Basic Qualifications',
    r'Who you are',
    r'About the team',
    r'About us',
    r'Compensation',
    r'Benefits',
    r'Logistics'
]

start_regex = re.compile(r'\b(?:' + '|'.join(resp_headers) + r')\b', re.I)
end_regex = re.compile(r'\b(?:' + '|'.join(end_headers) + r')\b', re.I)

found_count = 0
for j in jobs:
    desc = j['jobDescription']
    m_s = start_regex.search(desc)
    if m_s:
        found_count += 1

print(f"Jobs with recognizable responsibilities section: {found_count} / {len(jobs)} ({found_count/len(jobs)*100:.1f}%)")
